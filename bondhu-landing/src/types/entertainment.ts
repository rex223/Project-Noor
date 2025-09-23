// Entertainment and Analytics Types for Bondhu

export interface GameData {
  id: string
  name: string
  category: 'puzzle' | 'strategy' | 'creative' | 'social'
  description: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  duration: string
  icon: string
  learningInsights: string[]
  component: React.ComponentType<{ onGameComplete: (data: GameplayData) => void }>
}

export interface GameplayData {
  gameId: string
  userId: string
  sessionId: string
  startTime: Date
  endTime: Date
  completionRate: number
  choices: GameChoice[]
  performance: {
    speed: number
    accuracy: number
    persistence: number
    creativity: number
    social_interaction: number
  }
  emotionalState: 'frustrated' | 'engaged' | 'bored' | 'excited' | 'calm'
}

export interface GameChoice {
  timestamp: Date
  action: string
  context: string
  reasoning?: string
}

export interface VideoContent {
  id: string
  title: string
  description: string
  category: 'mental_health' | 'entertainment' | 'educational'
  duration: number
  thumbnail: string
  url: string
  tags: string[]
  personality_relevance: PersonalityRelevance
}

export interface VideoWatchData {
  contentId: string
  userId: string
  sessionId: string
  watchTime: number
  totalDuration: number
  completionRate: number
  interactions: VideoInteraction[]
  emotionalResponse: EmotionalResponse[]
  skipPatterns: SkipPattern[]
}

export interface VideoInteraction {
  timestamp: number
  action: 'pause' | 'play' | 'seek' | 'replay' | 'comment' | 'like' | 'share'
  context?: string
}

export interface MusicTrack {
  id: string
  title: string
  artist: string
  genre: string
  mood: string[]
  energy_level: number
  valence: number
  tempo: number
  duration: number
  url: string
  album_art?: string
}

export interface MusicListeningData {
  trackId: string
  userId: string
  sessionId: string
  playTime: number
  totalDuration: number
  skipTime?: number
  repeatCount: number
  volume: number
  mood_context: string
  activity_context: string
  social_context: 'alone' | 'with_friends' | 'public'
}

export interface PersonalityRelevance {
  openness: number
  conscientiousness: number
  extraversion: number
  agreeableness: number
  neuroticism: number
  confidence: number
}

export interface EmotionalResponse {
  timestamp: number
  emotion: 'joy' | 'sadness' | 'anger' | 'fear' | 'surprise' | 'disgust' | 'neutral'
  intensity: number
  context: string
}

export interface SkipPattern {
  startTime: number
  endTime: number
  reason?: 'boring' | 'too_difficult' | 'emotional' | 'time_constraint'
}

export interface EntertainmentAnalytics {
  userId: string
  period: 'daily' | 'weekly' | 'monthly'
  gaming: {
    total_time: number
    preferred_categories: string[]
    skill_progression: SkillProgression
    personality_insights: PersonalityInsight[]
  }
  video: {
    total_watch_time: number
    completion_rates: Record<string, number>
    content_preferences: ContentPreference[]
    attention_patterns: AttentionPattern[]
  }
  music: {
    total_listening_time: number
    mood_patterns: MoodPattern[]
    genre_preferences: GenrePreference[]
    discovery_rate: number
  }
  cross_modal_insights: CrossModalInsight[]
}

export interface SkillProgression {
  problem_solving: number
  creativity: number
  social_skills: number
  emotional_regulation: number
  focus: number
}

export interface PersonalityInsight {
  trait: string
  current_score: number
  trend: 'increasing' | 'decreasing' | 'stable'
  confidence: number
  supporting_evidence: string[]
}

export interface ContentPreference {
  category: string
  preference_score: number
  emotional_impact: number
  learning_value: number
}

export interface AttentionPattern {
  content_type: string
  average_watch_time: number
  optimal_duration: number
  drop_off_points: number[]
}

export interface MoodPattern {
  mood: string
  frequency: number
  music_correlation: string[]
  time_patterns: string[]
}

export interface GenrePreference {
  genre: string
  preference_score: number
  mood_association: string[]
  time_context: string[]
}

export interface CrossModalInsight {
  insight_type: string
  description: string
  evidence_sources: string[]
  personality_correlation: PersonalityRelevance
  actionable_recommendations: string[]
}

export interface ProfileDashboardData {
  personality_overview: {
    big_five_scores: Record<string, number>
    trait_evolution: TraitEvolution[]
    strengths: string[]
    growth_areas: string[]
  }
  entertainment_insights: {
    gaming_personality: GamePersonalityProfile
    viewing_behavior: ViewingBehaviorProfile
    musical_personality: MusicalPersonalityProfile
  }
  ai_recommendations: {
    content_suggestions: ContentSuggestion[]
    activity_recommendations: ActivityRecommendation[]
    conversation_topics: string[]
  }
  privacy_controls: {
    data_sharing_preferences: Record<string, boolean>
    retention_settings: Record<string, number>
    export_options: string[]
  }
}

export interface TraitEvolution {
  trait: string
  historical_scores: { date: Date; score: number }[]
  trend: 'improving' | 'declining' | 'stable'
  milestones: Milestone[]
}

export interface Milestone {
  date: Date
  description: string
  impact: string
  evidence: string[]
}

export interface GamePersonalityProfile {
  preferred_game_types: string[]
  problem_solving_style: string
  social_gaming_preference: number
  challenge_seeking: number
  persistence: number
  creativity_in_gaming: number
}

export interface ViewingBehaviorProfile {
  content_preference_map: Record<string, number>
  attention_span_insights: {
    average_session_length: number
    optimal_content_duration: number
    engagement_patterns: string[]
  }
  emotional_content_response: Record<string, number>
  learning_style_indicators: string[]
}

export interface MusicalPersonalityProfile {
  genre_personality_correlation: Record<string, number>
  mood_regulation_patterns: MoodRegulationPattern[]
  social_music_behavior: {
    sharing_frequency: number
    playlist_creation: number
    discovery_openness: number
  }
  sensory_preferences: {
    tempo_preference: number
    complexity_tolerance: number
    emotional_intensity: number
  }
}

export interface MoodRegulationPattern {
  mood_state: string
  music_strategy: string[]
  effectiveness: number
  frequency: number
}

export interface ContentSuggestion {
  type: 'game' | 'video' | 'music'
  content_id: string
  title: string
  reason: string
  personality_match: number
  mood_appropriateness: number
}

export interface ActivityRecommendation {
  activity: string
  description: string
  personality_benefits: string[]
  estimated_duration: string
  difficulty: 'easy' | 'medium' | 'hard'
}

export interface EntertainmentSession {
  id: string
  userId: string
  startTime: Date
  endTime?: Date
  activities: SessionActivity[]
  mood_before: string
  mood_after?: string
  notes?: string
}

export interface SessionActivity {
  type: 'gaming' | 'video' | 'music' | 'chat'
  content_id: string
  duration: number
  engagement_score: number
  learning_data?: any
}
