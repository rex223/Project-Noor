"use client"

import { useState, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Brain, Eye, EyeOff, RotateCcw } from 'lucide-react'

interface GameplayData {
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

interface GameChoice {
  timestamp: Date
  action: string
  context: string
  reasoning?: string
}

interface MemoryPalaceProps {
  onGameComplete: (data: GameplayData) => void
}

interface Card {
  id: number
  emoji: string
  isFlipped: boolean
  isMatched: boolean
}

const CARD_EMOJIS = ['🎯', '🌟', '🔥', '⭐', '🎨', '🎵', '🌈', '💎', '🍀', '🌸', '🦋', '🌙', '☀️', '🌍', '💝', '🎪']

export function MemoryPalace({ onGameComplete }: MemoryPalaceProps) {
  const [cards, setCards] = useState<Card[]>([])
  const [flippedCards, setFlippedCards] = useState<number[]>([])
  const [matchedPairs, setMatchedPairs] = useState<number>(0)
  const [moves, setMoves] = useState<number>(0)
  const [gameStarted, setGameStarted] = useState(false)
  const [gameCompleted, setGameCompleted] = useState(false)
  const [difficulty, setDifficulty] = useState<'easy' | 'medium' | 'hard'>('easy')
  const [showPreview, setShowPreview] = useState(false)
  const [previewTime, setPreviewTime] = useState(3)

  // Analytics
  const [gameChoices, setGameChoices] = useState<GameChoice[]>([])
  const [startTime, setStartTime] = useState<Date | null>(null)
  const [sessionId] = useState(() => Math.random().toString(36).substr(2, 9))
  const [wrongMatches, setWrongMatches] = useState(0)
  const [avgResponseTime, setAvgResponseTime] = useState(0)
  const [lastCardTime, setLastCardTime] = useState<number>(0)

  const getDifficultySettings = useCallback((diff: 'easy' | 'medium' | 'hard') => {
    switch (diff) {
      case 'easy':
        return { pairs: 6, previewTime: 3 }
      case 'medium':
        return { pairs: 8, previewTime: 2 }
      case 'hard':
        return { pairs: 12, previewTime: 1 }
    }
  }, [])

  const initializeGame = useCallback(() => {
    const settings = getDifficultySettings(difficulty)
    const selectedEmojis = CARD_EMOJIS.slice(0, settings.pairs)
    const cardPairs = [...selectedEmojis, ...selectedEmojis]
    
    // Shuffle cards
    const shuffledCards = cardPairs
      .map((emoji, index) => ({
        id: index,
        emoji,
        isFlipped: false,
        isMatched: false
      }))
      .sort(() => Math.random() - 0.5)
      .map((card, index) => ({ ...card, id: index }))

    setCards(shuffledCards)
    setFlippedCards([])
    setMatchedPairs(0)
    setMoves(0)
    setGameCompleted(false)
    setWrongMatches(0)
    setGameChoices([])
    setAvgResponseTime(0)
    setPreviewTime(settings.previewTime)
  }, [difficulty, getDifficultySettings])

  const startGame = useCallback(() => {
    setGameStarted(true)
    setStartTime(new Date())
    setShowPreview(true)
    initializeGame()

    // Track game start
    const choice: GameChoice = {
      timestamp: new Date(),
      action: 'game_start',
      context: `Started Memory Palace on ${difficulty} difficulty`,
      reasoning: `Selected ${difficulty} difficulty level`
    }
    setGameChoices([choice])

    // Show preview then start
    setTimeout(() => {
      setShowPreview(false)
      setLastCardTime(Date.now())
    }, previewTime * 1000)
  }, [difficulty, initializeGame, previewTime])

  const handleCardClick = useCallback((cardId: number) => {
    if (!gameStarted || showPreview || gameCompleted) return
    if (flippedCards.length >= 2) return
    if (flippedCards.includes(cardId)) return
    if (cards[cardId].isMatched) return

    const now = Date.now()
    const responseTime = now - lastCardTime
    setLastCardTime(now)

    // Update average response time
    setAvgResponseTime(prev => {
      const newAvg = prev === 0 ? responseTime : (prev + responseTime) / 2
      return newAvg
    })

    const newFlippedCards = [...flippedCards, cardId]
    setFlippedCards(newFlippedCards)

    // Update cards to show flipped state
    setCards(prev => prev.map(card => 
      card.id === cardId ? { ...card, isFlipped: true } : card
    ))

    // Track card selection
    const choice: GameChoice = {
      timestamp: new Date(),
      action: 'card_flip',
      context: `Flipped card ${cardId} (${cards[cardId].emoji}) - Response time: ${responseTime}ms`,
      reasoning: moves < 10 ? 'Exploring board layout' : 'Strategic memory recall'
    }
    setGameChoices(prev => [...prev, choice])

    // Check for match when two cards are flipped
    if (newFlippedCards.length === 2) {
      setMoves(prev => prev + 1)
      
      const [firstCardId, secondCardId] = newFlippedCards
      const firstCard = cards[firstCardId]
      const secondCard = cards[secondCardId]

      if (firstCard.emoji === secondCard.emoji) {
        // Match found
        setTimeout(() => {
          setCards(prev => prev.map(card => 
            (card.id === firstCardId || card.id === secondCardId) 
              ? { ...card, isMatched: true, isFlipped: false } 
              : card
          ))
          setMatchedPairs(prev => prev + 1)
          setFlippedCards([])

          const matchChoice: GameChoice = {
            timestamp: new Date(),
            action: 'match_found',
            context: `Matched ${firstCard.emoji} cards (${firstCardId}, ${secondCardId})`,
            reasoning: 'Successful memory recall and pattern matching'
          }
          setGameChoices(prev => [...prev, matchChoice])
        }, 1000)
      } else {
        // No match
        setWrongMatches(prev => prev + 1)
        setTimeout(() => {
          setCards(prev => prev.map(card => 
            (card.id === firstCardId || card.id === secondCardId) 
              ? { ...card, isFlipped: false } 
              : card
          ))
          setFlippedCards([])

          const noMatchChoice: GameChoice = {
            timestamp: new Date(),
            action: 'no_match',
            context: `No match: ${firstCard.emoji} vs ${secondCard.emoji}`,
            reasoning: 'Memory error or still learning pattern'
          }
          setGameChoices(prev => [...prev, noMatchChoice])
        }, 1500)
      }
    }
  }, [gameStarted, showPreview, gameCompleted, flippedCards, cards, moves, lastCardTime])

  const resetGame = useCallback(() => {
    setGameStarted(false)
    setGameCompleted(false)
    setCards([])
    setFlippedCards([])
    setMatchedPairs(0)
    setMoves(0)
    setStartTime(null)
    setWrongMatches(0)
    setGameChoices([])
    setAvgResponseTime(0)
  }, [])

  // Check for game completion
  useEffect(() => {
    const totalPairs = getDifficultySettings(difficulty).pairs
    if (matchedPairs === totalPairs && gameStarted && !gameCompleted) {
      setGameCompleted(true)

      if (startTime) {
        const endTime = new Date()
        const playDuration = (endTime.getTime() - startTime.getTime()) / 1000

        // Calculate performance metrics
        const accuracy = ((totalPairs / Math.max(moves, 1)) * 100)
        const speedScore = Math.max(0, 100 - (avgResponseTime / 1000) * 10)
        const memoryEfficiency = Math.max(0, 100 - (wrongMatches / totalPairs) * 25)

        const gameplayData: GameplayData = {
          gameId: 'memory_palace',
          userId: 'current_user',
          sessionId,
          startTime,
          endTime,
          completionRate: 100,
          choices: gameChoices,
          performance: {
            speed: Math.min(speedScore, 100),
            accuracy: Math.min(accuracy, 100),
            persistence: Math.min((playDuration / 180) * 100, 100), // 3 minute baseline
            creativity: Math.min(memoryEfficiency, 100),
            social_interaction: 0
          },
          emotionalState: moves <= totalPairs + 2 ? 'excited' : moves <= totalPairs + 5 ? 'engaged' : 'frustrated'
        }

        onGameComplete(gameplayData)
      }
    }
  }, [matchedPairs, gameStarted, gameCompleted, difficulty, getDifficultySettings, startTime, moves, avgResponseTime, wrongMatches, sessionId, gameChoices, onGameComplete])

  const renderCard = (card: Card) => {
    const shouldShow = card.isFlipped || card.isMatched || showPreview
    
    return (
      <div
        key={card.id}
        className={`
          aspect-square rounded-lg border-2 flex items-center justify-center text-3xl cursor-pointer
          transition-all duration-300 transform hover:scale-105
          ${shouldShow 
            ? card.isMatched 
              ? 'bg-green-100 border-green-400 text-green-800' 
              : 'bg-blue-100 border-blue-400' 
            : 'bg-gray-100 border-gray-300 hover:bg-gray-200'
          }
          ${flippedCards.includes(card.id) ? 'ring-2 ring-blue-500' : ''}
        `}
        onClick={() => handleCardClick(card.id)}
      >
        {shouldShow ? card.emoji : '?'}
      </div>
    )
  }

  const totalPairs = getDifficultySettings(difficulty).pairs
  const progress = (matchedPairs / totalPairs) * 100

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Brain className="h-5 w-5" />
            <span>Memory Palace</span>
          </div>
          <div className="flex gap-2">
            <Badge variant="secondary">Moves: {moves}</Badge>
            <Badge variant="secondary">Pairs: {matchedPairs}/{totalPairs}</Badge>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Difficulty Selection */}
          {!gameStarted && (
            <div className="space-y-4">
              <div>
                <h3 className="font-medium mb-2">Choose Difficulty:</h3>
                <div className="flex gap-2">
                  {(['easy', 'medium', 'hard'] as const).map((diff) => {
                    const settings = getDifficultySettings(diff)
                    return (
                      <Button
                        key={diff}
                        variant={difficulty === diff ? 'default' : 'outline'}
                        onClick={() => setDifficulty(diff)}
                        className="flex-1"
                      >
                        <div className="text-center">
                          <div className="font-medium capitalize">{diff}</div>
                          <div className="text-xs opacity-70">{settings.pairs} pairs</div>
                        </div>
                      </Button>
                    )
                  })}
                </div>
              </div>
              <Button onClick={startGame} className="w-full">
                <Brain className="h-4 w-4 mr-2" />
                Start Memory Challenge
              </Button>
            </div>
          )}

