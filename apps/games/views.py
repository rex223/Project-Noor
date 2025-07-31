from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def game_list(request):
    """Display available RPG games"""
    return render(request, 'games/game_list.html')

@login_required
def personality_quest(request):
    """Personality Quest RPG game"""
    return render(request, 'games/personality_quest.html')

@login_required  
def mood_dungeon(request):
    """Mood Dungeon RPG game"""
    return render(request, 'games/mood_dungeon.html')

@login_required
def social_arena(request):
    """Social Arena RPG game"""
    return render(request, 'games/social_arena.html')

@login_required
def stress_survival(request):
    """Stress Survival RPG game"""
    return render(request, 'games/stress_survival.html')

@login_required
def mindfulness_mystery(request):
    """Mindfulness Mystery RPG game"""
    return render(request, 'games/mindfulness_mystery.html')

@login_required
def emotion_explorer(request):
    """Emotion Explorer RPG game"""
    return render(request, 'games/emotion_explorer.html')
