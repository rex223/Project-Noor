"use client"

import { useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { Eye, EyeOff, Loader2 } from "lucide-react"
import Link from "next/link"

import { AuthLayout } from "@/components/auth/auth-layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
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

  const testimonials = [
    {
      text: "Bondhu remembers our conversations and helps me process my thoughts better each day.",
      author: "Arjun K., 22, Delhi",
      avatar: "AK"
    },
    {
      text: "It's like having a friend who's always there when I need to talk through my feelings.",
      author: "Priya S., 21, Mumbai",
      avatar: "PS"
    }
  ]

  const trustIndicators = [
    "🔒 Your conversations are private and encrypted",
    "🧠 AI that adapts to your unique personality", 
    "💚 24/7 emotional support when you need it"
  ]

  return (
    <AuthLayout
      title="Welcome back to Bondhu"
      subtitle="Your AI companion is ready to continue your journey of growth and understanding"
      testimonials={testimonials}
      trustIndicators={trustIndicators}
      variant="sign-in"
    >
      <div className="space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-bold">Sign in to continue</h1>
          <p className="text-muted-foreground">
            Access your account and reconnect with your AI companion
          </p>
        </div>

        {error && (
          <div className="bg-destructive/10 border border-destructive/20 text-destructive px-4 py-3 rounded-md text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="email" className="text-sm font-medium">
              Email address
            </label>
            <Input
              id="email"
              type="email"
              placeholder="your@email.com"
              {...register('email')}
              error={errors.email?.message}
              disabled={isLoading}
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="password" className="text-sm font-medium">
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
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                disabled={isLoading}
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="remember_me"
                checked={rememberMe || false}
                onCheckedChange={(checked) => setValue('remember_me', checked as boolean)}
                disabled={isLoading}
              />
              <label htmlFor="remember_me" className="text-sm">
                Remember me
              </label>
            </div>
            <Link 
              href="/forgot-password"
              className="text-sm text-primary hover:underline"
            >
              Forgot password?
            </Link>
          </div>

          <Button 
            type="submit" 
            className="w-full" 
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

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-background px-2 text-muted-foreground">Or continue with</span>
          </div>
        </div>

        <Button
          variant="outline"
          className="w-full"
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

        <p className="text-center text-sm text-muted-foreground">
          New to Bondhu?{" "}
          <Link href="/sign-up" className="text-primary hover:underline font-medium">
            Create an account
          </Link>
        </p>
      </div>
    </AuthLayout>
  )
}
