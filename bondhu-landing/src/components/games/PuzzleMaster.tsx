"use client"

import { useState, useEffect, useCallback, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Play, Pause, RotateCw, ArrowDown, ArrowLeft, ArrowRight } from 'lucide-react'

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

interface PuzzleMasterProps {
  onGameComplete: (data: GameplayData) => void
}

// Tetris-style piece shapes
const PIECES = [
  {
    shape: [[1, 1, 1, 1]], // I-piece
    color: '#00f5ff'
  },
  {
    shape: [
      [1, 1],
      [1, 1]
    ], // O-piece
    color: '#ffff00'
  },
  {
    shape: [
      [0, 1, 0],
      [1, 1, 1]
    ], // T-piece
    color: '#800080'
  },
  {
    shape: [
      [0, 1, 1],
      [1, 1, 0]
    ], // S-piece
    color: '#00ff00'
  },
  {
    shape: [
      [1, 1, 0],
      [0, 1, 1]
    ], // Z-piece
    color: '#ff0000'
  },
  {
    shape: [
      [1, 0, 0],
      [1, 1, 1]
    ], // L-piece
    color: '#ffa500'
  },
  {
    shape: [
      [0, 0, 1],
      [1, 1, 1]
    ], // J-piece
    color: '#0000ff'
  }
]

const BOARD_WIDTH = 10
const BOARD_HEIGHT = 20

