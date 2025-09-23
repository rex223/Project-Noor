"use client"

import { useState, useEffect, useCallback, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Slider } from '@/components/ui/slider'
import { Palette, Save, RotateCcw, Sparkles, Download } from 'lucide-react'

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

interface ColorSymphonyProps {
  onGameComplete: (data: GameplayData) => void
}

interface ColorStop {
  color: string
  position: number
}

interface Artwork {
  id: string
  name: string
  gradient: ColorStop[]
  pattern: 'linear' | 'radial' | 'conic'
  angle: number
  timestamp: Date
}

const COLOR_PALETTES = [
  { name: 'Sunset', colors: ['#FF6B6B', '#FFE66D', '#FF8E53', '#FF6B9D'] },
  { name: 'Ocean', colors: ['#4ECDC4', '#44A08D', '#096C82', '#1A535C'] },
  { name: 'Forest', colors: ['#95E1D3', '#F38BA8', '#56AB91', '#2F5233'] },
  { name: 'Cosmic', colors: ['#8B5CF6', '#A855F7', '#C084FC', '#DDD6FE'] },
  { name: 'Autumn', colors: ['#F59E0B', '#EF4444', '#DC2626', '#7C2D12'] },
  { name: 'Monochrome', colors: ['#000000', '#374151', '#6B7280', '#F9FAFB'] }
]

