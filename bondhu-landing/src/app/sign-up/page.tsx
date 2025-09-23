"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { Eye, EyeOff, Loader2, Brain, Shield, Heart, Zap } from "lucide-react"
import Link from "next/link"
import { motion } from "framer-motion"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { Logo } from "@/components/logo"
import { HeroBackground } from "@/components/sections/hero-background"
import { createClient } from "@/lib/supabase/client"
import { signUpSchema, type SignUpFormData } from "@/lib/auth/schemas"

export default function SignUpPage() {
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const router = useRouter()
  const supabase = createClient()

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch
  } = useForm<SignUpFormData>({
    resolver: zodResolver(signUpSchema)
  })

  const watchedValues = watch(['privacy_policy', 'terms_of_service', 'age_confirmation'])

  const onSubmit = async (data: SignUpFormData) => {
    setIsLoading(true)
    setError(null)

    try {
      // Sign up with Supabase
      const { data: authData, error: signUpError } = await supabase.auth.signUp({
        email: data.email,
        password: data.password,
        options: {
          data: {
            full_name: data.full_name,
          }
        }
      })

      if (signUpError) {
        throw signUpError
      }

      if (authData.user) {
        // Update or create profile record (use upsert to handle trigger-created profiles)
        const { error: profileError } = await supabase
          .from('profiles')
          .upsert({
            id: authData.user.id,
            full_name: data.full_name,
            onboarding_completed: false,
            personality_data: {}
          }, {
            onConflict: 'id'
          })

        if (profileError) {
          console.error('Profile creation error:', profileError)
          console.error('Profile error details:', JSON.stringify(profileError, null, 2))
          // Don't throw here, user is created, just continue
        } else {
          console.log('Profile created/updated successfully for user:', authData.user.id)
        }

        // Redirect to personality questionnaire
        router.push('/onboarding/personality')
        router.refresh()
      }
    } catch (err: unknown) {
      console.error('Sign up error:', err)
      const error = err as { message?: string }
      setError(
        error.message === 'User already registered'
          ? 'An account with this email already exists. Please sign in instead.'
          : error.message || 'Something went wrong. Please try again.'
      )
    } finally {
      setIsLoading(false)
    }
  }

  const handleGoogleSignUp = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback?redirectTo=${encodeURIComponent('/onboarding/personality')}`
        }
      })

      if (error) throw error
    } catch (err: unknown) {
      console.error('Google sign up error:', err)
      setError('Unable to sign up with Google. Please try again.')
      setIsLoading(false)
    }
  }

  const benefits = [
    {
      icon: Brain,
      title: "Personalized AI Companion",
      description: "AI that adapts to your unique personality and communication style"
    },
    {
      icon: Shield,
      title: "Privacy-First Approach",
      description: "Your conversations are encrypted and completely confidential"
    },
    {
      icon: Heart,
      title: "24/7 Emotional Support",
      description: "Always available when you need someone to talk to"
    },
    {
      icon: Zap,
      title: "Evidence-Based Methods",
      description: "Techniques backed by psychology research and mental health best practices"
    }
  ]

  const testimonials = [
    {
      text: "The personality assessment was surprisingly accurate. Bondhu really understands who I am.",
      author: "Sneha R.",
      location: "21, Bangalore",
      avatar: "SR"
    },
    {
      text: "Finally, an AI that doesn't feel robotic. It's like talking to a caring friend who gets me.",
      author: "Vikram M.",
      location: "23, Pune",
      avatar: "VM"
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
              <h1 className="text-3xl lg:text-4xl xl:text-5xl font-bold text-gray-900 tracking-tight leading-tight">
                Start your journey with Bondhu
              </h1>
              <p className="text-lg lg:text-xl text-muted-foreground leading-relaxed">
                Join thousands discovering better mental health through AI companionship
              </p>
            </motion.div>

            {/* Benefits Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="space-y-6 lg:space-y-8"
            >
              <h2 className="text-xl lg:text-2xl font-semibold text-gray-900">
                What makes Bondhu different?
              </h2>
              <div className="space-y-4 lg:space-y-6">
                {benefits.map((benefit, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.6, delay: 0.6 + index * 0.1 }}
                    className="flex items-start space-x-3 lg:space-x-4"
                  >
                    <div className="flex-shrink-0 w-10 h-10 lg:w-12 lg:h-12 bg-primary/10 rounded-xl flex items-center justify-center">
                      <benefit.icon className="w-5 h-5 lg:w-6 lg:h-6 text-primary" />
                    </div>
                    <div className="space-y-1">
                      <h3 className="font-semibold text-gray-900 text-sm lg:text-base">{benefit.title}</h3>
                      <p className="text-muted-foreground leading-relaxed text-sm lg:text-base">{benefit.description}</p>
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
                  className="bg-white/80 backdrop-blur-sm rounded-xl p-6 border border-gray-200/50 shadow-sm"
                >
                  <p className="text-gray-700 mb-4 italic leading-relaxed">
                    &quot;{testimonial.text}&quot;
                  </p>
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-primary">
                        {testimonial.avatar}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{testimonial.author}</p>
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
        <div className="w-full lg:w-2/5 flex items-center justify-center p-6 sm:p-8 lg:p-12 bg-white/80 backdrop-blur-sm min-h-screen lg:min-h-auto">
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
              <h1 className="text-xl sm:text-2xl font-semibold text-gray-900">Create your account</h1>
              <p className="text-sm sm:text-base text-muted-foreground">
                Begin your personalized mental health journey with AI support
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
              {/* Full Name Field */}
              <div className="space-y-2">
                <label htmlFor="full_name" className="text-sm font-medium text-gray-900">
                  Full name
                </label>
                <Input
                  id="full_name"
                  type="text"
                  placeholder="Enter your full name"
                  {...register('full_name')}
                  error={errors.full_name?.message}
                  disabled={isLoading}
                  className="h-10 sm:h-11"
                />
              </div>

              {/* Email Field */}
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium text-gray-900">
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
                <label htmlFor="password" className="text-sm font-medium text-gray-900">
                  Create password
                </label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Create a secure password"
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
                <p className="text-xs text-muted-foreground">
                  Minimum 8 characters with numbers and symbols
                </p>
              </div>

              {/* Consent Checkboxes */}
              <div className="space-y-4 pt-2">
                <div className="flex items-start space-x-3">
                  <Checkbox
                    id="privacy_policy"
                    checked={watchedValues[0] || false}
                    onCheckedChange={(checked) => setValue('privacy_policy', checked as boolean)}
                    disabled={isLoading}
                    className="mt-0.5"
                  />
                  <label htmlFor="privacy_policy" className="text-sm leading-5 text-gray-700">
                    I agree to Bondhu's{" "}
                    <Link href="/privacy" className="text-primary hover:underline font-medium" target="_blank">
                      Privacy Policy
                    </Link>
                  </label>
                </div>
                {errors.privacy_policy && (
                  <p className="text-xs text-destructive ml-6">{errors.privacy_policy.message}</p>
                )}

                <div className="flex items-start space-x-3">
                  <Checkbox
                    id="terms_of_service"
                    checked={watchedValues[1] || false}
                    onCheckedChange={(checked) => setValue('terms_of_service', checked as boolean)}
                    disabled={isLoading}
                    className="mt-0.5"
                  />
                  <label htmlFor="terms_of_service" className="text-sm leading-5 text-gray-700">
                    I accept the{" "}
                    <Link href="/terms" className="text-primary hover:underline font-medium" target="_blank">
                      Terms of Service
                    </Link>
                  </label>
                </div>
                {errors.terms_of_service && (
                  <p className="text-xs text-destructive ml-6">{errors.terms_of_service.message}</p>
                )}

                <div className="flex items-start space-x-3">
                  <Checkbox
                    id="age_confirmation"
                    checked={watchedValues[2] || false}
                    onCheckedChange={(checked) => setValue('age_confirmation', checked as boolean)}
                    disabled={isLoading}
                    className="mt-0.5"
                  />
                  <label htmlFor="age_confirmation" className="text-sm leading-5 text-gray-700">
                    I confirm I am 18 years or older
                  </label>
                </div>
                {errors.age_confirmation && (
                  <p className="text-xs text-destructive ml-6">{errors.age_confirmation.message}</p>
                )}
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
                    Creating account...
                  </>
                ) : (
                  'Create Account & Start Journey'
                )}
              </Button>
            </form>

            {/* Divider */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-gray-200" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-white px-2 text-muted-foreground font-medium">OR CONTINUE WITH</span>
              </div>
            </div>

            {/* Google Sign Up */}
            <Button
              variant="outline"
              className="w-full h-10 sm:h-11 border-gray-200 hover:bg-gray-50"
              onClick={handleGoogleSignUp}
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

            {/* Sign In Link */}
            <p className="text-center text-sm text-muted-foreground">
              Already have an account?{" "}
              <Link href="/sign-in" className="text-primary hover:underline font-medium">
                Sign in
              </Link>
            </p>

            {/* Mobile Benefits Preview */}
            <div className="lg:hidden mt-8 pt-8 border-t border-gray-200 space-y-4">
              <h3 className="text-center text-lg font-semibold text-gray-900 mb-4">
                Why choose Bondhu?
              </h3>
              <div className="grid grid-cols-2 gap-4">
                {benefits.slice(0, 4).map((benefit, index) => (
                  <div key={index} className="text-center space-y-2">
                    <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center mx-auto">
                      <benefit.icon className="w-5 h-5 text-primary" />
                    </div>
                    <h4 className="text-xs font-medium text-gray-900">{benefit.title}</h4>
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
