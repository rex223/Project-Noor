"""
WebSocket consumers for real-time chat functionality.
"""

import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import ChatSession, Message, AgentPersonality
from apps.ml.agent import PersonalityAgent

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time chat between user and AI agent.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.user = self.scope['user']
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Create or get chat session
        self.chat_session = await self.get_or_create_session()
        
        # Join the user's personal room
        self.room_group_name = f'chat_{self.user.id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send welcome message
        await self.send_agent_message("Hello! I'm here to chat with you. How are you feeling today?")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Update session status
        if hasattr(self, 'chat_session'):
            await self.update_session_status('paused')

    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            
            if message_type == 'message':
                await self.handle_user_message(data)
            elif message_type == 'typing':
                await self.handle_typing_indicator(data)
            elif message_type == 'feedback':
                await self.handle_message_feedback(data)
            elif message_type == 'mood_update':
                await self.handle_mood_update(data)
                
        except json.JSONDecodeError:
            await self.send_error("Invalid message format")

    async def handle_user_message(self, data):
        """Process user message and generate agent response."""
        content = data.get('content', '').strip()
        if not content:
            return
        
        # Save user message
        user_message = await self.save_message('user', content)
        
        # Show typing indicator
        await self.send(text_data=json.dumps({
            'type': 'agent_typing',
            'typing': True
        }))
        
        # Generate agent response
        agent_response = await self.generate_agent_response(content, user_message)
        
        # Save and send agent response
        await self.save_message('agent', agent_response)
        await self.send_agent_message(agent_response)
        
        # Update session analytics
        await self.update_session_analytics()

    async def handle_typing_indicator(self, data):
        """Handle typing indicator from user."""
        # Could be used for analytics or real-time features
        pass

    async def handle_message_feedback(self, data):
        """Handle user feedback on agent messages."""
        message_id = data.get('message_id')
        rating = data.get('rating')
        is_helpful = data.get('is_helpful')
        
        if message_id:
            await self.save_message_feedback(message_id, rating, is_helpful)

    async def handle_mood_update(self, data):
        """Handle user mood updates."""
        mood = data.get('mood')
        if mood:
            await self.update_user_mood(mood)

    async def generate_agent_response(self, user_message, message_obj):
        """Generate personalized agent response."""
        try:
            # Get agent personality for this user
            agent_personality = await self.get_agent_personality()
            
            # Initialize personality agent (ML model)
            personality_agent = PersonalityAgent(self.user, agent_personality)
            
            # Generate response based on personality and context
            response = await personality_agent.generate_response(
                user_message, 
                self.chat_session,
                message_obj
            )
            
            return response
            
        except Exception as e:
            # Fallback response
            return "I'm having trouble processing that right now. Could you try rephrasing?"

    async def send_agent_message(self, content):
        """Send agent message to client."""
        await self.send(text_data=json.dumps({
            'type': 'agent_message',
            'content': content,
            'timestamp': timezone.now().isoformat(),
            'agent_typing': False
        }))

    async def send_error(self, error_message):
        """Send error message to client."""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': error_message
        }))

    # Database operations (async)
    
    @database_sync_to_async
    def get_or_create_session(self):
        """Get or create chat session."""
        session, created = ChatSession.objects.get_or_create(
            id=self.session_id,
            defaults={
                'user': self.user,
                'status': 'active'
            }
        )
        return session

    @database_sync_to_async
    def save_message(self, message_type, content):
        """Save message to database."""
        message = Message.objects.create(
            session=self.chat_session,
            message_type=message_type,
            content=content
        )
        
        # Update session message count
        self.chat_session.message_count += 1
        self.chat_session.save()
        
        return message

    @database_sync_to_async
    def save_message_feedback(self, message_id, rating, is_helpful):
        """Save user feedback for a message."""
        try:
            message = Message.objects.get(id=message_id, session=self.chat_session)
            if rating:
                message.user_rating = rating
            if is_helpful is not None:
                message.is_helpful = is_helpful
            message.save()
        except Message.DoesNotExist:
            pass

    @database_sync_to_async
    def get_agent_personality(self):
        """Get or create agent personality for user."""
        personality, created = AgentPersonality.objects.get_or_create(
            user=self.user,
            defaults={
                'communication_style': 'casual',
                'enthusiasm_level': 0.7,
                'formality_level': 0.3,
                'proactivity_level': 0.5,
                'empathy_level': 0.8,
            }
        )
        return personality

    @database_sync_to_async
    def update_session_status(self, status):
        """Update chat session status."""
        self.chat_session.status = status
        if status == 'ended':
            self.chat_session.ended_at = timezone.now()
        self.chat_session.save()

    @database_sync_to_async
    def update_session_analytics(self):
        """Update session analytics."""
        # Update user profile
        profile = self.user.profile
        profile.increment_messages()
        
        # Could add more analytics here
        pass

    @database_sync_to_async
    def update_user_mood(self, mood):
        """Update user's current mood."""
        profile = self.user.profile
        profile.update_mood(mood)

    # Group message handlers
    
    async def chat_message(self, event):
        """Handle chat message from group."""
        message = event['message']
        await self.send(text_data=json.dumps(message))

    async def proactive_message(self, event):
        """Handle proactive message from agent."""
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'proactive_message',
            'content': message['content'],
            'trigger_type': message.get('trigger_type', 'general'),
            'timestamp': timezone.now().isoformat()
        }))
