"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { createClient } from "@/lib/supabase/client"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Slider } from "@/components/ui/slider"
import { Progress } from "@/components/ui/progress"
import { MessageCircle, User, Settings, Play, Send, Mic, Heart, Sword, Shield, Zap, Volume2, TrendingUp, BarChart3, Camera, Headphones, Gamepad2, Pause } from "lucide-react"
import type { Profile } from "@/types/auth"
import { Logo } from "@/components/logo"
import { ThemeToggle } from "@/components/theme-toggle"
import { HeroBackground } from "@/components/sections/hero-background"
import { DashboardStats } from "@/components/ui/dashboard-stats"
import { DashboardGrid } from "@/components/ui/dashboard-grid"
import { DashboardWelcome } from "@/components/ui/dashboard-welcome"
import { EnhancedChat } from "@/components/ui/enhanced-chat"
import Link from "next/link"
import { PuzzleMaster } from "@/components/games/PuzzleMaster"
import { MemoryPalace } from "@/components/games/MemoryPalace"
import { ColorSymphony } from "@/components/games/ColorSymphony"
import { VideoPlayer } from "@/components/video/VideoPlayer"
import { PersonalityRadarAdvanced } from "@/components/ui/personality-radar-advanced"
import { aiLearningEngine } from "@/lib/ai-learning-engine"

export default function DashboardPage() {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [activeSection, setActiveSection] = useState('chat')
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
              <DashboardGrid 
                onSectionChange={setActiveSection}
                activeSection={activeSection}
              />
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

        {/* Additional Dashboard Tabs - Now Secondary */}
        <Tabs value={activeSection} onValueChange={setActiveSection} className="w-full">
          <TabsList className="grid w-full grid-cols-4 mb-8 h-12">
            <TabsTrigger value="chat" className="flex items-center justify-center gap-1 sm:gap-2 px-2 sm:px-4 py-2">
              <MessageCircle className="h-4 w-4" />
              <span className="text-xs sm:text-sm font-medium">Chat</span>
            </TabsTrigger>
            <TabsTrigger value="entertainment" className="flex items-center justify-center gap-1 sm:gap-2 px-2 sm:px-4 py-2">
              <Play className="h-4 w-4" />
              <span className="text-xs sm:text-sm font-medium">Entertainment</span>
            </TabsTrigger>
            <TabsTrigger value="profile" className="flex items-center justify-center gap-1 sm:gap-2 px-2 sm:px-4 py-2">
              <User className="h-4 w-4" />
              <span className="text-xs sm:text-sm font-medium">Profile</span>
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center justify-center gap-1 sm:gap-2 px-2 sm:px-4 py-2">
              <Settings className="h-4 w-4" />
              <span className="text-xs sm:text-sm font-medium">Settings</span>
            </TabsTrigger>
          </TabsList>

          {/* Chat Tab */}
          <TabsContent value="chat" className="space-y-6">
            <div className="text-center py-12 bg-muted/30 rounded-xl border border-dashed border-border">
              <MessageCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">Main Chat Above</h3>
              <p className="text-muted-foreground max-w-md mx-auto">
                Your primary chat with Bondhu is featured above for easy access. 
                Scroll up to continue your conversation with your AI companion.
              </p>
              <Button 
                onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                className="mt-4"
                variant="outline"
              >
                Go to Chat
              </Button>
            </div>
          </TabsContent>

          {/* Entertainment Tab */}
          <TabsContent value="entertainment" className="space-y-6">
            <EntertainmentHub profile={profile} />
          </TabsContent>

          {/* Profile Tab */}
          <TabsContent value="profile" className="space-y-6">
            <ProfileDashboard profile={profile} />
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings" className="space-y-6">
            <SettingsPanel profile={profile} />
          </TabsContent>
        </Tabs>
      </main>
      </div>
    </div>
  )
}

