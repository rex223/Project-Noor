// AI Learning Engine for Cross-Modal Entertainment Data Analysis

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

export interface GameChoice {
  timestamp: Date
  action: string
  context: string
  reasoning?: string
}

export interface VideoInteraction {
  timestamp: number
  action: 'pause' | 'play' | 'seek' | 'replay' | 'comment' | 'like' | 'share'
  context?: string
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

export interface PersonalityInsights {
  bigFive: {
    openness: number
    conscientiousness: number
    extraversion: number
    agreeableness: number
    neuroticism: number
  }
  entertainmentProfile: {
    gaming: GamePersonalityProfile
    video: VideoPersonalityProfile
    music: MusicPersonalityProfile
  }
  crossModalInsights: CrossModalInsight[]
  recommendations: PersonalizedRecommendations
  trends: PersonalityTrends
}

export interface GamePersonalityProfile {
  problemSolvingStyle: 'analytical' | 'intuitive' | 'systematic' | 'creative'
  challengePreference: 'easy' | 'moderate' | 'difficult' | 'extreme'
  persistenceLevel: number // 0-100
  creativityScore: number // 0-100
  socialGamingPreference: number // 0-100
  riskTolerance: number // 0-100
  learningApproach: 'trial_error' | 'strategic' | 'exploratory' | 'methodical'
}

export interface VideoPersonalityProfile {
  attentionSpan: number // average watch duration
  contentPreferences: {
    educational: number
    entertainment: number
    mental_health: number
  }
  engagementPatterns: {
    skipTendency: number // 0-100
    completionRate: number // 0-100
    interactionFrequency: number // interactions per minute
  }
  learningStyle: 'visual' | 'auditory' | 'kinesthetic' | 'mixed'
  emotionalResponseProfile: {
    empathy: number
    emotional_stability: number
    content_sensitivity: number
  }
}

export interface MusicPersonalityProfile {
  moodRegulationStyle: 'active' | 'passive' | 'mixed'
  genrePreferences: Record<string, number>
  listeningBehavior: {
    focus_music_preference: number
    background_listening: number
    active_listening: number
  }
  emotionalAssociations: {
    happiness: string[] // preferred genres for happiness
    sadness: string[]
    stress: string[]
    creativity: string[]
  }
  socialListeningPreference: number // 0-100
  musicalSophistication: number // 0-100
}

export interface CrossModalInsight {
  type: 'correlation' | 'contradiction' | 'reinforcement' | 'evolution'
  description: string
  confidence: number // 0-100
  dataSources: ('gaming' | 'video' | 'music' | 'chat')[]
  personalityImpact: {
    trait: string
    direction: 'increase' | 'decrease' | 'stable'
    magnitude: number
  }
  actionableInsight: string
}

export interface PersonalizedRecommendations {
  games: GameRecommendation[]
  videos: VideoRecommendation[]
  music: MusicRecommendation[]
  activities: ActivityRecommendation[]
}

export interface GameRecommendation {
  gameId: string
  reason: string
  personalityMatch: number
  expectedBenefit: string
}

export interface VideoRecommendation {
  contentId: string
  reason: string
  optimalDuration: number
  personalityRelevance: string
}

export interface MusicRecommendation {
  genre: string
  mood: string
  reason: string
  optimalContext: string
}

export interface ActivityRecommendation {
  activity: string
  description: string
  personalityBenefits: string[]
  estimatedDuration: string
}

export interface PersonalityTrends {
  traits: Array<{
    trait: string
    trend: 'increasing' | 'decreasing' | 'stable'
    rate: number // change per week
    confidence: number
  }>
  entertainmentEvolution: {
    gaming: 'more_creative' | 'more_strategic' | 'more_social' | 'stable'
    video: 'longer_attention' | 'shorter_attention' | 'more_selective' | 'stable'
    music: 'more_diverse' | 'more_focused' | 'more_emotional' | 'stable'
  }
}

export class AILearningEngine {
  private gameplayHistory: GameplayData[] = []
  private videoHistory: VideoWatchData[] = []
  private musicHistory: MusicListeningData[] = []
  private lastAnalysis: PersonalityInsights | null = null

  // Add new data
  addGameplayData(data: GameplayData) {
    this.gameplayHistory.push(data)
    this.triggerAnalysis()
  }

  addVideoData(data: VideoWatchData) {
    this.videoHistory.push(data)
    this.triggerAnalysis()
  }

  addMusicData(data: MusicListeningData) {
    this.musicHistory.push(data)
    this.triggerAnalysis()
  }

