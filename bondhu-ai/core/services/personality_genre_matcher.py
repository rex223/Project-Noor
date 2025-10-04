"""
Personality-Genre Matching Service

Advanced system to map Big Five personality traits to video genre preferences
with dynamic weighting based on trait combinations and user behavior patterns.
"""

import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import numpy as np

from core.database.models import PersonalityTrait

logger = logging.getLogger("bondhu.personality_genre_matcher")


@dataclass
class GenreMatch:
    """Represents how well a genre matches a personality profile."""
    genre: str
    match_score: float  # 0.0 to 1.0
    contributing_traits: List[Tuple[PersonalityTrait, float]]  # Which traits contributed
    confidence: float  # How confident we are in this match
    reasoning: str  # Human-readable explanation


class PersonalityGenreMatcher:
    """Advanced personality-to-genre matching with trait interaction modeling."""
    
    def __init__(self):
        self.logger = logging.getLogger("bondhu.personality_genre_matcher")
        
        # Define base trait-genre relationships
        self.trait_genre_weights = self._build_trait_genre_matrix()
        
        # Define trait interaction effects
        self.trait_interactions = self._build_trait_interactions()
        
        # Define genre compatibility matrix (some genres work well together)
        self.genre_compatibility = self._build_genre_compatibility()

    def _build_trait_genre_matrix(self) -> Dict[PersonalityTrait, Dict[str, float]]:
        """Build comprehensive trait-to-genre weight matrix."""
        return {
            PersonalityTrait.OPENNESS: {
                # High openness: Creative, intellectual, adventurous content
                "art": 0.9,
                "documentaries": 0.85,
                "travel": 0.8,
                "science": 0.75,
                "culture": 0.75,
                "music": 0.7,
                "photography": 0.65,
                "crafts": 0.6,
                "education": 0.6,
                "food": 0.5,
                "technology": 0.5,
                # Lower for routine/predictable content
                "news": 0.3,
                "sports": 0.25,
                "gaming": 0.3,
            },
            
            PersonalityTrait.CONSCIENTIOUSNESS: {
                # High conscientiousness: Educational, productive, structured content
                "education": 0.9,
                "productivity": 0.85,
                "business": 0.8,
                "documentaries": 0.7,
                "fitness": 0.7,
                "technology": 0.6,
                "news": 0.6,
                "science": 0.6,
                "motivation": 0.8,
                # Lower for pure entertainment
                "comedy": 0.3,
                "entertainment": 0.25,
                "gaming": 0.2,
                "social_commentary": 0.4,
            },
            
            PersonalityTrait.EXTRAVERSION: {
                # High extraversion: Social, entertaining, energetic content
                "comedy": 0.9,
                "entertainment": 0.85,
                "social_commentary": 0.8,
                "music": 0.75,
                "travel": 0.7,
                "lifestyle": 0.7,
                "sports": 0.65,
                "gaming": 0.6,
                "fashion": 0.6,
                "food": 0.5,
                # Lower for solitary/quiet activities
                "education": 0.3,
                "documentaries": 0.25,
                "crafts": 0.2,
                "productivity": 0.3,
            },
            
            PersonalityTrait.AGREEABLENESS: {
                # High agreeableness: Harmonious, helpful, community-focused content
                "lifestyle": 0.85,
                "food": 0.8,
                "crafts": 0.75,
                "culture": 0.7,
                "education": 0.7,
                "motivation": 0.65,
                "travel": 0.6,
                "art": 0.6,
                "fitness": 0.5,
                "music": 0.5,
                # Lower for competitive/controversial content
                "gaming": 0.3,
                "sports": 0.25,
                "politics": 0.1,
                "social_commentary": 0.2,
            },
            
            PersonalityTrait.NEUROTICISM: {
                # High neuroticism: Calming, uplifting, stress-reducing content
                # Note: Higher neuroticism means MORE emotional reactivity, so we prefer calming content
                "motivation": 0.85,
                "lifestyle": 0.8,
                "fitness": 0.75,
                "music": 0.7,
                "comedy": 0.65,  # Positive comedy can reduce stress
                "art": 0.6,
                "crafts": 0.6,
                "outdoor": 0.7,
                "food": 0.5,
                # Much lower for stressful/negative content
                "news": 0.1,
                "politics": 0.05,
                "social_commentary": 0.15,
                "documentaries": 0.3,  # Depends on topic
            }
        }

    def _build_trait_interactions(self) -> Dict[Tuple[PersonalityTrait, PersonalityTrait], Dict[str, float]]:
        """Define how trait combinations affect genre preferences."""
        return {
            # High Openness + High Conscientiousness = Educational exploration
            (PersonalityTrait.OPENNESS, PersonalityTrait.CONSCIENTIOUSNESS): {
                "education": 0.2,
                "science": 0.15,
                "documentaries": 0.15,
                "technology": 0.1
            },
            
            # High Extraversion + High Agreeableness = Social entertainment
            (PersonalityTrait.EXTRAVERSION, PersonalityTrait.AGREEABLENESS): {
                "lifestyle": 0.15,
                "food": 0.1,
                "travel": 0.1,
                "comedy": 0.1
            },
            
            # High Conscientiousness + Low Neuroticism = Achievement content
            (PersonalityTrait.CONSCIENTIOUSNESS, PersonalityTrait.NEUROTICISM): {
                "business": 0.15,
                "productivity": 0.1,
                "motivation": 0.1,
                "fitness": 0.1
            },
            
            # High Openness + High Extraversion = Creative social content
            (PersonalityTrait.OPENNESS, PersonalityTrait.EXTRAVERSION): {
                "art": 0.1,
                "music": 0.1,
                "travel": 0.1,
                "culture": 0.1
            }
        }

    def _build_genre_compatibility(self) -> Dict[str, List[str]]:
        """Define which genres work well together in recommendations."""
        return {
            "education": ["science", "technology", "documentaries", "productivity"],
            "comedy": ["entertainment", "lifestyle", "music", "gaming"],
            "art": ["music", "photography", "crafts", "culture"],
            "fitness": ["motivation", "lifestyle", "outdoor", "food"],
            "technology": ["science", "education", "business", "productivity"],
            "travel": ["culture", "food", "photography", "outdoor"],
            "music": ["art", "entertainment", "culture", "comedy"],
            "food": ["lifestyle", "travel", "culture", "crafts"],
            "business": ["productivity", "motivation", "education", "technology"],
            "gaming": ["technology", "entertainment", "comedy", "social_commentary"]
        }

    def calculate_genre_matches(
        self, 
        personality_profile: Dict[PersonalityTrait, float],
        top_k: int = 10
    ) -> List[GenreMatch]:
        """Calculate how well each genre matches the personality profile."""
        
        # Normalize personality scores to 0-1 range
        normalized_profile = {}
        for trait, score in personality_profile.items():
            # Assume input scores are 0-100, normalize to 0-1
            normalized_profile[trait] = max(0, min(1, score / 100.0))
        
        genre_scores = {}
        genre_contributions = {}
        
        # Calculate base scores from individual traits
        for trait, trait_score in normalized_profile.items():
            if trait in self.trait_genre_weights:
                trait_weights = self.trait_genre_weights[trait]
                
                for genre, weight in trait_weights.items():
                    if genre not in genre_scores:
                        genre_scores[genre] = 0
                        genre_contributions[genre] = []
                    
                    contribution = trait_score * weight
                    genre_scores[genre] += contribution
                    genre_contributions[genre].append((trait, contribution))
        
        # Apply trait interaction bonuses
        for (trait1, trait2), interaction_weights in self.trait_interactions.items():
            score1 = normalized_profile.get(trait1, 0.5)
            score2 = normalized_profile.get(trait2, 0.5)
            
            # Special handling for neuroticism (inverted effect)
            if trait2 == PersonalityTrait.NEUROTICISM:
                score2 = 1.0 - score2  # Invert neuroticism for interaction
            
            interaction_strength = score1 * score2
            
            for genre, bonus in interaction_weights.items():
                if genre not in genre_scores:
                    genre_scores[genre] = 0
                    genre_contributions[genre] = []
                
                interaction_bonus = interaction_strength * bonus
                genre_scores[genre] += interaction_bonus
                genre_contributions[genre].append((trait1, interaction_bonus))
        
        # Create GenreMatch objects
        matches = []
        for genre, score in genre_scores.items():
            # Calculate confidence based on number of contributing traits
            num_contributors = len(genre_contributions[genre])
            confidence = min(1.0, num_contributors / 3.0)  # More traits = higher confidence
            
            # Generate reasoning
            top_contributors = sorted(
                genre_contributions[genre], 
                key=lambda x: x[1], 
                reverse=True
            )[:2]
            
            trait_names = [trait.value for trait, _ in top_contributors]
            reasoning = f"Strong match with your {' and '.join(trait_names)} traits"
            
            matches.append(GenreMatch(
                genre=genre,
                match_score=min(1.0, score),  # Cap at 1.0
                contributing_traits=genre_contributions[genre],
                confidence=confidence,
                reasoning=reasoning
            ))
        
        # Sort by match score and return top_k
        matches.sort(key=lambda x: x.match_score, reverse=True)
        return matches[:top_k]

    def get_diverse_genre_selection(
        self,
        personality_profile: Dict[PersonalityTrait, float],
        num_genres: int = 4,
        diversity_weight: float = 0.3
    ) -> List[GenreMatch]:
        """
        Select diverse genres that balance match quality with variety.
        
        Args:
            personality_profile: User's Big Five scores
            num_genres: Number of genres to select
            diversity_weight: How much to weight diversity vs match quality (0-1)
        """
        
        # Get all genre matches
        all_matches = self.calculate_genre_matches(personality_profile, top_k=20)
        
        if len(all_matches) <= num_genres:
            return all_matches
        
        selected_genres = []
        remaining_matches = all_matches.copy()
        
        # Always include the top match
        selected_genres.append(remaining_matches.pop(0))
        
        # Select remaining genres balancing quality and diversity
        while len(selected_genres) < num_genres and remaining_matches:
            best_candidate = None
            best_score = -1
            best_index = -1
            
            for i, candidate in enumerate(remaining_matches):
                # Calculate quality score
                quality_score = candidate.match_score
                
                # Calculate diversity score
                diversity_score = self._calculate_diversity_score(
                    candidate.genre, 
                    [g.genre for g in selected_genres]
                )
                
                # Combined score
                combined_score = (
                    (1 - diversity_weight) * quality_score +
                    diversity_weight * diversity_score
                )
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_candidate = candidate
                    best_index = i
            
            if best_candidate:
                selected_genres.append(best_candidate)
                remaining_matches.pop(best_index)
        
        return selected_genres

    def _calculate_diversity_score(self, candidate_genre: str, selected_genres: List[str]) -> float:
        """Calculate how diverse a candidate genre is from already selected genres."""
        if not selected_genres:
            return 1.0
        
        # Check genre compatibility matrix
        compatibility_scores = []
        
        for selected_genre in selected_genres:
            # Check if genres are in each other's compatibility lists
            candidate_compatible = self.genre_compatibility.get(candidate_genre, [])
            selected_compatible = self.genre_compatibility.get(selected_genre, [])
            
            if selected_genre in candidate_compatible or candidate_genre in selected_compatible:
                compatibility_scores.append(0.3)  # Some overlap, lower diversity
            else:
                compatibility_scores.append(1.0)  # No overlap, high diversity
        
        # Return average diversity score
        return sum(compatibility_scores) / len(compatibility_scores)

    def explain_genre_selection(
        self, 
        personality_profile: Dict[PersonalityTrait, float],
        selected_genres: List[GenreMatch]
    ) -> str:
        """Generate human-readable explanation for genre selection."""
        
        # Identify dominant traits
        normalized_profile = {
            trait: score / 100.0 for trait, score in personality_profile.items()
        }
        
        dominant_traits = [
            trait for trait, score in normalized_profile.items() 
            if score > 0.7
        ]
        
        moderate_traits = [
            trait for trait, score in normalized_profile.items() 
            if 0.4 <= score <= 0.7
        ]
        
        explanation_parts = []
        
        # Personality summary
        if dominant_traits:
            trait_names = [trait.value for trait in dominant_traits]
            explanation_parts.append(
                f"Based on your high {' and '.join(trait_names)} scores"
            )
        
        # Genre explanations
        genre_explanations = []
        for match in selected_genres:
            genre_explanations.append(
                f"{match.genre.title()} (match: {match.match_score:.1%})"
            )
        
        explanation_parts.append(
            f"we've selected these genres: {', '.join(genre_explanations)}"
        )
        
        # Diversity note
        explanation_parts.append(
            "This selection balances your personality preferences with content variety for discovery."
        )
        
        return ". ".join(explanation_parts) + "."


# Factory function
def create_personality_genre_matcher() -> PersonalityGenreMatcher:
    """Create a new personality-genre matcher instance."""
    return PersonalityGenreMatcher()