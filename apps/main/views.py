from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

def home(request):
    """NOOR's main interactive interface"""
    context = {
        'user': request.user,
    }
    return render(request, 'home.html', context)

@login_required
def dashboard(request):
    """User dashboard with personalized content"""
    # In a real implementation, you'd fetch user data
    context = {
        'user': request.user,
        'stats': {
            'total_sessions': 25,
            'total_games_played': 12,
            'total_messages': 150,
            'achievements': 8,
        }
    }
    return render(request, 'dashboard.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def api_chat_message(request):
    """API endpoint for chat messages"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Here you would integrate with your AI/ML models
        # For now, return a simple response
        response = generate_noor_response(message)
        
        return JsonResponse({
            'response': response,
            'timestamp': '12:00 PM',  # You'd use real timestamp
            'success': True
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def generate_noor_response(message):
    """Generate NOOR's response to user message"""
    message_lower = message.lower()
    
    # Simple keyword-based responses for demo
    if 'hello' in message_lower or 'hi' in message_lower:
        return "Hello! I'm so happy to see you today. How are you feeling?"
    
    elif 'music' in message_lower:
        return "I'd love to help you find the perfect music! What's your mood like right now? I can suggest some great tracks based on how you're feeling."
    
    elif 'game' in message_lower or 'play' in message_lower:
        return "Games are a great way to explore your personality! Would you like to try our Personality Quest or maybe battle some negative thoughts in Mood Dungeon?"
    
    elif 'sad' in message_lower or 'down' in message_lower:
        return "I'm here to support you. It's completely normal to feel sad sometimes. Would you like to talk about what's troubling you or try some mood-boosting activities?"
    
    elif 'happy' in message_lower or 'great' in message_lower:
        return "That's wonderful! I love hearing that you're feeling good. What's been bringing you joy today?"
    
    elif 'help' in message_lower:
        return "I'm here to help you in any way I can! Whether you want to chat, play games, listen to music, or just need someone to listen - I'm here for you."
    
    else:
        return "That's really interesting! I'm here to listen and support you. Tell me more about what's on your mind."
