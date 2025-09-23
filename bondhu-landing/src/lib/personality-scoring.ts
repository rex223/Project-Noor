import { PersonalityScores, TraitInsight } from '@/types/personality'
import { personalityQuestions } from '@/data/personality-questions'

export function calculatePersonalityScores(responses: Record<number, number>): PersonalityScores {
  // Validate all questions are answered
  const totalQuestions = 15
  const answeredQuestions = Object.keys(responses).length
  
  if (answeredQuestions !== totalQuestions) {
    throw new Error(`Incomplete assessment: ${answeredQuestions}/${totalQuestions} questions answered`)
  }

  // Group responses by trait
  const traitResponses: Record<string, number[]> = {
    openness: [],
    conscientiousness: [],
    extraversion: [],
    agreeableness: [],
    neuroticism: []
  }

  // Process each response
  Object.entries(responses).forEach(([questionIdStr, response]) => {
    const questionId = parseInt(questionIdStr)
    const question = personalityQuestions.find(q => q.id === questionId)
    
    if (!question) {
      throw new Error(`Question not found: ${questionId}`)
    }

    // Validate response range
    if (response < 1 || response > 5) {
      throw new Error(`Invalid response value: ${response} for question ${questionId}`)
    }

    // Apply reverse scoring if needed
    const processedResponse = question.isReversed 
      ? (6 - response) // 1→5, 2→4, 3→3, 4→2, 5→1
      : response

    traitResponses[question.traitId].push(processedResponse)
  })

  // Calculate trait averages and convert to 0-100 scale
  const scores: PersonalityScores = {
    openness: calculateTraitScore(traitResponses.openness),
    conscientiousness: calculateTraitScore(traitResponses.conscientiousness),
    extraversion: calculateTraitScore(traitResponses.extraversion),
    agreeableness: calculateTraitScore(traitResponses.agreeableness),
    neuroticism: calculateTraitScore(traitResponses.neuroticism)
  }

  return scores
}

function calculateTraitScore(responses: number[]): number {
  if (responses.length === 0) {
    throw new Error('No responses provided for trait calculation')
  }

  // Calculate average
  const sum = responses.reduce((acc, val) => acc + val, 0)
  const average = sum / responses.length

  // Convert to 0-100 scale: ((average - 1) / 4) * 100
  const score = ((average - 1) / 4) * 100

  // Round to whole number
  return Math.round(score)
}

export function generateTraitInsights(scores: PersonalityScores): TraitInsight[] {
  return [
    {
      traitId: 'openness',
      score: scores.openness,
      level: getScoreLevel(scores.openness),
      description: getOpennessDescription(scores.openness),
      bondhuAdaptation: getOpennessAdaptation(scores.openness),
      growthSuggestions: getOpennessGrowthSuggestions(scores.openness)
    },
    {
      traitId: 'conscientiousness',
      score: scores.conscientiousness,
      level: getScoreLevel(scores.conscientiousness),
      description: getConscientiousnessDescription(scores.conscientiousness),
      bondhuAdaptation: getConscientiousnessAdaptation(scores.conscientiousness),
      growthSuggestions: getConscientiousnessGrowthSuggestions(scores.conscientiousness)
    },
    {
      traitId: 'extraversion',
      score: scores.extraversion,
      level: getScoreLevel(scores.extraversion),
      description: getExtraversionDescription(scores.extraversion),
      bondhuAdaptation: getExtraversionAdaptation(scores.extraversion),
      growthSuggestions: getExtraversionGrowthSuggestions(scores.extraversion)
    },
    {
      traitId: 'agreeableness',
      score: scores.agreeableness,
      level: getScoreLevel(scores.agreeableness),
      description: getAgreeablenessDescription(scores.agreeableness),
      bondhuAdaptation: getAgreeablenessAdaptation(scores.agreeableness),
      growthSuggestions: getAgreeablenessGrowthSuggestions(scores.agreeableness)
    },
    {
      traitId: 'neuroticism',
      score: scores.neuroticism,
      level: getScoreLevel(scores.neuroticism),
      description: getNeuroticismDescription(scores.neuroticism),
      bondhuAdaptation: getNeuroticismAdaptation(scores.neuroticism),
      growthSuggestions: getNeuroticismGrowthSuggestions(scores.neuroticism)
    }
  ]
}

function getScoreLevel(score: number): 'low' | 'medium' | 'high' {
  if (score <= 30) return 'low'
  if (score <= 70) return 'medium'
  return 'high'
}

// Openness descriptions and adaptations
function getOpennessDescription(score: number): string {
  if (score <= 30) return "You prefer familiar experiences and practical approaches. You value tradition and find comfort in established ways of doing things."
  if (score <= 70) return "You balance creativity with practicality. You're open to new ideas while appreciating proven methods."
  return "You're highly creative and love exploring new ideas. You enjoy abstract thinking and novel experiences."
}

function getOpennessAdaptation(score: number): string {
  if (score <= 30) return "Bondhu will focus on practical, concrete advice and stick to familiar topics while gradually introducing new perspectives."
  if (score <= 70) return "Bondhu will balance creative suggestions with practical solutions, mixing familiar and novel approaches."
  return "Bondhu will engage with abstract concepts, encourage creative thinking, and explore philosophical topics with you."
}

