"use client"

import Image from "next/image"
import { useTheme } from "next-themes"
import { useEffect, useState } from "react"

interface LogoProps {
  className?: string
  width?: number
  height?: number
}

export function Logo({ className = "", width = 120, height = 40 }: LogoProps) {
  const { resolvedTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  // Don't render anything until mounted to avoid hydration mismatch
  if (!mounted) {
    return (
      <div 
        className={`${className}`} 
        style={{ width, height }}
      >
        {/* Placeholder while mounting */}
        <div className="flex items-center space-x-2">
          <span className="font-bold text-2xl">Bondhu</span>
          <span className="text-lg text-muted-foreground">বন্ধু</span>
        </div>
      </div>
    )
  }

  const isDark = resolvedTheme === "dark"
  const logoSrc = isDark ? "/Dark mode Logo.svg" : "/Light mode logo.svg"

  return (
    <div className={`flex items-center ${className}`}>
      <Image
        src={logoSrc}
        alt="Bondhu Logo"
        width={width}
        height={height}
        priority
        className="object-contain"
      />
    </div>
  )
}
