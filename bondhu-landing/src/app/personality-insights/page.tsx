"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { createClient } from "@/lib/supabase/client"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { ArrowLeft, User, RefreshCw, ChevronRight, Play } from "lucide-react"
import type { Profile } from "@/types/auth"
import { Logo } from "@/components/logo"
import { ThemeToggle } from "@/components/theme-toggle"
import Link from "next/link"
import { PersonalityRadarAdvanced } from "@/components/ui/personality-radar-advanced"

export default function PersonalityInsightsPage() {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()
  const supabase = createClient()

  useEffect(() => {
    const getProfile = async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser()

        if (!user) {
          router.push('/sign-in')
          return
        }

        const { data: profileData, error } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', user.id)
          .single()

        if (error) {
          console.error('Error fetching profile:', error)
          return
        }

        setProfile(profileData)
      } catch (error) {
        console.error('Error:', error)
      } finally {
        setIsLoading(false)
      }
    }

    getProfile()
  }, [supabase, router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Profile not found</h1>
          <Button onClick={() => router.push('/sign-in')}>
            Return to Sign In
          </Button>
        </div>
      </div>
    )
  }

  // Calculate profile completion based on available data
  const calculateProfileCompletion = () => {
    let completionScore = 0
    const maxScore = 100

    // Profile basic info (40 points)
    if (profile.full_name) completionScore += 20
    if (profile.avatar_url) completionScore += 20

    // Onboarding completed (20 points)
    if (profile.onboarding_completed) completionScore += 20

    // Personality assessment completed (40 points)
    if (profile.personality_data && Object.keys(profile.personality_data).length > 0) {
      completionScore += 40
    } else {
      // If no personality data but we're on this page, assume it's in progress
      completionScore += 20
    }

    return Math.min(completionScore, maxScore)
  }

  const profileCompletion = calculateProfileCompletion()

  // Mock personality data - in a real app, this would come from your AI analysis
  const personalityData = {
    traits: [
      { name: "Openness", score: 75, description: "Imagination, curiosity, artistic interests", color: "blue" },
      { name: "Conscientiousness", score: 68, description: "Organization, discipline, goal-orientation", color: "green" },
      { name: "Extraversion", score: 55, description: "Sociability, assertiveness, energy", color: "orange" },
      { name: "Agreeableness", score: 82, description: "Cooperation, trust, empathy", color: "purple" },
      { name: "Neuroticism", score: 45, description: "Emotional instability, anxiety, moodiness", color: "red" }
    ],
    topStrengths: [
      { name: "Agreeableness", score: 82 },
      { name: "Openness", score: 75 }
    ],
    growthOpportunities: [
      { name: "Extraversion", score: 55 },
      { name: "Conscientiousness", score: 68 }
    ],
    entertainmentInsights: {
      gamingCreativity: 70,
      videoFocus: 85,
      musicRegulation: 78,
      overallEngagement: 82
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-secondary/20">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            {/* Logo and Back Button */}
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" onClick={() => router.back()}>
                <ArrowLeft className="h-4 w-4 mr-1" />
                Back to Dashboard
              </Button>
              <Link href="/" className="flex items-center">
                <Logo width={140} height={50} />
              </Link>
              <div className="hidden sm:block">
                <h1 className="text-lg font-semibold text-muted-foreground">Personality Insights</h1>
              </div>
            </div>

            {/* Right Section */}
            <div className="flex items-center space-x-3">
              <ThemeToggle />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6 max-w-7xl">
        {/* Breadcrumb Navigation */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <button 
              onClick={() => router.push('/dashboard')}
              className="hover:text-foreground transition-colors"
            >
              Dashboard
            </button>
            <ChevronRight className="h-4 w-4" />
            <span className="text-foreground font-medium">Personality Insights</span>
          </div>
          <Button 
            variant="outline" 
            size="sm"
            className="flex items-center space-x-2"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Refresh Analysis</span>
          </Button>
        </div>

        {/* Hero Section */}
        <div className="mb-8">
          <Card className="bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-950/20 dark:to-teal-950/20 border-emerald-200 dark:border-emerald-800">
            <CardContent className="p-8">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-6">
                  <Avatar className="h-20 w-20 border-4 border-white shadow-lg">
                    <AvatarFallback className="text-2xl bg-gradient-to-br from-emerald-500 to-teal-500 text-white">
                      {profile.full_name?.split(' ').map(n => n[0]).join('') || 'U'}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                      {profile.full_name || 'Your'} Personality Profile
                    </h1>
                    <div className="flex items-center space-x-3">
                      <Badge variant="secondary" className="text-lg px-4 py-2 bg-emerald-100 text-emerald-800 dark:bg-emerald-800 dark:text-emerald-100">
                        🎨 The Creator
                      </Badge>
                      <span className="text-muted-foreground">Based on AI analysis</span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">
                    {profileCompletion}%
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Profile Completion
                  </div>
                  {profileCompletion < 100 && (
                    <div className="mt-2">
                      <div className="w-20 bg-gray-200 dark:bg-gray-700 rounded-full h-2 ml-auto">
                        <div 
                          className="bg-emerald-500 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${profileCompletion}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Profile Completion Info */}
        {profileCompletion < 100 && (
          <div className="mb-6">
            <Card className="bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800">
              <CardContent className="p-4">
                <div className="flex items-start space-x-3">
                  <div className="text-blue-500 mt-0.5">
                    💡
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200 mb-1">
                      Complete Your Profile ({profileCompletion}% done)
                    </h3>
                    <p className="text-xs text-blue-600 dark:text-blue-300">
                      {!profile.full_name && "Add your full name • "}
                      {!profile.avatar_url && "Upload a profile picture • "}
                      {!profile.onboarding_completed && "Complete onboarding • "}
                      {(!profile.personality_data || Object.keys(profile.personality_data).length === 0) && "Complete personality assessment • "}
                      Keep engaging with entertainment content to improve AI analysis accuracy.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Key Insights Row */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Card className="border-green-200 dark:border-green-800">
            <CardHeader className="pb-3">
              <CardTitle className="text-green-700 dark:text-green-300 flex items-center">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                Top Strengths
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {personalityData.topStrengths.map((strength) => (
                  <div key={strength.name} className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-950/20 rounded-lg">
                    <span className="font-medium text-green-800 dark:text-green-200">{strength.name}</span>
                    <Badge variant="secondary" className="bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100">
                      {strength.score}%
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="border-blue-200 dark:border-blue-800">
            <CardHeader className="pb-3">
              <CardTitle className="text-blue-700 dark:text-blue-300 flex items-center">
                <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
                Growth Opportunities
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {personalityData.growthOpportunities.map((opportunity) => (
                  <div key={opportunity.name} className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                    <span className="font-medium text-blue-800 dark:text-blue-200">{opportunity.name}</span>
                    <span className="text-sm text-blue-600 dark:text-blue-400">{opportunity.score}%</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          {/* Left Column - Detailed Analysis */}
          <div className="lg:col-span-3 space-y-6">


            {/* Entertainment Insights */}
            <Card className="border-purple-200 dark:border-purple-800">
              <CardHeader>
                <CardTitle className="flex items-center text-xl">
                  <Play className="h-6 w-6 mr-2 text-purple-500" />
                  Entertainment-Based Insights
                </CardTitle>
                <p className="text-sm text-muted-foreground">How your entertainment choices reflect your personality traits</p>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="text-center p-6 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950/20 dark:to-purple-900/20 rounded-xl border border-purple-200 dark:border-purple-800">
                    <div className="text-4xl font-bold text-purple-600 dark:text-purple-400 mb-2">
                      {personalityData.entertainmentInsights.gamingCreativity}%
                    </div>
                    <p className="text-sm font-semibold text-purple-700 dark:text-purple-300 mb-1">Gaming Creativity</p>
                    <p className="text-xs text-purple-600 dark:text-purple-400">Problem-solving skills</p>
                  </div>
                  <div className="text-center p-6 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950/20 dark:to-blue-900/20 rounded-xl border border-blue-200 dark:border-blue-800">
                    <div className="text-4xl font-bold text-blue-600 dark:text-blue-400 mb-2">
                      {personalityData.entertainmentInsights.videoFocus}%
                    </div>
                    <p className="text-sm font-semibold text-blue-700 dark:text-blue-300 mb-1">Video Focus</p>
                    <p className="text-xs text-blue-600 dark:text-blue-400">Attention span</p>
                  </div>
                  <div className="text-center p-6 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950/20 dark:to-green-900/20 rounded-xl border border-green-200 dark:border-green-800">
                    <div className="text-4xl font-bold text-green-600 dark:text-green-400 mb-2">
                      {personalityData.entertainmentInsights.musicRegulation}%
                    </div>
                    <p className="text-sm font-semibold text-green-700 dark:text-green-300 mb-1">Music Regulation</p>
                    <p className="text-xs text-green-600 dark:text-green-400">Emotional balance</p>
                  </div>
                  <div className="text-center p-6 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-950/20 dark:to-orange-900/20 rounded-xl border border-orange-200 dark:border-orange-800">
                    <div className="text-4xl font-bold text-orange-600 dark:text-orange-400 mb-2">
                      {personalityData.entertainmentInsights.overallEngagement}%
                    </div>
                    <p className="text-sm font-semibold text-orange-700 dark:text-orange-300 mb-1">Overall Engagement</p>
                    <p className="text-xs text-orange-600 dark:text-orange-400">Total interaction</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Detailed Trait Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">Big Five Personality Traits</CardTitle>
                <p className="text-sm text-muted-foreground">Detailed breakdown of your core personality dimensions</p>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {personalityData.traits.map((trait) => {
                    const isTopStrength = personalityData.topStrengths.some(s => s.name === trait.name)
                    const isGrowthArea = personalityData.growthOpportunities.some(g => g.name === trait.name)
                    
                    return (
                      <div key={trait.name} className={`p-4 rounded-lg border-l-4 ${
                        isTopStrength 
                          ? 'bg-green-50 dark:bg-green-950/20 border-l-green-500' 
                          : isGrowthArea 
                          ? 'bg-blue-50 dark:bg-blue-950/20 border-l-blue-500'
                          : 'bg-gray-50 dark:bg-gray-950/20 border-l-gray-400'
                      }`}>
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-3">
                            <div>
                              <h3 className={`text-lg font-semibold ${
                                isTopStrength 
                                  ? 'text-green-800 dark:text-green-200' 
                                  : isGrowthArea 
                                  ? 'text-blue-800 dark:text-blue-200'
                                  : 'text-gray-800 dark:text-gray-200'
                              }`}>
                                {trait.name}
                                {isTopStrength && (
                                  <Badge className="ml-2 bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100">
                                    💪 Top Strength
                                  </Badge>
                                )}
                                {isGrowthArea && (
                                  <Badge className="ml-2 bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100">
                                    🎯 Growth Area
                                  </Badge>
                                )}
                              </h3>
                              <p className="text-sm text-muted-foreground mt-1">{trait.description}</p>
                            </div>
                          </div>
                          <div className={`text-3xl font-bold ${
                            isTopStrength 
                              ? 'text-green-600 dark:text-green-400' 
                              : isGrowthArea 
                              ? 'text-blue-600 dark:text-blue-400'
                              : 'text-gray-600 dark:text-gray-400'
                          }`}>
                            {trait.score}%
                          </div>
                        </div>
                        <div className="w-full bg-muted rounded-full h-3">
                          <div
                            className={`h-3 rounded-full transition-all duration-700 ${
                              isTopStrength
                                ? 'bg-gradient-to-r from-green-400 to-green-600'
                                : isGrowthArea
                                ? 'bg-gradient-to-r from-blue-400 to-blue-600'
                                : trait.color === 'blue' ? 'bg-blue-500' :
                                  trait.color === 'green' ? 'bg-green-500' :
                                  trait.color === 'orange' ? 'bg-orange-500' :
                                  trait.color === 'purple' ? 'bg-purple-500' :
                                  'bg-red-500'
                            }`}
                            style={{ width: `${trait.score}%` }}
                          ></div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Radar Chart & Summary */}
          <div className="lg:col-span-2">
            <div className="sticky top-24 space-y-6">
              <PersonalityRadarAdvanced 
                personalityData={{
                  openness: 75,
                  conscientiousness: 68,
                  extraversion: 55,
                  agreeableness: 82,
                  neuroticism: 45
                }}
                entertainmentInsights={{
                  gaming_creativity: personalityData.entertainmentInsights.gamingCreativity,
                  video_attention_span: personalityData.entertainmentInsights.videoFocus,
                  music_emotional_regulation: personalityData.entertainmentInsights.musicRegulation,
                  overall_engagement: personalityData.entertainmentInsights.overallEngagement
                }}
              />
              
              {/* Quick Summary */}
              <Card className="bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/20 dark:to-teal-950/20">
                <CardHeader className="pb-3">
                  <CardTitle className="text-emerald-800 dark:text-emerald-200">Quick Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <p className="text-emerald-700 dark:text-emerald-300">
                      <strong>Personality Type:</strong> The Creator
                    </p>
                    <p className="text-muted-foreground">
                      High in creativity and cooperation, with strong potential for growth in social confidence and organization.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-center space-x-4 mt-8 pt-8 border-t">
          <Button onClick={() => router.push('/dashboard')} variant="outline" size="lg">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
          <Button size="lg" className="bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh AI Analysis
          </Button>
        </div>
      </main>
    </div>
  )
}