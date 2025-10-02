"""
Personality Analysis Agent for central personality processing and fusion.
Combines data from Music, Video, Gaming agents and survey responses using Big Five model.
"""

import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from agents.base_agent import BaseAgent
from core.config import get_config
from api.models.schemas import (
    DataSource, 
    PersonalityTraitModel as PersonalityTrait, 
    PersonalityScore,
    PersonalityProfile,
    AgentAnalysisResult,
    CrossModalAnalysis,
    ConfidenceLevel
)

class PersonalityAnalysisAgent(BaseAgent):
    """
    Central agent for personality analysis and cross-modal data fusion.
    Processes inputs from all other agents and survey data to create comprehensive personality profiles.
    """
    
    def __init__(self, user_id: str, **kwargs):
        """
        Initialize Personality Analysis Agent.
        
        Args:
            user_id: User ID for this agent session
            **kwargs: Additional arguments passed to BaseAgent
        """
        super().__init__(
            agent_type=DataSource.SURVEY,  # Using SURVEY as it processes all data
            user_id=user_id,
            **kwargs
        )
        
        # Cross-modal fusion weights (can be learned/adapted over time)
        self.fusion_weights = {
            DataSource.MUSIC: 0.25,
            DataSource.VIDEO: 0.25,
            DataSource.GAMING: 0.25,
            DataSource.SURVEY: 0.25,
            DataSource.CONVERSATION: 0.1  # Lower weight for conversation data
        }
        
        # Trait correlation matrix (based on Big Five research)
        self.trait_correlations = {
            PersonalityTrait.OPENNESS: {
                PersonalityTrait.CONSCIENTIOUSNESS: 0.1,
                PersonalityTrait.EXTRAVERSION: 0.2,
                PersonalityTrait.AGREEABLENESS: 0.1,
                PersonalityTrait.NEUROTICISM: -0.1
            },
            PersonalityTrait.CONSCIENTIOUSNESS: {
                PersonalityTrait.EXTRAVERSION: 0.1,
                PersonalityTrait.AGREEABLENESS: 0.2,
                PersonalityTrait.NEUROTICISM: -0.3
            },
            PersonalityTrait.EXTRAVERSION: {
                PersonalityTrait.AGREEABLENESS: 0.2,
                PersonalityTrait.NEUROTICISM: -0.2
            },
            PersonalityTrait.AGREEABLENESS: {
                PersonalityTrait.NEUROTICISM: -0.2
            }
        }
        
        # Confidence thresholds
        self.confidence_thresholds = {
            ConfidenceLevel.LOW: (0.0, 0.4),
            ConfidenceLevel.MEDIUM: (0.4, 0.7),
            ConfidenceLevel.HIGH: (0.7, 1.0)
        }
        
        # Survey questions to Big Five mapping
        self.survey_mappings = self._initialize_survey_mappings()
    
    def _initialize_survey_mappings(self) -> Dict[str, Dict[PersonalityTrait, float]]:
        """Initialize survey question to personality trait mappings."""
        return {
            # Openness questions
            "enjoy_new_experiences": {PersonalityTrait.OPENNESS: 0.8},
            "appreciate_art": {PersonalityTrait.OPENNESS: 0.7},
            "curious_about_world": {PersonalityTrait.OPENNESS: 0.8},
            "imaginative": {PersonalityTrait.OPENNESS: 0.7},
            "prefer_routine": {PersonalityTrait.OPENNESS: -0.6},
            
            # Conscientiousness questions
            "organized": {PersonalityTrait.CONSCIENTIOUSNESS: 0.8},
            "punctual": {PersonalityTrait.CONSCIENTIOUSNESS: 0.7},
            "detail_oriented": {PersonalityTrait.CONSCIENTIOUSNESS: 0.8},
            "procrastinate": {PersonalityTrait.CONSCIENTIOUSNESS: -0.7},
            "follow_through": {PersonalityTrait.CONSCIENTIOUSNESS: 0.8},
            
            # Extraversion questions
            "enjoy_parties": {PersonalityTrait.EXTRAVERSION: 0.8},
            "talk_to_strangers": {PersonalityTrait.EXTRAVERSION: 0.7},
            "energetic": {PersonalityTrait.EXTRAVERSION: 0.6},
            "prefer_solitude": {PersonalityTrait.EXTRAVERSION: -0.7},
            "outgoing": {PersonalityTrait.EXTRAVERSION: 0.8},
            
            # Agreeableness questions
            "empathetic": {PersonalityTrait.AGREEABLENESS: 0.8},
            "cooperative": {PersonalityTrait.AGREEABLENESS: 0.7},
            "trusting": {PersonalityTrait.AGREEABLENESS: 0.6},
            "competitive": {PersonalityTrait.AGREEABLENESS: -0.5},
            "helpful": {PersonalityTrait.AGREEABLENESS: 0.8},
            
            # Neuroticism questions
            "anxious": {PersonalityTrait.NEUROTICISM: 0.8},
            "moody": {PersonalityTrait.NEUROTICISM: 0.7},
            "stressed": {PersonalityTrait.NEUROTICISM: 0.8},
            "calm": {PersonalityTrait.NEUROTICISM: -0.7},
            "resilient": {PersonalityTrait.NEUROTICISM: -0.8}
        }
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the Personality Analysis Agent."""
        return """You are a Personality Analysis Agent specialized in comprehensive personality assessment using the Big Five model.