export function ColorSymphony({ onGameComplete }: ColorSymphonyProps) {
  const [currentArtwork, setCurrentArtwork] = useState<Artwork>({
    id: 'current',
    name: 'Untitled Creation',
    gradient: [
      { color: '#4F46E5', position: 0 },
      { color: '#06B6D4', position: 100 }
    ],
    pattern: 'linear',
    angle: 45,
    timestamp: new Date()
  })
  
  const [savedArtworks, setSavedArtworks] = useState<Artwork[]>([])
  const [selectedPalette, setSelectedPalette] = useState<string | null>(null)
  const [gameStarted, setGameStarted] = useState(false)
  const [colorHistory, setColorHistory] = useState<string[]>([])
  const [currentTool, setCurrentTool] = useState<'gradient' | 'pattern' | 'palette'>('gradient')
  
  // Analytics
  const [gameChoices, setGameChoices] = useState<GameChoice[]>([])
  const [startTime, setStartTime] = useState<Date | null>(null)
  const [sessionId] = useState(() => Math.random().toString(36).substr(2, 9))
  const [colorChanges, setColorChanges] = useState(0)
  const [patternChanges, setPatternChanges] = useState(0)
  const [creativeSessions, setCreativeSessions] = useState(0)
  const [uniqueColors, setUniqueColors] = useState(new Set<string>())

  const canvasRef = useRef<HTMLCanvasElement>(null)

  const startGame = useCallback(() => {
    setGameStarted(true)
    setStartTime(new Date())
    setGameChoices([])
    setColorChanges(0)
    setPatternChanges(0)
    setCreativeSessions(prev => prev + 1)
    setUniqueColors(new Set())

    const choice: GameChoice = {
      timestamp: new Date(),
      action: 'game_start',
      context: 'Started Color Symphony creative session',
      reasoning: 'Beginning artistic exploration and creative expression'
    }
    setGameChoices([choice])
  }, [])

  const updateGradientStyle = useCallback(() => {
    const { gradient, pattern, angle } = currentArtwork
    const colorStops = gradient
      .sort((a, b) => a.position - b.position)
      .map(stop => `${stop.color} ${stop.position}%`)
      .join(', ')

    switch (pattern) {
      case 'linear':
        return `linear-gradient(${angle}deg, ${colorStops})`
      case 'radial':
        return `radial-gradient(circle, ${colorStops})`
      case 'conic':
        return `conic-gradient(from ${angle}deg, ${colorStops})`
      default:
        return `linear-gradient(${angle}deg, ${colorStops})`
    }
  }, [currentArtwork])

  const addColorStop = useCallback(() => {
    const newPosition = Math.random() * 100
    const newColor = `hsl(${Math.random() * 360}, 70%, 60%)`
    
    setCurrentArtwork(prev => ({
      ...prev,
      gradient: [...prev.gradient, { color: newColor, position: newPosition }]
    }))

    setColorChanges(prev => prev + 1)
    setUniqueColors(prev => new Set([...prev, newColor]))

    const choice: GameChoice = {
      timestamp: new Date(),
      action: 'add_color_stop',
      context: `Added color stop: ${newColor} at ${newPosition.toFixed(1)}%`,
      reasoning: 'Expanding color complexity and artistic depth'
    }
    setGameChoices(prev => [...prev, choice])
  }, [])

  const updateColorStop = useCallback((index: number, color: string) => {
    setCurrentArtwork(prev => ({
      ...prev,
      gradient: prev.gradient.map((stop, i) => 
        i === index ? { ...stop, color } : stop
      )
    }))

    setColorChanges(prev => prev + 1)
    setUniqueColors(prev => new Set([...prev, color]))
    setColorHistory(prev => [...prev.slice(-10), color])

    const choice: GameChoice = {
      timestamp: new Date(),
      action: 'update_color',
      context: `Changed color at position ${index} to ${color}`,
      reasoning: 'Fine-tuning color harmony and aesthetic balance'
    }
    setGameChoices(prev => [...prev, choice])
  }, [])

  const updateColorPosition = useCallback((index: number, position: number) => {
    setCurrentArtwork(prev => ({
      ...prev,
      gradient: prev.gradient.map((stop, i) => 
        i === index ? { ...stop, position } : stop
      )
    }))

    const choice: GameChoice = {
      timestamp: new Date(),
      action: 'adjust_position',
      context: `Moved color stop ${index} to ${position}%`,
      reasoning: 'Adjusting gradient flow and visual composition'
    }
    setGameChoices(prev => [...prev, choice])
  }, [])

  const changePattern = useCallback((pattern: 'linear' | 'radial' | 'conic') => {
    setCurrentArtwork(prev => ({ ...prev, pattern }))
    setPatternChanges(prev => prev + 1)

    const choice: GameChoice = {
      timestamp: new Date(),
      action: 'change_pattern',
      context: `Changed gradient pattern to ${pattern}`,
      reasoning: 'Exploring different visual structures and compositions'
    }
    setGameChoices(prev => [...prev, choice])
  }, [])

  const changeAngle = useCallback((angle: number) => {
    setCurrentArtwork(prev => ({ ...prev, angle }))

    const choice: GameChoice = {
      timestamp: new Date(),
      action: 'adjust_angle',
      context: `Adjusted gradient angle to ${angle}°`,
      reasoning: 'Fine-tuning directional flow and visual dynamics'
    }
    setGameChoices(prev => [...prev, choice])
  }, [])

  const applyPalette = useCallback((palette: typeof COLOR_PALETTES[0]) => {
    const newGradient = palette.colors.map((color, index) => ({
      color,
      position: (index / (palette.colors.length - 1)) * 100
    }))

    setCurrentArtwork(prev => ({
      ...prev,
      gradient: newGradient
    }))

    setSelectedPalette(palette.name)
    setColorChanges(prev => prev + palette.colors.length)
    palette.colors.forEach(color => setUniqueColors(prev => new Set([...prev, color])))

    const choice: GameChoice = {
      timestamp: new Date(),
      action: 'apply_palette',
      context: `Applied ${palette.name} color palette`,
      reasoning: 'Using curated color harmony for cohesive aesthetic'
    }
    setGameChoices(prev => [...prev, choice])
  }, [])

  const saveArtwork = useCallback(() => {
    const artwork: Artwork = {
      ...currentArtwork,
      id: Date.now().toString(),
      timestamp: new Date()
    }

    setSavedArtworks(prev => [...prev, artwork])

    const choice: GameChoice = {
      timestamp: new Date(),
      action: 'save_artwork',
      context: `Saved artwork: ${artwork.name}`,
      reasoning: 'Preserving creative achievement and artistic expression'
    }
    setGameChoices(prev => [...prev, choice])
  }, [currentArtwork])

  const generateRandomArt = useCallback(() => {
    const patterns: ('linear' | 'radial' | 'conic')[] = ['linear', 'radial', 'conic']
    const randomPattern = patterns[Math.floor(Math.random() * patterns.length)]
    const randomAngle = Math.floor(Math.random() * 360)
    
    const colorCount = 2 + Math.floor(Math.random() * 4)
    const randomGradient = Array.from({ length: colorCount }, (_, i) => ({
      color: `hsl(${Math.random() * 360}, ${50 + Math.random() * 50}%, ${30 + Math.random() * 40}%)`,
      position: (i / (colorCount - 1)) * 100
    }))

    setCurrentArtwork(prev => ({
      ...prev,
      gradient: randomGradient,
      pattern: randomPattern,
      angle: randomAngle
    }))

    setColorChanges(prev => prev + colorCount)
    setPatternChanges(prev => prev + 1)
    randomGradient.forEach(stop => setUniqueColors(prev => new Set([...prev, stop.color])))

    const choice: GameChoice = {
      timestamp: new Date(),
      action: 'generate_random',
      context: `Generated random ${randomPattern} artwork with ${colorCount} colors`,
      reasoning: 'Embracing creative spontaneity and experimental exploration'
    }
    setGameChoices(prev => [...prev, choice])
  }, [])

  const resetArtwork = useCallback(() => {
    setCurrentArtwork({
      id: 'current',
      name: 'Untitled Creation',
      gradient: [
        { color: '#4F46E5', position: 0 },
        { color: '#06B6D4', position: 100 }
      ],
      pattern: 'linear',
      angle: 45,
      timestamp: new Date()
    })
    setSelectedPalette(null)

    const choice: GameChoice = {
      timestamp: new Date(),
      action: 'reset_artwork',
      context: 'Reset artwork to default state',
      reasoning: 'Starting fresh creative exploration'
    }
    setGameChoices(prev => [...prev, choice])
  }, [])

  const completeSession = useCallback(() => {
    if (!startTime) return

    const endTime = new Date()
    const sessionDuration = (endTime.getTime() - startTime.getTime()) / 1000

    // Calculate creativity metrics
    const colorDiversity = uniqueColors.size
    const experimentationRate = (colorChanges + patternChanges) / Math.max(sessionDuration / 60, 1)
    const persistenceScore = Math.min(sessionDuration / 300 * 100, 100) // 5 minute baseline
    const creativityScore = Math.min((colorDiversity * 10) + (experimentationRate * 5), 100)

    const gameplayData: GameplayData = {
      gameId: 'color_symphony',
      userId: 'current_user',
      sessionId,
      startTime,
      endTime,
      completionRate: savedArtworks.length > 0 ? 100 : Math.min((colorChanges + patternChanges) * 10, 100),
      choices: gameChoices,
      performance: {
        speed: Math.min(experimentationRate * 20, 100),
        accuracy: 100, // No wrong answers in art
        persistence: persistenceScore,
        creativity: creativityScore,
        social_interaction: 0
      },
      emotionalState: colorDiversity > 8 ? 'excited' : experimentationRate > 2 ? 'engaged' : 'calm'
    }

    onGameComplete(gameplayData)
  }, [startTime, sessionId, gameChoices, savedArtworks.length, colorChanges, patternChanges, uniqueColors.size, onGameComplete])

  const removeColorStop = useCallback((index: number) => {
    if (currentArtwork.gradient.length <= 2) return

    setCurrentArtwork(prev => ({
      ...prev,
      gradient: prev.gradient.filter((_, i) => i !== index)
    }))

    const choice: GameChoice = {
      timestamp: new Date(),
      action: 'remove_color_stop',
      context: `Removed color stop at index ${index}`,
      reasoning: 'Simplifying composition for cleaner aesthetic'
    }
    setGameChoices(prev => [...prev, choice])
  }, [currentArtwork.gradient.length])

  // Auto-save canvas as image
  useEffect(() => {
    if (!canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Create gradient on canvas
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height)
    currentArtwork.gradient.forEach(stop => {
      gradient.addColorStop(stop.position / 100, stop.color)
    })

    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, canvas.width, canvas.height)
  }, [currentArtwork])

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Palette className="h-5 w-5" />
            <span>Color Symphony</span>
          </div>
          <div className="flex gap-2">
            <Badge variant="secondary">Colors: {uniqueColors.size}</Badge>
            <Badge variant="secondary">Changes: {colorChanges + patternChanges}</Badge>
            <Badge variant="secondary">Saved: {savedArtworks.length}</Badge>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Start Game */}
          {!gameStarted && (
            <div className="text-center space-y-4">
              <p className="text-muted-foreground">
                Express your creativity through color, pattern, and composition. 
                Create beautiful gradients while Bondhu learns about your artistic preferences.
              </p>
              <Button onClick={startGame} className="w-full max-w-md">
                <Sparkles className="h-4 w-4 mr-2" />
                Begin Creative Journey
              </Button>
            </div>
          )}

          {gameStarted && (
            <>
              {/* Canvas Preview */}
              <div className="space-y-4">
                <div 
                  className="w-full h-64 rounded-lg border-2 border-gray-200 shadow-inner"
                  style={{ background: updateGradientStyle() }}
                />
                <canvas 
                  ref={canvasRef} 
                  width={400} 
                  height={200} 
                  className="hidden"
                />
              </div>

              {/* Tool Selection */}
              <div className="flex gap-2 justify-center">
                {[
                  { id: 'gradient', label: 'Colors', icon: '🎨' },
                  { id: 'pattern', label: 'Pattern', icon: '🔄' },
                  { id: 'palette', label: 'Palettes', icon: '🎭' }
                ].map(tool => (
                  <Button
                    key={tool.id}
                    variant={currentTool === tool.id ? 'default' : 'outline'}
                    onClick={() => setCurrentTool(tool.id as any)}
                    className="flex-1"
                  >
                    <span className="mr-2">{tool.icon}</span>
                    {tool.label}
                  </Button>
                ))}
              </div>

              {/* Gradient Controls */}
              {currentTool === 'gradient' && (
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <h3 className="font-medium">Gradient Colors</h3>
                    <Button size="sm" onClick={addColorStop}>
                      Add Color
                    </Button>
                  </div>
                  
                  <div className="space-y-3">
                    {currentArtwork.gradient.map((stop, index) => (
                      <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                        <input
                          type="color"
                          value={stop.color}
                          onChange={(e) => updateColorStop(index, e.target.value)}
                          className="w-8 h-8 rounded border"
                        />
                        <div className="flex-1">
                          <label className="text-xs text-gray-600">Position: {stop.position.toFixed(0)}%</label>
                          <Slider
                            value={[stop.position]}
                            onValueChange={([value]) => updateColorPosition(index, value)}
                            max={100}
                            step={1}
                            className="mt-1"
                          />
                        </div>
                        {currentArtwork.gradient.length > 2 && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => removeColorStop(index)}
                          >
                            ×
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Pattern Controls */}
              {currentTool === 'pattern' && (
                <div className="space-y-4">
                  <div>
                    <h3 className="font-medium mb-3">Gradient Pattern</h3>
                    <div className="grid grid-cols-3 gap-2">
                      {(['linear', 'radial', 'conic'] as const).map(pattern => (
                        <Button
                          key={pattern}
                          variant={currentArtwork.pattern === pattern ? 'default' : 'outline'}
                          onClick={() => changePattern(pattern)}
                          className="capitalize"
                        >
                          {pattern}
                        </Button>
                      ))}
                    </div>
                  </div>

                  {currentArtwork.pattern === 'linear' && (
                    <div>
                      <label className="text-sm font-medium">Angle: {currentArtwork.angle}°</label>
                      <Slider
                        value={[currentArtwork.angle]}
                        onValueChange={([value]) => changeAngle(value)}
                        max={360}
                        step={1}
                        className="mt-2"
                      />
                    </div>
                  )}
                </div>
              )}

              {/* Palette Controls */}
              {currentTool === 'palette' && (
                <div className="space-y-4">
                  <h3 className="font-medium">Color Palettes</h3>
                  <div className="grid grid-cols-2 gap-3">
                    {COLOR_PALETTES.map(palette => (
                      <Button
                        key={palette.name}
                        variant={selectedPalette === palette.name ? 'default' : 'outline'}
                        onClick={() => applyPalette(palette)}
                        className="h-auto p-3 flex flex-col items-start"
                      >
                        <span className="font-medium">{palette.name}</span>
                        <div className="flex space-x-1 mt-1">
                          {palette.colors.map((color, i) => (
                            <div
                              key={i}
                              className="w-4 h-4 rounded-full border"
                              style={{ backgroundColor: color }}
                            />
                          ))}
                        </div>
                      </Button>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-2">
                <Button onClick={generateRandomArt} variant="outline" className="flex-1">
                  <Sparkles className="h-4 w-4 mr-2" />
                  Surprise Me
                </Button>
                <Button onClick={saveArtwork} variant="outline" className="flex-1">
                  <Save className="h-4 w-4 mr-2" />
                  Save Art
                </Button>
                <Button onClick={resetArtwork} variant="outline" className="flex-1">
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Reset
                </Button>
                <Button onClick={completeSession} className="flex-1">
                  <Download className="h-4 w-4 mr-2" />
                  Complete
                </Button>
              </div>

              {/* Saved Artworks */}
              {savedArtworks.length > 0 && (
                <div className="space-y-3">
                  <h3 className="font-medium">Your Gallery</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {savedArtworks.map(artwork => (
                      <div
                        key={artwork.id}
                        className="aspect-square rounded-lg border cursor-pointer hover:scale-105 transition-transform"
                        style={{ 
                          background: (() => {
                            const colorStops = artwork.gradient
                              .sort((a, b) => a.position - b.position)
                              .map(stop => `${stop.color} ${stop.position}%`)
                              .join(', ')
                            return `${artwork.pattern}-gradient(${artwork.pattern === 'linear' ? `${artwork.angle}deg, ` : ''}${colorStops})`
                          })()
                        }}
                        onClick={() => setCurrentArtwork(artwork)}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Analytics Preview */}
              <div className="text-xs text-muted-foreground space-y-1 p-3 bg-gray-50 rounded-lg">
                <p className="font-medium">Creative Insights:</p>
                <p>• Color diversity: {uniqueColors.size} unique colors explored</p>
                <p>• Creative actions: {colorChanges + patternChanges} modifications made</p>
                <p>• Artistic style: {selectedPalette ? `${selectedPalette} palette preference` : 'Custom color exploration'}</p>
                <p>• Pattern preference: {currentArtwork.pattern} gradients</p>
              </div>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
