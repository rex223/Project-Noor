export interface PersonalityQuestion {
  id: number
  traitId: 'openness' | 'conscientiousness' | 'extraversion' | 'agreeableness' | 'neuroticism'
  scenario: string
  questionText: string
  isReversed: boolean
  userResponse?: number // 1-5 scale
}

export interface PersonalityTrait {
  id: 'openness' | 'conscientiousness' | 'extraversion' | 'agreeableness' | 'neuroticism'
  displayName: string
  storyTitle: string
  storyDescription: string
  color: string
  questions: PersonalityQuestion[]
  imageUrl: string
  completedQuestions: number
  totalQuestions: number
}

export interface PersonalityScores {
  openness: number // 0-100 scale
  conscientiousness: number
  extraversion: number
  agreeableness: number
  neuroticism: number
}

export interface LLMPersonalityContext {
  conversationStyle: string
  communicationPreferences: string
  supportApproach: string
  topicPreferences: string[]
  stressResponse: string
  motivationStyle: string
  interactionFrequency: string
  languageStyle: string
  conflictApproach: string
  emotionalSupport: string
  systemPrompt: string
}

export interface PersonalityProfile {
  userId: string
  scores: PersonalityScores
  rawResponses: Record<number, number> // questionId -> response
  completedAt: Date
  llmContext: LLMPersonalityContext
}

export interface PersonalityAssessmentState {
  currentCardIndex: number
  totalCards: number
  responses: Record<number, number>
  isCompleted: boolean
  startedAt: Date
  estimatedTimeRemaining?: number
}

export interface TraitInsight {
  traitId: string
  score: number
  level: 'low' | 'medium' | 'high'
  description: string
  bondhuAdaptation: string
  growthSuggestions: string[]
}

export interface AssessmentResults {
  scores: PersonalityScores
  insights: TraitInsight[]
  llmContext: LLMPersonalityContext
  personalityType: string
  strengthsOverview: string
  bondhuPersonalization: string
}



