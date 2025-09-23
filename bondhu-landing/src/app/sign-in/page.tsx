"use client"

import { useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { Eye, EyeOff, Loader2, MessageCircle, Shield, Heart, Zap } from "lucide-react"
import Link from "next/link"
import { motion } from "framer-motion"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { Logo } from "@/components/logo"
import { HeroBackground } from "@/components/sections/hero-background"
import { createClient } from "@/lib/supabase/client"
import { signInSchema, type SignInFormData } from "@/lib/auth/schemas"

export default function SignInPage() {
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const router = useRouter()
  const searchParams = useSearchParams()
  const redirectTo = searchParams.get('redirectTo') || '/dashboard'
  const supabase = createClient()

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch
  } = useForm<SignInFormData>({
    resolver: zodResolver(signInSchema)
  })

  const rememberMe = watch('remember_me')

  const onSubmit = async (data: SignInFormData) => {
    setIsLoading(true)
    setError(null)

    try {
      const { error: signInError } = await supabase.auth.signInWithPassword({
        email: data.email,
        password: data.password,
      })

      if (signInError) {
        throw signInError
      }

      router.push(redirectTo)
      router.refresh()
    } catch (err: unknown) {
      console.error('Sign in error:', err)
      const error = err as { message?: string }
      setError(
        error.message === 'Invalid login credentials'
          ? 'The email or password you entered is incorrect. Please try again.'
          : error.message || 'Something went wrong. Please try again.'
      )
    } finally {
      setIsLoading(false)
    }
  }

  const handleGoogleSignIn = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback?redirectTo=${encodeURIComponent(redirectTo)}`
        }
      })

      if (error) throw error
    } catch (err: unknown) {
      console.error('Google sign in error:', err)
      setError('Unable to sign in with Google. Please try again.')
      setIsLoading(false)
    }
  }

  const features = [
    {
      icon: MessageCircle,
      title: "Continue Your Conversations",
      description: "Pick up right where you left off with your AI companion"
    },
    {
      icon: Shield,
      title: "Secure & Private",
      description: "Your mental health data is encrypted and always confidential"
    },
    {
      icon: Heart,
      title: "Personalized Support",
      description: "AI that remembers your journey and adapts to your needs"
    },
    {
      icon: Zap,
      title: "Instant Access",
      description: "Get immediate support whenever you need someone to talk to"
    }
  ]

  const testimonials = [
    {
      text: "Bondhu remembers our conversations and helps me process my thoughts better each day.",
      author: "Arjun K.",
      location: "22, Delhi",
      avatar: "AK"
    },
    {
      text: "It's like having a friend who's always there when I need to talk through my feelings.",
      author: "Priya S.",
      location: "21, Mumbai",
      avatar: "PS"
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-secondary/20 relative overflow-hidden">
      {/* Background Animation */}
      <HeroBackground intensity="subtle" className="opacity-30" />
      
      <div className="relative z-10 min-h-screen flex flex-col lg:flex-row">
        {/* Left Panel - Branding and Content */}
        <div className="hidden lg:flex lg:w-3/5 p-6 xl:p-12 flex-col justify-between relative">
          {/* Logo Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="mb-8"
          >
            <Logo width={160} height={50} className="mb-8" />
          </motion.div>

          {/* Main Content */}
          <div className="flex-1 flex flex-col justify-center space-y-8 lg:space-y-12 max-w-2xl">
            {/* Header */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="space-y-4 lg:space-y-6"
            >
              <h1 className="text-3xl lg:text-4xl xl:text-5xl font-bold text-foreground tracking-tight leading-tight">
                Welcome back to Bondhu
              </h1>
              <p className="text-lg lg:text-xl text-muted-foreground leading-relaxed">
                Your AI companion is ready to continue your journey of growth and understanding
              </p>
            </motion.div>

            {/* Features Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="space-y-6 lg:space-y-8"
            >
              <h2 className="text-xl lg:text-2xl font-semibold text-foreground">
                Ready to reconnect?
              </h2>
              <div className="space-y-4 lg:space-y-6">
                {features.map((feature, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.6, delay: 0.6 + index * 0.1 }}
                    className="flex items-start space-x-3 lg:space-x-4"
                  >
                    <div className="flex-shrink-0 w-10 h-10 lg:w-12 lg:h-12 bg-primary/10 rounded-xl flex items-center justify-center">
                      <feature.icon className="w-5 h-5 lg:w-6 lg:h-6 text-primary" />
                    </div>
                    <div className="space-y-1">
                      <h3 className="font-semibold text-foreground text-sm lg:text-base">{feature.title}</h3>
                      <p className="text-muted-foreground leading-relaxed text-sm lg:text-base">{feature.description}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* Testimonials */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.8 }}
              className="space-y-6"
            >
              {testimonials.map((testimonial, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 1.0 + index * 0.2 }}
                  className="bg-card/80 backdrop-blur-sm rounded-xl p-6 border border-border/50 shadow-sm"
                >
                  <p className="text-foreground mb-4 italic leading-relaxed">
                    &quot;{testimonial.text}&quot;
                  </p>
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-primary">
                        {testimonial.avatar}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium text-foreground">{testimonial.author}</p>
                      <p className="text-sm text-muted-foreground">{testimonial.location}</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          </div>

          {/* Footer */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 1.2 }}
            className="text-muted-foreground text-sm"
          >
            © 2025 Bondhu. Empowering mental wellness through AI companionship.
          </motion.div>
        </div>

        {/* Right Panel - Form */}
        <div className="w-full lg:w-2/5 flex items-center justify-center p-6 sm:p-8 lg:p-12 bg-background/80 backdrop-blur-sm min-h-screen lg:min-h-auto border-l border-border/20">
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            className="w-full max-w-md space-y-6 lg:space-y-8"
          >
            {/* Mobile Logo */}
            <div className="lg:hidden text-center mb-6">
              <Logo width={120} height={40} className="sm:w-[140px] sm:h-[50px]" />
            </div>

            {/* Form Header */}
            <div className="text-center space-y-2">
              <h1 className="text-xl sm:text-2xl font-semibold text-foreground">Sign in to continue</h1>
              <p className="text-sm sm:text-base text-muted-foreground">
                Access your account and reconnect with your AI companion
              </p>
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-destructive/10 border border-destructive/20 text-destructive px-4 py-3 rounded-lg text-sm"
              >
                {error}
              </motion.div>
            )}

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5 lg:space-y-6">
              {/* Email Field */}
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium text-foreground">
                  Email address
                </label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter your email address"
                  {...register('email')}
                  error={errors.email?.message}
                  disabled={isLoading}
                  className="h-10 sm:h-11"
                />
              </div>

              {/* Password Field */}
              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium text-foreground">
                  Password
                </label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    {...register('password')}
                    error={errors.password?.message}
                    disabled={isLoading}
                    className="h-10 sm:h-11 pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                    disabled={isLoading}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              {/* Remember Me & Forgot Password */}
              <div className="flex items-center justify-between pt-2">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="remember_me"
                    checked={rememberMe || false}
                    onCheckedChange={(checked) => setValue('remember_me', checked as boolean)}
                    disabled={isLoading}
                    className="mt-0.5"
                  />
                  <label htmlFor="remember_me" className="text-sm text-foreground">
                    Remember me
                  </label>
                </div>
                <Link 
                  href="/forgot-password"
                  className="text-sm text-primary hover:underline font-medium"
                >
                  Forgot password?
                </Link>
              </div>

              {/* Submit Button */}
              <Button 
                type="submit" 
                className="w-full h-10 sm:h-11 bg-primary hover:bg-primary/90 text-primary-foreground font-medium"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  'Sign In'
                )}
              </Button>
            </form>

            {/* Divider */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-border" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground font-medium">OR CONTINUE WITH</span>
              </div>
            </div>

            {/* Google Sign In */}
            <Button
              variant="outline"
              className="w-full h-10 sm:h-11"
              onClick={handleGoogleSignIn}
              disabled={isLoading}
            >
              <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="currentColor"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="currentColor"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="currentColor"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              Continue with Google
            </Button>

            {/* Sign Up Link */}
            <p className="text-center text-sm text-muted-foreground">
              New to Bondhu?{" "}
              <Link href="/sign-up" className="text-primary hover:underline font-medium">
                Create an account
              </Link>
            </p>

            {/* Mobile Features Preview */}
            <div className="lg:hidden mt-8 pt-8 border-t border-border space-y-4">
              <h3 className="text-center text-lg font-semibold text-foreground mb-4">
                Welcome back!
              </h3>
              <div className="grid grid-cols-2 gap-4">
                {features.slice(0, 4).map((feature, index) => (
                  <div key={index} className="text-center space-y-2">
                    <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center mx-auto">
                      <feature.icon className="w-5 h-5 text-primary" />
                    </div>
                    <h4 className="text-xs font-medium text-foreground">{feature.title}</h4>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
