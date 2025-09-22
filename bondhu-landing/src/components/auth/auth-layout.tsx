"use client"

import { ReactNode } from "react"
import { motion } from "framer-motion"
import { Logo } from "@/components/logo"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"

interface Testimonial {
  text: string
  author: string
  avatar: string
}

interface AuthLayoutProps {
  children: ReactNode
  title: string
  subtitle: string
  testimonials: Testimonial[]
  trustIndicators?: string[]
  benefits?: string[]
  variant?: "sign-in" | "sign-up"
}

export function AuthLayout({
  children,
  title,
  subtitle,
  testimonials,
  trustIndicators = [],
  benefits = [],
  variant = "sign-in"
}: AuthLayoutProps) {
  const gradientDirection = variant === "sign-up" ? "bg-gradient-to-br" : "bg-gradient-to-bl"

  return (
    <div className="min-h-screen flex">
      {/* Left Panel - Branding */}
      <div className={`hidden lg:flex lg:w-1/2 ${gradientDirection} from-green-600 via-blue-600 to-purple-600 p-12 flex-col justify-between relative overflow-hidden`}>
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          {Array.from({ length: 20 }).map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-2 h-2 bg-white rounded-full"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
              }}
              animate={{
                scale: [1, 1.5, 1],
                opacity: [0.3, 0.8, 0.3],
              }}
              transition={{
                duration: 3 + Math.random() * 2,
                repeat: Infinity,
                delay: Math.random() * 2,
              }}
            />
          ))}
        </div>

        {/* Logo */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="relative z-10"
        >
          <div className="flex items-center space-x-3 text-white">
            <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
              <span className="text-xl font-bold">B</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold">Bondhu</h1>
              <p className="text-white/80 text-sm">বন্ধু</p>
            </div>
          </div>
        </motion.div>

        {/* Main Content */}
        <div className="relative z-10 space-y-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <h2 className="text-4xl font-bold text-white mb-4">{title}</h2>
            <p className="text-xl text-white/90 leading-relaxed">{subtitle}</p>
          </motion.div>

          {/* Trust Indicators or Benefits */}
          {(trustIndicators.length > 0 || benefits.length > 0) && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="space-y-3"
            >
              {trustIndicators.map((indicator, index) => (
                <div key={index} className="flex items-center space-x-3 text-white/90">
                  <div className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                    <span className="text-xs">✓</span>
                  </div>
                  <span className="text-sm">{indicator}</span>
                </div>
              ))}
              {benefits.map((benefit, index) => (
                <div key={index} className="flex items-center space-x-3 text-white/90">
                  <div className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                    <span className="text-xs">✓</span>
                  </div>
                  <span className="text-sm">{benefit}</span>
                </div>
              ))}
            </motion.div>
          )}

          {/* Testimonials */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="space-y-6"
          >
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
                <p className="text-white/90 mb-4 italic">&quot;{testimonial.text}&quot;</p>
                <div className="flex items-center space-x-3">
                  <Avatar className="w-10 h-10">
                    <AvatarFallback className="bg-white/20 text-white text-sm">
                      {testimonial.author.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="text-white font-medium text-sm">{testimonial.author}</p>
                  </div>
                </div>
              </div>
            ))}
          </motion.div>
        </div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="relative z-10 text-white/70 text-sm"
        >
          © 2025 Bondhu. Empowering mental wellness through AI companionship.
        </motion.div>
      </div>

      {/* Right Panel - Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-background">
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
          className="w-full max-w-md space-y-8"
        >
          {/* Mobile Logo */}
          <div className="lg:hidden text-center">
            <Logo width={120} height={40} />
          </div>

          {children}
        </motion.div>
      </div>
    </div>
  )
}