          {/* Preview Phase */}
          {showPreview && (
            <div className="text-center space-y-4">
              <div className="flex items-center justify-center space-x-2">
                <Eye className="h-5 w-5" />
                <span className="font-medium">Memorize the cards!</span>
              </div>
              <Progress value={(previewTime - (previewTime)) / previewTime * 100} className="w-full" />
              <p className="text-sm text-muted-foreground">
                Study the layout for {previewTime} seconds...
              </p>
            </div>
          )}

          {/* Game Board */}
          {gameStarted && (
            <div className={`grid gap-3 ${
              totalPairs <= 6 ? 'grid-cols-4' : 
              totalPairs <= 8 ? 'grid-cols-4' : 
              'grid-cols-6'
            }`}>
              {cards.map(renderCard)}
            </div>
          )}

          {/* Game Progress */}
          {gameStarted && !showPreview && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Progress</span>
                <span>{matchedPairs}/{totalPairs} pairs</span>
              </div>
              <Progress value={progress} className="w-full" />
            </div>
          )}

          {/* Game Completed */}
          {gameCompleted && (
            <div className="text-center space-y-4 p-4 bg-green-50 rounded-lg border border-green-200">
              <h3 className="text-lg font-bold text-green-800">🎉 Memory Palace Completed!</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="font-medium">Total Moves</div>
                  <div className="text-green-700">{moves}</div>
                </div>
                <div>
                  <div className="font-medium">Accuracy</div>
                  <div className="text-green-700">
                    {Math.round((totalPairs / Math.max(moves, 1)) * 100)}%
                  </div>
                </div>
                <div>
                  <div className="font-medium">Wrong Matches</div>
                  <div className="text-green-700">{wrongMatches}</div>
                </div>
                <div>
                  <div className="font-medium">Avg Response</div>
                  <div className="text-green-700">{Math.round(avgResponseTime)}ms</div>
                </div>
              </div>
              <div className="flex gap-2">
                <Button onClick={resetGame} variant="outline" className="flex-1">
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Play Again
                </Button>
                <Button onClick={() => setDifficulty(difficulty === 'easy' ? 'medium' : difficulty === 'medium' ? 'hard' : 'easy')} className="flex-1">
                  Try {difficulty === 'easy' ? 'Medium' : difficulty === 'medium' ? 'Hard' : 'Easy'}
                </Button>
              </div>
            </div>
          )}

          {/* Game Controls */}
          {gameStarted && !gameCompleted && !showPreview && (
            <div className="flex justify-center">
              <Button onClick={resetGame} variant="outline">
                <RotateCcw className="h-4 w-4 mr-2" />
                Reset Game
              </Button>
            </div>
          )}

          {/* Analytics Preview */}
          {gameStarted && (
            <div className="text-xs text-muted-foreground space-y-1">
              <p className="font-medium">Learning Insights:</p>
              <p>• Memory pattern recognition</p>
              <p>• Strategic thinking development</p>
              <p>• Attention to detail assessment</p>
              {avgResponseTime > 0 && <p>• Response time: {Math.round(avgResponseTime)}ms avg</p>}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
