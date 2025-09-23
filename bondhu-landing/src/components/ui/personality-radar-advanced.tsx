"use client"

import { useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from './card'
import { Badge } from './badge'

interface PersonalityData {
  openness: number
  conscientiousness: number
  extraversion: number
  agreeableness: number
  neuroticism: number
  trend?: 'increasing' | 'decreasing' | 'stable'
}

interface PersonalityRadarAdvancedProps {
  personalityData: PersonalityData
  entertainmentInsights?: {
    gaming_creativity: number
    video_attention_span: number
    music_emotional_regulation: number
    overall_engagement: number
  }
  className?: string
}

export function PersonalityRadarAdvanced({ 
  personalityData, 
  entertainmentInsights,
  className 
}: PersonalityRadarAdvancedProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  const traits = [
    { 
      key: 'openness', 
      label: 'Openness', 
      description: 'Imagination, curiosity, artistic interests',
      color: '#3B82F6' // blue
    },
    { 
      key: 'conscientiousness', 
      label: 'Conscientiousness', 
      description: 'Organization, discipline, goal-orientation',
      color: '#10B981' // green
    },
    { 
      key: 'extraversion', 
      label: 'Extraversion', 
      description: 'Sociability, assertiveness, energy',
      color: '#F59E0B' // orange
    },
    { 
      key: 'agreeableness', 
      label: 'Agreeableness', 
      description: 'Cooperation, trust, empathy',
      color: '#8B5CF6' // purple
    },
    { 
      key: 'neuroticism', 
      label: 'Neuroticism', 
      description: 'Emotional instability, anxiety, moodiness',
      color: '#EF4444' // red
    }
  ]

  const drawRadarChart = () => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const width = canvas.width
    const height = canvas.height
    const centerX = width / 2
    const centerY = height / 2
    const radius = Math.min(width, height) / 2 - 40

    // Clear canvas
    ctx.clearRect(0, 0, width, height)

    // Draw background circles
    const circles = 5
    for (let i = 1; i <= circles; i++) {
      const r = (radius * i) / circles
      ctx.beginPath()
      ctx.arc(centerX, centerY, r, 0, 2 * Math.PI)
      ctx.strokeStyle = '#E5E7EB'
      ctx.lineWidth = 1
      ctx.stroke()
    }

    // Draw axes
    const numTraits = traits.length
    const angleStep = (2 * Math.PI) / numTraits

    for (let i = 0; i < numTraits; i++) {
      const angle = i * angleStep - Math.PI / 2
      const x = centerX + radius * Math.cos(angle)
      const y = centerY + radius * Math.sin(angle)
      
      ctx.beginPath()
      ctx.moveTo(centerX, centerY)
      ctx.lineTo(x, y)
      ctx.strokeStyle = '#D1D5DB'
      ctx.lineWidth = 1
      ctx.stroke()
    }

    // Draw personality data
    ctx.beginPath()
    for (let i = 0; i < numTraits; i++) {
      const trait = traits[i]
      const value = personalityData[trait.key as keyof PersonalityData] as number || 0
      const normalizedValue = value / 100
      const angle = i * angleStep - Math.PI / 2
      const x = centerX + radius * normalizedValue * Math.cos(angle)
      const y = centerY + radius * normalizedValue * Math.sin(angle)
      
      if (i === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    }
    ctx.closePath()
    ctx.fillStyle = 'rgba(59, 130, 246, 0.1)'
    ctx.fill()
    ctx.strokeStyle = '#3B82F6'
    ctx.lineWidth = 2
    ctx.stroke()

    // Draw data points
    for (let i = 0; i < numTraits; i++) {
      const trait = traits[i]
      const value = personalityData[trait.key as keyof PersonalityData] as number || 0
      const normalizedValue = value / 100
      const angle = i * angleStep - Math.PI / 2
      const x = centerX + radius * normalizedValue * Math.cos(angle)
      const y = centerY + radius * normalizedValue * Math.sin(angle)
      
      ctx.beginPath()
      ctx.arc(x, y, 4, 0, 2 * Math.PI)
      ctx.fillStyle = trait.color
      ctx.fill()
      ctx.strokeStyle = '#FFFFFF'
      ctx.lineWidth = 2
      ctx.stroke()
    }

    // Draw labels
    for (let i = 0; i < numTraits; i++) {
      const trait = traits[i]
      const angle = i * angleStep - Math.PI / 2
      const labelRadius = radius + 25
      const x = centerX + labelRadius * Math.cos(angle)
      const y = centerY + labelRadius * Math.sin(angle)
      
      ctx.fillStyle = '#374151'
      ctx.font = '12px Inter, sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(trait.label, x, y)
    }

    // Draw score labels
    for (let i = 1; i <= circles; i++) {
      const score = (i * 20).toString()
      ctx.fillStyle = '#9CA3AF'
      ctx.font = '10px Inter, sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText(score, centerX + 5, centerY - (radius * i) / circles + 3)
    }
  }

  useEffect(() => {
    drawRadarChart()
  }, [personalityData])

  // Calculate personality insights
  const getPersonalityType = () => {
    const { openness, conscientiousness, extraversion, agreeableness, neuroticism } = personalityData
    
    if (openness > 70 && conscientiousness > 70) return "The Innovator"
    if (extraversion > 70 && agreeableness > 70) return "The Connector"
    if (conscientiousness > 70 && agreeableness > 70) return "The Helper"
    if (openness > 70 && extraversion > 70) return "The Explorer"
    if (conscientiousness > 70 && neuroticism < 40) return "The Achiever"
    if (agreeableness > 70 && neuroticism < 40) return "The Peacemaker"
    if (openness > 60 && conscientiousness > 60) return "The Creator"
    return "The Balanced Individual"
  }

  const getTopStrengths = () => {
    const scores = Object.entries(personalityData)
      .filter(([key]) => key !== 'trend')
      .map(([key, value]) => ({ 
        trait: traits.find(t => t.key === key)?.label || key, 
        score: value as number 
      }))
      .sort((a, b) => b.score - a.score)
      .slice(0, 2)
    
    return scores
  }

  const getGrowthAreas = () => {
    const scores = Object.entries(personalityData)
      .filter(([key]) => key !== 'trend' && key !== 'neuroticism') // Exclude neuroticism as lower is better
      .map(([key, value]) => ({ 
        trait: traits.find(t => t.key === key)?.label || key, 
        score: value as number 
      }))
      .sort((a, b) => a.score - b.score)
      .slice(0, 2)
    
    return scores
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Main Radar Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Personality Profile</span>
            <Badge variant="secondary">{getPersonalityType()}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col lg:flex-row items-center gap-6">
            <div className="relative">
              <canvas
                ref={canvasRef}
                width={300}
                height={300}
                className="max-w-full h-auto"
              />
            </div>
            
            <div className="flex-1 space-y-4">
              <div>
                <h4 className="font-medium mb-3">Trait Breakdown</h4>
                <div className="space-y-3">
                  {traits.map(trait => {
                    const score = personalityData[trait.key as keyof PersonalityData] as number || 0
                    return (
                      <div key={trait.key} className="space-y-1">
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium">{trait.label}</span>
                          <span className="text-sm font-bold" style={{ color: trait.color }}>
                            {score}%
                          </span>
                        </div>
                        <div className="w-full h-2 bg-gray-200 rounded-full">
                          <div
                            className="h-2 rounded-full transition-all duration-500"
                            style={{ 
                              width: `${score}%`,
                              backgroundColor: trait.color 
                            }}
                          />
                        </div>
                        <p className="text-xs text-muted-foreground">{trait.description}</p>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Insights Grid */}
      <div className="grid md:grid-cols-2 gap-4">
        {/* Top Strengths */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Top Strengths</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {getTopStrengths().map((strength, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-sm font-medium">{strength.trait}</span>
                  <Badge variant="default">{strength.score}%</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Growth Areas */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Growth Opportunities</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {getGrowthAreas().map((area, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-sm font-medium">{area.trait}</span>
                  <Badge variant="outline">{area.score}%</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Entertainment Integration */}
      {entertainmentInsights && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Entertainment-Based Insights</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-purple-600">
                  {entertainmentInsights.gaming_creativity}%
                </div>
                <div className="text-sm text-muted-foreground">Gaming Creativity</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-blue-600">
                  {entertainmentInsights.video_attention_span}%
                </div>
                <div className="text-sm text-muted-foreground">Video Focus</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">
                  {entertainmentInsights.music_emotional_regulation}%
                </div>
                <div className="text-sm text-muted-foreground">Music Regulation</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-orange-600">
                  {entertainmentInsights.overall_engagement}%
                </div>
                <div className="text-sm text-muted-foreground">Overall Engagement</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