  // Main analysis function
  private triggerAnalysis() {
    // Only analyze if we have sufficient data
    if (this.gameplayHistory.length + this.videoHistory.length + this.musicHistory.length < 3) {
      return
    }

    this.lastAnalysis = this.performComprehensiveAnalysis()
  }

  private performComprehensiveAnalysis(): PersonalityInsights {
    const gamingProfile = this.analyzeGamingBehavior()
    const videoProfile = this.analyzeVideoBehavior()
    const musicProfile = this.analyzeMusicBehavior()
    const bigFiveEstimate = this.estimateBigFiveTraits(gamingProfile, videoProfile, musicProfile)
    const crossModalInsights = this.generateCrossModalInsights(gamingProfile, videoProfile, musicProfile)

    return {
      bigFive: bigFiveEstimate,
      entertainmentProfile: {
        gaming: gamingProfile,
        video: videoProfile,
        music: musicProfile
      },
      crossModalInsights,
      recommendations: this.generateRecommendations(bigFiveEstimate, gamingProfile, videoProfile, musicProfile),
      trends: this.analyzeTrends()
    }
  }

  private analyzeGamingBehavior(): GamePersonalityProfile {
    if (this.gameplayHistory.length === 0) {
      return this.getDefaultGamingProfile()
    }

    const recentGames = this.gameplayHistory.slice(-10) // Last 10 games
    
    // Analyze problem-solving style
    const creativityScores = recentGames.map(g => g.performance.creativity)
    const avgCreativity = creativityScores.reduce((a, b) => a + b, 0) / creativityScores.length

    const persistenceScores = recentGames.map(g => g.performance.persistence)
    const avgPersistence = persistenceScores.reduce((a, b) => a + b, 0) / persistenceScores.length

    const speedScores = recentGames.map(g => g.performance.speed)
    const avgSpeed = speedScores.reduce((a, b) => a + b, 0) / speedScores.length

    // Determine problem-solving style
    let problemSolvingStyle: GamePersonalityProfile['problemSolvingStyle'] = 'systematic'
    if (avgCreativity > 70) problemSolvingStyle = 'creative'
    else if (avgSpeed > 70) problemSolvingStyle = 'intuitive'
    else if (avgPersistence > 80) problemSolvingStyle = 'analytical'

    // Analyze challenge preference
    const completionRates = recentGames.map(g => g.completionRate)
    const avgCompletion = completionRates.reduce((a, b) => a + b, 0) / completionRates.length
    
    let challengePreference: GamePersonalityProfile['challengePreference'] = 'moderate'
    if (avgCompletion > 90) challengePreference = 'easy'
    else if (avgCompletion < 50) challengePreference = 'difficult'

    return {
      problemSolvingStyle,
      challengePreference,
      persistenceLevel: avgPersistence,
      creativityScore: avgCreativity,
      socialGamingPreference: 20, // Most games are single-player for now
      riskTolerance: avgSpeed, // Higher speed indicates more risk tolerance
      learningApproach: avgCreativity > 60 ? 'exploratory' : 'methodical'
    }
  }

  private analyzeVideoBehavior(): VideoPersonalityProfile {
    if (this.videoHistory.length === 0) {
      return this.getDefaultVideoProfile()
    }

    const recentVideos = this.videoHistory.slice(-10)
    
    // Calculate attention span
    const watchTimes = recentVideos.map(v => v.watchTime)
    const avgWatchTime = watchTimes.reduce((a, b) => a + b, 0) / watchTimes.length

    // Calculate completion rates
    const completionRates = recentVideos.map(v => v.completionRate)
    const avgCompletion = completionRates.reduce((a, b) => a + b, 0) / completionRates.length

    // Analyze skip patterns
    const totalSkips = recentVideos.reduce((total, v) => total + v.skipPatterns.length, 0)
    const skipTendency = Math.min((totalSkips / recentVideos.length) * 20, 100) // Normalize to 0-100

    // Analyze interaction frequency
    const totalInteractions = recentVideos.reduce((total, v) => total + v.interactions.length, 0)
    const avgInteractionFreq = totalInteractions / recentVideos.length

    return {
      attentionSpan: avgWatchTime,
      contentPreferences: {
        educational: 70, // Mock - would analyze based on content categories
        entertainment: 60,
        mental_health: 80
      },
      engagementPatterns: {
        skipTendency,
        completionRate: avgCompletion,
        interactionFrequency: avgInteractionFreq
      },
      learningStyle: avgCompletion > 80 ? 'visual' : 'mixed',
      emotionalResponseProfile: {
        empathy: 75, // Would analyze based on content choices and responses
        emotional_stability: Math.max(100 - skipTendency, 0),
        content_sensitivity: skipTendency > 50 ? 80 : 40
      }
    }
  }

