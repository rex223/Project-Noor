"""
Personality Agent - Core ML component for dynamic personality adaptation.
"""

import numpy as np
import json
import asyncio
from typing import Dict, List, Tuple, Optional
from django.conf import settings
from apps.personality.models import PersonalityAssessment, AdaptationPolicy
from apps.chat.models import Message, ChatSession


class PersonalityAgent:
    """
    Reinforcement Learning agent that adapts to user personality.
    """
    
    def __init__(self, user, agent_personality):
        self.user = user
        self.agent_personality = agent_personality
        self.personality_vector = self._get_user_personality_vector()
        self.context_history = []
        
    def _get_user_personality_vector(self):
        """Get the latest personality assessment vector."""
        latest_assessment = PersonalityAssessment.objects.filter(
            user=self.user,
            is_active=True
        ).first()
        
        if latest_assessment:
            return latest_assessment.personality_vector
        else:
            # Default personality vector if no assessment
            return [0.5, 0.5, 0.5, 0.5, 0.5]  # Neutral personality
    
    async def generate_response(self, user_message: str, chat_session: ChatSession, message_obj: Message) -> str:
        """
        Generate a personalized response based on user personality and context.
        """
        try:
            # Analyze user message
            message_analysis = await self._analyze_message(user_message)
            
            # Get conversation context
            context = await self._get_conversation_context(chat_session)
            
            # Generate response based on personality adaptation
            response = await self._generate_adaptive_response(
                user_message, 
                message_analysis, 
                context
            )
            
            # Update agent learning
            await self._update_agent_learning(user_message, response, message_analysis)
            
            return response
            
        except Exception as e:
            # Fallback response
            return self._get_fallback_response(user_message)
    
    async def _analyze_message(self, message: str) -> Dict:
        """Analyze user message for sentiment, emotion, and topics."""
        # Placeholder implementation - would use actual NLP models
        analysis = {
            'sentiment': 'neutral',
            'sentiment_score': 0.0,
            'emotions': ['neutral'],
            'topics': [],
            'urgency': 'low',
            'personality_indicators': {}
        }
        
        # Simple keyword-based analysis (placeholder)
        if any(word in message.lower() for word in ['sad', 'depressed', 'down']):
            analysis['sentiment'] = 'negative'
            analysis['sentiment_score'] = -0.7
            analysis['emotions'] = ['sadness']
        elif any(word in message.lower() for word in ['happy', 'excited', 'great']):
            analysis['sentiment'] = 'positive'
            analysis['sentiment_score'] = 0.7
            analysis['emotions'] = ['happiness']
        
        return analysis
    
    async def _get_conversation_context(self, chat_session: ChatSession) -> Dict:
        """Get recent conversation context."""
        # Get recent messages from session
        recent_messages = Message.objects.filter(
            session=chat_session
        ).order_by('-timestamp')[:10]
        
        context = {
            'recent_topics': [],
            'mood_trend': 'stable',
            'engagement_level': 'medium',
            'conversation_flow': 'natural'
        }
        
        # Analyze recent messages for context
        for msg in recent_messages:
            if msg.sentiment:
                # Track sentiment trends
                pass
        
        return context
    
    async def _generate_adaptive_response(self, user_message: str, analysis: Dict, context: Dict) -> str:
        """Generate response adapted to user's personality and current state."""
        # Get user's personality traits
        openness, conscientiousness, extraversion, agreeableness, neuroticism = self.personality_vector
        
        # Adapt response style based on personality
        response_style = self._determine_response_style(analysis, context)
        
        # Generate base response
        base_response = self._generate_base_response(user_message, analysis)
        
        # Apply personality-based modifications
        adapted_response = self._apply_personality_adaptation(
            base_response, 
            response_style, 
            analysis
        )
        
        return adapted_response
    
    def _determine_response_style(self, analysis: Dict, context: Dict) -> Dict:
        """Determine appropriate response style based on user state."""
        openness, conscientiousness, extraversion, agreeableness, neuroticism = self.personality_vector
        
        style = {
            'formality': self.agent_personality.formality_level,
            'enthusiasm': self.agent_personality.enthusiasm_level,
            'empathy': self.agent_personality.empathy_level,
            'proactivity': self.agent_personality.proactivity_level
        }
        
        # Adjust based on user's current emotional state
        if analysis['sentiment'] == 'negative':
            style['empathy'] = min(style['empathy'] + 0.2, 1.0)
            style['enthusiasm'] = max(style['enthusiasm'] - 0.1, 0.0)
        
        # Adjust based on personality traits
        if extraversion < 0.3:  # Introverted user
            style['enthusiasm'] = max(style['enthusiasm'] - 0.1, 0.0)
            style['formality'] = min(style['formality'] + 0.1, 1.0)
        
        if neuroticism > 0.7:  # High anxiety
            style['empathy'] = min(style['empathy'] + 0.3, 1.0)
            style['reassurance'] = 0.8
        
        return style
    
    def _generate_base_response(self, user_message: str, analysis: Dict) -> str:
        """Generate base response using simple templates."""
        # This would be replaced with actual language models
        
        if analysis['sentiment'] == 'negative':
            responses = [
                "I can hear that you're going through a tough time. Would you like to talk about it?",
                "It sounds like you're feeling down. I'm here to listen and support you.",
                "That sounds really difficult. How can I help you feel better?"
            ]
        elif analysis['sentiment'] == 'positive':
            responses = [
                "That's wonderful to hear! I'm so glad you're feeling good.",
                "Your positive energy is contagious! Tell me more about what's making you happy.",
                "I love hearing good news! What's been the highlight of your day?"
            ]
        else:
            responses = [
                "Thanks for sharing that with me. What would you like to talk about?",
                "I'm here and ready to chat. What's on your mind?",
                "How are you feeling right now? I'd love to know more about your day."
            ]
        
        # Simple random selection (would be more sophisticated)
        import random
        return random.choice(responses)
    
    def _apply_personality_adaptation(self, base_response: str, style: Dict, analysis: Dict) -> str:
        """Apply personality-based modifications to the response."""
        response = base_response
        
        # Adjust formality
        if style['formality'] > 0.7:
            response = response.replace("I'm", "I am")
            response = response.replace("you're", "you are")
        elif style['formality'] < 0.3:
            response = response.replace("I am", "I'm")
            response = response.replace("you are", "you're")
        
        # Adjust enthusiasm
        if style['enthusiasm'] > 0.7:
            if not response.endswith('!'):
                response = response.replace('.', '!')
        
        # Add empathy markers
        if style['empathy'] > 0.7 and analysis['sentiment'] == 'negative':
            empathy_starters = [
                "I really understand how that feels. ",
                "That must be so hard for you. ",
                "I can imagine how difficult this is. "
            ]
            import random
            response = random.choice(empathy_starters) + response
        
        return response
    
    async def _update_agent_learning(self, user_message: str, agent_response: str, analysis: Dict):
        """Update the agent's learning based on this interaction."""
        # This would implement actual RL updates
        
        # For now, just track interaction count
        self.agent_personality.total_interactions += 1
        self.agent_personality.save()
    
    def _get_fallback_response(self, user_message: str) -> str:
        """Fallback response when generation fails."""
        fallback_responses = [
            "I'm having trouble processing that right now. Could you try rephrasing?",
            "Sorry, I didn't quite understand that. Can you tell me more?",
            "I'm here to listen. What would you like to talk about?",
            "Let me think about that. In the meantime, how are you feeling?"
        ]
        
        import random
        return random.choice(fallback_responses)
    
    def should_send_proactive_message(self) -> Tuple[bool, str]:
        """Determine if agent should send a proactive message."""
        # Check user's last activity
        from django.utils import timezone
        from datetime import timedelta
        
        last_activity = self.user.profile.last_activity
        time_since_activity = timezone.now() - last_activity
        
        # Send proactive message if user has been inactive for a while
        if time_since_activity > timedelta(hours=24):
            return True, "inactivity"
        
        # Check if user seems to need support based on mood
        if self.user.profile.current_mood in ['sad', 'anxious', 'stressed']:
            return True, "mood_support"
        
        return False, None
    
    def generate_proactive_message(self, trigger_type: str) -> str:
        """Generate a proactive message based on trigger type."""
        messages = {
            'inactivity': [
                "Hey! I've been thinking about you. How are you doing today?",
                "It's been a while since we last talked. What's new with you?",
                "Just checking in! How has your day been?"
            ],
            'mood_support': [
                "I noticed you might be feeling down. Want to talk about it?",
                "I'm here if you need someone to listen. How are you holding up?",
                "Sometimes it helps to share what's on your mind. I'm here for you."
            ],
            'achievement': [
                "Congratulations on your recent achievement! How does it feel?",
                "I'm so proud of your progress! Tell me about your success.",
                "You've been doing amazingly well! What's your secret?"
            ]
        }
        
        import random
        return random.choice(messages.get(trigger_type, messages['inactivity']))