function getOpennessGrowthSuggestions(score: number): string[] {
  if (score <= 30) return ["Try one new activity each week", "Read about different cultures", "Practice creative writing"]
  if (score <= 70) return ["Explore artistic hobbies", "Travel to new places", "Learn about different perspectives"]
  return ["Share your creative ideas", "Mentor others in creativity", "Apply imagination to solve problems"]
}

// Conscientiousness descriptions and adaptations
function getConscientiousnessDescription(score: number): string {
  if (score <= 30) return "You prefer flexibility and spontaneity. You work well in the moment and adapt quickly to changing situations."
  if (score <= 70) return "You balance structure with flexibility. You can be organized when needed while staying adaptable."
  return "You're highly organized and goal-oriented. You excel at planning ahead and following through on commitments."
}

function getConscientiousnessAdaptation(score: number): string {
  if (score <= 30) return "Bondhu will offer flexible suggestions and help you build gentle routines without being overwhelming."
  if (score <= 70) return "Bondhu will provide structured guidance when needed while respecting your need for spontaneity."
  return "Bondhu will help you create detailed plans and track your progress toward mental health goals."
}

function getConscientiousnessGrowthSuggestions(score: number): string[] {
  if (score <= 30) return ["Use simple planning tools", "Set one small goal daily", "Create basic routines"]
  if (score <= 70) return ["Balance planning with spontaneity", "Track important goals", "Develop time management skills"]
  return ["Share planning strategies", "Help others stay organized", "Set long-term wellness goals"]
}

// Extraversion descriptions and adaptations
function getExtraversionDescription(score: number): string {
  if (score <= 30) return "You gain energy from quiet reflection and prefer meaningful one-on-one conversations over large groups."
  if (score <= 70) return "You enjoy both social time and solitude. You're comfortable in groups but also value quiet reflection."
  return "You're energized by social interaction and enjoy being around people. You're outgoing and expressive."
}

function getExtraversionAdaptation(score: number): string {
  if (score <= 30) return "Bondhu will respect your need for quiet reflection and suggest gentle, low-key activities."
  if (score <= 70) return "Bondhu will balance social suggestions with quiet activities based on your current energy level."
  return "Bondhu will encourage social connections and group activities as part of your wellness journey."
}

function getExtraversionGrowthSuggestions(score: number): string[] {
  if (score <= 30) return ["Practice small social interactions", "Join online communities", "Attend low-key gatherings"]
  if (score <= 70) return ["Balance social and alone time", "Try different social settings", "Express yourself creatively"]
  return ["Use social energy positively", "Help others feel included", "Practice active listening"]
}

// Agreeableness descriptions and adaptations
function getAgreeablenessDescription(score: number): string {
  if (score <= 30) return "You value honesty and direct communication. You're comfortable with healthy conflict and standing up for your beliefs."
  if (score <= 70) return "You balance compassion with assertiveness. You care about others while maintaining healthy boundaries."
  return "You're naturally compassionate and trusting. You prioritize harmony and genuinely care about others' wellbeing."
}

function getAgreeablenessAdaptation(score: number): string {
  if (score <= 30) return "Bondhu will provide direct, honest feedback and help you develop empathy while respecting your straightforward style."
  if (score <= 70) return "Bondhu will help you balance caring for others with self-care and boundary setting."
  return "Bondhu will celebrate your compassion while helping you set healthy boundaries and practice self-compassion."
}

function getAgreeablenessGrowthSuggestions(score: number): string[] {
  if (score <= 30) return ["Practice active listening", "Consider others' perspectives", "Express appreciation more often"]
  if (score <= 70) return ["Set healthy boundaries", "Practice assertive communication", "Balance giving and receiving"]
  return ["Maintain healthy boundaries", "Practice saying no kindly", "Channel compassion into self-care"]
}

// Neuroticism descriptions and adaptations
function getNeuroticismDescription(score: number): string {
  if (score <= 30) return "You tend to stay calm under pressure and bounce back quickly from setbacks. You have a naturally stable emotional state."
  if (score <= 70) return "You experience normal emotional ups and downs. You can manage stress well but benefit from good coping strategies."
  return "You may experience emotions intensely and feel stress more acutely. You're sensitive and deeply empathetic."
}

function getNeuroticismAdaptation(score: number): string {
  if (score <= 30) return "Bondhu will help you maintain your emotional stability and use your calm nature to support others."
  if (score <= 70) return "Bondhu will provide balanced emotional support and help you develop effective stress management techniques."
  return "Bondhu will offer extra emotional support, gentle stress management techniques, and frequent check-ins during difficult times."
}

function getNeuroticismGrowthSuggestions(score: number): string[] {
  if (score <= 30) return ["Share coping strategies", "Support others in stress", "Maintain healthy habits"]
  if (score <= 70) return ["Develop stress management tools", "Practice mindfulness", "Build emotional awareness"]
  return ["Practice self-compassion", "Use calming techniques", "Build a strong support network"]
}


