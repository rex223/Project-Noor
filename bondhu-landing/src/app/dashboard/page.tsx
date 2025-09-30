"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { createClient } from "@/lib/supabase/client"
import { useBondhuAPI } from "@/hooks/use-bondhu-api"
import { useAnalysisProgress } from "@/hooks/use-analysis-progress"
import ProgressTracking from "@/components/ui/progress-tracking"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Slider } from "@/components/ui/slider"
import { Progress } from "@/components/ui/progress"
import { User, Play, Heart, Sword, Shield, Zap, Volume2, TrendingUp, BarChart3, Camera, Headphones, Gamepad2, Pause, ChevronRight, ArrowLeft } from "lucide-react"
import Link from "next/link"
import type { Profile } from "@/types/auth"
import { Logo } from "@/components/logo"
import { ThemeToggle } from "@/components/theme-toggle"
import { HeroBackground } from "@/components/sections/hero-background"
import { DashboardStats } from "@/components/ui/dashboard-stats"
import { DashboardGrid } from "@/components/ui/dashboard-grid"
import { DashboardWelcome } from "@/components/ui/dashboard-welcome"
import { EnhancedChat } from "@/components/ui/enhanced-chat"
import { PuzzleMaster } from "@/components/games/PuzzleMaster"
import { MemoryPalace } from "@/components/games/MemoryPalace"
import { ColorSymphony } from "@/components/games/ColorSymphony"
import { useEntertainmentRecommendations } from "@/hooks/use-entertainment-recommendations"
import { VideoPlayer } from "@/components/video/VideoPlayer"
import { PersonalityRadarAdvanced } from "@/components/ui/personality-radar-advanced"
import { aiLearningEngine } from "@/lib/ai-learning-engine"
import { GlowingEffect } from "@/components/ui/glowing-effect"

export default function DashboardPage() {
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

  const handleSignOut = async () => {
    await supabase.auth.signOut()
    router.push('/')
    router.refresh()
  }

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-secondary/20 relative overflow-hidden">
      {/* Background Animation */}
      <HeroBackground intensity="subtle" className="opacity-30" />

      <div className="relative z-10">
        {/* Header */}
        <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex h-16 items-center justify-between">
              {/* Logo Section */}
              <div className="flex items-center space-x-4">
                <Link href="/" className="flex items-center">
                  <Logo width={140} height={50} />
                </Link>
                <div className="hidden sm:block">
                  <h1 className="text-lg font-semibold text-muted-foreground">Dashboard</h1>
                </div>
              </div>

              {/* Right Section */}
              <div className="flex items-center space-x-3">
                <ThemeToggle />
                <Avatar>
                  {profile.avatar_url && (
                    <AvatarImage
                      src={profile.avatar_url}
                      alt={profile.full_name || 'User avatar'}
                    />
                  )}
                  <AvatarFallback>
                    {profile.full_name?.split(' ').map(n => n[0]).join('') || 'U'}
                  </AvatarFallback>
                </Avatar>
                <div className="hidden md:block">
                  <p className="text-sm font-medium">{profile.full_name}</p>
                  <p className="text-xs text-muted-foreground">Level 1 Explorer</p>
                </div>
                <Button variant="outline" onClick={handleSignOut} size="sm">
                  Sign Out
                </Button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="container mx-auto px-4 py-6">
          {/* Compact Welcome Section */}
          <DashboardWelcome userName={profile.full_name?.split(' ')[0] || 'Friend'} compact={true} />

          {/* Main Dashboard Layout - 50% Chat + 50% Explore More */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-6">
            {/* Chat Section - 50% width */}
            <div>
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-2xl font-bold">Chat with Bondhu</h3>
                  <p className="text-muted-foreground">Your AI companion is ready to listen and support you</p>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="flex items-center space-x-1 text-sm text-muted-foreground">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                    <span>Online</span>
                  </div>
                </div>
              </div>
              <EnhancedChat profile={profile} />
            </div>

            {/* Right Column - Explore More + Your Progress */}
            <div className="space-y-8">
              {/* Explore More Section */}
              <div>
                <div className="mb-4">
                  <h3 className="text-xl font-bold">Explore More</h3>
                  <p className="text-sm text-muted-foreground">Discover features and tools for your mental wellness journey</p>
                </div>
                <DashboardGrid currentPage="dashboard" />
              </div>

              {/* Your Progress Section */}
              <div>
                <div className="mb-4">
                  <h3 className="text-xl font-bold">Your Progress</h3>
                  <p className="text-sm text-muted-foreground">Track your mental wellness journey</p>
                </div>
                <DashboardStats />
              </div>
            </div>
          </div>

        </main>
      </div>
    </div>
  )
}


