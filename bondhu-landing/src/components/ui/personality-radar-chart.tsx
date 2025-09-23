"use client"

import { motion } from "framer-motion"
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from "recharts"
import { PersonalityScores } from "@/types/personality"
import { cn } from "@/lib/utils"

interface PersonalityRadarChartProps {
  scores: PersonalityScores
  className?: string
  showAnimation?: boolean
}

export function PersonalityRadarChart({ 
  scores, 
  className,
  showAnimation = true 
}: PersonalityRadarChartProps) {
  // Transform scores for radar chart
  const chartData = [
    {
      trait: 'Openness',
      fullName: 'Openness to Experience',
      score: scores.openness,
      color: '#22c55e'
    },
    {
      trait: 'Extraversion',
      fullName: 'Extraversion',
      score: scores.extraversion,
      color: '#8b5cf6'
    },
    {
      trait: 'Agreeableness',
      fullName: 'Agreeableness',
      score: scores.agreeableness,
      color: '#f59e0b'
    },
    {
      trait: 'Conscientiousness',
      fullName: 'Conscientiousness',
      score: scores.conscientiousness,
      color: '#3b82f6'
    },
    {
      trait: 'Emotional Sensitivity',
      fullName: 'Emotional Sensitivity',
      score: scores.neuroticism,
      color: '#f97316'
    }
  ]

  // Calculate personality type based on dominant traits
  const getPersonalityType = () => {
    const maxTrait = chartData.reduce((prev, current) => 
      prev.score > current.score ? prev : current
    )
    const secondMax = chartData
      .filter(trait => trait !== maxTrait)
      .reduce((prev, current) => prev.score > current.score ? prev : current)
    
    return `${maxTrait.trait} ${secondMax.trait}`
  }

  const personalityType = getPersonalityType()

  return (
    <motion.div
      initial={showAnimation ? { opacity: 0, scale: 0.9 } : {}}
      animate={showAnimation ? { opacity: 1, scale: 1 } : {}}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className={cn("space-y-6", className)}
    >
      {/* Chart Container */}
      <div className="relative">
        <div className="bg-gradient-to-br from-background via-background to-secondary/10 rounded-xl p-6 border">
          <div className="text-center mb-6">
            <h3 className="text-xl font-semibold mb-2">Your Personality Profile</h3>
            <p className="text-sm text-muted-foreground">
              Dominant traits: <span className="font-medium text-foreground">{personalityType}</span>
            </p>
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={chartData} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                <PolarGrid 
                  gridType="polygon" 
                  className="opacity-30"
                />
                <PolarAngleAxis 
                  dataKey="trait" 
                  tick={{ 
                    fontSize: 12, 
                    fontWeight: 500,
                    fill: 'hsl(var(--foreground))'
                  }}
                  className="text-foreground"
                />
                <PolarRadiusAxis 
                  angle={90} 
                  domain={[0, 100]} 
                  tick={{ 
                    fontSize: 10,
                    fill: 'hsl(var(--muted-foreground))'
                  }}
                  tickCount={6}
                />
                <Radar
                  name="Personality"
                  dataKey="score"
                  stroke="hsl(var(--primary))"
                  fill="hsl(var(--primary))"
                  fillOpacity={0.1}
                  strokeWidth={2}
                  dot={{ 
                    r: 4, 
                    fill: "hsl(var(--primary))",
                    strokeWidth: 2,
                    stroke: "hsl(var(--background))"
                  }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Score Breakdown */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {chartData.map((trait, index) => (
          <motion.div
            key={trait.trait}
            initial={showAnimation ? { opacity: 0, y: 20 } : {}}
            animate={showAnimation ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.4, delay: showAnimation ? index * 0.1 : 0 }}
            className="bg-card border rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center space-x-3 mb-3">
              <div 
                className="w-4 h-4 rounded-full"
                style={{ backgroundColor: trait.color }}
              />
              <h4 className="font-medium text-sm">{trait.trait}</h4>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold" style={{ color: trait.color }}>
                  {trait.score}
                </span>
                <span className="text-xs text-muted-foreground">/ 100</span>
              </div>
              
              {/* Progress bar */}
              <div className="w-full bg-muted rounded-full h-2">
                <motion.div
                  initial={showAnimation ? { width: 0 } : { width: `${trait.score}%` }}
                  animate={{ width: `${trait.score}%` }}
                  transition={{ duration: 1, delay: showAnimation ? index * 0.1 + 0.5 : 0 }}
                  className="h-2 rounded-full transition-all duration-300"
                  style={{ backgroundColor: trait.color }}
                />
              </div>
              
              {/* Level indicator */}
              <div className="text-center">
                <span className={cn(
                  "text-xs px-2 py-1 rounded-full font-medium",
                  trait.score <= 30 
                    ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300"
                    : trait.score <= 70
                    ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300"
                    : "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300"
                )}>
                  {trait.score <= 30 ? 'Low' : trait.score <= 70 ? 'Moderate' : 'High'}
                </span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Personality Insights */}
      <motion.div
        initial={showAnimation ? { opacity: 0, y: 20 } : {}}
        animate={showAnimation ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.6, delay: showAnimation ? 0.8 : 0 }}
        className="bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5 rounded-xl p-6 border"
      >
        <div className="text-center space-y-4">
          <div className="space-y-2">
            <h3 className="text-lg font-semibold flex items-center justify-center space-x-2">
              <span>🎭</span>
              <span>Your Unique Personality</span>
            </h3>
            <p className="text-sm text-muted-foreground">
              Based on your responses, here's how Bondhu will adapt to support you
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4">
            <div className="space-y-2">
              <div className="text-2xl">🧠</div>
              <h4 className="font-medium">Thinking Style</h4>
              <p className="text-sm text-muted-foreground">
                {scores.openness > 70 
                  ? "Creative and abstract thinker"
                  : scores.openness < 30
                  ? "Practical and concrete thinker"
                  : "Balanced thinking approach"}
              </p>
            </div>

            <div className="space-y-2">
              <div className="text-2xl">🤝</div>
              <h4 className="font-medium">Social Energy</h4>
              <p className="text-sm text-muted-foreground">
                {scores.extraversion > 70
                  ? "Energized by social interaction"
                  : scores.extraversion < 30
                  ? "Energized by quiet reflection"
                  : "Flexible social energy"}
              </p>
            </div>

            <div className="space-y-2">
              <div className="text-2xl">💖</div>
              <h4 className="font-medium">Support Style</h4>
              <p className="text-sm text-muted-foreground">
                {scores.neuroticism > 70
                  ? "Benefits from gentle, frequent support"
                  : scores.neuroticism < 30
                  ? "Thrives with practical, solution-focused support"
                  : "Adapts to varying support needs"}
              </p>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}

// Additional component for compact view
export function PersonalityRadarChartCompact({ 
  scores, 
  className 
}: PersonalityRadarChartProps) {
  const chartData = [
    { trait: 'O', fullName: 'Openness', score: scores.openness, color: '#22c55e' },
    { trait: 'E', fullName: 'Extraversion', score: scores.extraversion, color: '#8b5cf6' },
    { trait: 'A', fullName: 'Agreeableness', score: scores.agreeableness, color: '#f59e0b' },
    { trait: 'C', fullName: 'Conscientiousness', score: scores.conscientiousness, color: '#3b82f6' },
    { trait: 'ES', fullName: 'Emotional Sensitivity', score: scores.neuroticism, color: '#f97316' }
  ]

  return (
    <div className={cn("bg-card border rounded-lg p-4", className)}>
      <div className="h-40">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={chartData}>
            <PolarGrid gridType="polygon" className="opacity-20" />
            <PolarAngleAxis 
              dataKey="trait" 
              tick={{ fontSize: 10, fill: 'hsl(var(--foreground))' }}
            />
            <PolarRadiusAxis domain={[0, 100]} tick={false} />
            <Radar
              name="Personality"
              dataKey="score"
              stroke="hsl(var(--primary))"
              fill="hsl(var(--primary))"
              fillOpacity={0.1}
              strokeWidth={2}
              dot={{ r: 2, fill: "hsl(var(--primary))" }}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
