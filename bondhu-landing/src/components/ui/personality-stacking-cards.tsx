"use client"

import { useRef, useState } from "react"
import { motion, useScroll, useTransform, MotionValue } from "framer-motion"
// Removed ReactLenis - using button-controlled navigation instead
import { PersonalityTrait } from "@/types/personality"
import { PersonalityQuestionCard } from "./personality-question-card"
import { Button } from "./button"
import { Card, CardContent, CardHeader } from "./card"
import { Progress } from "./progress"
import { Logo } from "../logo"
import { cn } from "@/lib/utils"

interface PersonalityStackingCardsProps {
  traits: PersonalityTrait[]
  onResponseChange: (questionId: number, response: number) => void
  onComplete: () => void
  responses: Record<number, number>
  className?: string
}

interface CardData {
  id: string
  type: 'intro' | 'trait'
  title: string
  description: string
  trait?: PersonalityTrait
  color: string
  icon: string
}

interface PersonalityCardProps {
  i: number
  cardData: CardData
  currentCard: number
  responses: Record<number, number>
  onResponseChange: (questionId: number, response: number) => void
  onContinue: (cardIndex: number) => void
  onPrevious: () => void
  canProceed: boolean
  isLast: boolean
  onComplete: () => void
}

const PersonalityCard = ({
  i,
  cardData,
  currentCard,
  responses,
  onResponseChange,
  onContinue,
  onPrevious,
  canProceed,
  isLast,
  onComplete
}: PersonalityCardProps) => {
  // Calculate position and scale based on current card state
  const isActive = i === currentCard
  const isCompleted = i < currentCard
  const isPending = i > currentCard
  
  // Determine card transform properties
  const getCardTransform = () => {
    if (isActive) {
      return {
        scale: 1,
        y: 0,
        zIndex: 30,
        opacity: 1
      }
    } else if (isCompleted) {
      return {
        scale: 0.9 - (currentCard - i) * 0.05,
        y: -50 - (currentCard - i) * 25,
        zIndex: 30 - (currentCard - i),
        opacity: 0.6
      }
    } else {
      return {
        scale: 0.95,
        y: 50,
        zIndex: 10,
        opacity: 0.3
      }
    }
  }
  
  const transform = getCardTransform()

  return (
    <motion.div
      className='absolute inset-0 flex items-center justify-center'
      animate={{
        scale: transform.scale,
        y: transform.y,
        opacity: transform.opacity,
        zIndex: transform.zIndex
      }}
      transition={{
        duration: 0.6,
        ease: "easeInOut"
      }}
    >
      <motion.div
        style={{
          backgroundColor: 'white',
          boxShadow: `0 0 0 3px ${cardData.color}, 0 25px 50px -12px rgba(0, 0, 0, 0.3)`
        }}
        className={`flex flex-col h-[80vh] w-[90%] max-w-6xl rounded-2xl shadow-2xl overflow-hidden bg-white dark:bg-gray-900 ${
          isActive && !canProceed ? 'ring-2 ring-orange-400 ring-opacity-50' : ''
        }`}
      >
        {/* Card Header */}
        <div className="p-8 border-b border-border/10">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div 
                className="w-12 h-12 rounded-2xl flex items-center justify-center text-2xl"
                style={{ backgroundColor: cardData.color + '30' }}
              >
                {cardData.icon}
              </div>
              <div>
                <h2 className='text-3xl font-bold text-foreground'>{cardData.title}</h2>
                <p className="text-muted-foreground">
                  {cardData.type === 'intro' ? 'Welcome to your journey' : `${cardData.trait?.displayName}`}
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-muted-foreground">Card {i + 1} of 6</div>
            </div>
          </div>
        </div>

        {/* Card Content */}
        <div className="flex-1 grid lg:grid-cols-2 min-h-0">
          {/* Left Panel - Content */}
          <div className="p-6 lg:p-8 flex flex-col space-y-6 overflow-y-auto max-h-[calc(80vh-120px)]">
            <div className="space-y-4">
              <p className="text-base text-muted-foreground leading-relaxed">
                {cardData.description}
              </p>
            </div>

            {/* Intro Card Instructions */}
            {cardData.type === 'intro' && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Your Journey Ahead:</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {[
                    "🎭 Experience 5 immersive scenarios",
                    "⚡ Answer honestly—there are no wrong choices",
                    "🌱 Help Bondhu learn your unique personality",
                    "⏱️ Takes about 5-7 minutes to complete"
                  ].map((instruction, idx) => (
                    <div key={idx} className="flex items-center space-x-2 p-3 bg-secondary/30 rounded-lg">
                      <span className="text-sm">{instruction}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Trait Questions */}
            {cardData.type === 'trait' && cardData.trait && (
              <div className="space-y-4 flex-1">
                {cardData.trait.questions.map((question, qIndex) => (
                  <PersonalityQuestionCard
                    key={question.id}
                    question={{...question, userResponse: responses[question.id]}}
                    questionIndex={qIndex}
                    totalQuestions={cardData.trait.questions.length}
                    onResponseChange={onResponseChange}
                  />
                ))}
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="pt-6 flex justify-between items-center">
              {/* Previous Button */}
              <Button
                onClick={onPrevious}
                disabled={i === 0}
                variant="outline"
                size="lg"
                className="group"
              >
                <svg
                  width='16'
                  height='12'
                  viewBox='0 0 22 12'
                  fill='none'
                  xmlns='http://www.w3.org/2000/svg'
                  className="mr-2 group-hover:-translate-x-1 transition-transform rotate-180"
                >
                  <path
                    d='M21.5303 6.53033C21.8232 6.23744 21.8232 5.76256 21.5303 5.46967L16.7574 0.696699C16.4645 0.403806 15.9896 0.403806 15.6967 0.696699C15.4038 0.989592 15.4038 1.46447 15.6967 1.75736L19.9393 6L15.6967 10.2426C15.4038 10.5355 15.4038 11.0104 15.6967 11.3033C15.9896 11.5962 16.4645 11.5962 16.7574 11.3033L21.5303 6.53033ZM0 6.75L21 6.75V5.25L0 5.25L0 6.75Z'
                    fill='currentColor'
                  />
                </svg>
                Previous
              </Button>

              {/* Continue/Complete Button */}
              <div className="flex flex-col items-end">
                <Button
                  onClick={isLast ? onComplete : () => onContinue(i)}
                  disabled={!canProceed}
                  size="lg"
                  className="group"
                  style={{
                    backgroundColor: canProceed ? cardData.color : undefined
                  }}
                >
                  {isLast ? (
                    "Complete Quest 🎉"
                  ) : (
                    <>
                      Continue Journey
                      <svg
                        width='16'
                        height='12'
                        viewBox='0 0 22 12'
                        fill='none'
                        xmlns='http://www.w3.org/2000/svg'
                        className="ml-2 group-hover:translate-x-1 transition-transform"
                      >
                        <path
                          d='M21.5303 6.53033C21.8232 6.23744 21.8232 5.76256 21.5303 5.46967L16.7574 0.696699C16.4645 0.403806 15.9896 0.403806 15.6967 0.696699C15.4038 0.989592 15.4038 1.46447 15.6967 1.75736L19.9393 6L15.6967 10.2426C15.4038 10.5355 15.4038 11.0104 15.6967 11.3033C15.9896 11.5962 16.4645 11.5962 16.7574 11.3033L21.5303 6.53033ZM0 6.75L21 6.75V5.25L0 5.25L0 6.75Z'
                          fill='currentColor'
                        />
                      </svg>
                    </>
                  )}
                </Button>
                
                {!canProceed && cardData.type === 'trait' && (
                  <p className="text-sm text-muted-foreground mt-2">
                    Please answer all questions to continue
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Right Panel - Visual */}
          <div 
            className="relative overflow-hidden hidden lg:block"
            style={{
              background: `linear-gradient(135deg, ${cardData.color}20 0%, ${cardData.color}10 100%)`
            }}
          >
            <motion.div
              className="absolute inset-0 flex items-center justify-center"
            >
              {/* Animated Background Element */}
              <motion.div
                animate={{
                  scale: [1, 1.1, 1],
                  rotate: [0, 5, -5, 0]
                }}
                transition={{
                  duration: 8,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
                className="w-80 h-80 rounded-full opacity-20"
                style={{ backgroundColor: cardData.color }}
              />
              
              {/* Large Icon */}
              <div className="absolute text-8xl opacity-30">
                {cardData.icon}
              </div>
            </motion.div>

            {/* Progress Indicator */}
            <div className="absolute bottom-8 right-8 text-right">
              <div className="text-4xl font-bold opacity-30" style={{ color: cardData.color }}>
                {i + 1}
              </div>
              <div className="text-sm opacity-60" style={{ color: cardData.color }}>
                of 6
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}

export function PersonalityStackingCards({
  traits,
  onResponseChange,
  onComplete,
  responses,
  className
}: PersonalityStackingCardsProps) {
  const container = useRef(null)
  const [currentCard, setCurrentCard] = useState(0)

  // Prepare card data
  const cards: CardData[] = [
    {
      id: 'intro',
      type: 'intro',
      title: 'Welcome to Neuron Valley',
      description: "Welcome, traveler! You're about to embark on a unique journey through Neuron Valley, where every path reveals something special about who you are. This isn't just any quest—it's a discovery of your inner self, helping your AI companion Bondhu understand how to support you best.",
      color: '#8b5cf6',
      icon: '🏔️'
    },
    ...traits.map(trait => ({
      id: trait.id,
      type: 'trait' as const,
      title: trait.storyTitle,
      description: trait.storyDescription,
      trait,
      color: trait.color,
      icon: trait.id === 'openness' ? '🌳' :
            trait.id === 'extraversion' ? '🎪' :
            trait.id === 'agreeableness' ? '🤝' :
            trait.id === 'conscientiousness' ? '⛰️' :
            trait.id === 'neuroticism' ? '⛈️' : '✨'
    }))
  ]

  // Calculate progress
  const totalQuestions = traits.reduce((sum, trait) => sum + trait.questions.length, 0)
  const answeredQuestions = Object.keys(responses).length
  const progress = (answeredQuestions / totalQuestions) * 100

  // Check if current trait is complete
  const getCurrentTraitCompletion = (trait: PersonalityTrait) => {
    return trait.questions.every(q => responses[q.id] !== undefined)
  }

  // Check if can proceed from card
  const canProceedFromCard = (cardIndex: number) => {
    if (cardIndex === 0) return true // Intro card
    const trait = cards[cardIndex].trait
    return trait ? getCurrentTraitCompletion(trait) : false
  }

  const handleContinue = (cardIndex: number) => {
    // Only allow progression if current card is completed
    if (canProceedFromCard(cardIndex)) {
      setCurrentCard(cardIndex + 1)
    }
  }

  const handlePrevious = () => {
    if (currentCard > 0) {
      setCurrentCard(currentCard - 1)
    }
  }

  const isAssessmentComplete = answeredQuestions === totalQuestions

  return (
    <div className={cn("relative", className)}>
      {/* Fixed Progress Header */}
        <header className="fixed top-0 left-0 right-0 z-50 bg-background/95 backdrop-blur border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Logo width={100} height={32} />
              <div className="hidden sm:block">
                <h1 className="text-lg font-semibold">Personality Discovery</h1>
                <p className="text-sm text-muted-foreground">Neuron Valley Quest</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
                <div className="text-right" aria-live="polite">
                  <p className="text-sm font-medium" aria-label={`${answeredQuestions} of ${totalQuestions} questions completed`}>
                    {answeredQuestions}/{totalQuestions}
                  </p>
                <p className="text-xs text-muted-foreground">Questions</p>
              </div>
                <Progress 
                  value={progress} 
                  className="w-24" 
                  aria-label={`Assessment progress: ${Math.round(progress)}% complete`}
                />
            </div>
          </div>
        </div>
        </header>

        {/* Main Content */}
        <main className="bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 dark:from-green-950/20 dark:via-blue-950/20 dark:to-purple-950/20 pt-20" ref={container}>
          {/* Stacking Cards Section */}
          <section className="h-screen relative overflow-hidden">
            {cards.map((card, i) => (
              <PersonalityCard
                key={card.id}
                i={i}
                cardData={card}
                currentCard={currentCard}
                responses={responses}
                onResponseChange={onResponseChange}
                onContinue={handleContinue}
                onPrevious={handlePrevious}
                canProceed={canProceedFromCard(i)}
                isLast={i === cards.length - 1}
                onComplete={onComplete}
              />
            ))}
          </section>
        </main>
    </div>
  )
}