// Entertainment Hub Component
function EntertainmentHub({ profile }: { profile: Profile }) {
  const { getEntertainmentRecommendations } = useBondhuAPI()
  const [quickRecommendations, setQuickRecommendations] = useState<any>(null)
  const [loadingRecommendations, setLoadingRecommendations] = useState(false)

  // Load quick recommendations
  useEffect(() => {
    const loadQuickRecs = async () => {
      if (!profile?.id) return

      setLoadingRecommendations(true)
      try {
        const recs = await getEntertainmentRecommendations(profile.id, {
          limit_per_category: 3,
          include_context: true
        })

        if (recs) {
          setQuickRecommendations(recs)
        }
      } catch (error) {
        console.error('Failed to load quick recommendations:', error)
      } finally {
        setLoadingRecommendations(false)
      }
    }

    loadQuickRecs()
  }, [profile?.id, getEntertainmentRecommendations])

  return (
    <div className="space-y-6">
      {/* Entertainment Navigation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Play className="h-5 w-5" />
              <span>Entertainment Hub</span>
            </div>
            <Link href="/entertainment">
              <Button variant="outline" size="sm">
                <ChevronRight className="h-4 w-4 mr-1" />
                View All
              </Button>
            </Link>
          </CardTitle>
          <p className="text-muted-foreground">
            AI-powered recommendations based on your personality profile
          </p>
        </CardHeader>
        <CardContent>
          {loadingRecommendations ? (
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-20 bg-muted rounded-lg"></div>
                  </div>
                ))}
              </div>
            </div>
          ) : quickRecommendations ? (
            <div className="space-y-6">
              {/* Quick Recommendations Overview */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {quickRecommendations.recommendations.music?.[0] && (
                  <div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Headphones className="h-4 w-4 text-purple-600" />
                      <Badge className="text-purple-600 bg-purple-100 dark:bg-purple-900/20">Music</Badge>
                    </div>
                    <h4 className="font-semibold mb-1 line-clamp-1">
                      {quickRecommendations.recommendations.music[0].title}
                    </h4>
                    {quickRecommendations.recommendations.music[0].artist && (
                      <p className="text-sm text-muted-foreground mb-2">
                        by {quickRecommendations.recommendations.music[0].artist}
                      </p>
                    )}
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {quickRecommendations.recommendations.music[0].reasoning}
                    </p>
                  </div>
                )}

                {quickRecommendations.recommendations.videos?.[0] && (
                  <div className="p-4 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/20 dark:to-cyan-950/20 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Camera className="h-4 w-4 text-blue-600" />
                      <Badge className="text-blue-600 bg-blue-100 dark:bg-blue-900/20">Video</Badge>
                    </div>
                    <h4 className="font-semibold mb-1 line-clamp-1">
                      {quickRecommendations.recommendations.videos[0].title}
                    </h4>
                    {quickRecommendations.recommendations.videos[0].creator && (
                      <p className="text-sm text-muted-foreground mb-2">
                        by {quickRecommendations.recommendations.videos[0].creator}
                      </p>
                    )}
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {quickRecommendations.recommendations.videos[0].reasoning}
                    </p>
                  </div>
                )}

                {quickRecommendations.recommendations.games?.[0] && (
                  <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/20 dark:to-emerald-950/20 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Gamepad2 className="h-4 w-4 text-green-600" />
                      <Badge className="text-green-600 bg-green-100 dark:bg-green-900/20">Game</Badge>
                    </div>
                    <h4 className="font-semibold mb-1 line-clamp-1">
                      {quickRecommendations.recommendations.games[0].title}
                    </h4>
                    {quickRecommendations.recommendations.games[0].developer && (
                      <p className="text-sm text-muted-foreground mb-2">
                        by {quickRecommendations.recommendations.games[0].developer}
                      </p>
                    )}
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {quickRecommendations.recommendations.games[0].reasoning}
                    </p>
                  </div>
                )}
              </div>

              {/* Context Information */}
              <div className="flex items-center justify-between text-sm text-muted-foreground border-t pt-4">
                <div className="flex items-center space-x-4">
                  <span>{Math.round(quickRecommendations.overall_confidence)}% match confidence</span>
                  <span>Generated {quickRecommendations.context.time_of_day}</span>
                </div>
                <Link href="/entertainment">
                  <Button variant="ghost" size="sm">
                    Explore More <ChevronRight className="h-3 w-3 ml-1" />
                  </Button>
                </Link>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <Play className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-muted-foreground mb-4">No recommendations available yet.</p>
              <p className="text-sm text-muted-foreground mb-4">
                Complete your personality analysis to get personalized entertainment suggestions.
              </p>
              <Link href="/entertainment">
                <Button variant="outline">
                  <Play className="h-4 w-4 mr-2" />
                  Explore Entertainment
                </Button>
              </Link>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )

  // Entertainment Statistics Component
  function EntertainmentStats({ entertainmentInsights }: {
    entertainmentInsights: any;
  }) {
    if (!entertainmentInsights?.stats) {
      return (
        <div className="text-center py-8">
          <p className="text-sm text-muted-foreground">No entertainment statistics available yet</p>
        </div>
      );
    }

    const { stats } = entertainmentInsights;

    return (
      <div className="grid grid-cols-3 gap-4">
        {/* Music Stats */}
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600 dark:text-green-400">
            {stats.musicInteractions || 0}
          </div>
          <p className="text-xs text-muted-foreground">Songs Played</p>
        </div>

        {/* Video Stats */}
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            {stats.videoInteractions || 0}
          </div>
          <p className="text-xs text-muted-foreground">Videos Watched</p>
        </div>

        {/* Game Stats */}
        <div className="text-center">
          <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
            {stats.gameInteractions || 0}
          </div>
          <p className="text-xs text-muted-foreground">Games Played</p>
        </div>
      </div>
    );
  }
}

// Gaming Section Component
function GamingSection({ profile }: { profile: Profile }) {
  const [selectedGame, setSelectedGame] = useState<string | null>(null)
  const [gameResults, setGameResults] = useState<any[]>([])

  const games = [
    {
      id: 'puzzle_master',
      name: 'Puzzle Master',
      category: 'Puzzle',
      description: 'Test your spatial reasoning and pattern recognition',
      icon: '🧩',
      difficulty: 'Medium',
      insights: ['Problem-solving approach', 'Spatial reasoning', 'Persistence patterns'],
      duration: '10-15 min',
      component: PuzzleMaster
    },
    {
      id: 'memory_palace',
      name: 'Memory Palace',
      category: 'Strategy',
      description: 'Enhance memory and strategic thinking',
      icon: '🧠',
      difficulty: 'Easy',
      insights: ['Memory patterns', 'Strategic planning', 'Attention to detail'],
      duration: '5-10 min',
      component: MemoryPalace
    },
    {
      id: 'color_symphony',
      name: 'Color Symphony',
      category: 'Creative',
      description: 'Express creativity through color and pattern',
      icon: '🎨',
      difficulty: 'Easy',
      insights: ['Creative expression', 'Aesthetic preferences', 'Emotional associations'],
      duration: '15-20 min',
      component: ColorSymphony
    }
  ]

  const handleGameComplete = (gameData: any) => {
    setGameResults(prev => [...prev, gameData])
    setSelectedGame(null)

    // Send data to AI learning engine
    aiLearningEngine.addGameplayData(gameData)

    // Here you would typically send the data to your analytics service
    console.log('Game completed:', gameData)

    // Show completion message or insights
    // You could integrate with Bondhu AI here to provide immediate feedback
  }

  const selectedGameData = games.find(game => game.id === selectedGame)

  if (selectedGame && selectedGameData) {
    const GameComponent = selectedGameData.component
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold">Playing: {selectedGameData.name}</h3>
          <Button variant="outline" onClick={() => setSelectedGame(null)}>
            Back to Games
          </Button>
        </div>
        <GameComponent onGameComplete={handleGameComplete} />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-4">
        {games.map((game) => (
          <Card key={game.id} className="p-4 hover:shadow-md transition-shadow cursor-pointer relative">
            <GlowingEffect disabled={false} proximity={150} spread={40} blur={2} />
            <div className="flex items-center justify-between relative z-10">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center text-2xl">
                  {game.icon}
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold">{game.name}</h4>
                  <p className="text-sm text-muted-foreground mb-2">{game.description}</p>
                  <div className="flex flex-wrap gap-1 mb-2">
                    {game.insights.map((insight, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {insight}
                      </Badge>
                    ))}
                  </div>
                  <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                    <span>Duration: {game.duration}</span>
                    <span>Difficulty: {game.difficulty}</span>
                  </div>
                </div>
              </div>
              <Button onClick={() => setSelectedGame(game.id)}>
                <Play className="h-4 w-4 mr-2" />
                Play
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {/* Recent Game Results */}
      {gameResults.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Recent Gaming Sessions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {gameResults.slice(-3).map((result, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-medium">{result.gameId}</span>
                    <Badge variant="secondary">{Math.round(result.completionRate)}% Complete</Badge>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-sm text-muted-foreground">
                    <span>Creativity: {Math.round(result.performance.creativity)}%</span>
                    <span>Speed: {Math.round(result.performance.speed)}%</span>
                    <span>Accuracy: {Math.round(result.performance.accuracy)}%</span>
                    <span>Mood: {result.emotionalState}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

// Video Section Component
function VideoSection({ profile }: { profile: Profile }) {
  const [selectedCategory, setSelectedCategory] = useState('mental_health')
  const [selectedVideo, setSelectedVideo] = useState<any | null>(null)
  const [watchHistory, setWatchHistory] = useState<any[]>([])

  const categories = [
    { id: 'mental_health', name: 'Wellness', icon: '🧘', color: 'bg-green-100 text-green-800' },
    { id: 'educational', name: 'Learning', icon: '📚', color: 'bg-blue-100 text-blue-800' },
    { id: 'entertainment', name: 'Fun', icon: '🎭', color: 'bg-purple-100 text-purple-800' }
  ]

  const videos = [
    {
      id: '1',
      title: '5-Minute Breathing Exercise',
      description: 'Learn powerful breathing techniques to manage stress and anxiety in your daily life.',
      category: 'mental_health',
      duration: 323, // 5:23 in seconds
      thumbnail: '🌿',
      url: '/videos/breathing-exercise.mp4', // Mock URL
      tags: ['breathing', 'anxiety', 'mindfulness', 'stress relief'],
      insights: ['Stress response', 'Mindfulness engagement', 'Focus duration']
    },
    {
      id: '2',
      title: 'Understanding Emotions',
      description: 'Explore the science behind emotions and learn healthy ways to process and express your feelings.',
      category: 'educational',
      duration: 765, // 12:45 in seconds
      thumbnail: '🧠',
      url: '/videos/understanding-emotions.mp4',
      tags: ['emotions', 'psychology', 'self-awareness', 'mental health'],
      insights: ['Learning style', 'Attention span', 'Concept retention']
    },
    {
      id: '3',
      title: 'Comedy Therapy Session',
      description: 'Discover how laughter can be medicine with this collection of therapeutic comedy content.',
      category: 'entertainment',
      duration: 510, // 8:30 in seconds
      thumbnail: '😄',
      url: '/videos/comedy-therapy.mp4',
      tags: ['humor', 'laughter therapy', 'positive psychology', 'mood boost'],
      insights: ['Humor preferences', 'Emotional response', 'Social content']
    },
    {
      id: '4',
      title: 'Meditation for Beginners',
      description: 'Start your meditation journey with simple, effective techniques for inner peace.',
      category: 'mental_health',
      duration: 900, // 15:00 in seconds
      thumbnail: '🧘‍♀️',
      url: '/videos/meditation-beginners.mp4',
      tags: ['meditation', 'mindfulness', 'relaxation', 'spiritual wellness'],
      insights: ['Attention span', 'Spiritual openness', 'Focus ability']
    },
    {
      id: '5',
      title: 'The Science of Happiness',
      description: 'Explore research-backed strategies for increasing life satisfaction and well-being.',
      category: 'educational',
      duration: 1020, // 17:00 in seconds
      thumbnail: '😊',
      url: '/videos/science-happiness.mp4',
      tags: ['happiness', 'positive psychology', 'well-being', 'research'],
      insights: ['Learning preferences', 'Scientific thinking', 'Optimism levels']
    },
    {
      id: '6',
      title: 'Creative Expression Workshop',
      description: 'Unlock your creative potential through guided artistic exercises and self-expression.',
      category: 'entertainment',
      duration: 1800, // 30:00 in seconds
      thumbnail: '🎨',
      url: '/videos/creative-workshop.mp4',
      tags: ['creativity', 'art therapy', 'self-expression', 'artistic'],
      insights: ['Creativity levels', 'Artistic preferences', 'Self-expression style']
    }
  ]

  const handleVideoComplete = (watchData: any) => {
    setWatchHistory(prev => [...prev, watchData])
    setSelectedVideo(null)

    // Send data to AI learning engine
    aiLearningEngine.addVideoData(watchData)

    // Here you would send analytics to your backend
    console.log('Video watch completed:', watchData)
  }

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (selectedVideo) {
    return (
      <VideoPlayer
        video={selectedVideo}
        onWatchComplete={handleVideoComplete}
        onClose={() => setSelectedVideo(null)}
      />
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2 mb-4">
        {categories.map((category) => (
          <Button
            key={category.id}
            variant={selectedCategory === category.id ? 'default' : 'outline'}
            onClick={() => setSelectedCategory(category.id)}
            size="sm"
          >
            <span className="mr-2">{category.icon}</span>
            {category.name}
          </Button>
        ))}
      </div>

      <div className="grid gap-4">
        {videos.filter(v => v.category === selectedCategory).map((video) => (
          <Card key={video.id} className="p-4 hover:shadow-md transition-shadow cursor-pointer relative">
            <GlowingEffect disabled={false} proximity={150} spread={40} blur={2} />
            <div className="flex items-center space-x-4 relative z-10">
              <div className="w-20 h-16 bg-gradient-to-r from-red-500 to-orange-500 rounded-lg flex items-center justify-center text-3xl flex-shrink-0">
                {video.thumbnail}
              </div>
              <div className="flex-1 min-w-0">
                <h4 className="font-medium text-lg mb-1">{video.title}</h4>
                <p className="text-sm text-muted-foreground mb-2 line-clamp-2">{video.description}</p>
                <div className="flex items-center space-x-4 text-sm text-muted-foreground mb-2">
                  <span>Duration: {formatDuration(video.duration)}</span>
                  <span>Category: {categories.find(c => c.id === video.category)?.name}</span>
                </div>
                <div className="flex flex-wrap gap-1 mb-2">
                  {video.tags.slice(0, 3).map((tag, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                  {video.tags.length > 3 && (
                    <Badge variant="outline" className="text-xs">
                      +{video.tags.length - 3} more
                    </Badge>
                  )}
                </div>
                <div className="flex flex-wrap gap-1">
                  <span className="text-xs text-muted-foreground mr-2">Learning insights:</span>
                  {video.insights.map((insight, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {insight}
                    </Badge>
                  ))}
                </div>
              </div>
              <Button onClick={() => setSelectedVideo(video)} className="flex-shrink-0">
                <Play className="h-4 w-4 mr-2" />
                Watch
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {/* Watch History */}
      {watchHistory.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Recent Viewing</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {watchHistory.slice(-3).map((history, index) => {
                const video = videos.find(v => v.id === history.contentId)
                return (
                  <div key={index} className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium">{video?.title}</span>
                      <Badge variant="secondary">{Math.round(history.completionRate)}% Watched</Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-sm text-muted-foreground">
                      <span>Watch time: {Math.round(history.watchTime)}s</span>
                      <span>Interactions: {history.interactions.length}</span>
                      <span>Skips: {history.skipPatterns.length}</span>
                      <span>Completion: {Math.round(history.completionRate)}%</span>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

// Music Section Component
function MusicSection({ profile }: { profile: Profile }) {
  const [selectedMood, setSelectedMood] = useState('')
  const [currentTrack, setCurrentTrack] = useState<any | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [listeningHistory, setListeningHistory] = useState<any[]>([])
  const [volume, setVolume] = useState(0.7)

  const moods = [
    {
      name: 'Focus',
      emoji: '🎯',
      color: 'bg-blue-100',
      description: 'Deep work and concentration',
      gradient: 'from-blue-500 to-cyan-500',
      hoverGradient: 'from-blue-600 to-cyan-600'
    },
    {
      name: 'Relax',
      emoji: '🌊',
      color: 'bg-green-100',
      description: 'Calm and peaceful',
      gradient: 'from-green-500 to-emerald-500',
      hoverGradient: 'from-green-600 to-emerald-600'
    },
    {
      name: 'Energy',
      emoji: '⚡',
      color: 'bg-orange-100',
      description: 'Upbeat and motivating',
      gradient: 'from-orange-500 to-red-500',
      hoverGradient: 'from-orange-600 to-red-600'
    },
    {
      name: 'Creative',
      emoji: '🎨',
      color: 'bg-purple-100',
      description: 'Inspiration and flow',
      gradient: 'from-purple-500 to-pink-500',
      hoverGradient: 'from-purple-600 to-pink-600'
    },
    {
      name: 'Social',
      emoji: '🎉',
      color: 'bg-pink-100',
      description: 'Social and uplifting',
      gradient: 'from-pink-500 to-rose-500',
      hoverGradient: 'from-pink-600 to-rose-600'
    },
    {
      name: 'Sleep',
      emoji: '😴',
      color: 'bg-indigo-100',
      description: 'Wind down and rest',
      gradient: 'from-indigo-500 to-purple-500',
      hoverGradient: 'from-indigo-600 to-purple-600'
    }
  ]

  const playlists = [
    {
      id: 1,
      name: 'Deep Focus Flow',
      mood: 'Focus',
      tracks: 24,
      duration: '1h 45m',
      cover: '🎵',
      genre: 'Ambient',
      insights: ['Concentration patterns', 'Productivity preferences', 'Attention sustainability'],
      tracks_list: [
        { id: 1, title: 'Concentrated Mind', artist: 'Focus Collective', duration: 240 },
        { id: 2, title: 'Deep Work Mode', artist: 'Productivity Sounds', duration: 300 },
        { id: 3, title: 'Mental Clarity', artist: 'Study Beats', duration: 280 }
      ]
    },
    {
      id: 2,
      name: 'Calm Waves',
      mood: 'Relax',
      tracks: 18,
      duration: '1h 12m',
      cover: '🌙',
      genre: 'Nature Sounds',
      insights: ['Relaxation style', 'Stress relief patterns', 'Evening preferences'],
      tracks_list: [
        { id: 4, title: 'Ocean Breeze', artist: 'Nature Collective', duration: 360 },
        { id: 5, title: 'Peaceful Mind', artist: 'Relaxation Masters', duration: 420 },
        { id: 6, title: 'Gentle Rain', artist: 'Calm Sounds', duration: 300 }
      ]
    },
    {
      id: 3,
      name: 'Creative Spark',
      mood: 'Creative',
      tracks: 20,
      duration: '1h 30m',
      cover: '✨',
      genre: 'Instrumental',
      insights: ['Creative thinking', 'Artistic inspiration', 'Flow state enhancement'],
      tracks_list: [
        { id: 7, title: 'Artistic Vision', artist: 'Creative Minds', duration: 270 },
        { id: 8, title: 'Innovation Flow', artist: 'Inspiration Hub', duration: 315 },
        { id: 9, title: 'Creative Energy', artist: 'Art Sounds', duration: 290 }
      ]
    },
    {
      id: 4,
      name: 'Energy Boost',
      mood: 'Energy',
      tracks: 15,
      duration: '1h 0m',
      cover: '🔥',
      genre: 'Upbeat',
      insights: ['Energy levels', 'Motivation patterns', 'Activity preferences'],
      tracks_list: [
        { id: 10, title: 'Power Up', artist: 'Energy Collective', duration: 210 },
        { id: 11, title: 'High Vibes', artist: 'Motivation Music', duration: 240 },
        { id: 12, title: 'Peak Performance', artist: 'Energy Sounds', duration: 225 }
      ]
    }
  ]

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const playTrack = (track: any, playlist: any) => {
    setCurrentTrack({ ...track, playlist: playlist.name, mood: playlist.mood })
    setIsPlaying(true)
    setCurrentTime(0)

    // Track listening analytics
    const listeningData = {
      trackId: track.id,
      userId: 'current_user',
      sessionId: Math.random().toString(36).substr(2, 9),
      playTime: 0,
      totalDuration: track.duration,
      skipTime: undefined,
      repeatCount: 0,
      volume: volume,
      mood_context: playlist.mood,
      activity_context: 'entertainment',
      social_context: 'alone' as const
    }

    // Send to AI learning engine
    aiLearningEngine.addMusicData(listeningData)

    setListeningHistory(prev => [...prev, {
      trackId: track.id,
      sessionId: listeningData.sessionId,
      startTime: new Date(),
      mood: playlist.mood,
      playlistId: playlist.id
    }])
  }

  const togglePlayPause = () => {
    setIsPlaying(!isPlaying)
  }

  // Simulate track progress
  useEffect(() => {
    let interval: NodeJS.Timeout
    if (isPlaying && currentTrack) {
      interval = setInterval(() => {
        setCurrentTime(prev => {
          if (prev >= currentTrack.duration) {
            setIsPlaying(false)
            return 0
          }
          return prev + 1
        })
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [isPlaying, currentTrack])

  return (
    <div className="space-y-6">
      {/* Mood Selection */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
        {moods.map((mood) => (
          <div
            key={mood.name}
            onClick={() => setSelectedMood(mood.name)}
            className={`
              relative overflow-hidden rounded-xl p-6 cursor-pointer transition-all duration-300 ease-in-out transform hover:scale-[1.02] group
              ${selectedMood === mood.name
                ? `bg-gradient-to-br ${mood.gradient} text-white shadow-md dark:shadow-lg shadow-${mood.gradient.split('-')[1]}-500/20 dark:shadow-${mood.gradient.split('-')[1]}-500/10`
                : 'bg-white dark:bg-card hover:bg-gray-50/50 dark:hover:bg-card/80 border border-gray-200/60 dark:border-border/40 hover:border-gray-300/80 dark:hover:border-border/60'
              }
            `}
          >
            <GlowingEffect disabled={false} proximity={120} spread={35} blur={1.5} />
            {/* Background gradient overlay for selected state */}
            {selectedMood === mood.name && (
              <div className={`absolute inset-0 bg-gradient-to-br ${mood.hoverGradient} opacity-0 group-hover:opacity-100 transition-opacity duration-300`} />
            )}

            {/* Content */}
            <div className="relative z-10 flex flex-col items-center text-center space-y-2">
              <div className={`
                text-3xl mb-1 transition-transform duration-300 group-hover:scale-105
                ${selectedMood === mood.name ? 'drop-shadow-sm' : ''}
              `}>
                {mood.emoji}
              </div>
              <h3 className={`
                font-semibold text-sm 
                ${selectedMood === mood.name
                  ? 'text-white'
                  : 'text-gray-900 dark:text-gray-100'
                }
              `}>
                {mood.name}
              </h3>
              <p className={`
                text-xs leading-tight
                ${selectedMood === mood.name
                  ? 'text-white/80'
                  : 'text-gray-500 dark:text-gray-400'
                }
              `}>
                {mood.description}
              </p>
            </div>

            {/* Shine effect for unselected buttons */}
            {selectedMood !== mood.name && (
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                <div className={`absolute inset-0 bg-gradient-to-r ${mood.gradient} opacity-5 dark:opacity-10`} />
                <div className="absolute -inset-x-full h-full bg-gradient-to-r from-transparent via-white/20 dark:via-white/10 to-transparent transform -skew-x-12 animate-shine" />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Current Player */}
      {currentTrack && (
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center text-2xl">
                🎵
              </div>
              <div className="flex-1">
                <h4 className="font-medium">{currentTrack.title}</h4>
                <p className="text-sm text-muted-foreground">{currentTrack.artist}</p>
                <p className="text-xs text-muted-foreground">
                  {currentTrack.playlist} • {currentTrack.mood} Mood
                </p>
              </div>
              <div className="flex items-center space-x-4">
                <Button size="sm" onClick={togglePlayPause}>
                  {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                </Button>
                <div className="flex items-center space-x-2">
                  <Volume2 className="h-4 w-4" />
                  <div className="w-16">
                    <Slider
                      value={[volume]}
                      max={1}
                      step={0.1}
                      onValueChange={([val]: number[]) => setVolume(val)}
                    />
                  </div>
                </div>
              </div>
            </div>
            <div className="mt-4">
              <div className="flex justify-between text-sm text-muted-foreground mb-1">
                <span>{formatTime(currentTime)}</span>
                <span>{formatTime(currentTrack.duration)}</span>
              </div>
              <Slider
                value={[currentTime]}
                max={currentTrack.duration}
                step={1}
                onValueChange={([time]: number[]) => setCurrentTime(time)}
                className="w-full"
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Playlists */}
      {selectedMood && (
        <div className="space-y-4">
          <h3 className="font-semibold text-lg">
            {selectedMood} Playlists
          </h3>
          {playlists.filter(p => p.mood === selectedMood).map((playlist) => (
            <Card key={playlist.id} className="overflow-hidden relative">
              <GlowingEffect disabled={false} proximity={150} spread={40} blur={2} />
              <CardHeader className="pb-3 relative z-10">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="w-16 h-16 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-lg flex items-center justify-center text-3xl">
                      {playlist.cover}
                    </div>
                    <div>
                      <CardTitle className="text-lg">{playlist.name}</CardTitle>
                      <p className="text-sm text-muted-foreground">
                        {playlist.tracks} tracks • {playlist.duration} • {playlist.genre}
                      </p>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {playlist.insights.map((insight, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {insight}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                  <Button onClick={() => playTrack(playlist.tracks_list[0], playlist)}>
                    <Play className="h-4 w-4 mr-2" />
                    Play All
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="pt-0 relative z-10">
                <div className="space-y-2">
                  {playlist.tracks_list.slice(0, 3).map((track, index) => (
                    <div
                      key={track.id}
                      className="flex items-center justify-between p-2 hover:bg-gray-50/50 dark:hover:bg-card/60 rounded cursor-pointer transition-colors duration-200"
                      onClick={() => playTrack(track, playlist)}
                    >
                      <div className="flex items-center space-x-3">
                        <span className="text-sm text-muted-foreground w-6">{index + 1}</span>
                        <div>
                          <p className="text-sm font-medium">{track.title}</p>
                          <p className="text-xs text-muted-foreground">{track.artist}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs text-muted-foreground">
                          {formatTime(track.duration)}
                        </span>
                        <Button size="sm" variant="ghost">
                          <Play className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  ))}
                  {playlist.tracks_list.length > 3 && (
                    <p className="text-sm text-muted-foreground text-center pt-2">
                      +{playlist.tracks_list.length - 3} more tracks
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* No mood selected */}
      {!selectedMood && (
        <div className="text-center py-8">
          <h3 className="text-lg font-medium mb-2">Choose Your Mood</h3>
          <p className="text-muted-foreground">
            Select a mood above to discover personalized playlists that match your current state of mind.
          </p>
        </div>
      )}

      {/* Listening Analytics */}
      {listeningHistory.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Recent Listening</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {listeningHistory.slice(-3).map((history, index) => {
                const track = playlists
                  .flatMap(p => p.tracks_list)
                  .find(t => t.id === history.trackId)
                return (
                  <div key={index} className="p-3 bg-gray-50/50 dark:bg-card/40 rounded-lg border border-gray-200/40 dark:border-border/20">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium">{track?.title}</span>
                      <Badge variant="secondary">{history.mood} Mood</Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-sm text-muted-foreground">
                      <span>Artist: {track?.artist}</span>
                      <span>Duration: {track ? formatTime(track.duration) : 'N/A'}</span>
                      <span>Started: {new Date(history.startTime).toLocaleTimeString()}</span>
                      <span>Playlist ID: {history.playlistId}</span>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Learning Insights */}
      <div className="text-xs text-muted-foreground space-y-1 p-3 bg-gray-50/50 dark:bg-card/40 rounded-lg border border-gray-200/40 dark:border-border/20">
        <p className="font-medium">Music Learning Insights:</p>
        <p>• Mood-based listening preferences and patterns</p>
        <p>• Genre exploration and musical taste development</p>
        <p>• Emotional regulation through music selection</p>
        <p>• Focus and productivity correlation with specific sounds</p>
        {selectedMood && <p>• Current preference: {selectedMood} mood exploration</p>}
      </div>
    </div>
  )
}

// Profile Dashboard Component
function ProfileDashboard({ profile }: { profile: Profile }) {
  const [aiInsights, setAiInsights] = useState<any>(null)
  const [refreshKey, setRefreshKey] = useState(0)
  const [realPersonalityData, setRealPersonalityData] = useState<any>(null)

  const { analyzePersonality, getAnalysisStatus, getPersonalityProfile, isLoading: apiLoading } = useBondhuAPI()

  // Enhanced progress tracking for analysis
  const progressTracker = useAnalysisProgress({
    pollInterval: 2000, // Poll every 2 seconds
    maxRetries: 5,
    onComplete: (result) => {
      console.log('✅ Dashboard analysis completed:', result)
      // Refresh insights with new data
      setRefreshKey(prev => prev + 1)
    },
    onError: (error) => {
      console.error('❌ Dashboard analysis error:', error)
    },
    onStepUpdate: (step) => {
      console.log('📊 Dashboard step update:', step.name, `${step.progress}%`)
    }
  })

  // Get AI insights
  useEffect(() => {
    const insights = aiLearningEngine.getLatestInsights()
    setAiInsights(insights)
  }, [refreshKey])

  // Refresh insights periodically
  useEffect(() => {
    const interval = setInterval(() => {
      setRefreshKey(prev => prev + 1)
    }, 30000) // Refresh every 30 seconds

    return () => clearInterval(interval)
  }, [])

  const triggerPersonalityAnalysis = async () => {
    if (!profile?.id || progressTracker.isTracking) return

    try {
      console.log('🚀 Triggering comprehensive personality analysis...')

      const response = await analyzePersonality({
        user_id: profile.id,
        requested_agents: ['music', 'video', 'gaming'],
        force_refresh: true,
        include_cross_modal: true,
        survey_responses: {}, // Could include any additional survey data
        conversation_history: [] // Could include chat history
      })

      if (response.analysis_id) {
        console.log('📈 Analysis started:', response.analysis_id)

        // Start enhanced progress tracking
        progressTracker.startTracking(response.analysis_id)
      }

    } catch (error) {
      console.error('❌ Analysis trigger error:', error)
      progressTracker.resetProgress()
    }
  }



  // Load real personality data
  useEffect(() => {
    const loadPersonalityData = async () => {
      if (!profile?.id || realPersonalityData) return

      try {
        console.log('📊 Loading dashboard personality data...')
        const response = await getPersonalityProfile(profile.id)

        if (response && response.scores) {
          const transformedData = {
            openness: Math.round(response.scores.openness.score),
            conscientiousness: Math.round(response.scores.conscientiousness.score),
            extraversion: Math.round(response.scores.extraversion.score),
            agreeableness: Math.round(response.scores.agreeableness.score),
            neuroticism: Math.round(response.scores.neuroticism.score),
            overall_confidence: response.overall_confidence,
            data_sources: response.data_sources
          }
          setRealPersonalityData(transformedData)
          console.log('✅ Dashboard personality data loaded')
        }
      } catch (error) {
        console.warn('⚠️ Could not load personality data, using mock data:', error)
      }
    }

    loadPersonalityData()
  }, [profile?.id])

  // Use real personality data if available, otherwise fall back to mock
  const personalityData = realPersonalityData || aiInsights?.bigFive || {
    openness: 75,
    conscientiousness: 68,
    extraversion: 55,
    agreeableness: 82,
    neuroticism: 45
  }

  const entertainmentInsights = aiInsights ? {
    gaming_creativity: aiInsights.entertainmentProfile.gaming.creativityScore,
    video_attention_span: Math.round(aiInsights.entertainmentProfile.video.attentionSpan / 6), // Convert to percentage
    music_emotional_regulation: aiInsights.entertainmentProfile.music.listeningBehavior.focus_music_preference,
    overall_engagement: Math.round((
      aiInsights.entertainmentProfile.gaming.persistenceLevel +
      aiInsights.entertainmentProfile.video.engagementPatterns.completionRate +
      aiInsights.entertainmentProfile.music.listeningBehavior.active_listening
    ) / 3)
  } : {
    gaming_creativity: 70,
    video_attention_span: 85,
    music_emotional_regulation: 78,
    overall_engagement: 82
  }

  return (
    <div className="space-y-6">
      {/* Advanced Personality Overview */}
      <PersonalityRadarAdvanced
        personalityData={personalityData}
        entertainmentInsights={entertainmentInsights}
      />

      {/* AI-Generated Cross-Modal Insights */}
      {aiInsights?.crossModalInsights && aiInsights.crossModalInsights.length > 0 && (
        <Card className="relative">
          <GlowingEffect disabled={false} proximity={150} spread={40} blur={2} />
          <CardHeader className="relative z-10">
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5" />
              <span>AI-Generated Insights</span>
            </CardTitle>
            <p className="text-muted-foreground">
              Cross-modal analysis of your entertainment behavior patterns
            </p>
          </CardHeader>
          <CardContent className="relative z-10">
            <div className="space-y-4">
              {aiInsights.crossModalInsights.map((insight: any, index: number) => (
                <div key={index} className="p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-purple-900">{insight.type.charAt(0).toUpperCase() + insight.type.slice(1)} Discovery</h4>
                    <Badge variant="secondary">{insight.confidence}% Confidence</Badge>
                  </div>
                  <p className="text-sm text-purple-800 mb-2">{insight.description}</p>
                  <p className="text-xs text-purple-600 font-medium">💡 {insight.actionableInsight}</p>
                  <div className="flex gap-1 mt-2">
                    {insight.dataSources.map((source: string) => (
                      <Badge key={source} variant="outline" className="text-xs">
                        {source}
                      </Badge>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Entertainment Behavior Analysis */}
      {aiInsights?.entertainmentProfile && (
        <div className="grid md:grid-cols-3 gap-6">
          {/* Gaming Analysis */}
          <Card className="relative">
            <GlowingEffect disabled={false} proximity={150} spread={40} blur={2} />
            <CardHeader className="relative z-10">
              <CardTitle className="text-lg">Gaming Personality</CardTitle>
            </CardHeader>
            <CardContent className="relative z-10">
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm">Problem Solving Style</span>
                  <Badge variant="secondary">{aiInsights.entertainmentProfile.gaming.problemSolvingStyle}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Creativity</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 h-2 bg-gray-200 rounded-full">
                      <div
                        className="h-2 bg-purple-500 rounded-full"
                        style={{ width: `${aiInsights.entertainmentProfile.gaming.creativityScore}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium">{aiInsights.entertainmentProfile.gaming.creativityScore}%</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Persistence</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 h-2 bg-gray-200 rounded-full">
                      <div
                        className="h-2 bg-blue-500 rounded-full"
                        style={{ width: `${aiInsights.entertainmentProfile.gaming.persistenceLevel}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium">{aiInsights.entertainmentProfile.gaming.persistenceLevel}%</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Challenge Preference</span>
                  <Badge variant="outline">{aiInsights.entertainmentProfile.gaming.challengePreference}</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Video Analysis */}
          <Card className="relative">
            <GlowingEffect disabled={false} proximity={150} spread={40} blur={2} />
            <CardHeader className="relative z-10">
              <CardTitle className="text-lg">Viewing Behavior</CardTitle>
            </CardHeader>
            <CardContent className="relative z-10">
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm">Attention Span</span>
                  <span className="text-sm font-medium">{Math.round(aiInsights.entertainmentProfile.video.attentionSpan / 60)}m avg</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Completion Rate</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 h-2 bg-gray-200 rounded-full">
                      <div
                        className="h-2 bg-green-500 rounded-full"
                        style={{ width: `${aiInsights.entertainmentProfile.video.engagementPatterns.completionRate}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium">{Math.round(aiInsights.entertainmentProfile.video.engagementPatterns.completionRate)}%</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Learning Style</span>
                  <Badge variant="secondary">{aiInsights.entertainmentProfile.video.learningStyle}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Skip Tendency</span>
                  <Badge variant="outline">{Math.round(aiInsights.entertainmentProfile.video.engagementPatterns.skipTendency)}%</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Music Analysis */}
          <Card className="relative">
            <GlowingEffect disabled={false} proximity={150} spread={40} blur={2} />
            <CardHeader className="relative z-10">
              <CardTitle className="text-lg">Music Personality</CardTitle>
            </CardHeader>
            <CardContent className="relative z-10">
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm">Regulation Style</span>
                  <Badge variant="secondary">{aiInsights.entertainmentProfile.music.moodRegulationStyle}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Focus Preference</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 h-2 bg-gray-200 rounded-full">
                      <div
                        className="h-2 bg-orange-500 rounded-full"
                        style={{ width: `${aiInsights.entertainmentProfile.music.listeningBehavior.focus_music_preference}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium">{aiInsights.entertainmentProfile.music.listeningBehavior.focus_music_preference}%</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Musical Sophistication</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 h-2 bg-gray-200 rounded-full">
                      <div
                        className="h-2 bg-indigo-500 rounded-full"
                        style={{ width: `${aiInsights.entertainmentProfile.music.musicalSophistication}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium">{aiInsights.entertainmentProfile.music.musicalSophistication}%</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Social Listening</span>
                  <Badge variant="outline">{aiInsights.entertainmentProfile.music.socialListeningPreference}%</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* AI Recommendations */}
      {aiInsights?.recommendations && (
        <Card className="relative">
          <GlowingEffect disabled={false} proximity={150} spread={40} blur={2} />
          <CardHeader className="relative z-10">
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5" />
              <span>Personalized AI Recommendations</span>
            </CardTitle>
            <p className="text-muted-foreground">
              Based on comprehensive analysis of your entertainment patterns
            </p>
          </CardHeader>
          <CardContent className="relative z-10">
            <div className="grid md:grid-cols-2 gap-4">
              {/* Game Recommendations */}
              {aiInsights.recommendations.games.length > 0 && (
                <div className="space-y-3">
                  <h4 className="font-medium text-purple-900">🎮 Game Suggestions</h4>
                  {aiInsights.recommendations.games.map((rec: any, index: number) => (
                    <div key={index} className="p-3 bg-purple-50 rounded-lg border border-purple-200">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium text-purple-900">{rec.gameId.replace('_', ' ')}</span>
                        <Badge variant="secondary">{rec.personalityMatch}% Match</Badge>
                      </div>
                      <p className="text-sm text-purple-800">{rec.reason}</p>
                      <p className="text-xs text-purple-600 mt-1">✨ {rec.expectedBenefit}</p>
                    </div>
                  ))}
                </div>
              )}

              {/* Activity Recommendations */}
              {aiInsights.recommendations.activities.length > 0 && (
                <div className="space-y-3">
                  <h4 className="font-medium text-green-900">🌱 Growth Activities</h4>
                  {aiInsights.recommendations.activities.map((rec: any, index: number) => (
                    <div key={index} className="p-3 bg-green-50 rounded-lg border border-green-200">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium text-green-900">{rec.activity}</span>
                        <Badge variant="outline">{rec.estimatedDuration}</Badge>
                      </div>
                      <p className="text-sm text-green-800">{rec.description}</p>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {rec.personalityBenefits.slice(0, 2).map((benefit: string, i: number) => (
                          <span key={i} className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                            {benefit}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Personality Trends */}
      {aiInsights?.trends && (
        <Card className="relative">
          <GlowingEffect disabled={false} proximity={150} spread={40} blur={2} />
          <CardHeader className="relative z-10">
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5" />
              <span>Personality Evolution</span>
            </CardTitle>
            <p className="text-muted-foreground">
              How your personality traits are evolving through entertainment choices
            </p>
          </CardHeader>
          <CardContent className="relative z-10">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium mb-3">Trait Trends</h4>
                <div className="space-y-2">
                  {aiInsights.trends.traits.map((trend: any, index: number) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <span className="text-sm font-medium capitalize">{trend.trait}</span>
                      <div className="flex items-center space-x-2">
                        <span className={`text-sm ${trend.trend === 'increasing' ? 'text-green-600' :
                          trend.trend === 'decreasing' ? 'text-red-600' : 'text-gray-600'
                          }`}>
                          {trend.trend === 'increasing' ? '↗️' : trend.trend === 'decreasing' ? '↘️' : '➡️'}
                          {trend.trend}
                        </span>
                        <Badge variant="outline">{trend.confidence}%</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-3">Entertainment Evolution</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span className="text-sm">🎮 Gaming</span>
                    <Badge variant="secondary">{aiInsights.trends.entertainmentEvolution.gaming.replace('_', ' ')}</Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span className="text-sm">📺 Video</span>
                    <Badge variant="secondary">{aiInsights.trends.entertainmentEvolution.video.replace('_', ' ')}</Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span className="text-sm">🎵 Music</span>
                    <Badge variant="secondary">{aiInsights.trends.entertainmentEvolution.music.replace('_', ' ')}</Badge>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Analysis Controls */}
      <div className="flex flex-col items-center space-y-4">
        {progressTracker.isTracking ? (
          <ProgressTracking
            analysisId={progressTracker.analysisId}
            overallProgress={progressTracker.overallProgress}
            currentStep={progressTracker.currentStep}
            steps={progressTracker.steps}
            status={progressTracker.status}
            startTime={progressTracker.startTime}
            estimatedDuration={300} // 5 minutes
            onCancel={() => {
              progressTracker.stopTracking()
            }}
            onRetry={() => {
              progressTracker.resetProgress()
              triggerPersonalityAnalysis()
            }}
            showDetails={false} // Compact view for dashboard
            compact={true}
          />
        ) : (
          <Button
            onClick={triggerPersonalityAnalysis}
            variant="outline"
            className="flex items-center space-x-2"
            disabled={!profile?.id || apiLoading}
          >
            <TrendingUp className="h-4 w-4" />
            <span>Run Full AI Analysis</span>
          </Button>
        )}
      </div>
    </div>
  )
}

// Simple Personality Radar Chart Component
function PersonalityRadarChart({ profile }: { profile: Profile }) {
  const traits = [
    { name: 'Openness', score: 75, color: 'text-blue-600' },
    { name: 'Conscientiousness', score: 68, color: 'text-green-600' },
    { name: 'Extraversion', score: 55, color: 'text-orange-600' },
    { name: 'Agreeableness', score: 82, color: 'text-purple-600' },
    { name: 'Neuroticism', score: 45, color: 'text-red-600' }
  ]

  return (
    <div className="grid md:grid-cols-2 gap-6">
      <div className="space-y-4">
        {traits.map((trait) => (
          <div key={trait.name} className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">{trait.name}</span>
              <span className={`text-sm font-bold ${trait.color}`}>{trait.score}%</span>
            </div>
            <div className="w-full h-3 bg-gray-200 rounded-full">
              <div
                className={`h-3 rounded-full ${trait.color.replace('text-', 'bg-')}`}
                style={{ width: `${trait.score}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
      <div className="flex items-center justify-center">
        <div className="text-center">
          <div className="w-32 h-32 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center mb-4">
            <span className="text-white text-lg font-bold">Your Profile</span>
          </div>
          <p className="text-sm text-muted-foreground">
            Balanced Creative Explorer
          </p>
        </div>
      </div>
    </div>
  )
}

