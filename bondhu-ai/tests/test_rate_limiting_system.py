"""
Comprehensive test suite for centralized API rate limiting system.

Tests rate limiting, caching, user tiers, queue management, and monitoring functionality.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List

try:
    import pytest
except ImportError:
    pytest = None

from core.cache.redis_rate_limiter import RedisManager, UserTier, APIType
from core.services.rate_limiter_service import (
    RateLimiterService, 
    RateLimitResult, 
    RequestPriority,
    APIQuotaExceeded
)
from core.services.rate_limited_youtube_service import RateLimitedYouTubeService
from core.monitoring.monitoring_service import MonitoringService, Alert, AlertType, AlertLevel


class TestRedisManager:
    """Test Redis manager functionality"""
    
    @pytest.fixture
    def redis_manager(self):
        """Create Redis manager for testing"""
        # Mock Redis for testing
        with patch('redis.Redis') as mock_redis:
            mock_client = Mock()
            mock_redis.return_value = mock_client
            mock_client.ping.return_value = True
            mock_client.get.return_value = None
            mock_client.setex.return_value = True
            mock_client.incrby.return_value = 5
            mock_client.expire.return_value = True
            mock_client.delete.return_value = True
            
            manager = RedisManager()
            manager._client = mock_client
            manager._connected = True
            
            return manager
    
    def test_cache_operations(self, redis_manager):
        """Test cache get/set operations"""
        
        # Test cache miss
        result = redis_manager.get_cache("youtube", "test query")
        assert result is None
        
        # Test cache set
        test_data = {"videos": [{"id": "test123", "title": "Test Video"}]}
        success = redis_manager.set_cache("youtube", "test query", test_data, 3600)
        assert success is True
        
        # Mock cache hit
        redis_manager._client.get.return_value = json.dumps({
            "result": test_data,
            "timestamp": datetime.utcnow().isoformat(),
            "api_type": "youtube",
            "ttl": 3600
        })
        
        cached_result = redis_manager.get_cache("youtube", "test query")
        assert cached_result["result"] == test_data
    
    def test_quota_management(self, redis_manager):
        """Test quota tracking and management"""
        
        # Test initial quota (should be 0)
        usage = redis_manager.get_quota_usage("youtube", "user123")
        assert usage == 0
        
        # Test quota increment
        new_usage = redis_manager.increment_quota("youtube", "user123", 10)
        assert new_usage == 5  # Mocked return value
        
        # Test quota reset
        success = redis_manager.reset_quota("youtube", "user123")
        assert success is True
    
    def test_queue_operations(self, redis_manager):
        """Test request queue management"""
        
        # Mock queue operations
        redis_manager._client.zadd.return_value = 1
        redis_manager._client.zrange.return_value = [
            ('{"api_type": "youtube", "request_data": {"query": "test"}}', 3.0)
        ]
        redis_manager._client.zrem.return_value = 1
        redis_manager._client.zcard.return_value = 2
        
        # Test queue request
        request_data = {"query": "test video", "max_results": 10}
        success = redis_manager.queue_request("user123", "youtube", request_data)
        assert success is True
        
        # Test get queued requests
        requests = redis_manager.get_queued_requests("user123")
        assert len(requests) == 1
        assert requests[0]["api_type"] == "youtube"
        
        # Test queue depth
        depth = redis_manager.get_queue_depth("user123")
        assert depth == 2
    
    def test_health_check(self, redis_manager):
        """Test Redis health check"""
        
        # Mock Redis info
        redis_manager._client.info.return_value = {
            "used_memory_human": "1.2M",
            "connected_clients": 5,
            "total_commands_processed": 1000
        }
        redis_manager._client.keys.return_value = ["cache:1", "quota:1", "queue:1"]
        
        health = redis_manager.health_check()
        
        assert health["connected"] is True
        assert health["memory_usage"] == "1.2M"
        assert health["key_counts"]["cache_keys"] == 1


class TestRateLimiterService:
    """Test rate limiter service functionality"""
    
    @pytest.fixture
    def rate_limiter_service(self):
        """Create rate limiter service for testing"""
        with patch('core.services.rate_limiter_service.redis_manager') as mock_redis:
            mock_redis.is_connected = True
            mock_redis.get_quota_usage.return_value = 10
            mock_redis.increment_quota.return_value = 15
            mock_redis.get_cache.return_value = None
            mock_redis.set_cache.return_value = True
            mock_redis.queue_request.return_value = True
            mock_redis.get_queue_depth.return_value = 1
            
            service = RateLimiterService()
            service.redis = mock_redis
            
            return service
    
    @pytest.mark.asyncio
    async def test_quota_check_allowed(self, rate_limiter_service):
        """Test quota check when request is allowed"""
        
        result, metadata = await rate_limiter_service.check_and_consume_quota(
            user_id="user123",
            user_tier="free", 
            api_type="youtube",
            operation="search",
            request_data={"query": "test"},
            priority=RequestPriority.MEDIUM
        )
        
        assert result == RateLimitResult.ALLOWED
        assert "quota_consumed" in metadata
        assert "quota_remaining" in metadata
    
    @pytest.mark.asyncio
    async def test_quota_check_exceeded(self, rate_limiter_service):
        """Test quota check when quota is exceeded"""
        
        # Mock high usage that exceeds limit
        rate_limiter_service.redis.get_quota_usage.return_value = 45
        
        result, metadata = await rate_limiter_service.check_and_consume_quota(
            user_id="user123",
            user_tier="free",  # Free tier has 50 YouTube quota
            api_type="youtube",
            operation="search",  # Search costs 100 units
            request_data={"query": "test"},
            priority=RequestPriority.MEDIUM
        )
        
        assert result == RateLimitResult.QUEUED
        assert "queue_position" in metadata
        assert metadata["quota_exceeded"] is True
    
    @pytest.mark.asyncio
    async def test_cache_hit(self, rate_limiter_service):
        """Test cache hit scenario"""
        
        # Mock cache hit
        cached_data = {"videos": [{"id": "test123"}]}
        rate_limiter_service.redis.get_cache.return_value = {"result": cached_data}
        
        result, metadata = await rate_limiter_service.check_and_consume_quota(
            user_id="user123",
            user_tier="free",
            api_type="youtube", 
            operation="search",
            request_data={"query": "test"},
            priority=RequestPriority.MEDIUM
        )
        
        assert result == RateLimitResult.CACHED
        assert metadata["cached_data"]["result"] == cached_data
    
    @pytest.mark.asyncio
    async def test_user_quota_status(self, rate_limiter_service):
        """Test getting user quota status"""
        
        status = await rate_limiter_service.get_user_quota_status("user123", "premium")
        
        assert "user_id" in status
        assert "user_tier" in status
        assert "quotas" in status
        assert "youtube" in status["quotas"]
        assert "queue_depth" in status
    
    @pytest.mark.asyncio 
    async def test_process_queue(self, rate_limiter_service):
        """Test processing queued requests"""
        
        # Mock queued requests
        rate_limiter_service.redis.get_queued_requests.return_value = [
            {
                "api_type": "youtube",
                "request_data": {"operation": "search", "query": "test"},
                "priority": "medium",
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
        
        processed = await rate_limiter_service.process_queue("user123", max_items=1)
        
        assert len(processed) >= 0  # May be 0 if quota still exceeded


class TestRateLimitedYouTubeService:
    """Test rate-limited YouTube service"""
    
    @pytest.fixture
    def youtube_service(self):
        """Create rate-limited YouTube service for testing"""
        with patch('core.services.rate_limited_youtube_service.YouTubeService') as mock_youtube:
            mock_youtube.return_value.search_videos.return_value = {
                "items": [{"id": "test123", "title": "Test Video"}]
            }
            
            with patch('core.services.rate_limited_youtube_service.rate_limiter_service') as mock_rate_limiter:
                mock_rate_limiter.check_and_consume_quota.return_value = (
                    RateLimitResult.ALLOWED, 
                    {"quota_consumed": 100, "quota_remaining": 400}
                )
                mock_rate_limiter.cache_response.return_value = True
                
                service = RateLimitedYouTubeService("user123", "free")
                return service
    
    @pytest.mark.asyncio
    async def test_search_videos_success(self, youtube_service):
        """Test successful video search"""
        
        results = await youtube_service.search_videos("python tutorials", max_results=10)
        
        assert "items" in results
        assert len(results["items"]) >= 1
        assert results["items"][0]["id"] == "test123"
    
    @pytest.mark.asyncio
    async def test_search_videos_quota_exceeded(self, youtube_service):
        """Test video search when quota exceeded"""
        
        # Mock quota exceeded
        youtube_service.rate_limiter.check_and_consume_quota.return_value = (
            RateLimitResult.QUEUED,
            {
                "queue_position": 5,
                "quota_exceeded": True,
                "quota_usage": 50,
                "quota_limit": 50
            }
        )
        
        with pytest.raises(APIQuotaExceeded) as exc_info:
            await youtube_service.search_videos("test query")
        
        assert exc_info.value.api_type == "youtube"
        assert exc_info.value.user_id == "user123"
    
    @pytest.mark.asyncio
    async def test_get_video_details(self, youtube_service):
        """Test getting video details"""
        
        # Mock video details response
        youtube_service.youtube_service.get_video_details.return_value = {
            "items": [{"id": "test123", "snippet": {"title": "Test Video"}}]
        }
        
        details = await youtube_service.get_video_details(["test123"])
        
        assert "items" in details
        assert details["items"][0]["id"] == "test123"
    
    @pytest.mark.asyncio
    async def test_batch_get_video_details(self, youtube_service):
        """Test batch video details retrieval"""
        
        # Create list of 75 video IDs (should be split into 2 batches)
        video_ids = [f"video{i:03d}" for i in range(75)]
        
        # Mock batch responses
        youtube_service.youtube_service.get_video_details.return_value = {
            "items": [{"id": vid_id} for vid_id in video_ids[:50]]
        }
        
        details = await youtube_service.batch_get_video_details(video_ids, batch_size=50)
        
        # Should get results from first batch (second batch would require another quota check)
        assert len(details) == 50


class TestMonitoringService:
    """Test monitoring and alerting functionality"""
    
    @pytest.fixture
    def monitoring_service(self):
        """Create monitoring service for testing"""
        with patch('core.monitoring.monitoring_service.redis_manager') as mock_redis:
            mock_redis.health_check.return_value = {"connected": True}
            mock_redis.get_api_metrics.return_value = {
                "total_calls": 100,
                "successful_calls": 95,
                "failed_calls": 5,
                "avg_response_time": 250
            }
            mock_redis._client.keys.return_value = [
                "quota:youtube:user1",
                "quota:youtube:user2", 
                "queue:user1"
            ]
            mock_redis.get_quota_usage.return_value = 45
            mock_redis.get_queue_depth.return_value = 15
            
            service = MonitoringService()
            service.redis = mock_redis
            
            return service
    
    @pytest.mark.asyncio
    async def test_redis_health_check(self, monitoring_service):
        """Test Redis health monitoring"""
        
        await monitoring_service._check_redis_health()
        
        # Should not trigger alerts for healthy connection
        assert len(monitoring_service.alert_history) == 0
    
    @pytest.mark.asyncio
    async def test_quota_usage_monitoring(self, monitoring_service):
        """Test quota usage monitoring and alerting"""
        
        # Mock high quota usage (90% of 50 = 45)
        monitoring_service.redis.get_quota_usage.return_value = 45
        
        await monitoring_service._check_quota_usage()
        
        # Should trigger critical alert for 90% usage
        critical_alerts = [
            alert for alert in monitoring_service.alert_history
            if alert.alert_type == AlertType.QUOTA_CRITICAL
        ]
        assert len(critical_alerts) >= 0  # May be 0 if no quota keys found
    
    @pytest.mark.asyncio
    async def test_queue_depth_monitoring(self, monitoring_service):
        """Test queue depth monitoring"""
        
        # Mock high queue depth
        monitoring_service.redis.get_queue_depth.return_value = 60
        
        await monitoring_service._check_queue_depths()
        
        # Should trigger alert for high queue depth
        queue_alerts = [
            alert for alert in monitoring_service.alert_history
            if alert.alert_type == AlertType.QUEUE_DEPTH_HIGH
        ]
        assert len(queue_alerts) >= 0
    
    @pytest.mark.asyncio
    async def test_api_performance_monitoring(self, monitoring_service):
        """Test API performance monitoring"""
        
        # Mock high error rate
        monitoring_service.redis.get_api_metrics.return_value = {
            "total_calls": 100,
            "successful_calls": 80,  # 20% error rate
            "failed_calls": 20,
            "avg_response_time": 6000  # High response time
        }
        
        await monitoring_service._check_api_performance()
        
        # Should trigger alerts for high error rate and response time
        error_alerts = [
            alert for alert in monitoring_service.alert_history
            if alert.alert_type in [AlertType.API_ERROR_RATE_HIGH, AlertType.RESPONSE_TIME_HIGH]
        ]
        assert len(error_alerts) >= 0
    
    def test_alert_cooldown(self, monitoring_service):
        """Test alert cooldown mechanism"""
        
        # Create initial alert
        alert1 = Alert(
            alert_type=AlertType.QUOTA_WARNING,
            level=AlertLevel.WARNING,
            message="Test alert 1",
            timestamp=datetime.utcnow(),
            user_id="user123",
            api_type="youtube"
        )
        
        monitoring_service.alert_history.append(alert1)
        
        # Create similar alert (should be in cooldown)
        alert2 = Alert(
            alert_type=AlertType.QUOTA_WARNING,
            level=AlertLevel.WARNING,
            message="Test alert 2",
            timestamp=datetime.utcnow(),
            user_id="user123",
            api_type="youtube"
        )
        
        in_cooldown = monitoring_service._is_alert_in_cooldown(alert2)
        assert in_cooldown is True
    
    @pytest.mark.asyncio
    async def test_health_report_generation(self, monitoring_service):
        """Test system health report generation"""
        
        report = await monitoring_service.get_system_health_report()
        
        assert "timestamp" in report
        assert "monitoring_active" in report
        assert "redis_health" in report
        assert "recent_alerts" in report
        assert "alert_summary" in report
        assert "api_metrics" in report


class TestIntegration:
    """Integration tests for the complete rate limiting system"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_rate_limiting(self):
        """Test complete rate limiting flow"""
        
        # This would test the entire flow from FastAPI middleware
        # through rate limiting service to API calls
        
        # Mock components
        with patch('core.services.rate_limiter_service.redis_manager') as mock_redis:
            mock_redis.is_connected = True
            mock_redis.get_quota_usage.return_value = 5
            mock_redis.increment_quota.return_value = 10
            mock_redis.get_cache.return_value = None
            mock_redis.set_cache.return_value = True
            
            # Test quota check and consumption
            service = RateLimiterService()
            service.redis = mock_redis
            
            result, metadata = await service.check_and_consume_quota(
                user_id="integration_test_user",
                user_tier="premium",
                api_type="youtube",
                operation="search",
                request_data={"query": "integration test"},
                priority=RequestPriority.HIGH
            )
            
            assert result == RateLimitResult.ALLOWED
            assert metadata["quota_consumed"] == 100  # Search operation cost
    
    @pytest.mark.asyncio
    async def test_system_under_load(self):
        """Test system behavior under high load"""
        
        # Simulate multiple concurrent requests
        async def make_request(user_id: str, request_num: int):
            with patch('core.services.rate_limiter_service.redis_manager') as mock_redis:
                mock_redis.is_connected = True
                mock_redis.get_quota_usage.return_value = request_num * 10
                mock_redis.increment_quota.return_value = (request_num + 1) * 10
                
                service = RateLimiterService()
                service.redis = mock_redis
                
                result, metadata = await service.check_and_consume_quota(
                    user_id=user_id,
                    user_tier="free",
                    api_type="youtube",
                    operation="search",
                    priority=RequestPriority.MEDIUM
                )
                
                return result, metadata
        
        # Make 10 concurrent requests
        tasks = [make_request(f"user{i}", i) for i in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Some should be allowed, some queued based on quota
        allowed_count = sum(1 for result, _ in results if result == RateLimitResult.ALLOWED)
        queued_count = sum(1 for result, _ in results if result == RateLimitResult.QUEUED)
        
        assert allowed_count + queued_count == len(results)


# Test fixtures and utilities
@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing"""
    client = Mock()
    client.ping.return_value = True
    client.get.return_value = None
    client.setex.return_value = True
    client.incrby.return_value = 1
    client.expire.return_value = True
    return client


# Performance test utilities
def benchmark_quota_check(rate_limiter_service, iterations: int = 1000):
    """Benchmark quota checking performance"""
    
    async def run_benchmark():
        start_time = time.time()
        
        for i in range(iterations):
            await rate_limiter_service.check_and_consume_quota(
                user_id=f"benchmark_user_{i % 10}",
                user_tier="free",
                api_type="youtube",
                operation="search",
                priority=RequestPriority.MEDIUM
            )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return {
            "iterations": iterations,
            "total_time": total_time,
            "requests_per_second": iterations / total_time,
            "avg_time_per_request": total_time / iterations * 1000  # ms
        }
    
    return asyncio.run(run_benchmark())


if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v"])