  private analyzeMusicBehavior(): MusicPersonalityProfile {
    if (this.musicHistory.length === 0) {
      return this.getDefaultMusicProfile()
    }

    // For now, return a sample profile since music data structure needs more implementation
    return {
      moodRegulationStyle: 'active',
      genrePreferences: {
        'ambient': 80,
        'classical': 60,
        'electronic': 40,
        'jazz': 70
      },
      listeningBehavior: {
        focus_music_preference: 85,
        background_listening: 60,
        active_listening: 40
      },
      emotionalAssociations: {
        happiness: ['upbeat', 'pop'],
        sadness: ['classical', 'ambient'],
        stress: ['nature_sounds', 'meditation'],
        creativity: ['instrumental', 'jazz']
      },
      socialListeningPreference: 30,
      musicalSophistication: 65
    }
  }

  private estimateBigFiveTraits(
    gaming: GamePersonalityProfile,
    video: VideoPersonalityProfile,
    music: MusicPersonalityProfile
  ) {
    // Estimate Big Five traits based on entertainment behavior
    const openness = Math.round(
      (gaming.creativityScore * 0.4 + 
       video.contentPreferences.educational * 0.3 + 
       music.musicalSophistication * 0.3)
    )

    const conscientiousness = Math.round(
      (gaming.persistenceLevel * 0.5 + 
       video.engagementPatterns.completionRate * 0.3 + 
       music.listeningBehavior.focus_music_preference * 0.2)
    )

    const extraversion = Math.round(
      (gaming.socialGamingPreference * 0.4 + 
       music.socialListeningPreference * 0.4 + 
       video.emotionalResponseProfile.empathy * 0.2)
    )

    const agreeableness = Math.round(
      (video.emotionalResponseProfile.empathy * 0.6 + 
       gaming.socialGamingPreference * 0.2 + 
       music.emotionalAssociations.happiness.length * 10 * 0.2)
    )

    const neuroticism = Math.round(
      Math.max(0, 100 - (
        video.emotionalResponseProfile.emotional_stability * 0.5 + 
        gaming.persistenceLevel * 0.3 + 
        (100 - music.musicalSophistication) * 0.2
      ))
    )

    return {
      openness: Math.min(100, Math.max(0, openness)),
      conscientiousness: Math.min(100, Math.max(0, conscientiousness)),
      extraversion: Math.min(100, Math.max(0, extraversion)),
      agreeableness: Math.min(100, Math.max(0, agreeableness)),
      neuroticism: Math.min(100, Math.max(0, neuroticism))
    }
  }

  private generateCrossModalInsights(
    gaming: GamePersonalityProfile,
    video: VideoPersonalityProfile,
    music: MusicPersonalityProfile
  ): CrossModalInsight[] {
    const insights: CrossModalInsight[] = []

    // Gaming-Video correlation
    if (gaming.creativityScore > 70 && video.contentPreferences.educational > 70) {
      insights.push({
        type: 'correlation',
        description: 'High gaming creativity correlates with preference for educational content',
        confidence: 85,
        dataSources: ['gaming', 'video'],
        personalityImpact: {
          trait: 'openness',
          direction: 'increase',
          magnitude: 5
        },
        actionableInsight: 'Consider creative educational content that combines learning with interactive elements'
      })
    }

    // Music-Video correlation
    if (music.moodRegulationStyle === 'active' && video.attentionSpan > 300) {
      insights.push({
        type: 'correlation',
        description: 'Active music mood regulation aligns with longer video attention spans',
        confidence: 78,
        dataSources: ['music', 'video'],
        personalityImpact: {
          trait: 'conscientiousness',
          direction: 'increase',
          magnitude: 3
        },
        actionableInsight: 'Use music as a focus tool while consuming longer-form content'
      })
    }

    // Gaming-Music correlation
    if (gaming.persistenceLevel > 80 && music.listeningBehavior.focus_music_preference > 70) {
      insights.push({
        type: 'reinforcement',
        description: 'High gaming persistence reinforces preference for focus-enhancing music',
        confidence: 82,
        dataSources: ['gaming', 'music'],
        personalityImpact: {
          trait: 'conscientiousness',
          direction: 'increase',
          magnitude: 4
        },
        actionableInsight: 'Leverage your natural persistence by pairing challenging tasks with focus music'
      })
    }

    return insights
  }

