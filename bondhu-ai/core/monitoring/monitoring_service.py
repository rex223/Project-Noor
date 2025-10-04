"""
Monitoring and Alerting System for API Rate Limiting

Provides comprehensive monitoring of quota usage, API performance,
and automated alerting when thresholds are exceeded.
"""

import asyncio
import logging
import smtplib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass
from enum import Enum

from core.services.rate_limiter_service import rate_limiter_service
from core.cache.redis_rate_limiter import redis_manager, APIType

logger = logging.getLogger("bondhu.monitoring")


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertType(Enum):
    """Types of alerts that can be triggered"""
    QUOTA_WARNING = "quota_warning"
    QUOTA_CRITICAL = "quota_critical"
    QUOTA_EXCEEDED = "quota_exceeded"
    QUEUE_DEPTH_HIGH = "queue_depth_high"
    CACHE_HIT_RATE_LOW = "cache_hit_rate_low"
    API_ERROR_RATE_HIGH = "api_error_rate_high"
    RESPONSE_TIME_HIGH = "response_time_high"
    REDIS_DISCONNECTED = "redis_disconnected"
    SYSTEM_OVERLOAD = "system_overload"


@dataclass
class Alert:
    """Alert data structure"""
    alert_type: AlertType
    level: AlertLevel
    message: str
    timestamp: datetime
    user_id: Optional[str] = None
    api_type: Optional[str] = None
    current_value: Optional[float] = None
    threshold_value: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class MonitoringService:
    """Service for monitoring API usage and system health"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize monitoring service"""
        self.config = config or self._get_default_config()
        self.rate_limiter = rate_limiter_service
        self.redis = redis_manager
        
        # Alert handlers
        self.alert_handlers: List[Callable[[Alert], None]] = []
        
        # Monitoring state
        self.monitoring_active = False
        self.last_check_time = datetime.utcnow()
        self.alert_history: List[Alert] = []
        
        # Metrics cache
        self.metrics_cache = {}
        self.cache_expiry = datetime.utcnow()
        
        logger.info("MonitoringService initialized")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default monitoring configuration"""
        return {
            "enabled": True,
            "check_interval": 60,  # seconds
            "alert_thresholds": {
                "quota_warning": 0.7,      # 70%
                "quota_critical": 0.9,     # 90%
                "queue_depth_high": 50,
                "cache_hit_rate_low": 0.4, # 40%
                "api_error_rate_high": 0.1, # 10%
                "response_time_high": 5000  # 5 seconds
            },
            "alert_cooldown": 300,  # 5 minutes between same alerts
            "email": {
                "enabled": False,
                "smtp_server": "localhost",
                "smtp_port": 587,
                "from_email": "alerts@bondhuai.com",
                "to_emails": ["admin@bondhuai.com"]
            }
        }
    
    # ===== MONITORING METHODS =====
    
    async def start_monitoring(self):
        """Start continuous monitoring"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        logger.info("Starting continuous monitoring")
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        logger.info("Monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.config["check_interval"])
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(10)  # Short delay before retrying
    
    async def _perform_health_checks(self):
        """Perform all health checks and trigger alerts if needed"""
        
        current_time = datetime.utcnow()
        
        # Check Redis health
        await self._check_redis_health()
        
        # Check quota usage for all APIs
        await self._check_quota_usage()
        
        # Check queue depths
        await self._check_queue_depths()
        
        # Check API performance metrics
        await self._check_api_performance()
        
        # Check cache performance
        await self._check_cache_performance()
        
        # Clean up old alerts
        self._cleanup_old_alerts()
        
        self.last_check_time = current_time
    
    async def _check_redis_health(self):
        """Check Redis connection and health"""
        try:
            health_status = self.redis.health_check()
            
            if not health_status.get("connected", False):
                await self._trigger_alert(Alert(
                    alert_type=AlertType.REDIS_DISCONNECTED,
                    level=AlertLevel.CRITICAL,
                    message="Redis connection lost",
                    timestamp=datetime.utcnow(),
                    metadata=health_status
                ))
                
        except Exception as e:
            await self._trigger_alert(Alert(
                alert_type=AlertType.REDIS_DISCONNECTED,
                level=AlertLevel.EMERGENCY,
                message=f"Redis health check failed: {str(e)}",
                timestamp=datetime.utcnow()
            ))
    
    async def _check_quota_usage(self):
        """Check quota usage across all users and APIs"""
        
        # Get list of active users (this would come from user management system)
        # For now, check cached quota data
        
        try:
            warning_threshold = self.config["alert_thresholds"]["quota_warning"]
            critical_threshold = self.config["alert_thresholds"]["quota_critical"]
            
            # Check quota usage from Redis keys
            quota_keys = self.redis._client.keys("quota:*:*") if self.redis.is_connected else []
            
            for key in quota_keys:
                try:
                    # Parse key: quota:api_type:user_id
                    _, api_type, user_id = key.split(":", 2)
                    
                    # Get usage and limits
                    current_usage = self.redis.get_quota_usage(api_type, user_id)
                    
                    # Get user tier and limits (would need user management integration)
                    user_tier = "free"  # Default assumption
                    limit = self._get_api_limit(api_type, user_tier)
                    
                    if limit > 0:
                        usage_percentage = current_usage / limit
                        
                        if usage_percentage >= critical_threshold:
                            await self._trigger_alert(Alert(
                                alert_type=AlertType.QUOTA_CRITICAL,
                                level=AlertLevel.CRITICAL,
                                message=f"Critical quota usage: {api_type} at {usage_percentage:.1%}",
                                timestamp=datetime.utcnow(),
                                user_id=user_id,
                                api_type=api_type,
                                current_value=usage_percentage,
                                threshold_value=critical_threshold
                            ))
                            
                        elif usage_percentage >= warning_threshold:
                            await self._trigger_alert(Alert(
                                alert_type=AlertType.QUOTA_WARNING,
                                level=AlertLevel.WARNING,
                                message=f"High quota usage: {api_type} at {usage_percentage:.1%}",
                                timestamp=datetime.utcnow(),
                                user_id=user_id,
                                api_type=api_type,
                                current_value=usage_percentage,
                                threshold_value=warning_threshold
                            ))
                            
                except Exception as e:
                    logger.error(f"Error checking quota for key {key}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Quota usage check failed: {e}")
    
    async def _check_queue_depths(self):
        """Check request queue depths"""
        
        try:
            threshold = self.config["alert_thresholds"]["queue_depth_high"]
            
            # Get queue keys
            queue_keys = self.redis._client.keys("queue:*") if self.redis.is_connected else []
            
            for key in queue_keys:
                try:
                    # Parse key: queue:user_id
                    _, user_id = key.split(":", 1)
                    
                    queue_depth = self.redis.get_queue_depth(user_id)
                    
                    if queue_depth >= threshold:
                        await self._trigger_alert(Alert(
                            alert_type=AlertType.QUEUE_DEPTH_HIGH,
                            level=AlertLevel.WARNING,
                            message=f"High queue depth for user {user_id}: {queue_depth} items",
                            timestamp=datetime.utcnow(),
                            user_id=user_id,
                            current_value=queue_depth,
                            threshold_value=threshold
                        ))
                        
                except Exception as e:
                    logger.error(f"Error checking queue depth for key {key}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Queue depth check failed: {e}")
    
    async def _check_api_performance(self):
        """Check API performance metrics"""
        
        try:
            error_rate_threshold = self.config["alert_thresholds"]["api_error_rate_high"]
            response_time_threshold = self.config["alert_thresholds"]["response_time_high"]
            
            today = datetime.utcnow().strftime("%Y-%m-%d")
            
            for api_type in APIType:
                metrics = self.redis.get_api_metrics(api_type.value, today)
                
                if metrics:
                    # Check error rate
                    total_calls = metrics.get("total_calls", 0)
                    failed_calls = metrics.get("failed_calls", 0)
                    
                    if total_calls > 0:
                        error_rate = failed_calls / total_calls
                        
                        if error_rate >= error_rate_threshold:
                            await self._trigger_alert(Alert(
                                alert_type=AlertType.API_ERROR_RATE_HIGH,
                                level=AlertLevel.WARNING,
                                message=f"High error rate for {api_type.value}: {error_rate:.1%}",
                                timestamp=datetime.utcnow(),
                                api_type=api_type.value,
                                current_value=error_rate,
                                threshold_value=error_rate_threshold
                            ))
                    
                    # Check response time
                    avg_response_time = metrics.get("avg_response_time", 0)
                    
                    if avg_response_time >= response_time_threshold:
                        await self._trigger_alert(Alert(
                            alert_type=AlertType.RESPONSE_TIME_HIGH,
                            level=AlertLevel.WARNING,
                            message=f"High response time for {api_type.value}: {avg_response_time:.0f}ms",
                            timestamp=datetime.utcnow(),
                            api_type=api_type.value,
                            current_value=avg_response_time,
                            threshold_value=response_time_threshold
                        ))
                        
        except Exception as e:
            logger.error(f"API performance check failed: {e}")
    
    async def _check_cache_performance(self):
        """Check cache hit rates and performance"""
        
        try:
            threshold = self.config["alert_thresholds"]["cache_hit_rate_low"] 
            
            # Calculate cache hit rate from Redis metrics
            # This would need to be implemented based on actual cache metrics
            
            # For now, placeholder implementation
            cache_hit_rate = 0.65  # Example value
            
            if cache_hit_rate < threshold:
                await self._trigger_alert(Alert(
                    alert_type=AlertType.CACHE_HIT_RATE_LOW,
                    level=AlertLevel.WARNING,
                    message=f"Low cache hit rate: {cache_hit_rate:.1%}",
                    timestamp=datetime.utcnow(),
                    current_value=cache_hit_rate,
                    threshold_value=threshold
                ))
                
        except Exception as e:
            logger.error(f"Cache performance check failed: {e}")
    
    # ===== ALERT MANAGEMENT =====
    
    async def _trigger_alert(self, alert: Alert):
        """Trigger an alert if not in cooldown period"""
        
        # Check if this alert type is in cooldown
        if self._is_alert_in_cooldown(alert):
            return
        
        # Add to alert history
        self.alert_history.append(alert)
        
        # Log the alert
        log_level = {
            AlertLevel.INFO: logger.info,
            AlertLevel.WARNING: logger.warning,
            AlertLevel.CRITICAL: logger.error,
            AlertLevel.EMERGENCY: logger.critical
        }
        
        log_level[alert.level](f"ALERT [{alert.level.value.upper()}]: {alert.message}")
        
        # Trigger alert handlers
        for handler in self.alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                logger.error(f"Alert handler error: {e}")
    
    def _is_alert_in_cooldown(self, alert: Alert) -> bool:
        """Check if alert type is in cooldown period"""
        
        cooldown_period = timedelta(seconds=self.config["alert_cooldown"])
        current_time = datetime.utcnow()
        
        # Check recent alerts of same type
        for past_alert in reversed(self.alert_history):
            if (past_alert.alert_type == alert.alert_type and
                past_alert.user_id == alert.user_id and
                past_alert.api_type == alert.api_type):
                
                time_diff = current_time - past_alert.timestamp
                if time_diff < cooldown_period:
                    return True
                break
        
        return False
    
    def _cleanup_old_alerts(self):
        """Remove old alerts from history"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        self.alert_history = [
            alert for alert in self.alert_history 
            if alert.timestamp > cutoff_time
        ]
    
    # ===== ALERT HANDLERS =====
    
    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """Add custom alert handler"""
        self.alert_handlers.append(handler)
        logger.info(f"Alert handler added: {handler.__name__}")
    
    async def email_alert_handler(self, alert: Alert):
        """Send alert via email"""
        
        if not self.config["email"]["enabled"]:
            return
            
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.config["email"]["from_email"]
            msg['To'] = ", ".join(self.config["email"]["to_emails"])
            msg['Subject'] = f"Bondhu AI Alert [{alert.level.value.upper()}]: {alert.alert_type.value}"
            
            # Email body
            body = f"""
            Alert Details:
            
            Type: {alert.alert_type.value}
            Level: {alert.level.value}
            Message: {alert.message}
            Timestamp: {alert.timestamp.isoformat()}
            
            """
            
            if alert.user_id:
                body += f"User ID: {alert.user_id}\n"
            if alert.api_type:
                body += f"API Type: {alert.api_type}\n"
            if alert.current_value is not None:
                body += f"Current Value: {alert.current_value}\n"
            if alert.threshold_value is not None:
                body += f"Threshold: {alert.threshold_value}\n"
            
            if alert.metadata:
                body += f"\nAdditional Info:\n{alert.metadata}\n"
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(
                self.config["email"]["smtp_server"],
                self.config["email"]["smtp_port"]
            )
            server.starttls()
            
            text = msg.as_string()
            server.sendmail(
                self.config["email"]["from_email"],
                self.config["email"]["to_emails"],
                text
            )
            server.quit()
            
            logger.info(f"Alert email sent: {alert.alert_type.value}")
            
        except Exception as e:
            logger.error(f"Failed to send alert email: {e}")
    
    # ===== METRICS AND REPORTING =====
    
    async def get_system_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive system health report"""
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "monitoring_active": self.monitoring_active,
            "last_check": self.last_check_time.isoformat(),
            "redis_health": self.redis.health_check(),
            "recent_alerts": []
        }
        
        # Add recent alerts (last 24 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        recent_alerts = [
            {
                "type": alert.alert_type.value,
                "level": alert.level.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "user_id": alert.user_id,
                "api_type": alert.api_type
            }
            for alert in self.alert_history
            if alert.timestamp > cutoff_time
        ]
        
        report["recent_alerts"] = recent_alerts
        report["alert_summary"] = {
            "total": len(recent_alerts),
            "critical": len([a for a in recent_alerts if a["level"] == "critical"]),
            "warning": len([a for a in recent_alerts if a["level"] == "warning"])
        }
        
        # Add API metrics
        report["api_metrics"] = {}
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        for api_type in APIType:
            metrics = self.redis.get_api_metrics(api_type.value, today)
            if metrics:
                report["api_metrics"][api_type.value] = metrics
        
        return report
    
    def _get_api_limit(self, api_type: str, user_tier: str) -> int:
        """Get API limit for user tier (helper method)"""
        # This should integrate with the rate limiter configuration
        tier_limits = {
            "free": {"youtube": 50, "spotify": 20, "openai": 100, "gaming": 50},
            "premium": {"youtube": 500, "spotify": 180, "openai": 1000, "gaming": 200},
            "enterprise": {"youtube": 2000, "spotify": 500, "openai": 5000, "gaming": 1000}
        }
        
        return tier_limits.get(user_tier, {}).get(api_type, 0)


# Initialize singleton
monitoring_service = MonitoringService()

# Add default email alert handler
monitoring_service.add_alert_handler(monitoring_service.email_alert_handler)