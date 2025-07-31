from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@login_required
def chat(request):
    """NOOR's interactive chat interface"""
    return render(request, 'chat/chat.html')

@csrf_exempt
def chat_api(request):
    """API endpoint for chat messages"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            
            if not message:
                return JsonResponse({'error': 'Message cannot be empty'}, status=400)
            
            # Generate NOOR's response
            response = generate_noor_response(message)
            
            return JsonResponse({
                'response': response,
                'success': True
            })
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def generate_noor_response(message):
    """Generate NOOR's response based on user message"""
    message_lower = message.lower()
    
    # Emotion detection responses
    if any(word in message_lower for word in ['sad', 'depressed', 'down', 'upset']):
        return "I can sense you're feeling down right now. It's completely okay to feel this way. Would you like to talk about what's making you feel sad? Sometimes just sharing can help lighten the load. 💙"
    
    elif any(word in message_lower for word in ['happy', 'excited', 'great', 'awesome', 'wonderful']):
        return "That's wonderful! I love hearing that you're feeling good. What's bringing you joy today? I'd love to celebrate with you! ✨"
    
    elif any(word in message_lower for word in ['anxious', 'worried', 'stressed', 'nervous']):
        return "Anxiety can feel overwhelming, but remember that you're not alone. Let's try some breathing exercises together. Breathe in for 4 counts... hold for 4... and out for 4. What specific thoughts are making you feel anxious?"
    
    elif any(word in message_lower for word in ['angry', 'mad', 'frustrated', 'annoyed']):
        return "I can hear that you're feeling frustrated. It's natural to feel anger sometimes. Would you like to talk about what triggered these feelings? Sometimes expressing it can help us understand it better."
    
    # Activity suggestions
    elif 'music' in message_lower or 'song' in message_lower:
        return "Music is such a powerful mood enhancer! Based on your personality, I think you might enjoy some <strong>lo-fi beats</strong> for focus or <strong>upbeat indie</strong> to boost energy. What genre matches your mood right now?"
    
    elif 'game' in message_lower or 'play' in message_lower:
        return "Let's have some fun! I have several personality-based games we could try:<br>• <strong>Personality Quest</strong> - Discover hidden traits<br>• <strong>Mood Dungeon</strong> - Battle negative thoughts<br>• <strong>Social Arena</strong> - Practice conversations<br>Which sounds interesting?"
    
    elif 'joke' in message_lower or 'funny' in message_lower:
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything! 😄",
            "I told my computer a joke about WiFi. It couldn't connect! 💻",
            "Why did the AI go to therapy? It had too many deep learning issues! 🤖",
            "What do you call a stressed-out Gen Z? A Zoomie with too many tabs open! 📱"
        ]
        import random
        return random.choice(jokes)
    
    # Support and help
    elif any(word in message_lower for word in ['help', 'support', 'need']):
        return "I'm here to support you in whatever way I can. Whether you need someone to listen, help process your feelings, or just want to chat - I'm here. What kind of support would be most helpful for you right now?"
    
    elif any(word in message_lower for word in ['lonely', 'alone', 'isolated']):
        return "Feeling lonely is tough, but please know that you're not truly alone. I'm here with you, and there are people who care about you. Would you like to talk about what's making you feel this way, or would you prefer we do something together like a game or listening to music?"
    
    # Greetings
    elif any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
        return "Hello! I'm so happy to see you today. How are you feeling? I'm here to listen, support, and maybe have some fun together!"
    
    # Default responses
    else:
        responses = [
            "That's really interesting! Tell me more about how that makes you feel.",
            "I appreciate you sharing that with me. What aspects of this situation are most important to you?",
            "It sounds like you're processing a lot right now. How can I best support you through this?",
            "I can hear that this matters to you. What would you like to explore further?",
            "Thank you for trusting me with your thoughts. What emotions are coming up for you around this?"
        ]
        import random
        return random.choice(responses)