  private generateRecommendations(
    bigFive: PersonalityInsights['bigFive'],
    gaming: GamePersonalityProfile,
    video: VideoPersonalityProfile,
    music: MusicPersonalityProfile
  ): PersonalizedRecommendations {
    const gameRecs: GameRecommendation[] = []
    const videoRecs: VideoRecommendation[] = []
    const musicRecs: MusicRecommendation[] = []
    const activityRecs: ActivityRecommendation[] = []

    // Game recommendations based on personality
    if (bigFive.openness > 70) {
      gameRecs.push({
        gameId: 'color_symphony',
        reason: 'Your high openness suggests you\'ll enjoy creative expression games',
        personalityMatch: 85,
        expectedBenefit: 'Enhanced creative thinking and artistic exploration'
      })
    }

    if (gaming.persistenceLevel > 70) {
      gameRecs.push({
        gameId: 'puzzle_master',
        reason: 'Your persistence makes you well-suited for challenging puzzle games',
        personalityMatch: 80,
        expectedBenefit: 'Improved problem-solving skills and mental flexibility'
      })
    }

    // Video recommendations
    if (video.attentionSpan > 600 && bigFive.openness > 60) {
      videoRecs.push({
        contentId: 'science_happiness',
        reason: 'Your attention span and openness make you ideal for educational content',
        optimalDuration: 900,
        personalityRelevance: 'Matches your learning style and intellectual curiosity'
      })
    }

    // Music recommendations
    if (music.moodRegulationStyle === 'active') {
      musicRecs.push({
        genre: 'ambient',
        mood: 'focus',
        reason: 'Your active mood regulation style pairs well with ambient focus music',
        optimalContext: 'During work or study sessions'
      })
    }

    // Activity recommendations
    if (bigFive.conscientiousness > 70 && gaming.creativityScore > 60) {
      activityRecs.push({
        activity: 'Creative Goal Setting',
        description: 'Set artistic or creative goals with structured milestones',
        personalityBenefits: ['Combines your organization skills with creativity', 'Enhances long-term project completion'],
        estimatedDuration: '30-45 minutes weekly'
      })
    }

    return {
      games: gameRecs,
      videos: videoRecs,
      music: musicRecs,
      activities: activityRecs
    }
  }

  private analyzeTrends(): PersonalityTrends {
    // Simple trend analysis - would be more sophisticated in production
    return {
      traits: [
        {
          trait: 'openness',
          trend: 'increasing',
          rate: 0.5,
          confidence: 70
        },
        {
          trait: 'conscientiousness',
          trend: 'stable',
          rate: 0.1,
          confidence: 85
        }
      ],
      entertainmentEvolution: {
        gaming: 'more_creative',
        video: 'longer_attention',
        music: 'more_diverse'
      }
    }
  }

  // Default profiles for when no data is available
  private getDefaultGamingProfile(): GamePersonalityProfile {
    return {
      problemSolvingStyle: 'systematic',
      challengePreference: 'moderate',
      persistenceLevel: 50,
      creativityScore: 50,
      socialGamingPreference: 30,
      riskTolerance: 50,
      learningApproach: 'methodical'
    }
  }

  private getDefaultVideoProfile(): VideoPersonalityProfile {
    return {
      attentionSpan: 300,
      contentPreferences: {
        educational: 50,
        entertainment: 50,
        mental_health: 50
      },
      engagementPatterns: {
        skipTendency: 30,
        completionRate: 70,
        interactionFrequency: 2
      },
      learningStyle: 'mixed',
      emotionalResponseProfile: {
        empathy: 60,
        emotional_stability: 70,
        content_sensitivity: 40
      }
    }
  }

  private getDefaultMusicProfile(): MusicPersonalityProfile {
    return {
      moodRegulationStyle: 'mixed',
      genrePreferences: {},
      listeningBehavior: {
        focus_music_preference: 50,
        background_listening: 50,
        active_listening: 50
      },
      emotionalAssociations: {
        happiness: [],
        sadness: [],
        stress: [],
        creativity: []
      },
      socialListeningPreference: 50,
      musicalSophistication: 50
    }
  }

  // Public methods to get insights
  getLatestInsights(): PersonalityInsights | null {
    return this.lastAnalysis
  }

  getRecommendations(): PersonalizedRecommendations | null {
    return this.lastAnalysis?.recommendations || null
  }

  getCrossModalInsights(): CrossModalInsight[] {
    return this.lastAnalysis?.crossModalInsights || []
  }

  getPersonalityEstimate() {
    return this.lastAnalysis?.bigFive || null
  }

  // Method to export data for external AI services
  exportForExternalAnalysis() {
    return {
      gameplayHistory: this.gameplayHistory,
      videoHistory: this.videoHistory,
      musicHistory: this.musicHistory,
      currentInsights: this.lastAnalysis
    }
  }
}

// Singleton instance
export const aiLearningEngine = new AILearningEngine()