Your capabilities include:
- Fusing personality insights from multiple data sources (music, video, gaming, surveys)
- Applying cross-modal validation and correlation analysis
- Generating comprehensive personality profiles with confidence scores
- Tracking personality evolution over time
- Providing evidence-based personality insights

You work with the Big Five personality traits:
- Openness to Experience: creativity, curiosity, intellectual interests
- Conscientiousness: organization, persistence, goal-orientation
- Extraversion: sociability, energy, positive emotions
- Agreeableness: cooperation, trust, empathy
- Neuroticism: emotional instability, anxiety, negative emotions

Your analysis process:
1. Collect insights from specialized agents (Music, Video, Gaming)
2. Process survey responses and conversation data
3. Apply cross-modal fusion with appropriate weights
4. Validate consistency across data sources
5. Generate confidence scores for each trait
6. Create comprehensive personality profiles
7. Track changes and evolution over time

Provide scientifically-grounded assessments while being sensitive to individual differences and cultural contexts."""
    
    async def collect_data(self, force_refresh: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Collect personality data from all sources.
        
        Args:
            force_refresh: Whether to force refresh of cached data
            **kwargs: Additional arguments including agent results and survey data
            
        Returns:
            Dictionary containing all personality-relevant data
        """
        data = {
            "agent_results": [],
            "survey_responses": {},
            "conversation_history": [],
            "historical_profiles": [],
            "cross_modal_correlations": {},
            "data_quality_metrics": {}
        }
        
        try:
            # Collect agent analysis results
            agent_results = kwargs.get("agent_results", [])
            data["agent_results"] = agent_results
            
            # Collect survey responses
            survey_data = kwargs.get("survey_responses", {})
            data["survey_responses"] = survey_data
            
            # Collect conversation history for additional insights
            conversation_data = kwargs.get("conversation_history", [])
            data["conversation_history"] = conversation_data
            
            # Collect historical personality profiles for trend analysis
            historical_data = kwargs.get("historical_profiles", [])
            data["historical_profiles"] = historical_data
            
            # Calculate data quality metrics
            data["data_quality_metrics"] = await self._assess_data_quality(data)
            
            # Perform initial cross-modal correlation analysis
            if agent_results:
                data["cross_modal_correlations"] = await self._calculate_cross_modal_correlations(agent_results)
            
            self.logger.info(f"Collected personality data from {len(agent_results)} agents, {len(survey_data)} survey items")
            return data
            
        except Exception as e:
            self.logger.error(f"Error collecting personality data: {e}")
            return data
    
    async def analyze_personality(self, data: Dict[str, Any]) -> Dict[PersonalityTrait, float]:
        """
        Perform comprehensive personality analysis using cross-modal fusion.
        
        Args:
            data: All collected personality data
            
        Returns:
            Dictionary mapping personality traits to fused scores (0-100)
        """
        # Initialize scores
        fused_scores = {trait: 50.0 for trait in PersonalityTrait}
        
        if not data:
            return fused_scores
        
        # Collect scores from all sources
        source_scores = await self._collect_source_scores(data)
        
        # Apply cross-modal fusion
        fused_scores = await self._apply_cross_modal_fusion(source_scores)
        
        # Apply trait correlations for consistency
        fused_scores = await self._apply_trait_correlations(fused_scores)
        
        # Normalize scores
        for trait in fused_scores:
            fused_scores[trait] = max(0, min(100, fused_scores[trait]))
        
        self.logger.info(f"Cross-modal personality analysis completed: {fused_scores}")
        return fused_scores
    
    async def _collect_source_scores(self, data: Dict[str, Any]) -> Dict[DataSource, Dict[PersonalityTrait, float]]:
        """Collect personality scores from all data sources."""
        source_scores = {}
        
        # Process agent results
        agent_results = data.get("agent_results", [])
        for result in agent_results:
            if result.personality_insights:
                source_scores[result.agent_type] = result.personality_insights
        
        # Process survey responses
        survey_responses = data.get("survey_responses", {})
        if survey_responses:
            survey_scores = await self._analyze_survey_responses(survey_responses)
            source_scores[DataSource.SURVEY] = survey_scores
        
        # Process conversation history
        conversation_history = data.get("conversation_history", [])
        if conversation_history:
            conversation_scores = await self._analyze_conversation_patterns(conversation_history)
            source_scores[DataSource.CONVERSATION] = conversation_scores
        
        return source_scores
    
    async def _analyze_survey_responses(self, survey_responses: Dict[str, Any]) -> Dict[PersonalityTrait, float]:
        """Analyze survey responses for personality insights."""
        trait_scores = {trait: 50.0 for trait in PersonalityTrait}
        trait_counts = {trait: 0 for trait in PersonalityTrait}
        
        for question_id, response in survey_responses.items():
            if question_id in self.survey_mappings:
                mappings = self.survey_mappings[question_id]
                
                # Convert response to numerical score (assuming 1-5 or 1-7 scale)
                if isinstance(response, (int, float)):
                    score = response
                elif isinstance(response, str):
                    # Handle text responses
                    score = self._convert_text_response_to_score(response)
                else:
                    continue
                
                # Normalize score to 0-1 range (assuming 1-5 scale)
                normalized_score = (score - 1) / 4 if score >= 1 else 0.5
                
                # Apply to relevant traits
                for trait, weight in mappings.items():
                    if weight > 0:
                        trait_scores[trait] += (normalized_score * 100) * abs(weight)
                    else:
                        trait_scores[trait] += ((1 - normalized_score) * 100) * abs(weight)
                    trait_counts[trait] += 1
        
        # Average scores by number of questions per trait
        for trait in trait_scores:
            if trait_counts[trait] > 0:
                trait_scores[trait] = trait_scores[trait] / trait_counts[trait]
        
        return trait_scores
    
    def _convert_text_response_to_score(self, response: str) -> float:
        """Convert text response to numerical score."""
        response_lower = response.lower()
        
        # Mapping text responses to scores
        if any(word in response_lower for word in ["strongly agree", "very much", "always"]):
            return 5.0
        elif any(word in response_lower for word in ["agree", "often", "usually"]):
            return 4.0
        elif any(word in response_lower for word in ["neutral", "sometimes", "maybe"]):
            return 3.0
        elif any(word in response_lower for word in ["disagree", "rarely", "seldom"]):
            return 2.0
        elif any(word in response_lower for word in ["strongly disagree", "never", "not at all"]):
            return 1.0
        else:
            return 3.0  # Default neutral
    
    async def _analyze_conversation_patterns(self, conversation_history: List[Dict[str, Any]]) -> Dict[PersonalityTrait, float]:
        """Analyze conversation patterns for personality insights."""
        trait_scores = {trait: 50.0 for trait in PersonalityTrait}
        
        if not conversation_history:
            return trait_scores
        
        # Simple conversation analysis (can be enhanced with NLP)
        total_messages = len(conversation_history)
        
        # Analyze message characteristics
        long_messages = 0
        question_messages = 0
        emotional_messages = 0
        
        for message in conversation_history:
            content = message.get("content", "")
            
            # Long messages might indicate extraversion or openness
            if len(content) > 100:
                long_messages += 1
            
            # Questions might indicate curiosity (openness)
            if "?" in content:
                question_messages += 1
            
            # Emotional language might indicate neuroticism or agreeableness
            emotional_words = ["feel", "emotion", "happy", "sad", "angry", "excited", "worried"]
            if any(word in content.lower() for word in emotional_words):
                emotional_messages += 1
        
        # Apply conversation-based adjustments
        if total_messages > 0:
            long_message_ratio = long_messages / total_messages
            question_ratio = question_messages / total_messages
            emotional_ratio = emotional_messages / total_messages
            
            # Adjust traits based on conversation patterns
            trait_scores[PersonalityTrait.EXTRAVERSION] += (long_message_ratio - 0.3) * 10
            trait_scores[PersonalityTrait.OPENNESS] += (question_ratio - 0.2) * 15
            trait_scores[PersonalityTrait.NEUROTICISM] += (emotional_ratio - 0.3) * 10
            trait_scores[PersonalityTrait.AGREEABLENESS] += (emotional_ratio - 0.3) * 8
        
        return trait_scores
    
    async def _apply_cross_modal_fusion(self, source_scores: Dict[DataSource, Dict[PersonalityTrait, float]]) -> Dict[PersonalityTrait, float]:
        """Apply cross-modal fusion to combine scores from different sources."""
        fused_scores = {trait: 0.0 for trait in PersonalityTrait}
        total_weights = {trait: 0.0 for trait in PersonalityTrait}
        
        for source, scores in source_scores.items():
            source_weight = self.fusion_weights.get(source, 0.1)
            
            for trait, score in scores.items():
                fused_scores[trait] += score * source_weight
                total_weights[trait] += source_weight
        
        # Normalize by total weights
        for trait in fused_scores:
            if total_weights[trait] > 0:
                fused_scores[trait] = fused_scores[trait] / total_weights[trait]
            else:
                fused_scores[trait] = 50.0  # Default neutral score
        
        return fused_scores
    
    async def _apply_trait_correlations(self, scores: Dict[PersonalityTrait, float]) -> Dict[PersonalityTrait, float]:
        """Apply trait correlations to ensure psychological consistency."""
        adjusted_scores = scores.copy()
        
        for trait1, correlations in self.trait_correlations.items():
            for trait2, correlation in correlations.items():
                # Apply bidirectional correlation adjustment
                if trait1 in scores and trait2 in scores:
                    # Correlation strength influences how much traits should align
                    score1_normalized = (scores[trait1] - 50) / 50  # -1 to 1
                    score2_normalized = (scores[trait2] - 50) / 50  # -1 to 1
                    
                    # Expected score2 based on correlation with score1
                    expected_score2 = 50 + (score1_normalized * correlation * 50)
                    
                    # Adjust score2 slightly towards expected value
                    adjustment_strength = 0.1  # How much to adjust (10%)
                    adjusted_scores[trait2] += (expected_score2 - scores[trait2]) * adjustment_strength
        
        return adjusted_scores
    
    async def _calculate_cross_modal_correlations(self, agent_results: List[AgentAnalysisResult]) -> Dict[str, Dict[str, float]]:
        """Calculate correlations between different agent assessments."""
        correlations = {}
        
        if len(agent_results) < 2:
            return correlations
        
        # Create matrix of scores by agent and trait
        agent_scores = {}
        for result in agent_results:
            agent_scores[result.agent_type.value] = result.personality_insights
        
        # Calculate pairwise correlations between agents
        agent_names = list(agent_scores.keys())
        for i, agent1 in enumerate(agent_names):
            correlations[agent1] = {}
            for j, agent2 in enumerate(agent_names):
                if i != j:
                    correlation = await self._calculate_agent_correlation(
                        agent_scores[agent1], agent_scores[agent2]
                    )
                    correlations[agent1][agent2] = correlation
        
        return correlations
    
    async def _calculate_agent_correlation(self, scores1: Dict[PersonalityTrait, float], scores2: Dict[PersonalityTrait, float]) -> float:
        """Calculate correlation between two agent assessments."""
        if not scores1 or not scores2:
            return 0.0
        
        # Get common traits
        common_traits = set(scores1.keys()) & set(scores2.keys())
        if len(common_traits) < 2:
            return 0.0
        
        # Calculate Pearson correlation
        values1 = [scores1[trait] for trait in common_traits]
        values2 = [scores2[trait] for trait in common_traits]
        
        try:
            # Simple correlation calculation
            mean1 = sum(values1) / len(values1)
            mean2 = sum(values2) / len(values2)
            
            numerator = sum((v1 - mean1) * (v2 - mean2) for v1, v2 in zip(values1, values2))
            denominator1 = sum((v1 - mean1) ** 2 for v1 in values1) ** 0.5
            denominator2 = sum((v2 - mean2) ** 2 for v2 in values2) ** 0.5
            
            if denominator1 * denominator2 == 0:
                return 0.0
            
            correlation = numerator / (denominator1 * denominator2)
            return correlation
            
        except Exception as e:
            self.logger.error(f"Error calculating correlation: {e}")
            return 0.0
    
    async def _assess_data_quality(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Assess the quality of available personality data."""
        quality_metrics = {
            "overall_quality": 0.0,
            "data_completeness": 0.0,
            "cross_modal_consistency": 0.0,
            "temporal_stability": 0.0,
            "source_reliability": 0.0
        }
        
        # Data completeness
        agent_results = data.get("agent_results", [])
        survey_responses = data.get("survey_responses", {})
        
        completeness_score = 0.0
        if agent_results:
            completeness_score += 0.6  # 60% for agent data
        if survey_responses:
            completeness_score += 0.4  # 40% for survey data
        
        quality_metrics["data_completeness"] = completeness_score
        
        # Cross-modal consistency (based on correlations)
        correlations = data.get("cross_modal_correlations", {})
        if correlations:
            all_correlations = []
            for agent1_corrs in correlations.values():
                all_correlations.extend(agent1_corrs.values())
            
            if all_correlations:
                avg_correlation = sum(abs(corr) for corr in all_correlations) / len(all_correlations)
                quality_metrics["cross_modal_consistency"] = avg_correlation
        
        # Source reliability (based on data richness)
        reliability_score = 0.0
        for result in agent_results:
            if result.status.value == "completed" and result.confidence_scores:
                avg_confidence = sum(result.confidence_scores.values()) / len(result.confidence_scores)
                reliability_score += avg_confidence / len(agent_results)
        
        quality_metrics["source_reliability"] = reliability_score
        
        # Overall quality (weighted average)
        quality_metrics["overall_quality"] = (
            quality_metrics["data_completeness"] * 0.4 +
            quality_metrics["cross_modal_consistency"] * 0.3 +
            quality_metrics["source_reliability"] * 0.3
        )
        
        return quality_metrics
    
    async def create_personality_profile(self, data: Dict[str, Any]) -> PersonalityProfile:
        """Create a comprehensive personality profile from all available data."""
        # Get fused personality scores
        fused_scores = await self.analyze_personality(data)
        
        # Calculate confidence scores
        confidence_scores = await self._calculate_overall_confidence_scores(data, fused_scores)
        
        # Create PersonalityScore objects
        personality_scores = {}
        for trait, score in fused_scores.items():
            confidence = confidence_scores.get(trait, 0.5)
            
            personality_scores[trait] = PersonalityScore(
                trait=trait,
                score=score,
                confidence=confidence,
                confidence_level=self._get_confidence_level(confidence),
                data_points=self._count_data_points_for_trait(data, trait)
            )
        
        # Calculate overall confidence
        overall_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.0
        
        # Determine data sources
        data_sources = []
        if data.get("agent_results"):
            data_sources.extend([result.agent_type for result in data["agent_results"]])
        if data.get("survey_responses"):
            data_sources.append(DataSource.SURVEY)
        if data.get("conversation_history"):
            data_sources.append(DataSource.CONVERSATION)
        
        # Create profile
        profile = PersonalityProfile(
            user_id=self.user_id,
            scores=personality_scores,
            overall_confidence=overall_confidence,
            data_sources=list(set(data_sources))  # Remove duplicates
        )
        
        return profile
    
    async def _calculate_overall_confidence_scores(self, data: Dict[str, Any], scores: Dict[PersonalityTrait, float]) -> Dict[PersonalityTrait, float]:
        """Calculate confidence scores for each personality trait."""
        confidence_scores = {}
        
        for trait in PersonalityTrait:
            confidence = 0.0
            confidence_count = 0
            
            # Confidence from agent results
            agent_results = data.get("agent_results", [])
            for result in agent_results:
                if trait in result.confidence_scores:
                    confidence += result.confidence_scores[trait]
                    confidence_count += 1
            
            # Base confidence from data quality
            data_quality = data.get("data_quality_metrics", {}).get("overall_quality", 0.5)
            confidence += data_quality
            confidence_count += 1
            
            # Confidence from cross-modal consistency
            correlations = data.get("cross_modal_correlations", {})
            if correlations:
                consistency_boost = min(0.2, data_quality * 0.3)
                confidence += consistency_boost
            
            # Average confidence
            confidence_scores[trait] = confidence / confidence_count if confidence_count > 0 else 0.5
            
            # Cap confidence at 1.0
            confidence_scores[trait] = min(1.0, confidence_scores[trait])
        
        return confidence_scores
    
    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Convert numerical confidence to confidence level enum."""
        for level, (min_val, max_val) in self.confidence_thresholds.items():
            if min_val <= confidence < max_val:
                return level
        return ConfidenceLevel.HIGH if confidence >= 0.7 else ConfidenceLevel.LOW
    
    def _count_data_points_for_trait(self, data: Dict[str, Any], trait: PersonalityTrait) -> int:
        """Count the number of data points contributing to a trait assessment."""
        count = 0
        
        # Count from agent results
        agent_results = data.get("agent_results", [])
        for result in agent_results:
            if trait in result.personality_insights:
                count += 1
        
        # Count from survey responses
        survey_responses = data.get("survey_responses", {})
        for question_id in survey_responses:
            if question_id in self.survey_mappings and trait in self.survey_mappings[question_id]:
                count += 1
        
        # Count from conversation history (simplified)
        if data.get("conversation_history"):
            count += 1
        
        return count
    
    async def _get_trait_confidence(self, trait: PersonalityTrait, data: Dict[str, Any]) -> float:
        """Calculate confidence for specific traits based on all available data."""
        base_confidence = 0.2
        
        # More data sources = higher confidence
        data_sources = len(data.get("agent_results", []))
        if data.get("survey_responses"):
            data_sources += 1
        if data.get("conversation_history"):
            data_sources += 1
        
        base_confidence += min(0.3, data_sources * 0.1)
        
        # Data quality affects confidence
        data_quality = data.get("data_quality_metrics", {}).get("overall_quality", 0.5)
        base_confidence += data_quality * 0.2
        
        # Cross-modal consistency affects confidence
        consistency = data.get("data_quality_metrics", {}).get("cross_modal_consistency", 0.5)
        base_confidence += consistency * 0.1
        
        return min(0.8, base_confidence)  # Cap at 80% confidence