export function PuzzleMaster({ onGameComplete }: PuzzleMasterProps) {
  const [board, setBoard] = useState<(string | null)[][]>(
    Array(BOARD_HEIGHT).fill(null).map(() => Array(BOARD_WIDTH).fill(null))
  )
  const [currentPiece, setCurrentPiece] = useState<any>(null)
  const [currentPosition, setCurrentPosition] = useState({ x: 0, y: 0 })
  const [score, setScore] = useState(0)
  const [level, setLevel] = useState(1)
  const [linesCleared, setLinesCleared] = useState(0)
  const [gameRunning, setGameRunning] = useState(false)
  const [gameOver, setGameOver] = useState(false)
  const [gameStarted, setGameStarted] = useState(false)
  const [dropTime, setDropTime] = useState(1000)
  
  // Analytics tracking
  const [gameChoices, setGameChoices] = useState<GameChoice[]>([])
  const [startTime, setStartTime] = useState<Date | null>(null)
  const [sessionId] = useState(() => Math.random().toString(36).substr(2, 9))
  const [moveCount, setMoveCount] = useState(0)
  const [rotationCount, setRotationCount] = useState(0)
  const [quickDropCount, setQuickDropCount] = useState(0)

  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  // Generate random piece
  const generatePiece = useCallback(() => {
    const piece = PIECES[Math.floor(Math.random() * PIECES.length)]
    return {
      ...piece,
      shape: piece.shape.map(row => [...row])
    }
  }, [])

  // Rotate piece
  const rotatePiece = useCallback((piece: any) => {
    const rotated = piece.shape[0].map((_: any, index: number) =>
      piece.shape.map((row: any) => row[index]).reverse()
    )
    return { ...piece, shape: rotated }
  }, [])

  // Check if position is valid
  const isValidPosition = useCallback((piece: any, position: { x: number; y: number }, testBoard?: any) => {
    const currentBoard = testBoard || board
    
    for (let y = 0; y < piece.shape.length; y++) {
      for (let x = 0; x < piece.shape[y].length; x++) {
        if (piece.shape[y][x]) {
          const newX = position.x + x
          const newY = position.y + y
          
          if (
            newX < 0 ||
            newX >= BOARD_WIDTH ||
            newY >= BOARD_HEIGHT ||
            (newY >= 0 && currentBoard[newY][newX])
          ) {
            return false
          }
        }
      }
    }
    return true
  }, [board])

  // Place piece on board
  const placePiece = useCallback(() => {
    if (!currentPiece) return

    const newBoard = board.map(row => [...row])
    
    currentPiece.shape.forEach((row: any, y: number) => {
      row.forEach((cell: any, x: number) => {
        if (cell) {
          const boardY = currentPosition.y + y
          const boardX = currentPosition.x + x
          if (boardY >= 0) {
            newBoard[boardY][boardX] = currentPiece.color
          }
        }
      })
    })

    setBoard(newBoard)
    
    // Check for completed lines
    const completedLines: number[] = []
    newBoard.forEach((row, index) => {
      if (row.every(cell => cell !== null)) {
        completedLines.push(index)
      }
    })

    if (completedLines.length > 0) {
      // Remove completed lines
      const filteredBoard = newBoard.filter((_, index) => !completedLines.includes(index))
      const newLines = Array(completedLines.length).fill(null).map(() => Array(BOARD_WIDTH).fill(null))
      const updatedBoard = [...newLines, ...filteredBoard]
      
      setBoard(updatedBoard)
      setLinesCleared(prev => prev + completedLines.length)
      setScore(prev => prev + completedLines.length * 100 * level)
      
      // Track line clearing as analytical data
      const choice: GameChoice = {
        timestamp: new Date(),
        action: 'line_cleared',
        context: `Cleared ${completedLines.length} lines at level ${level}`,
        reasoning: `Strategic piece placement resulted in line completion`
      }
      setGameChoices(prev => [...prev, choice])
    }

    // Generate new piece
    const newPiece = generatePiece()
    const newPosition = { x: Math.floor(BOARD_WIDTH / 2) - 1, y: 0 }
    
    if (!isValidPosition(newPiece, newPosition, newBoard)) {
      setGameOver(true)
      setGameRunning(false)
    } else {
      setCurrentPiece(newPiece)
      setCurrentPosition(newPosition)
    }
  }, [board, currentPiece, currentPosition, generatePiece, isValidPosition, level])

  // Move piece
  const movePiece = useCallback((direction: 'left' | 'right' | 'down') => {
    if (!currentPiece || !gameRunning) return

    const newPosition = { ...currentPosition }
    
    switch (direction) {
      case 'left':
        newPosition.x -= 1
        setMoveCount(prev => prev + 1)
        break
      case 'right':
        newPosition.x += 1
        setMoveCount(prev => prev + 1)
        break
      case 'down':
        newPosition.y += 1
        break
    }

    if (isValidPosition(currentPiece, newPosition)) {
      setCurrentPosition(newPosition)
      
      // Track movement choices
      const choice: GameChoice = {
        timestamp: new Date(),
        action: `move_${direction}`,
        context: `Moved piece ${direction} to position (${newPosition.x}, ${newPosition.y})`,
      }
      setGameChoices(prev => [...prev, choice])
    } else if (direction === 'down') {
      placePiece()
    }
  }, [currentPiece, currentPosition, gameRunning, isValidPosition, placePiece])

  // Rotate current piece
  const handleRotate = useCallback(() => {
    if (!currentPiece || !gameRunning) return

    const rotated = rotatePiece(currentPiece)
    if (isValidPosition(rotated, currentPosition)) {
      setCurrentPiece(rotated)
      setRotationCount(prev => prev + 1)
      
      const choice: GameChoice = {
        timestamp: new Date(),
        action: 'rotate',
        context: `Rotated piece at position (${currentPosition.x}, ${currentPosition.y})`,
        reasoning: 'Strategic rotation for better placement'
      }
      setGameChoices(prev => [...prev, choice])
    }
  }, [currentPiece, currentPosition, gameRunning, isValidPosition, rotatePiece])

  // Quick drop
  const handleQuickDrop = useCallback(() => {
    if (!currentPiece || !gameRunning) return

    let newPosition = { ...currentPosition }
    while (isValidPosition(currentPiece, { ...newPosition, y: newPosition.y + 1 })) {
      newPosition.y += 1
    }
    
    setCurrentPosition(newPosition)
    setQuickDropCount(prev => prev + 1)
    
    const choice: GameChoice = {
      timestamp: new Date(),
      action: 'quick_drop',
      context: `Quick dropped piece to position (${newPosition.x}, ${newPosition.y})`,
      reasoning: 'Aggressive placement for speed'
    }
    setGameChoices(prev => [...prev, choice])
    
    // Place piece immediately
    setTimeout(placePiece, 50)
  }, [currentPiece, currentPosition, gameRunning, isValidPosition, placePiece])

  // Start game
  const startGame = useCallback(() => {
    setGameStarted(true)
    setGameRunning(true)
    setGameOver(false)
    setScore(0)
    setLevel(1)
    setLinesCleared(0)
    setMoveCount(0)
    setRotationCount(0)
    setQuickDropCount(0)
    setGameChoices([])
    setStartTime(new Date())
    
    const newBoard = Array(BOARD_HEIGHT).fill(null).map(() => Array(BOARD_WIDTH).fill(null))
    setBoard(newBoard)
    
    const firstPiece = generatePiece()
    setCurrentPiece(firstPiece)
    setCurrentPosition({ x: Math.floor(BOARD_WIDTH / 2) - 1, y: 0 })
  }, [generatePiece])

  // Pause/Resume game
  const togglePause = useCallback(() => {
    setGameRunning(prev => !prev)
  }, [])

  // Game over handling
  const handleGameComplete = useCallback(() => {
    if (!startTime) return

    const endTime = new Date()
    const playDuration = (endTime.getTime() - startTime.getTime()) / 1000

    // Calculate performance metrics
    const avgMovesPerMinute = (moveCount / playDuration) * 60
    const rotationEfficiency = rotationCount / Math.max(moveCount, 1)
    const aggressiveness = quickDropCount / Math.max(linesCleared, 1)
    
    const gameplayData: GameplayData = {
      gameId: 'puzzle_master',
      userId: 'current_user', // This would come from auth context
      sessionId,
      startTime,
      endTime,
      completionRate: Math.min((score / 1000) * 100, 100),
      choices: gameChoices,
      performance: {
        speed: Math.min(avgMovesPerMinute / 60 * 100, 100),
        accuracy: Math.max(100 - (moveCount / Math.max(score / 10, 1)), 0),
        persistence: Math.min(playDuration / 300 * 100, 100), // 5 minute baseline
        creativity: Math.min(rotationEfficiency * 200, 100),
        social_interaction: 0 // Single player game
      },
      emotionalState: score > 500 ? 'excited' : score > 200 ? 'engaged' : playDuration > 180 ? 'frustrated' : 'calm'
    }

    onGameComplete(gameplayData)
  }, [startTime, sessionId, gameChoices, score, moveCount, rotationCount, quickDropCount, linesCleared, onGameComplete])

  // Game loop
  useEffect(() => {
    if (gameRunning && !gameOver) {
      intervalRef.current = setInterval(() => {
        movePiece('down')
      }, dropTime)
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [gameRunning, gameOver, dropTime, movePiece])

  // Handle game over
  useEffect(() => {
    if (gameOver && gameStarted) {
      handleGameComplete()
    }
  }, [gameOver, gameStarted, handleGameComplete])

  // Level progression
  useEffect(() => {
    const newLevel = Math.floor(linesCleared / 10) + 1
    if (newLevel !== level) {
      setLevel(newLevel)
      setDropTime(Math.max(100, 1000 - (newLevel - 1) * 100))
    }
  }, [linesCleared, level])

  // Keyboard controls
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (!gameRunning) return

      switch (e.key) {
        case 'ArrowLeft':
          e.preventDefault()
          movePiece('left')
          break
        case 'ArrowRight':
          e.preventDefault()
          movePiece('right')
          break
        case 'ArrowDown':
          e.preventDefault()
          movePiece('down')
          break
        case 'ArrowUp':
        case ' ':
          e.preventDefault()
          handleRotate()
          break
        case 'Enter':
          e.preventDefault()
          handleQuickDrop()
          break
      }
    }

    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [gameRunning, movePiece, handleRotate, handleQuickDrop])

  // Render board with current piece
  const renderBoard = () => {
    const displayBoard = board.map(row => [...row])
    
    // Add current piece to display board
    if (currentPiece) {
      currentPiece.shape.forEach((row: any, y: number) => {
        row.forEach((cell: any, x: number) => {
          if (cell) {
            const boardY = currentPosition.y + y
            const boardX = currentPosition.x + x
            if (boardY >= 0 && boardY < BOARD_HEIGHT && boardX >= 0 && boardX < BOARD_WIDTH) {
              displayBoard[boardY][boardX] = currentPiece.color
            }
          }
        })
      })
    }

    return displayBoard.map((row, y) => (
      <div key={y} className="flex">
        {row.map((cell, x) => (
          <div
            key={x}
            className={`w-6 h-6 border border-gray-300 ${
              cell ? 'border-gray-600' : 'bg-gray-50'
            }`}
            style={{ backgroundColor: cell || undefined }}
          />
        ))}
      </div>
    ))
  }

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Puzzle Master</span>
          <div className="flex gap-2">
            <Badge variant="secondary">Score: {score}</Badge>
            <Badge variant="secondary">Level: {level}</Badge>
            <Badge variant="secondary">Lines: {linesCleared}</Badge>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Game Board */}
          <div className="flex-1 flex flex-col items-center">
            <div className="border-2 border-gray-400 p-2 bg-white">
              {renderBoard()}
            </div>
            
            {/* Game Over Overlay */}
            {gameOver && (
              <div className="mt-4 text-center">
                <h3 className="text-lg font-bold text-red-600 mb-2">Game Over!</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Final Score: {score} | Lines Cleared: {linesCleared}
                </p>
                <Button onClick={startGame}>Play Again</Button>
              </div>
            )}
          </div>

          {/* Controls & Info */}
          <div className="w-full lg:w-64 space-y-4">
            {!gameStarted ? (
              <Button onClick={startGame} className="w-full">
                <Play className="h-4 w-4 mr-2" />
                Start Game
              </Button>
            ) : (
              <div className="space-y-2">
                <Button 
                  onClick={togglePause} 
                  variant="outline" 
                  className="w-full"
                  disabled={gameOver}
                >
                  {gameRunning ? <Pause className="h-4 w-4 mr-2" /> : <Play className="h-4 w-4 mr-2" />}
                  {gameRunning ? 'Pause' : 'Resume'}
                </Button>
                
                <Button onClick={startGame} variant="outline" className="w-full">
                  Restart
                </Button>
              </div>
            )}

            {/* Mobile Controls */}
            <div className="lg:hidden grid grid-cols-3 gap-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => movePiece('left')}
                disabled={!gameRunning}
              >
                <ArrowLeft className="h-4 w-4" />
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={handleRotate}
                disabled={!gameRunning}
              >
                <RotateCw className="h-4 w-4" />
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => movePiece('right')}
                disabled={!gameRunning}
              >
                <ArrowRight className="h-4 w-4" />
              </Button>
              <div></div>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => movePiece('down')}
                disabled={!gameRunning}
              >
                <ArrowDown className="h-4 w-4" />
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={handleQuickDrop}
                disabled={!gameRunning}
              >
                Drop
              </Button>
            </div>

            {/* Instructions */}
            <div className="space-y-2 text-xs text-muted-foreground">
              <p className="font-medium">Controls:</p>
              <p>← → : Move</p>
              <p>↓ : Soft drop</p>
              <p>↑ / Space : Rotate</p>
              <p>Enter : Quick drop</p>
            </div>

            {/* Analytics Preview */}
            <div className="space-y-2 text-xs">
              <p className="font-medium">Analytics:</p>
              <p>Moves: {moveCount}</p>
              <p>Rotations: {rotationCount}</p>
              <p>Quick Drops: {quickDropCount}</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