// Chat Interface Component
function ChatInterface({ profile }: { profile: Profile }) {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'bondhu',
      message: `Hello ${profile.full_name?.split(' ')[0] || 'Friend'}! I'm Bondhu, your AI companion. I've reviewed your personality profile and I'm excited to support you on your journey. How are you feeling today? 🌟`,
      timestamp: new Date().toLocaleTimeString(),
    }
  ])
  const [newMessage, setNewMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)

  const sendMessage = async () => {
    if (!newMessage.trim()) return

    const userMessage = {
      id: Date.now(),
      sender: 'user',
      message: newMessage,
      timestamp: new Date().toLocaleTimeString(),
    }

    setMessages(prev => [...prev, userMessage])
    setNewMessage('')
    setIsTyping(true)

    // Simulate AI response with personalized content
    setTimeout(() => {
      const personalizedResponses = [
        `I appreciate you sharing that with me, ${profile.full_name?.split(' ')[0]}. Based on your personality profile, I can see this relates to your goals. Tell me more about how this makes you feel.`,
        "That's really insightful! I can sense the depth in your thoughts. What aspects of this situation feel most important to you right now?",
        "I'm here to listen and support you through this. Your journey matters to me, and I want to help you navigate these feelings.",
        "Thank you for trusting me with your thoughts. What emotions are coming up for you as we discuss this?",
        "I can hear that this matters to you deeply. Let's explore this together - you're not alone in this."
      ]

      const aiMessage = {
        id: Date.now() + 1,
        sender: 'bondhu',
        message: personalizedResponses[Math.floor(Math.random() * personalizedResponses.length)],
        timestamp: new Date().toLocaleTimeString(),
      }

      setMessages(prev => [...prev, aiMessage])
      setIsTyping(false)
    }, 1000 + Math.random() * 2000)
  }

  const quickMessages = [
    "How are you feeling today?",
    "I need some motivation",
    "Let's talk about my goals",
    "I'm feeling anxious",
    "Tell me something positive"
  ]

  return (
    <div className="grid lg:grid-cols-3 gap-6">
      {/* Main Chat */}
      <div className="lg:col-span-2">
        <Card className="h-[600px] flex flex-col">
          <CardHeader className="border-b">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center">
                  <Heart className="h-5 w-5 text-white" />
                </div>
                <div>
                  <CardTitle>Bondhu AI Companion</CardTitle>
                  <p className="text-sm text-muted-foreground">Always here for you</p>
                </div>
              </div>
              <Badge variant="secondary" className="bg-green-100 text-green-800">
                Online
              </Badge>
            </div>
          </CardHeader>

          <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${msg.sender === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                    }`}
                >
                  <p className="text-sm">{msg.message}</p>
                  <p className="text-xs opacity-70 mt-1">{msg.timestamp}</p>
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-muted px-4 py-2 rounded-lg">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
          </CardContent>

          <div className="p-4 border-t">
            <div className="flex space-x-2">
              <Input
                placeholder="Type your message..."
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                className="flex-1"
              />
              <Button onClick={sendMessage} size="icon">
                <Send className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="icon">
                <Mic className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </Card>
      </div>

      {/* Quick Actions & Profile */}
      <div className="space-y-6">
        {/* Quick Messages */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Quick Start</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {quickMessages.map((msg, index) => (
              <Button
                key={index}
                variant="outline"
                size="sm"
                className="w-full justify-start text-xs"
                onClick={() => setNewMessage(msg)}
              >
                {msg}
              </Button>
            ))}
          </CardContent>
        </Card>

        {/* Personality Insights */}
        {profile.personality_data && (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Your Goals</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {(profile.personality_data as any).mental_health_goals?.slice(0, 3).map((goal: string, index: number) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    {goal}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

// Entertainment Hub Component
function EntertainmentHub({ profile }: { profile: Profile }) {
  const [activeSection, setActiveSection] = useState('games')
  const [currentMood, setCurrentMood] = useState('')

  return (
    <div className="space-y-6">
      {/* Entertainment Navigation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Play className="h-5 w-5" />
            <span>Entertainment Hub</span>
          </CardTitle>
          <p className="text-muted-foreground">
            Explore games, videos, and music while Bondhu learns about your personality
          </p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4 mb-6">
            <Button
              variant={activeSection === 'games' ? 'default' : 'outline'}
              onClick={() => setActiveSection('games')}
              className="h-16 flex flex-col space-y-1"
            >
              <Gamepad2 className="h-6 w-6" />
              <span className="text-sm">Games</span>
            </Button>
            <Button
              variant={activeSection === 'videos' ? 'default' : 'outline'}
              onClick={() => setActiveSection('videos')}
              className="h-16 flex flex-col space-y-1"
            >
              <Camera className="h-6 w-6" />
              <span className="text-sm">Videos</span>
            </Button>
            <Button
              variant={activeSection === 'music' ? 'default' : 'outline'}
              onClick={() => setActiveSection('music')}
              className="h-16 flex flex-col space-y-1"
            >
              <Headphones className="h-6 w-6" />
              <span className="text-sm">Music</span>
            </Button>
          </div>

          {/* Dynamic Content Area */}
          {activeSection === 'games' && <GamingSection profile={profile} />}
          {activeSection === 'videos' && <VideoSection profile={profile} />}
          {activeSection === 'music' && <MusicSection profile={profile} />}
        </CardContent>
      </Card>
    </div>
  )
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
          <Card key={game.id} className="p-4 hover:shadow-md transition-shadow cursor-pointer">
            <div className="flex items-center justify-between">
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
          <Card key={video.id} className="p-4 hover:shadow-md transition-shadow cursor-pointer">
            <div className="flex items-center space-x-4">
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
              relative overflow-hidden rounded-xl p-6 cursor-pointer transition-all duration-300 ease-in-out transform hover:scale-105 group
              ${selectedMood === mood.name 
                ? `bg-gradient-to-br ${mood.gradient} text-white shadow-lg shadow-${mood.gradient.split('-')[1]}-500/25` 
                : 'bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-700'
              }
            `}
          >
            {/* Background gradient overlay for selected state */}
            {selectedMood === mood.name && (
              <div className={`absolute inset-0 bg-gradient-to-br ${mood.hoverGradient} opacity-0 group-hover:opacity-100 transition-opacity duration-300`} />
            )}
            
            {/* Content */}
            <div className="relative z-10 flex flex-col items-center text-center space-y-2">
              <div className={`
                text-3xl mb-1 transition-transform duration-300 group-hover:scale-110
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
                <div className={`absolute inset-0 bg-gradient-to-r ${mood.gradient} opacity-5`} />
                <div className="absolute -inset-x-full h-full bg-gradient-to-r from-transparent via-white/20 to-transparent transform -skew-x-12 animate-shine" />
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
            <Card key={playlist.id} className="overflow-hidden">
              <CardHeader className="pb-3">
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
              <CardContent className="pt-0">
                <div className="space-y-2">
                  {playlist.tracks_list.slice(0, 3).map((track, index) => (
                    <div
                      key={track.id}
                      className="flex items-center justify-between p-2 hover:bg-gray-50 rounded cursor-pointer"
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
                  <div key={index} className="p-3 bg-gray-50 rounded-lg">
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
      <div className="text-xs text-muted-foreground space-y-1 p-3 bg-gray-50 rounded-lg">
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

  // Mock personality data - in real app this would come from profile
  const personalityData = aiInsights?.bigFive || {
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
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5" />
              <span>AI-Generated Insights</span>
            </CardTitle>
            <p className="text-muted-foreground">
              Cross-modal analysis of your entertainment behavior patterns
            </p>
          </CardHeader>
          <CardContent>
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
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Gaming Personality</CardTitle>
            </CardHeader>
            <CardContent>
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
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Viewing Behavior</CardTitle>
            </CardHeader>
            <CardContent>
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
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Music Personality</CardTitle>
            </CardHeader>
            <CardContent>
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
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5" />
              <span>Personalized AI Recommendations</span>
            </CardTitle>
            <p className="text-muted-foreground">
              Based on comprehensive analysis of your entertainment patterns
            </p>
          </CardHeader>
          <CardContent>
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
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5" />
              <span>Personality Evolution</span>
            </CardTitle>
            <p className="text-muted-foreground">
              How your personality traits are evolving through entertainment choices
            </p>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium mb-3">Trait Trends</h4>
                <div className="space-y-2">
                  {aiInsights.trends.traits.map((trend: any, index: number) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <span className="text-sm font-medium capitalize">{trend.trait}</span>
                      <div className="flex items-center space-x-2">
                        <span className={`text-sm ${
                          trend.trend === 'increasing' ? 'text-green-600' : 
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

      {/* Manual Refresh */}
      <div className="flex justify-center">
        <Button 
          onClick={() => setRefreshKey(prev => prev + 1)}
          variant="outline"
          className="flex items-center space-x-2"
        >
          <TrendingUp className="h-4 w-4" />
          <span>Refresh AI Analysis</span>
        </Button>
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

// Settings Panel Component
function SettingsPanel({ profile }: { profile: Profile }) {
  const [dataSettings, setDataSettings] = useState({
    gamingData: true,
    videoData: true,
    musicData: true,
    personalityAnalytics: true,
    aiRecommendations: true,
    crossModalInsights: true,
    dataRetention: 365, // days
    shareAnonymized: false,
    exportFormat: 'json'
  })

  const [exportStatus, setExportStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [deleteStatus, setDeleteStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')

  const handleSettingChange = (setting: string, value: boolean | number | string) => {
    setDataSettings(prev => ({ ...prev, [setting]: value }))
    // In real app, this would sync with backend
    console.log('Updated setting:', setting, value)
  }

  const handleExportData = async () => {
    setExportStatus('loading')
    try {
      // Get all data from AI learning engine
      const exportData = aiLearningEngine.exportForExternalAnalysis()
      
      // Add user profile data
      const fullExport = {
        profile: {
          id: profile.id,
          full_name: profile.full_name,
          created_at: profile.created_at,
          personality_data: profile.personality_data
        },
        entertainmentData: exportData,
        settings: dataSettings,
        exportDate: new Date().toISOString()
      }

      // Create and download file
      const blob = new Blob([JSON.stringify(fullExport, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `bondhu-data-export-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      setExportStatus('success')
      setTimeout(() => setExportStatus('idle'), 3000)
    } catch (error) {
      console.error('Export failed:', error)
      setExportStatus('error')
      setTimeout(() => setExportStatus('idle'), 3000)
    }
  }

  const handleDeleteData = async (dataType: 'gaming' | 'video' | 'music' | 'all') => {
    if (!confirm(`Are you sure you want to delete all ${dataType} data? This action cannot be undone.`)) {
      return
    }

    setDeleteStatus('loading')
    try {
      // In real app, this would call backend API
      console.log('Deleting data type:', dataType)
      
      // For demo, we'll clear the AI learning engine data
      if (dataType === 'all') {
        // Would reset the entire learning engine
        console.log('All entertainment data deleted')
      }

      setDeleteStatus('success')
      setTimeout(() => setDeleteStatus('idle'), 3000)
    } catch (error) {
      console.error('Delete failed:', error)
      setDeleteStatus('error')
      setTimeout(() => setDeleteStatus('idle'), 3000)
    }
  }

  return (
    <div className="space-y-6">
      {/* Privacy Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Settings className="h-5 w-5" />
            <span>Privacy & Data Controls</span>
          </CardTitle>
          <p className="text-muted-foreground">
            Manage how Bondhu collects and uses your data for personalization
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* Entertainment Data Collection */}
            <div>
              <h4 className="font-medium mb-4">Entertainment Data Collection</h4>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="font-medium">Gaming Analytics</h5>
                    <p className="text-sm text-muted-foreground">Track game choices, performance, and playing patterns</p>
                  </div>
                  <Button
                    variant={dataSettings.gamingData ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleSettingChange('gamingData', !dataSettings.gamingData)}
                  >
                    {dataSettings.gamingData ? 'Enabled' : 'Disabled'}
                  </Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="font-medium">Video Viewing Analytics</h5>
                    <p className="text-sm text-muted-foreground">Monitor watch time, completion rates, and content preferences</p>
                  </div>
                  <Button
                    variant={dataSettings.videoData ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleSettingChange('videoData', !dataSettings.videoData)}
                  >
                    {dataSettings.videoData ? 'Enabled' : 'Disabled'}
                  </Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="font-medium">Music Listening Analytics</h5>
                    <p className="text-sm text-muted-foreground">Analyze listening habits, mood patterns, and genre preferences</p>
                  </div>
                  <Button
                    variant={dataSettings.musicData ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleSettingChange('musicData', !dataSettings.musicData)}
                  >
                    {dataSettings.musicData ? 'Enabled' : 'Disabled'}
                  </Button>
                </div>
              </div>
            </div>

            {/* AI Features */}
            <div>
              <h4 className="font-medium mb-4">AI Features</h4>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="font-medium">Personality Analytics</h5>
                    <p className="text-sm text-muted-foreground">Generate Big Five personality insights from behavior patterns</p>
                  </div>
                  <Button
                    variant={dataSettings.personalityAnalytics ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleSettingChange('personalityAnalytics', !dataSettings.personalityAnalytics)}
                  >
                    {dataSettings.personalityAnalytics ? 'Enabled' : 'Disabled'}
                  </Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="font-medium">AI Recommendations</h5>
                    <p className="text-sm text-muted-foreground">Receive personalized content and activity suggestions</p>
                  </div>
                  <Button
                    variant={dataSettings.aiRecommendations ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleSettingChange('aiRecommendations', !dataSettings.aiRecommendations)}
                  >
                    {dataSettings.aiRecommendations ? 'Enabled' : 'Disabled'}
                  </Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="font-medium">Cross-Modal Insights</h5>
                    <p className="text-sm text-muted-foreground">Analyze patterns across different entertainment types</p>
                  </div>
                  <Button
                    variant={dataSettings.crossModalInsights ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleSettingChange('crossModalInsights', !dataSettings.crossModalInsights)}
                  >
                    {dataSettings.crossModalInsights ? 'Enabled' : 'Disabled'}
                  </Button>
                </div>
              </div>
            </div>

            {/* Data Retention */}
            <div>
              <h4 className="font-medium mb-4">Data Retention</h4>
              <div className="space-y-3">
                <div>
                  <label className="text-sm font-medium">Keep my data for:</label>
                  <select
                    value={dataSettings.dataRetention}
                    onChange={(e) => handleSettingChange('dataRetention', Number(e.target.value))}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                  >
                    <option value={30}>30 days</option>
                    <option value={90}>3 months</option>
                    <option value={180}>6 months</option>
                    <option value={365}>1 year</option>
                    <option value={730}>2 years</option>
                    <option value={-1}>Until I delete it</option>
                  </select>
                </div>
                <p className="text-xs text-muted-foreground">
                  Data older than this will be automatically deleted. Analysis and insights will be preserved.
                </p>
              </div>
            </div>

            {/* Anonymized Sharing */}
            <div className="flex items-center justify-between">
              <div>
                <h5 className="font-medium">Contribute to Research</h5>
                <p className="text-sm text-muted-foreground">Share anonymized data to improve mental health AI research</p>
              </div>
              <Button
                variant={dataSettings.shareAnonymized ? "default" : "outline"}
                size="sm"
                onClick={() => handleSettingChange('shareAnonymized', !dataSettings.shareAnonymized)}
              >
                {dataSettings.shareAnonymized ? 'Contributing' : 'Not Contributing'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Data Management */}
      <Card>
        <CardHeader>
          <CardTitle>Data Management & Export</CardTitle>
          <p className="text-muted-foreground">
            Download, view, or delete your personal data
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Export Data */}
            <div className="p-4 border rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h4 className="font-medium">Export Your Data</h4>
                  <p className="text-sm text-muted-foreground">
                    Download all your data in JSON format
                  </p>
                </div>
                <Button 
                  onClick={handleExportData}
                  disabled={exportStatus === 'loading'}
                  className="flex items-center space-x-2"
                >
                  {exportStatus === 'loading' && <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>}
                  <span>
                    {exportStatus === 'loading' ? 'Exporting...' : 
                     exportStatus === 'success' ? 'Exported!' : 
                     exportStatus === 'error' ? 'Error' : 'Export Data'}
                  </span>
                </Button>
              </div>
              <div className="text-xs text-muted-foreground space-y-1">
                <p>• Includes: Profile, entertainment data, analytics, preferences</p>
                <p>• Format: JSON file compatible with data portability standards</p>
                <p>• Privacy: Your personal data only, no other users' information</p>
              </div>
            </div>

            {/* View Data Usage */}
            <div className="p-4 border rounded-lg">
              <h4 className="font-medium mb-3">Data Usage Summary</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Entertainment Sessions:</span>
                  <span className="font-medium ml-2">47</span>
                </div>
                <div>
                  <span className="text-muted-foreground">AI Insights Generated:</span>
                  <span className="font-medium ml-2">23</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Games Played:</span>
                  <span className="font-medium ml-2">12</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Videos Watched:</span>
                  <span className="font-medium ml-2">8</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Music Sessions:</span>
                  <span className="font-medium ml-2">27</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Total Data Size:</span>
                  <span className="font-medium ml-2">2.3 MB</span>
                </div>
              </div>
            </div>

            {/* Delete Specific Data */}
            <div className="p-4 border border-red-200 rounded-lg">
              <h4 className="font-medium text-red-900 mb-3">Delete Specific Data</h4>
              <div className="grid gap-3">
                <Button 
                  variant="outline" 
                  className="w-full justify-start text-red-600 hover:text-red-700 border-red-200 hover:border-red-300"
                  onClick={() => handleDeleteData('gaming')}
                  disabled={deleteStatus === 'loading'}
                >
                  Delete Gaming Data
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start text-red-600 hover:text-red-700 border-red-200 hover:border-red-300"
                  onClick={() => handleDeleteData('video')}
                  disabled={deleteStatus === 'loading'}
                >
                  Delete Video Data
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start text-red-600 hover:text-red-700 border-red-200 hover:border-red-300"
                  onClick={() => handleDeleteData('music')}
                  disabled={deleteStatus === 'loading'}
                >
                  Delete Music Data
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start text-red-600 hover:text-red-700 border-red-200 hover:border-red-300"
                  onClick={() => handleDeleteData('all')}
                  disabled={deleteStatus === 'loading'}
                >
                  Delete All Entertainment Data
                </Button>
              </div>
              <p className="text-xs text-red-600 mt-3">
                Warning: Deleted data cannot be recovered. Your personality insights will be preserved.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Account Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Account Settings</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Account Status</h4>
                <p className="text-sm text-muted-foreground">Active since {new Date(profile.created_at).toLocaleDateString()}</p>
              </div>
              <Badge variant="secondary">Active</Badge>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Email Notifications</h4>
                <p className="text-sm text-muted-foreground">Weekly insights and recommendations</p>
              </div>
              <Button variant="outline" size="sm">Configure</Button>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Two-Factor Authentication</h4>
                <p className="text-sm text-muted-foreground">Additional security for your account</p>
              </div>
              <Button variant="outline" size="sm">Enable</Button>
            </div>

            <div className="pt-4 border-t">
              <Button variant="outline" className="w-full text-red-600 hover:text-red-700">
                Deactivate Account
              </Button>
              <p className="text-xs text-muted-foreground mt-2 text-center">
                This will disable your account but preserve your data for 30 days
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Privacy Information */}
      <Card>
        <CardHeader>
          <CardTitle>Privacy Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm">
            <div>
              <h5 className="font-medium">Data Processing</h5>
              <p className="text-muted-foreground">
                Your entertainment data is processed locally and encrypted before storage. 
                AI analysis happens on secure servers with strict access controls.
              </p>
            </div>
            <div>
              <h5 className="font-medium">Data Sharing</h5>
              <p className="text-muted-foreground">
                We never sell personal data. Anonymized research contributions are optional 
                and help improve mental health AI for everyone.
              </p>
            </div>
            <div>
              <h5 className="font-medium">Your Rights</h5>
              <p className="text-muted-foreground">
                You have the right to access, correct, delete, or port your data at any time. 
                Contact support for assistance with data requests.
              </p>
            </div>
            <div className="pt-3 border-t">
              <div className="flex gap-4">
                <Button variant="ghost" size="sm">Privacy Policy</Button>
                <Button variant="ghost" size="sm">Terms of Service</Button>
                <Button variant="ghost" size="sm">Contact Support</Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Status Messages */}
      {(exportStatus === 'success' || deleteStatus === 'success') && (
        <div className="fixed bottom-4 right-4 p-4 bg-green-50 border border-green-200 rounded-lg shadow-lg">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-green-500 rounded-full"></div>
            <span className="text-green-800 font-medium">
              {exportStatus === 'success' ? 'Data exported successfully!' : 'Data deleted successfully!'}
            </span>
          </div>
        </div>
      )}

      {(exportStatus === 'error' || deleteStatus === 'error') && (
        <div className="fixed bottom-4 right-4 p-4 bg-red-50 border border-red-200 rounded-lg shadow-lg">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-red-500 rounded-full"></div>
            <span className="text-red-800 font-medium">
              Operation failed. Please try again.
            </span>
          </div>
        </div>
      )}
    </div>
  )
}