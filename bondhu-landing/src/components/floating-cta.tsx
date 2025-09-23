"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { MessageCircle, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import Link from "next/link"

export function FloatingCTA() {
  const [isVisible, setIsVisible] = useState(false)
  const [isDismissed, setIsDismissed] = useState(false)
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    setIsMounted(true)
  }, [])

  useEffect(() => {
    const handleScroll = () => {
      const heroSection = document.querySelector("section")
      if (heroSection && !isDismissed) {
        const heroBottom = heroSection.offsetTop + heroSection.offsetHeight
        const scrollY = window.scrollY
        setIsVisible(scrollY > heroBottom)
      }
    }

    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [isDismissed])

  const handleDismiss = (e: React.MouseEvent) => {
    e.stopPropagation()
    setIsDismissed(true)
    setIsVisible(false)
  }

  if (!isMounted) {
    return null
  }

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.8, y: 20 }}
          className="fixed bottom-6 right-6 z-40"
        >
          <div className="relative">
            <Button
              size="lg"
              className="rounded-full h-14 px-6 shadow-lg bg-primary hover:bg-primary/90 text-primary-foreground"
              asChild
            >
              <Link href="/sign-up" className="flex items-center space-x-2">
                <MessageCircle className="h-5 w-5" />
                <span className="hidden sm:inline">Chat with Bondhu</span>
              </Link>
            </Button>

            <Button
              variant="ghost"
              size="sm"
              className="absolute -top-2 -right-2 h-6 w-6 p-0 rounded-full bg-background border shadow-sm"
              onClick={handleDismiss}
            >
              <X className="h-3 w-3" />
            </Button>

            {/* Pulse effect */}
            <div className="absolute inset-0 rounded-full bg-primary/20 animate-ping -z-10" />
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