class PersonalityClassifier:
    """
    ML model for classifying personality traits from user interactions.
    """
    
    def __init__(self):
        self.model = None  # Would load actual ML model
        
    def predict_personality(self, features: Dict) -> Dict:
        """Predict personality traits from user features."""
        # Placeholder implementation
        return {
            'openness': 0.6,
            'conscientiousness': 0.7,
            'extraversion': 0.5,
            'agreeableness': 0.8,
            'neuroticism': 0.3,
            'confidence': 0.75
        }
    
    def extract_features(self, user_data: Dict) -> np.ndarray:
        """Extract features from user data for personality prediction."""
        # Placeholder feature extraction
        features = np.array([0.5] * 20)  # 20-dimensional feature vector
        return features


class RecommendationEngine:
    """
    ML-powered recommendation engine for content and activities.
    """
    
    def __init__(self, user):
        self.user = user
        
    def recommend_content(self, content_type: str, mood: str = None) -> List[Dict]:
        """Recommend content based on user personality and mood."""
        # Placeholder recommendations
        recommendations = []
        
        if content_type == 'music':
            recommendations = [
                {'title': 'Calming Playlist', 'type': 'music', 'score': 0.9},
                {'title': 'Upbeat Songs', 'type': 'music', 'score': 0.8},
            ]
        elif content_type == 'articles':
            recommendations = [
                {'title': 'Self-Care Tips', 'type': 'article', 'score': 0.85},
                {'title': 'Mindfulness Guide', 'type': 'article', 'score': 0.75},
            ]
        
        return recommendations
    
    def recommend_activities(self, current_mood: str) -> List[Dict]:
        """Recommend activities based on current mood and personality."""
        activities = []
        
        if current_mood == 'sad':
            activities = [
                {'name': 'Mood Tracking Exercise', 'duration': 5, 'score': 0.9},
                {'name': 'Breathing Exercise', 'duration': 3, 'score': 0.8},
            ]
        elif current_mood == 'stressed':
            activities = [
                {'name': 'Quick Meditation', 'duration': 10, 'score': 0.95},
                {'name': 'Progressive Relaxation', 'duration': 15, 'score': 0.85},
            ]
        
        return activities
