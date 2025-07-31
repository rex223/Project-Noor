"""
Personality assessment views and APIs.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
import json
import asyncio
from datetime import datetime, timedelta

from .models import (
    PersonalityTrait, PersonalityAssessment, PersonalityEvolution,
    PersonalityInsight, AdaptationPolicy
)
from apps.ml.agent import PersonalityAgent, PersonalityClassifier


class PersonalityAssessmentView(LoginRequiredMixin, TemplateView):
    """Main personality assessment interface."""
    template_name = 'personality/assessment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user's latest assessment
        latest_assessment = PersonalityAssessment.objects.filter(
            user=self.request.user,
            is_active=True
        ).first()
        
        # Get personality traits for the form
        traits = PersonalityTrait.objects.all()
        
        context.update({
            'latest_assessment': latest_assessment,
            'traits': traits,
            'has_previous_assessment': latest_assessment is not None,
        })
        
        return context


class PersonalityDashboardView(LoginRequiredMixin, TemplateView):
    """Personality insights and evolution dashboard."""
    template_name = 'personality/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user's assessments
        assessments = PersonalityAssessment.objects.filter(
            user=self.request.user
        ).order_by('-created_at')[:5]
        
        # Get latest insights
        insights = PersonalityInsight.objects.filter(
            user=self.request.user
        ).order_by('-created_at')[:10]
        
        # Get personality evolution
        evolution = PersonalityEvolution.objects.filter(
            user=self.request.user
        ).order_by('-created_at')[:5]
        
        # Calculate personality summary
        latest_assessment = assessments.first() if assessments else None
        personality_summary = self._get_personality_summary(latest_assessment)
        
        context.update({
            'assessments': assessments,
            'insights': insights,
            'evolution': evolution,
            'personality_summary': personality_summary,
            'latest_assessment': latest_assessment,
        })
        
        return context
    
    def _get_personality_summary(self, assessment):
        """Generate personality summary from latest assessment."""
        if not assessment:
            return None
            
        traits = {
            'Openness': assessment.openness,
            'Conscientiousness': assessment.conscientiousness,
            'Extraversion': assessment.extraversion,
            'Agreeableness': assessment.agreeableness,
            'Neuroticism': assessment.neuroticism,
        }
        
        # Find dominant traits (> 0.6)
        dominant_traits = {k: v for k, v in traits.items() if v > 0.6}
        
        # Find areas for growth (< 0.4)
        growth_areas = {k: v for k, v in traits.items() if v < 0.4}
        
        return {
            'traits': traits,
            'dominant_traits': dominant_traits,
            'growth_areas': growth_areas,
            'assessment_date': assessment.created_at,
        }


@method_decorator(csrf_exempt, name='dispatch')
class PersonalityAssessmentAPIView(LoginRequiredMixin, View):
    """API for submitting personality assessment."""
    
    def post(self, request):
        """Submit personality assessment results."""
        try:
            data = json.loads(request.body)
            
            # Validate assessment data
            required_fields = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing field: {field}'}, status=400)
                
                score = float(data[field])
                if not 0.0 <= score <= 1.0:
                    return JsonResponse({'error': f'Invalid score for {field}: must be between 0.0 and 1.0'}, status=400)
            
            # Create new assessment
            assessment = PersonalityAssessment.objects.create(
                user=request.user,
                assessment_type=data.get('assessment_type', 'survey'),
                openness=data['openness'],
                conscientiousness=data['conscientiousness'],
                extraversion=data['extraversion'],
                agreeableness=data['agreeableness'],
                neuroticism=data['neuroticism'],
                confidence_scores=data.get('confidence_scores', {}),
                insights=data.get('insights', {}),
            )
            
            # Check for evolution if there's a previous assessment
            previous_assessment = PersonalityAssessment.objects.filter(
                user=request.user,
                created_at__lt=assessment.created_at
            ).order_by('-created_at').first()
            
            if previous_assessment:
                evolution = PersonalityEvolution.create_evolution(
                    previous_assessment, 
                    assessment
                )
            
            # Generate insights asynchronously
            self._generate_insights_async(assessment)
            
            return JsonResponse({
                'success': True,
                'assessment_id': str(assessment.id),
                'personality_vector': assessment.personality_vector,
                'dominant_traits': assessment.get_dominant_traits(),
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def _generate_insights_async(self, assessment):
        """Generate personality insights asynchronously."""
        # This would typically be done with Celery, but for now we'll do it synchronously
        classifier = PersonalityClassifier()
        
        # Generate insights based on personality traits
        insights_data = [
            {
                'type': 'strength',
                'title': self._get_strength_insight(assessment),
                'description': self._get_strength_description(assessment),
            },
            {
                'type': 'growth_area',
                'title': self._get_growth_insight(assessment),
                'description': self._get_growth_description(assessment),
            },
            {
                'type': 'recommendation',
                'title': 'Personalized Recommendations',
                'description': self._get_recommendations(assessment),
            }
        ]
        
        # Create insight objects
        for insight_data in insights_data:
            PersonalityInsight.objects.create(
                user=assessment.user,
                assessment=assessment,
                insight_type=insight_data['type'],
                title=insight_data['title'],
                description=insight_data['description'],
                relevance_score=0.8,
                confidence_score=0.7,
            )
    
    def _get_strength_insight(self, assessment):
        """Generate strength insight title."""
        traits = {
            'openness': assessment.openness,
            'conscientiousness': assessment.conscientiousness,
            'extraversion': assessment.extraversion,
            'agreeableness': assessment.agreeableness,
            'neuroticism': 1 - assessment.neuroticism,  # Invert neuroticism
        }
        
        strongest_trait = max(traits, key=traits.get)
        strength_titles = {
            'openness': 'Creative and Open-Minded',
            'conscientiousness': 'Organized and Reliable',
            'extraversion': 'Social and Energetic',
            'agreeableness': 'Compassionate and Cooperative',
            'neuroticism': 'Emotionally Stable and Calm',
        }
        
        return strength_titles.get(strongest_trait, 'Unique Personality Strength')
    
    def _get_strength_description(self, assessment):
        """Generate strength insight description."""
        return "Your personality shows strong positive traits that can be leveraged for personal growth and success."
    
    def _get_growth_insight(self, assessment):
        """Generate growth area insight title."""
        traits = {
            'openness': assessment.openness,
            'conscientiousness': assessment.conscientiousness,
            'extraversion': assessment.extraversion,
            'agreeableness': assessment.agreeableness,
            'neuroticism': assessment.neuroticism,
        }
        
        growth_trait = min(traits, key=traits.get)
        growth_titles = {
            'openness': 'Exploring New Experiences',
            'conscientiousness': 'Building Better Habits',
            'extraversion': 'Social Confidence',
            'agreeableness': 'Assertiveness Balance',
            'neuroticism': 'Emotional Regulation',
        }
        
        return growth_titles.get(growth_trait, 'Personal Development Area')
    
    def _get_growth_description(self, assessment):
        """Generate growth area description."""
        return "There are opportunities for growth in certain areas that could enhance your overall well-being."
    
    def _get_recommendations(self, assessment):
        """Generate personalized recommendations."""
        return "Based on your personality profile, here are some personalized recommendations for activities and content."


@method_decorator(csrf_exempt, name='dispatch')
class PersonalityInsightsAPIView(LoginRequiredMixin, View):
    """API for getting personality insights."""
    
    def get(self, request):
        """Get user's personality insights."""
        try:
            insights = PersonalityInsight.objects.filter(
                user=request.user
            ).order_by('-created_at')[:20]
            
            insights_data = []
            for insight in insights:
                insights_data.append({
                    'id': str(insight.id),
                    'type': insight.insight_type,
                    'title': insight.title,
                    'description': insight.description,
                    'relevance_score': insight.relevance_score,
                    'confidence_score': insight.confidence_score,
                    'is_read': insight.is_read,
                    'created_at': insight.created_at.isoformat(),
                })
            
            return JsonResponse({
                'success': True,
                'insights': insights_data,
                'total_count': insights.count(),
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def post(self, request):
        """Mark insight as read or provide feedback."""
        try:
            data = json.loads(request.body)
            insight_id = data.get('insight_id')
            action = data.get('action')  # 'mark_read', 'rate', 'feedback'
            
            insight = get_object_or_404(PersonalityInsight, id=insight_id, user=request.user)
            
            if action == 'mark_read':
                insight.is_read = True
                insight.save()
            elif action == 'rate':
                rating = int(data.get('rating', 0))
                if 1 <= rating <= 5:
                    insight.user_rating = rating
                    insight.save()
            elif action == 'feedback':
                is_helpful = data.get('is_helpful', False)
                insight.is_helpful = is_helpful
                insight.save()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class PersonalityGameDataView(LoginRequiredMixin, View):
    """API for receiving personality data from games."""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        """Receive personality data from game interactions."""
        try:
            data = json.loads(request.body)
            
            game_type = data.get('game_type')
            game_results = data.get('results', {})
            
            # Process game results and update personality assessment
            personality_scores = self._process_game_results(game_type, game_results)
            
            if personality_scores:
                # Create a game-based assessment
                assessment = PersonalityAssessment.objects.create(
                    user=request.user,
                    assessment_type='game_based',
                    openness=personality_scores.get('openness', 0.5),
                    conscientiousness=personality_scores.get('conscientiousness', 0.5),
                    extraversion=personality_scores.get('extraversion', 0.5),
                    agreeableness=personality_scores.get('agreeableness', 0.5),
                    neuroticism=personality_scores.get('neuroticism', 0.5),
                    insights={'game_type': game_type, 'raw_results': game_results},
                )
                
                return JsonResponse({
                    'success': True,
                    'assessment_id': str(assessment.id),
                    'personality_update': personality_scores,
                })
            
            return JsonResponse({'success': True, 'message': 'Game data recorded'})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def _process_game_results(self, game_type, results):
        """Process game results into personality scores."""
        # Placeholder implementation - would be more sophisticated
        personality_scores = {}
        
        if game_type == 'personality-quest':
            # Map quest choices to personality traits
            personality_scores = {
                'openness': results.get('creativity_score', 0.5),
                'conscientiousness': results.get('planning_score', 0.5),
                'extraversion': results.get('social_score', 0.5),
                'agreeableness': results.get('cooperation_score', 0.5),
                'neuroticism': 1 - results.get('stress_handling', 0.5),
            }
        elif game_type == 'mood-dungeon':
            # Map mood battle results to traits
            personality_scores = {
                'neuroticism': 1 - results.get('emotional_regulation', 0.5),
                'conscientiousness': results.get('persistence', 0.5),
            }
        
        return personality_scores
