"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { createClient } from "@/lib/supabase/client"
import { PersonalityStackingCards } from "@/components/ui/personality-stacking-cards"
import { PersonalityRadarChart } from "@/components/ui/personality-radar-chart"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { personalityTraits } from "@/data/personality-questions"
import { calculatePersonalityScores, generateTraitInsights } from "@/lib/personality-scoring"
import { generateLLMContext } from "@/lib/personality-llm-context"
import { PersonalityScores, AssessmentResults } from "@/types/personality"

type AssessmentPhase = 'assessment' | 'results' | 'completion'

export default function PersonalityQuestionnairePage() {
  const [currentPhase, setCurrentPhase] = useState<AssessmentPhase>('assessment')
  const [responses, setResponses] = useState<Record<number, number>>({})
  const [assessmentResults, setAssessmentResults] = useState<AssessmentResults | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const router = useRouter()
  const supabase = createClient()

  // Check if user is authenticated on mount
  useEffect(() => {
    checkAuthentication()
  }, [])

  const checkAuthentication = async () => {
    try {
      const { data: { session }, error: sessionError } = await supabase.auth.getSession()
      if (sessionError || !session) {
        router.push('/sign-in?redirectTo=/onboarding/personality')
        return
      }

      // Check if personality assessment already completed
      const { data: profile } = await supabase
        .from('profiles')
        .select('personality_completed_at, onboarding_completed')
        .eq('id', session.user.id)
        .single()

      if (profile?.personality_completed_at) {
        // Already completed, redirect to dashboard
        router.push('/dashboard')
      }
    } catch (error) {
      console.error('Authentication check failed:', error)
    }
  }

  const handleResponseChange = (questionId: number, response: number) => {
    setResponses(prev => ({
      ...prev,
      [questionId]: response
    }))
  }

  const handleAssessmentComplete = async () => {
    setIsLoading(true)
    setError(null)

    try {
      console.log('🎯 Starting personality assessment completion...')

      // First check session
      const { data: { session }, error: sessionError } = await supabase.auth.getSession()
      if (sessionError || !session) {
        throw new Error('Authentication session expired. Please sign in again.')
      }

      // Calculate personality scores
      console.log('📊 Calculating personality scores...')
      const scores = calculatePersonalityScores(responses)
      console.log('Calculated scores:', scores)

      // Generate insights
      const insights = generateTraitInsights(scores)
      
      // Generate LLM context
      const llmContext = generateLLMContext(scores)

      // Create assessment results
      const results: AssessmentResults = {
        scores,
        insights,
        llmContext,
        personalityType: generatePersonalityType(scores),
        strengthsOverview: generateStrengthsOverview(scores),
        bondhuPersonalization: generateBondhuPersonalization(scores)
      }

      setAssessmentResults(results)

      // Save to Supabase using the custom function
      console.log('💾 Saving personality data to Supabase...')
      const { data, error: saveError } = await supabase.rpc('update_personality_assessment', {
        user_id: session.user.id,
        p_openness: scores.openness,
        p_conscientiousness: scores.conscientiousness,
        p_extraversion: scores.extraversion,
        p_agreeableness: scores.agreeableness,
        p_neuroticism: scores.neuroticism,
        p_llm_context: llmContext,
        p_raw_responses: responses
      })

      if (saveError) {
        console.error('Supabase save error:', saveError)
        throw new Error(`Failed to save personality data: ${saveError.message}`)
      }

      console.log('✅ Personality assessment saved successfully!')
      
      // Move to results phase
      setCurrentPhase('results')

    } catch (error: any) {
      console.error('❌ Assessment completion error:', error)
      setError(error.message || 'Failed to complete assessment. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleContinueToDashboard = () => {
    setCurrentPhase('completion')
    
    // Add a small delay for the completion animation
    setTimeout(() => {
      router.push('/dashboard')
    }, 2000)
  }

  const generatePersonalityType = (scores: PersonalityScores): string => {
    const traits = [
      { name: 'Creative Explorer', condition: scores.openness > 70 },
      { name: 'Social Butterfly', condition: scores.extraversion > 70 },
      { name: 'Compassionate Helper', condition: scores.agreeableness > 70 },
      { name: 'Goal Achiever', condition: scores.conscientiousness > 70 },
      { name: 'Sensitive Soul', condition: scores.neuroticism > 70 }
    ]

    const dominantTraits = traits.filter(trait => trait.condition)
    if (dominantTraits.length > 0) {
      return dominantTraits[0].name
    }

    return "Balanced Individual"
  }

  const generateStrengthsOverview = (scores: PersonalityScores): string => {
    const strengths = []
    
    if (scores.openness > 60) strengths.push("creative thinking")
    if (scores.extraversion > 60) strengths.push("social connection")
    if (scores.agreeableness > 60) strengths.push("empathy and compassion")
    if (scores.conscientiousness > 60) strengths.push("organization and determination")
    if (scores.neuroticism < 40) strengths.push("emotional stability")

    if (strengths.length === 0) {
      return "You have a well-balanced personality with adaptable strengths in different situations."
    }

    return `Your key strengths include ${strengths.join(', ')}. These qualities make you uniquely capable of ${
      strengths.length > 2 ? 'handling diverse challenges and supporting others' : 
      'approaching life with your distinctive perspective'
    }.`
  }

  const generateBondhuPersonalization = (scores: PersonalityScores): string => {
    const adaptations = []
    
    if (scores.openness > 70) adaptations.push("explore creative approaches to your mental health journey")
    if (scores.extraversion > 70) adaptations.push("suggest social activities and group support options")
    if (scores.agreeableness > 70) adaptations.push("help you balance caring for others with self-care")
    if (scores.conscientiousness > 70) adaptations.push("create structured plans and track your wellness goals")
    if (scores.neuroticism > 70) adaptations.push("provide extra emotional support and gentle coping strategies")

    return `Based on your personality, Bondhu will ${adaptations.join(', ')}. This personalized approach ensures you get the most relevant and effective support for your unique needs.`
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 dark:from-green-950/20 dark:via-blue-950/20 dark:to-purple-950/20">
      <AnimatePresence mode="wait">
        {currentPhase === 'assessment' && (
          <motion.div
            key="assessment"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <PersonalityStackingCards
              traits={personalityTraits}
              onResponseChange={handleResponseChange}
              onComplete={handleAssessmentComplete}
              responses={responses}
            />
            
            {/* Loading overlay */}
            {isLoading && (
              <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center">
                <Card className="w-96 p-6">
                  <CardContent className="space-y-4">
                    <div className="text-center">
                      <div className="w-16 h-16 mx-auto mb-4 relative">
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                          className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full"
                        />
                      </div>
                      <h3 className="text-lg font-semibold mb-2">Analyzing Your Personality</h3>
                      <p className="text-sm text-muted-foreground">
                        Processing your responses and creating your personalized Bondhu experience...
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Error overlay */}
            {error && (
              <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center">
                <Card className="w-96 p-6 border-destructive">
                  <CardContent className="space-y-4">
                    <div className="text-center">
                      <div className="text-4xl mb-4">😔</div>
                      <h3 className="text-lg font-semibold mb-2 text-destructive">Assessment Error</h3>
                      <p className="text-sm text-muted-foreground mb-4">{error}</p>
                      <Button 
                        onClick={() => setError(null)}
                        className="w-full"
                      >
                        Try Again
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </motion.div>
        )}

        {currentPhase === 'results' && assessmentResults && (
          <motion.div
            key="results"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.1 }}
            transition={{ duration: 0.6 }}
            className="min-h-screen p-4 md:p-8"
          >
            <div className="max-w-6xl mx-auto space-y-8">
              {/* Celebration Header */}
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="text-center space-y-4"
              >
                <div className="text-6xl">🎉</div>
                <h1 className="text-4xl md:text-5xl font-bold text-foreground">
                  Quest Complete!
                </h1>
                <p className="text-xl text-muted-foreground">
                  You've successfully explored Neuron Valley and discovered your unique personality profile
                </p>
              </motion.div>

              {/* Personality Results */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                <PersonalityRadarChart scores={assessmentResults.scores} />
              </motion.div>

              {/* Personality Type & Insights */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="grid md:grid-cols-2 gap-6"
              >
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <span>🎭</span>
                      <span>Your Personality Type</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <h3 className="text-2xl font-bold text-primary">{assessmentResults.personalityType}</h3>
                      <p className="text-muted-foreground leading-relaxed">
                        {assessmentResults.strengthsOverview}
                      </p>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <span>🤖</span>
                      <span>Bondhu Personalization</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground leading-relaxed">
                      {assessmentResults.bondhuPersonalization}
                    </p>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Continue Button */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 }}
                className="text-center pt-8"
              >
                <Button
                  onClick={handleContinueToDashboard}
                  size="lg"
                  className="px-8 py-4 text-lg"
                >
                  Meet Your Personalized Bondhu 🚀
                </Button>
                <p className="text-sm text-muted-foreground mt-4">
                  Ready to start your mental health journey with AI that understands you
                </p>
              </motion.div>
            </div>
          </motion.div>
        )}

        {currentPhase === 'completion' && (
          <motion.div
            key="completion"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1, ease: "easeOut" }}
            className="min-h-screen flex items-center justify-center"
          >
            <div className="text-center space-y-6">
              <motion.div
                animate={{ 
                  scale: [1, 1.2, 1],
                  rotate: [0, 360, 0]
                }}
                transition={{ 
                  duration: 2,
                  ease: "easeInOut"
                }}
                className="text-8xl"
              >
                ✨
              </motion.div>
              <h1 className="text-3xl font-bold">
                Welcome to your personalized Bondhu experience!
              </h1>
              <p className="text-muted-foreground">
                Taking you to your dashboard...
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}