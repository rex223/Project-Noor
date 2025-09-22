"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { createClient } from "@/lib/supabase/client"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"

const questions = [
  {
    id: 'openness',
    question: 'I enjoy exploring new ideas and experiences',
    trait: 'Openness to Experience'
  },
  {
    id: 'conscientiousness', 
    question: 'I am organized and like to plan ahead',
    trait: 'Conscientiousness'
  },
  {
    id: 'extraversion',
    question: 'I feel energized when around other people',
    trait: 'Extraversion'
  },
  {
    id: 'agreeableness',
    question: 'I tend to trust others and assume they have good intentions',
    trait: 'Agreeableness'
  },
  {
    id: 'neuroticism',
    question: 'I often worry about things that might go wrong',
    trait: 'Emotional Stability'
  }
]

const mentalHealthGoals = [
  'Reduce anxiety and stress',
  'Improve mood and emotional regulation',
  'Better sleep quality',
  'Increase self-confidence',
  'Develop coping strategies',
  'Build better relationships'
]

export default function PersonalityQuestionnairePage() {
  const [currentStep, setCurrentStep] = useState(0)
  const [answers, setAnswers] = useState<Record<string, number>>({})
  const [selectedGoals, setSelectedGoals] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)
  
  const router = useRouter()
  const supabase = createClient()

  const totalSteps = questions.length + 1 // +1 for goals step
  const progress = ((currentStep + 1) / totalSteps) * 100

  const handleAnswerSelect = (questionId: string, value: number) => {
    setAnswers(prev => ({ ...prev, [questionId]: value }))
  }

  const handleNext = () => {
    if (currentStep < totalSteps - 1) {
      setCurrentStep(prev => prev + 1)
    }
  }

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1)
    }
  }

  const handleGoalToggle = (goal: string) => {
    setSelectedGoals(prev => 
      prev.includes(goal) 
        ? prev.filter(g => g !== goal)
        : [...prev, goal]
    )
  }

  const handleComplete = async () => {
    setIsLoading(true)
    
    try {
      const personalityData = {
        ...answers,
        mental_health_goals: selectedGoals,
        completed_at: new Date().toISOString()
      }

      const { data: { user } } = await supabase.auth.getUser()
      
      if (!user) {
        throw new Error('No authenticated user')
      }

      const { error } = await supabase
        .from('profiles')
        .update({
          personality_data: personalityData,
          onboarding_completed: true,
          updated_at: new Date().toISOString()
        })
        .eq('id', user.id)

      if (error) throw error

      router.push('/dashboard')
      router.refresh()
    } catch (error) {
      console.error('Error saving personality data:', error)
      // Handle error - could show toast or error message
    } finally {
      setIsLoading(false)
    }
  }

  const canProceed = () => {
    if (currentStep < questions.length) {
      return answers[questions[currentStep].id] !== undefined
    }
    return selectedGoals.length > 0
  }

  const scaleLabels = [
    'Strongly Disagree',
    'Disagree', 
    'Neutral',
    'Agree',
    'Strongly Agree'
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 dark:from-green-950/20 dark:via-blue-950/20 dark:to-purple-950/20 p-4">
      <div className="max-w-2xl mx-auto pt-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">Personality Discovery</h1>
          <p className="text-muted-foreground">
            Help Bondhu understand you better with this quick assessment
          </p>
          <div className="mt-4">
            <Progress value={progress} className="w-full" />
            <p className="text-sm text-muted-foreground mt-2">
              Step {currentStep + 1} of {totalSteps}
            </p>
          </div>
        </div>

        {/* Question Cards */}
        {currentStep < questions.length ? (
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Card className="p-6">
              <CardHeader>
                <CardTitle className="text-xl">
                  {questions[currentStep].question}
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  {questions[currentStep].trait}
                </p>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 gap-3">
                  {scaleLabels.map((label, index) => (
                    <button
                      key={index}
                      onClick={() => handleAnswerSelect(questions[currentStep].id, index + 1)}
                      className={`p-4 text-left rounded-lg border transition-colors ${
                        answers[questions[currentStep].id] === index + 1
                          ? 'border-primary bg-primary/10'
                          : 'border-border hover:border-primary/50'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span>{label}</span>
                        <span className="text-sm text-muted-foreground">{index + 1}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ) : (
          // Goals Selection
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card className="p-6">
              <CardHeader>
                <CardTitle className="text-xl">
                  What are your mental health goals?
                </CardTitle>
                <p className="text-muted-foreground">
                  Select all that apply. This helps Bondhu personalize your experience.
                </p>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {mentalHealthGoals.map((goal, index) => (
                    <button
                      key={index}
                      onClick={() => handleGoalToggle(goal)}
                      className={`p-4 text-left rounded-lg border transition-colors ${
                        selectedGoals.includes(goal)
                          ? 'border-primary bg-primary/10'
                          : 'border-border hover:border-primary/50'
                      }`}
                    >
                      {goal}
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Navigation */}
        <div className="flex justify-between mt-8">
          <Button
            variant="outline"
            onClick={handleBack}
            disabled={currentStep === 0}
          >
            Back
          </Button>
          
          {currentStep < questions.length ? (
            <Button
              onClick={handleNext}
              disabled={!canProceed()}
            >
              Next
            </Button>
          ) : (
            <Button
              onClick={handleComplete}
              disabled={!canProceed() || isLoading}
            >
              {isLoading ? 'Completing...' : 'Complete & Continue'}
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
