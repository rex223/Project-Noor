"""Test that the simple recommendations service returns a structured response.

This does not spin up the full FastAPI app; instead it directly calls the
service function to validate shape. Network calls may still occur if API key is set.
"""
import asyncio

from core.services.simple_video_recommender import get_simple_recommendations


def test_simple_recommendations_basic(monkeypatch):
    # Force deterministic personality by monkeypatching builder if desired
    async def fake_build(*args, **kwargs):
        return {
            'openness': 0.6,
            'conscientiousness': 0.5,
            'extraversion': 0.4,
            'agreeableness': 0.5,
            'neuroticism': 0.3,
        }

    # Instead of patching internal, just call service (keeps things simple)
    payload = asyncio.run(get_simple_recommendations(user_id="test-user", max_results=5))

    assert 'success' in payload and payload['success'] is True
    assert 'data' in payload
    data = payload['data']
    assert 'personality_profile' in data
    assert 'recommendations' in data
    assert isinstance(data['recommendations'], list)
    assert 'total_count' in data
