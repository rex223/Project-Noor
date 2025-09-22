"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Badge } from "@/components/ui/badge"
import { HeroBackground } from "./hero-background"
import { EnhancedHeroCTA } from "./enhanced-hero-cta"

export function HeroSection() {
  const [isCtaHovered, setIsCtaHovered] = useState(false)

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-background via-background to-secondary/20">
      {/* New Animated Breathing Circles Background */}
      <HeroBackground intensity={isCtaHovered ? "enhanced" : "normal"} />
      
      {/* Original Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden" style={{ zIndex: 1 }}>
        {/* Bengali Script Background */}
        <motion.div
          className="absolute top-1/4 left-1/4 text-9xl font-bold text-muted/5 select-none"
          animate={{
            rotate: [0, 10, -10, 0],
            scale: [1, 1.1, 0.9, 1],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          বন্ধু
        </motion.div>

        {/* Floating Geometric Shapes */}
        {Array.from({ length: 6 }).map((_, i) => {
          // Fixed positions to avoid hydration mismatch
          const positions = [
            { left: "10%", top: "20%" },
            { left: "80%", top: "15%" },
            { left: "25%", top: "70%" },
            { left: "70%", top: "60%" },
            { left: "45%", top: "30%" },
            { left: "85%", top: "80%" },
          ]
          const delays = [0, 0.5, 1, 1.5, 2, 2.5]
          const durations = [4, 5, 6, 7, 8, 9]
          
          return (
            <motion.div
              key={i}
              className="absolute w-4 h-4 bg-primary/10 rounded-full"
              style={{
                left: positions[i].left,
                top: positions[i].top,
              }}
              animate={{
                y: [-20, 20, -20],
                x: [-10, 10, -10],
                opacity: [0.3, 0.7, 0.3],
              }}
              transition={{
                duration: durations[i],
                repeat: Infinity,
                ease: "easeInOut",
                delay: delays[i],
              }}
            />
          )
        })}

        {/* Connection Lines */}
        <svg className="absolute inset-0 w-full h-full">
          <motion.path
            d="M 100,200 Q 400,100 700,300 T 1000,200"
            stroke="currentColor"
            strokeWidth="1"
            fill="none"
            className="text-primary/20"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
          />
          <motion.path
            d="M 200,400 Q 500,300 800,500 T 1100,400"
            stroke="currentColor"
            strokeWidth="1"
            fill="none"
            className="text-primary/15"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut", delay: 1 }}
          />
        </svg>

        {/* Glowing Orbs */}
        {Array.from({ length: 3 }).map((_, i) => {
          const orbPositions = [
            { left: "20%", top: "20%" },
            { left: "50%", top: "40%" },
            { left: "80%", top: "60%" },
          ]
          const orbDurations = [5, 6, 7]
          
          return (
            <motion.div
              key={`orb-${i}`}
              className="absolute w-32 h-32 rounded-full bg-gradient-to-r from-primary/20 to-secondary/20 blur-xl"
              style={{
                left: orbPositions[i].left,
                top: orbPositions[i].top,
              }}
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.3, 0.6, 0.3],
              }}
              transition={{
                duration: orbDurations[i],
                repeat: Infinity,
                ease: "easeInOut",
              }}
            />
          )
        })}
      </div>

      {/* Content */}
      <div className="relative z-20 container mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <Badge variant="secondary" className="mb-6">
            🚀 Now in Beta - Join 10,000+ users
          </Badge>
        </motion.div>

        <motion.h1
          className="text-4xl md:text-6xl font-bold text-center mb-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          Meet Your Digital{" "}
          <span className="bg-gradient-to-r from-primary to-primary/80 bg-clip-text text-transparent">
            বন্ধু
          </span>
        </motion.h1>

        <motion.p
          className="text-xl text-muted-foreground max-w-2xl mx-auto text-center mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          An AI companion that adapts to your personality, grows with your journey, 
          and becomes the friend you&apos;ve always needed.
        </motion.p>

        <EnhancedHeroCTA onHover={setIsCtaHovered} />

        {/* Scroll Indicator */}
        <motion.div
          className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
          animate={{
            y: [0, 10, 0],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          <div className="w-6 h-10 border-2 border-muted-foreground rounded-full flex justify-center">
            <motion.div
              className="w-1 h-3 bg-muted-foreground rounded-full mt-2"
              animate={{
                opacity: [0, 1, 0],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            />
          </div>
        </motion.div>
      </div>
    </section>
  )
}
