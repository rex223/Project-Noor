"use client"

import { useEffect, useState } from "react"

interface HeroBackgroundProps {
  intensity?: "subtle" | "normal" | "enhanced"
  className?: string
}

export function HeroBackground({ intensity = "normal", className = "" }: HeroBackgroundProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false)
  const [isInViewport, setIsInViewport] = useState(true)
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    setIsMounted(true)
    
    // Check for reduced motion preference
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)")
    setPrefersReducedMotion(mediaQuery.matches)

    // Listen for changes in motion preference
    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches)
    }

    mediaQuery.addEventListener("change", handleChange)

    // Intersection Observer for performance optimization
    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsInViewport(entry.isIntersecting)
      },
      { threshold: 0.1 }
    )

    // Observe the hero section
    const heroSection = document.querySelector("section")
    if (heroSection) {
      observer.observe(heroSection)
    }

    // Fade in the background after component mounts
    const timer = setTimeout(() => setIsVisible(true), 100)

    return () => {
      mediaQuery.removeEventListener("change", handleChange)
      if (heroSection) observer.unobserve(heroSection)
      clearTimeout(timer)
    }
  }, [])

  // Adjust circle sizes based on intensity - using CSS classes for responsive behavior
  const getCircleSize = (baseSize: number) => {
    let sizeMultiplier = 1
    
    switch (intensity) {
      case "subtle":
        sizeMultiplier = 0.7
        break
      case "enhanced":
        sizeMultiplier = 1.3
        break
      default:
        sizeMultiplier = 1
    }

    return baseSize * sizeMultiplier
  }

  // Get responsive class names for different screen sizes
  const getResponsiveClass = () => {
    return "scale-[0.7] md:scale-[0.85] lg:scale-100"
  }

  // Get animation classes based on motion preference and viewport visibility
  const getAnimationClass = (animationType: string) => {
    if (prefersReducedMotion || !isInViewport) {
      return "bondhu-static-circle"
    }
    
    return animationType
  }

  // Don't render until mounted to avoid hydration mismatch
  if (!isMounted) {
    return (
      <div 
        className={`absolute inset-0 overflow-hidden pointer-events-none opacity-0 ${className}`}
        aria-hidden="true"
      />
    )
  }

  // Don't render animations if not in viewport for performance
  if (!isInViewport && isVisible) {
    return (
      <div 
        className={`absolute inset-0 overflow-hidden pointer-events-none opacity-30 ${className}`}
        aria-hidden="true"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-secondary/5" />
      </div>
    )
  }

  return (
    <div 
      className={`absolute inset-0 overflow-hidden pointer-events-none transition-opacity duration-1000 ${
        isVisible ? "opacity-100" : "opacity-0"
      } ${getResponsiveClass()} ${className}`}
      aria-hidden="true"
      style={{ contain: "layout style paint" }}
    >
      {/* Large Circle - Top Right */}
      <div
        className={`absolute rounded-full ${getAnimationClass("bondhu-breathe bondhu-shimmer")}`}
        style={{
          width: `${getCircleSize(400)}px`,
          height: `${getCircleSize(400)}px`,
          top: "-20%",
          right: "-15%",
          background: `radial-gradient(circle at 30% 40%, 
            rgba(34, 197, 94, 0.1) 0%,
            rgba(59, 130, 246, 0.08) 35%,
            rgba(147, 51, 234, 0.06) 70%,
            transparent 100%)`,
          filter: "blur(1px)",
        }}
      />

      {/* Medium Circle - Bottom Left */}
      <div
        className={`absolute rounded-full ${getAnimationClass("bondhu-breathe-alt bondhu-pulse")}`}
        style={{
          width: `${getCircleSize(300)}px`,
          height: `${getCircleSize(300)}px`,
          bottom: "-10%",
          left: "-10%",
          background: `radial-gradient(circle at 60% 30%, 
            rgba(59, 130, 246, 0.12) 0%,
            rgba(34, 197, 94, 0.08) 40%,
            rgba(168, 85, 247, 0.06) 80%,
            transparent 100%)`,
          filter: "blur(0.5px)",
        }}
      />

      {/* Small Circle - Center Right */}
      <div
        className={`absolute rounded-full ${getAnimationClass("bondhu-breathe-delayed bondhu-rotate")}`}
        style={{
          width: `${getCircleSize(200)}px`,
          height: `${getCircleSize(200)}px`,
          top: "35%",
          right: "15%",
          background: `radial-gradient(circle at 50% 50%, 
            rgba(147, 51, 234, 0.1) 0%,
            rgba(34, 197, 94, 0.07) 50%,
            transparent 100%)`,
          filter: "blur(0.8px)",
        }}
      />

      {/* Connecting Lines - Subtle */}
      <svg 
        className="absolute inset-0 w-full h-full"
        style={{ zIndex: -1 }}
      >
        <defs>
          <linearGradient id="bondhu-line-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style={{ stopColor: "rgba(34, 197, 94, 0.05)", stopOpacity: 1 }} />
            <stop offset="50%" style={{ stopColor: "rgba(59, 130, 246, 0.08)", stopOpacity: 1 }} />
            <stop offset="100%" style={{ stopColor: "rgba(147, 51, 234, 0.05)", stopOpacity: 1 }} />
          </linearGradient>
        </defs>
        
        {/* Curved connecting line */}
        <path
          d="M 50,100 Q 200,200 400,150 T 800,200"
          stroke="url(#bondhu-line-gradient)"
          strokeWidth="1"
          fill="none"
          opacity={prefersReducedMotion ? "0.02" : "0.05"}
          className={!prefersReducedMotion ? "bondhu-pulse" : ""}
        />
        
        {/* Second connecting curve */}
        <path
          d="M 150,400 Q 350,300 600,350 T 900,300"
          stroke="url(#bondhu-line-gradient)"
          strokeWidth="1"
          fill="none"
          opacity={prefersReducedMotion ? "0.02" : "0.04"}
          className={!prefersReducedMotion ? "bondhu-pulse" : ""}
          style={{ animationDelay: "3s" }}
        />
      </svg>

      {/* Additional Micro Circles for Depth */}
      <div
        className={`absolute rounded-full ${getAnimationClass("bondhu-pulse bondhu-rotate-reverse")}`}
        style={{
          width: `${getCircleSize(80)}px`,
          height: `${getCircleSize(80)}px`,
          top: "20%",
          left: "25%",
          background: `radial-gradient(circle, 
            rgba(34, 197, 94, 0.08) 0%,
            transparent 70%)`,
          filter: "blur(1px)",
        }}
      />

      <div
        className={`absolute rounded-full ${getAnimationClass("bondhu-pulse bondhu-rotate")}`}
        style={{
          width: `${getCircleSize(60)}px`,
          height: `${getCircleSize(60)}px`,
          bottom: "30%",
          right: "30%",
          background: `radial-gradient(circle, 
            rgba(59, 130, 246, 0.06) 0%,
            transparent 70%)`,
          filter: "blur(1.2px)",
          animationDelay: "5s",
        }}
      />

      {/* Holographic Shimmer Overlay */}
      <div
        className={`absolute inset-0 ${getAnimationClass("bondhu-shimmer")}`}
        style={{
          background: `linear-gradient(45deg, 
            transparent 0%,
            rgba(34, 197, 94, 0.02) 25%,
            rgba(59, 130, 246, 0.03) 50%,
            rgba(147, 51, 234, 0.02) 75%,
            transparent 100%)`,
          mixBlendMode: "normal",
        }}
      />
    </div>
  )
}
