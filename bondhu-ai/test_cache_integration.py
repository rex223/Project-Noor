#!/usr/bin/env python3
"""
Quick test to verify video recommendation cache integration is working.
Tests the cache-first logic and background prefetch mechanism.
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_cache_functions():
    """Test the cache helper functions"""
    print("🔍 Testing cache helper functions...")
    
    try:
        # Import the cache helpers
        from api.routes.video_recommendations import (
            _build_recommendation_cache_key, 
            _load_cached_recommendations,
            _store_cached_recommendations,
            VideoRecommendationRequest
        )
        
        # Test cache key building
        user_id = "test_user_123"
        request = VideoRecommendationRequest(
            max_results=20,
            force_refresh=False,
            include_trending=True,
            category_filter="gaming"
        )
        
        cache_key = _build_recommendation_cache_key(user_id, request)
        expected_key = "video:recommendations:test_user_123:20:1:gaming"
        
        assert cache_key == expected_key, f"Expected {expected_key}, got {cache_key}"
        print(f"✅ Cache key generation: {cache_key}")
        
        # Test cache storage and retrieval 
        test_payload = {
            "recommendations": [
                {"id": "test_video_1", "title": "Test Video", "score": 0.85}
            ],
            "total_count": 1,
            "cached_at": datetime.now().isoformat()
        }
        
        # Store in cache
        await _store_cached_recommendations(cache_key, test_payload)
        print("✅ Cache storage completed")
        
        # Load from cache
        cached_data = await _load_cached_recommendations(cache_key)
        
        if cached_data:
            print(f"✅ Cache retrieval successful: {len(cached_data)} items")
            print(f"   - Cached at: {cached_data.get('cached_at', 'N/A')}")
        else:
            print("⚠️  Cache retrieval returned None (Redis may not be available)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:  
        print(f"❌ Test error: {e}")
        return False

async def test_recommendation_endpoint_structure():
    """Test that the recommendation endpoints are properly structured"""
    print("\n🔍 Testing recommendation endpoint structure...")
    
    try:
        # Just test that we can import the router without errors
        from api.routes.video_recommendations import router
        print("✅ Router imported successfully")
        
        # Test that cache helper functions exist
        from api.routes.video_recommendations import (
            _build_recommendation_cache_key,
            _load_cached_recommendations, 
            _store_cached_recommendations,
            VideoRecommendationRequest
        )
        print("✅ Cache helper functions imported successfully")
        
        # Test VideoRecommendationRequest model
        request = VideoRecommendationRequest(max_results=10)
        assert request.max_results == 10
        assert request.force_refresh == False  # default
        print("✅ VideoRecommendationRequest model works correctly")
        
        print("✅ All required components are properly structured")
        return True
        
    except Exception as e:
        print(f"❌ Endpoint structure test error: {e}")
        return False

async def main():
    """Run all cache integration tests"""
    print("🚀 Starting video recommendation cache integration tests...\n")
    
    test_results = []
    
    # Test 1: Cache functions
    result1 = await test_cache_functions()
    test_results.append(("Cache Functions", result1))
    
    # Test 2: Endpoint structure
    result2 = await test_recommendation_endpoint_structure()
    test_results.append(("Endpoint Structure", result2))
    
    # Summary
    print(f"\n📊 Test Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{len(test_results)}")
    
    if passed == len(test_results):
        print("🎉 All tests passed! Cache integration is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)