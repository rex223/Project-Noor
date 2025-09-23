"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { ArrowRight, Play } from "lucide-react"
import { Button } from "@/components/ui/button"
import Link from "next/link"

interface EnhancedHeroCTAProps {
  onHover?: (isHovered: boolean) => void
}

export function EnhancedHeroCTA({ onHover }: EnhancedHeroCTAProps) {
  const [isSecondaryHovered, setIsSecondaryHovered] = useState(false)

  return (
    <motion.div
      className="flex flex-col sm:flex-row gap-4 justify-center items-center"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, delay: 0.6 }}
    >
      <motion.div
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onHoverStart={() => {
          onHover?.(true)
        }}
        onHoverEnd={() => {
          onHover?.(false)
        }}
      >
        <Button
          size="lg"
          className="h-12 px-8 relative overflow-hidden group"
          asChild
        >
          <Link href="/sign-up" className="flex items-center gap-2 relative z-10">
            Start Chatting Now
            <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />

            {/* Animated background effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-primary via-blue-600 to-primary bg-[length:200%_100%] animate-pulse group-hover:animate-none group-hover:bg-[position:100%_0%] transition-all duration-500 -z-10" />
          </Link>
        </Button>
      </motion.div>

      <motion.div
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onHoverStart={() => setIsSecondaryHovered(true)}
        onHoverEnd={() => setIsSecondaryHovered(false)}
      >
        <Button
          variant="outline"
          size="lg"
          className="h-12 px-8 relative overflow-hidden group backdrop-blur-sm border-primary/20 hover:border-primary/40"
          asChild
        >
          <Link href="#demo" className="flex items-center gap-2 relative z-10">
            <motion.div
              animate={{
                rotate: isSecondaryHovered ? 360 : 0,
                scale: isSecondaryHovered ? 1.1 : 1
              }}
              transition={{ duration: 0.3 }}
            >
              <Play className="h-4 w-4" />
            </motion.div>
            Watch Demo

            {/* Subtle shimmer effect on hover */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-primary/10 to-transparent transform -skew-x-12 group-hover:translate-x-full transition-transform duration-700 -z-10" />
          </Link>
        </Button>
      </motion.div>
    </motion.div>
  )
}
