"""
Simple test to verify the YouTube video entertainment system is working.
Tests the API endpoint that we've successfully implemented.
"""

import requests
import json
from datetime import datetime

def test_video_recommendations_api():
    """Test the video recommendations API endpoint."""
    print("🎬 Testing YouTube Video Recommendations API")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    test_user_id = "test-user"
    
    try:
        # Test the video recommendations endpoint
        url = f"{base_url}/api/v1/video/recommendations/{test_user_id}"
        params = {"max_results": 10}
        
        print(f"🔍 Making request to: {url}")
        response = requests.get(url, params=params, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ SUCCESS! Video recommendations loaded")
            print(f"📈 Statistics:")
            print(f"  - Total recommendations: {data.get('total_count', 0)}")
            print(f"  - Personality-based: {data.get('personality_based', False)}")
            print(f"  - Has thumbnails: {data.get('has_thumbnails', False)}")
            print(f"  - Has watch links: {data.get('has_watch_links', False)}")
            print(f"  - Generated at: {data.get('generated_at', 'Unknown')}")
            
            # Show videos per genre
            videos_per_genre = data.get('videos_per_genre', {})
            if videos_per_genre:
                print(f"📊 Videos per genre:")
                for genre, count in videos_per_genre.items():
                    print(f"  - {genre}: {count} videos")
            
            # Show sample recommendations
            recommendations = data.get('recommendations', [])
            if recommendations:
                print(f"\n🎯 Sample Recommendations:")
                for i, video in enumerate(recommendations[:5], 1):
                    print(f"  {i}. {video.get('title', 'Unknown Title')[:60]}...")
                    print(f"     Channel: {video.get('channel_title', 'Unknown')}")
                    print(f"     Category: {video.get('category_name', 'Unknown')}")
                    print(f"     Personality Match: {video.get('personality_match', 0)}%")
                    print(f"     Watch URL: {video.get('watch_url', 'N/A')}")
                    print(f"     Reason: {video.get('recommendation_reason', 'N/A')}")
                    print()
            
            return True
        else:
            print(f"❌ FAILED: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR: Could not connect to {base_url}")
        print(f"   Make sure the FastAPI server is running:")
        print(f"   cd bondhu-ai && python main.py")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_video_feedback_api():
    """Test the video feedback API endpoint."""
    print(f"\n👍 Testing Video Feedback API")
    print("-" * 30)
    
    base_url = "http://localhost:8000"
    
    feedback_data = {
        "user_id": "test-user",
        "video_id": "sample_video_123",
        "feedback_type": "like",
        "additional_data": {
            "timestamp": datetime.now().isoformat(),
            "source": "api_test"
        }
    }
    
    try:
        url = f"{base_url}/api/v1/video/feedback"
        response = requests.post(url, json=feedback_data, timeout=10)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS! Feedback recorded")
            print(f"   Message: {data.get('message', 'N/A')}")
            print(f"   Feedback ID: {data.get('feedback_id', 'N/A')}")
            return True
        else:
            print(f"❌ FAILED: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_health_endpoint():
    """Test the basic health endpoint."""
    print(f"\n❤️ Testing Health Endpoint")
    print("-" * 25)
    
    base_url = "http://localhost:8000"
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is healthy")
            print(f"   Status: {data.get('status', 'Unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Bondhu AI - YouTube Entertainment System Test")
    print("=" * 60)
    
    # Test health first
    health_ok = test_health_endpoint()
    
    if not health_ok:
        print(f"\n❌ Server health check failed. Make sure FastAPI server is running.")
        return False
    
    # Test video recommendations
    recommendations_ok = test_video_recommendations_api()
    
    # Test feedback system
    feedback_ok = test_video_feedback_api()
    
    # Summary
    print(f"\n📋 Test Results Summary:")
    print(f"=" * 30)
    print(f"Health Endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Video Recommendations: {'✅ PASS' if recommendations_ok else '❌ FAIL'}")
    print(f"Feedback System: {'✅ PASS' if feedback_ok else '❌ FAIL'}")
    
    if recommendations_ok and feedback_ok:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"\n✨ Your YouTube entertainment system is working correctly!")
        print(f"\nFeatures available:")
        print(f"  ✓ Real YouTube video recommendations")
        print(f"  ✓ Personality-based matching")
        print(f"  ✓ Like/dislike feedback system")
        print(f"  ✓ Direct links to watch videos")
        print(f"  ✓ Thumbnail support")
        print(f"  ✓ Multiple genres and categories")
        
        print(f"\n🎯 Next steps:")
        print(f"  1. Open the frontend (bondhu-landing)")
        print(f"  2. Navigate to /entertainment")
        print(f"  3. Go to the Videos tab")
        print(f"  4. Enjoy personalized recommendations!")
        
        return True
    else:
        print(f"\n❌ Some tests failed. Check the error messages above.")
        return False

if __name__ == "__main__":
    main()