"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { cn } from "@/lib/utils"

interface PersonalitySliderProps {
  value?: number
  onValueChange: (value: number) => void
  disabled?: boolean
  questionId: number
  className?: string
}

const sliderLabels = [
  { value: 1, label: "Strongly Disagree", short: "SD" },
  { value: 2, label: "Disagree", short: "D" },
  { value: 3, label: "Neutral", short: "N" },
  { value: 4, label: "Agree", short: "A" },
  { value: 5, label: "Strongly Agree", short: "SA" }
]

export function PersonalitySlider({ 
  value, 
  onValueChange, 
  disabled = false, 
  questionId,
  className 
}: PersonalitySliderProps) {
  const [hoveredValue, setHoveredValue] = useState<number | null>(null)
  const [isPressed, setIsPressed] = useState(false)

  const handleValueSelect = (selectedValue: number) => {
    if (disabled) return
    onValueChange(selectedValue)
    
    // Add haptic feedback effect
    setIsPressed(true)
    setTimeout(() => setIsPressed(false), 150)
  }

  const getSliderColor = (sliderValue: number) => {
    const activeValue = hoveredValue ?? value
    if (!activeValue) return "bg-muted border-border"
    
    if (sliderValue === activeValue) {
      if (sliderValue <= 2) return "bg-red-100 border-red-300 dark:bg-red-900/30 dark:border-red-700"
      if (sliderValue === 3) return "bg-yellow-100 border-yellow-300 dark:bg-yellow-900/30 dark:border-yellow-700"
      return "bg-green-100 border-green-300 dark:bg-green-900/30 dark:border-green-700"
    }
    
    if (value === sliderValue) {
      return "bg-primary/20 border-primary/40"
    }
    
    return "bg-muted/50 border-border"
  }

  const getTextColor = (sliderValue: number) => {
    const activeValue = hoveredValue ?? value
    if (sliderValue === activeValue) {
      if (sliderValue <= 2) return "text-red-700 dark:text-red-300"
      if (sliderValue === 3) return "text-yellow-700 dark:text-yellow-300"
      return "text-green-700 dark:text-green-300"
    }
    
    if (value === sliderValue) {
      return "text-primary"
    }
    
    return "text-muted-foreground"
  }

  return (
    <div className={cn("space-y-4", className)}>
      {/* Slider Track */}
      <div className="relative">
        <div className="flex justify-between items-center space-x-2">
          {sliderLabels.map((item) => (
            <motion.button
              key={item.value}
              type="button"
              onClick={() => handleValueSelect(item.value)}
              onMouseEnter={() => setHoveredValue(item.value)}
              onMouseLeave={() => setHoveredValue(null)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  handleValueSelect(item.value)
                }
              }}
              disabled={disabled}
              aria-label={`${item.label} - ${item.value} out of 5`}
              aria-pressed={value === item.value}
              role="radio"
              tabIndex={0}
              className={cn(
                "relative w-12 h-12 rounded-full border-2 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:ring-offset-2",
                "hover:scale-110 active:scale-95",
                getSliderColor(item.value),
                disabled && "opacity-50 cursor-not-allowed hover:scale-100"
              )}
              whileHover={!disabled ? { scale: 1.1 } : {}}
              whileTap={!disabled ? { scale: 0.95 } : {}}
              animate={
                value === item.value && isPressed
                  ? { scale: [1, 1.2, 1], rotate: [0, 5, -5, 0] }
                  : {}
              }
              transition={{ duration: 0.15 }}
            >
              <span className={cn(
                "text-xs font-medium transition-colors",
                getTextColor(item.value)
              )}>
                {item.short}
              </span>
              
              {/* Selection indicator */}
              <AnimatePresence>
                {value === item.value && (
                  <motion.div
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0, opacity: 0 }}
                    className="absolute -top-1 -right-1 w-4 h-4 bg-primary rounded-full border-2 border-background flex items-center justify-center"
                  >
                    <div className="w-1.5 h-1.5 bg-primary-foreground rounded-full" />
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.button>
          ))}
        </div>

        {/* Connecting line */}
        <div className="absolute top-1/2 left-6 right-6 h-0.5 bg-border -translate-y-1/2 -z-10" />
        
        {/* Progress line */}
        {value && (
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${((value - 1) / 4) * 100}%` }}
            className="absolute top-1/2 left-6 h-1 bg-gradient-to-r from-red-400 via-yellow-400 to-green-400 -translate-y-1/2 rounded-full"
            style={{ maxWidth: "calc(100% - 3rem)" }}
          />
        )}
      </div>

      {/* Labels */}
      <div className="flex justify-between text-xs text-muted-foreground px-1">
        <span>Strongly Disagree</span>
        <span>Strongly Agree</span>
      </div>

      {/* Current selection display */}
      <AnimatePresence>
        {(value || hoveredValue) && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="text-center"
          >
            <div className={cn(
              "inline-flex items-center space-x-2 px-3 py-1.5 rounded-full text-sm font-medium transition-colors",
              hoveredValue 
                ? "bg-muted/50 text-muted-foreground"
                : "bg-primary/10 text-primary"
            )}>
              <span>
                {sliderLabels.find(item => item.value === (hoveredValue ?? value))?.label}
              </span>
              {!hoveredValue && value && (
                <motion.span
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="text-primary"
                >
                  ✓
                </motion.span>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
