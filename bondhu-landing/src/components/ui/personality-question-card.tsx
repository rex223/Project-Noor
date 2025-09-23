"use client"

import { motion } from "framer-motion"
import { PersonalityQuestion } from "@/types/personality"
import { PersonalitySlider } from "./personality-slider"
import { cn } from "@/lib/utils"

interface PersonalityQuestionCardProps {
  question: PersonalityQuestion
  questionIndex: number
  totalQuestions: number
  onResponseChange: (questionId: number, response: number) => void
  className?: string
}

export function PersonalityQuestionCard({
  question,
  questionIndex,
  totalQuestions,
  onResponseChange,
  className
}: PersonalityQuestionCardProps) {
  const handleResponseChange = (response: number) => {
    onResponseChange(question.id, response)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: questionIndex * 0.1 }}
      className={cn(
        "bg-card border border-border rounded-xl p-6 space-y-6",
        "hover:shadow-md transition-shadow duration-200",
        className
      )}
    >
      {/* Question Header */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-muted-foreground">
            Question {questionIndex + 1} of {totalQuestions}
          </span>
          <div className="flex items-center space-x-1">
            {Array.from({ length: totalQuestions }).map((_, i) => (
              <div
                key={i}
                className={cn(
                  "w-2 h-2 rounded-full transition-colors",
                  i <= questionIndex ? "bg-primary" : "bg-muted"
                )}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Scenario Text */}
      <div className="space-y-3">
        <div className="p-4 bg-secondary/30 rounded-lg border-l-4 border-primary">
          <p className="text-sm text-muted-foreground italic leading-relaxed">
            {question.scenario}
          </p>
        </div>
      </div>

      {/* Question Text */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-foreground leading-relaxed">
          {question.questionText}
        </h3>
      </div>

      {/* Response Slider */}
      <div className="space-y-2">
        <PersonalitySlider
          value={question.userResponse}
          onValueChange={handleResponseChange}
          questionId={question.id}
        />
      </div>

      {/* Response Feedback */}
      {question.userResponse && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex items-center justify-center space-x-2 pt-2"
        >
          <div className="w-8 h-8 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
            <motion.span
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 500 }}
              className="text-green-600 dark:text-green-400 text-sm"
            >
              ✓
            </motion.span>
          </div>
          <span className="text-sm text-green-600 dark:text-green-400 font-medium">
            Response recorded
          </span>
        </motion.div>
      )}
    </motion.div>
  )
}


