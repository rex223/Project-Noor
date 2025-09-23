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
import { MessageCircle, User, Settings, Music, Video, Gamepad2, Send, Mic, Heart, Sword, Shield, Zap, Play, Volume2 } from "lucide-react"
import type { Profile } from "@/types/auth"

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
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-secondary/20">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center">
              <span className="text-white font-bold text-sm">বন্ধু</span>
            </div>
            <h1 className="text-2xl font-bold">Bondhu Dashboard</h1>
          </div>
          <div className="flex items-center space-x-4">
            <Avatar>
              <AvatarFallback>
                {profile.full_name?.split(' ').map(n => n[0]).join('') || 'U'}
              </AvatarFallback>
            </Avatar>
            <div className="hidden md:block">
              <p className="text-sm font-medium">{profile.full_name}</p>
              <p className="text-xs text-muted-foreground">Level 1 Explorer</p>
            </div>
            <Button variant="outline" onClick={handleSignOut}>
              Sign Out
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold mb-2">
            Welcome back, {profile.full_name?.split(' ')[0] || 'Friend'}! 👋
          </h2>
          <p className="text-muted-foreground">
            Your AI companion awaits - explore, discover, and grow together!
          </p>
        </div>

        {/* Main Dashboard Tabs */}
        <Tabs defaultValue="chat" className="w-full">
          <TabsList className="grid w-full grid-cols-4 mb-8">
            <TabsTrigger value="chat" className="flex items-center gap-2">
              <MessageCircle className="h-4 w-4" />
              <span className="hidden sm:inline">Chat</span>
            </TabsTrigger>
            <TabsTrigger value="music" className="flex items-center gap-2">
              <Music className="h-4 w-4" />
              <span className="hidden sm:inline">Music</span>
            </TabsTrigger>
            <TabsTrigger value="videos" className="flex items-center gap-2">
              <Video className="h-4 w-4" />
              <span className="hidden sm:inline">Videos</span>
            </TabsTrigger>
            <TabsTrigger value="games" className="flex items-center gap-2">
              <Gamepad2 className="h-4 w-4" />
              <span className="hidden sm:inline">RPG</span>
            </TabsTrigger>
          </TabsList>

          {/* Chat Tab */}
          <TabsContent value="chat" className="space-y-6">
            <ChatInterface profile={profile} />
          </TabsContent>

          {/* Music Tab */}
          <TabsContent value="music" className="space-y-6">
            <MusicRecommender profile={profile} />
          </TabsContent>

          {/* Videos Tab */}
          <TabsContent value="videos" className="space-y-6">
            <VideoRecommender profile={profile} />
          </TabsContent>

          {/* Games Tab */}
          <TabsContent value="games" className="space-y-6">
            <RPGGames profile={profile} />
          </TabsContent>
        </Tabs>
      </main>
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
                  <span className="text-white font-bold text-sm">বন্ধু</span>
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

// Music Recommender Component
function MusicRecommender({ profile }: { profile: Profile }) {
  const [mood, setMood] = useState('')
  const [recommendations, setRecommendations] = useState<any[]>([])
  const [isPlaying, setIsPlaying] = useState<number | null>(null)

  const moods = [
    { name: 'Happy', emoji: '😊', color: 'bg-yellow-100 text-yellow-800' },
    { name: 'Sad', emoji: '😢', color: 'bg-blue-100 text-blue-800' },
    { name: 'Energetic', emoji: '⚡', color: 'bg-orange-100 text-orange-800' },
    { name: 'Calm', emoji: '🧘', color: 'bg-green-100 text-green-800' },
    { name: 'Romantic', emoji: '💕', color: 'bg-pink-100 text-pink-800' },
    { name: 'Focus', emoji: '🎯', color: 'bg-purple-100 text-purple-800' }
  ]

  const generateRecommendations = (selectedMood: string) => {
    setMood(selectedMood)
    const mockRecommendations = [
      {
        id: 1,
        title: `${selectedMood} Vibes Playlist`,
        artist: 'Curated by AI',
        mood: selectedMood,
        duration: '45 min',
        tracks: 15,
        cover: '🎵'
      },
      {
        id: 2,
        title: `Deep ${selectedMood} Mix`,
        artist: 'Bondhu Recommendations',
        mood: selectedMood,
        duration: '32 min',
        tracks: 12,
        cover: '🎶'
      },
      {
        id: 3,
        title: `${selectedMood} Journey`,
        artist: 'Personalized Mix',
        mood: selectedMood,
        duration: '28 min',
        tracks: 10,
        cover: '🎼'
      }
    ]
    setRecommendations(mockRecommendations)
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Music className="h-5 w-5" />
            <span>Music Recommender</span>
          </CardTitle>
          <p className="text-muted-foreground">
            Tell me your mood and I'll curate the perfect playlist for you
          </p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
            {moods.map((moodOption) => (
              <Button
                key={moodOption.name}
                variant={mood === moodOption.name ? "default" : "outline"}
                onClick={() => generateRecommendations(moodOption.name)}
                className="h-20 flex flex-col space-y-2"
              >
                <span className="text-2xl">{moodOption.emoji}</span>
                <span>{moodOption.name}</span>
              </Button>
            ))}
          </div>

          {recommendations.length > 0 && (
            <div className="space-y-3">
              <h3 className="font-semibold">Recommended for your {mood} mood:</h3>
              {recommendations.map((rec) => (
                <Card key={rec.id} className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center text-white text-xl">
                        {rec.cover}
                      </div>
                      <div>
                        <h4 className="font-medium">{rec.title}</h4>
                        <p className="text-sm text-muted-foreground">
                          {rec.artist} • {rec.tracks} tracks • {rec.duration}
                        </p>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setIsPlaying(isPlaying === rec.id ? null : rec.id)}
                      >
                        {isPlaying === rec.id ? <Volume2 className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                        {isPlaying === rec.id ? 'Playing' : 'Play'}
                      </Button>
                      <Button size="sm">
                        <Heart className="h-4 w-4 mr-2" />
                        Save
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

// Video Recommender Component  
function VideoRecommender({ profile }: { profile: Profile }) {
  const categories = [
    { name: 'Motivational', icon: '🚀', color: 'bg-blue-100 text-blue-800' },
    { name: 'Educational', icon: '📚', color: 'bg-green-100 text-green-800' },
    { name: 'Relaxation', icon: '🧘', color: 'bg-purple-100 text-purple-800' },
    { name: 'Entertainment', icon: '🎭', color: 'bg-orange-100 text-orange-800' }
  ]

  const [selectedCategory, setSelectedCategory] = useState('')
  const [videos, setVideos] = useState<any[]>([])

  const loadVideos = (category: string) => {
    setSelectedCategory(category)
    const mockVideos = [
      {
        id: 1,
        title: `Best ${category} Content for You`,
        channel: 'Bondhu Curated',
        views: '1.2M',
        duration: '15:30',
        thumbnail: '🎬',
        description: `Personalized ${category.toLowerCase()} content based on your profile`
      },
      {
        id: 2,
        title: `Daily ${category} Dose`,
        channel: 'AI Recommendations',
        views: '856K',
        duration: '8:45',
        thumbnail: '📹',
        description: `Short and impactful ${category.toLowerCase()} videos`
      },
      {
        id: 3,
        title: `${category} Journey`,
        channel: 'Personalized Content',
        views: '432K',
        duration: '22:15',
        thumbnail: '🎥',
        description: `Deep dive into ${category.toLowerCase()} topics`
      }
    ]
    setVideos(mockVideos)
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Video className="h-5 w-5" />
            <span>Video Recommender</span>
          </CardTitle>
          <p className="text-muted-foreground">
            Discover videos tailored to your interests and current needs
          </p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {categories.map((category) => (
              <Button
                key={category.name}
                variant={selectedCategory === category.name ? "default" : "outline"}
                onClick={() => loadVideos(category.name)}
                className="h-24 flex flex-col space-y-2"
              >
                <span className="text-2xl">{category.icon}</span>
                <span>{category.name}</span>
              </Button>
            ))}
          </div>

          {videos.length > 0 && (
            <div className="space-y-4">
              <h3 className="font-semibold">{selectedCategory} Videos for You:</h3>
              <div className="grid gap-4">
                {videos.map((video) => (
                  <Card key={video.id} className="p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-center space-x-4">
                      <div className="w-24 h-16 bg-gradient-to-r from-red-500 to-pink-500 rounded-lg flex items-center justify-center text-white text-2xl">
                        {video.thumbnail}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium">{video.title}</h4>
                        <p className="text-sm text-muted-foreground mb-1">
                          {video.channel} • {video.views} views • {video.duration}
                        </p>
                        <p className="text-xs text-muted-foreground">{video.description}</p>
                      </div>
                      <Button size="sm" className="flex items-center space-x-2">
                        <Play className="h-4 w-4" />
                        <span>Watch</span>
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

// RPG Games Component
function RPGGames({ profile }: { profile: Profile }) {
  const [playerStats, setPlayerStats] = useState({
    level: 1,
    experience: 0,
    health: 100,
    mana: 50,
    gold: 25,
    questsCompleted: 0
  })

  const games = [
    {
      id: 1,
      name: 'Emotional Quest',
      description: 'Embark on a journey of self-discovery and emotional intelligence',
      difficulty: 'Beginner',
      icon: <Sword className="h-6 w-6" />,
      color: 'bg-green-100 text-green-800',
      reward: '+10 XP, +5 Gold',
      duration: '15-20 mins'
    },
    {
      id: 2,
      name: 'Anxiety Dungeon',
      description: 'Navigate through anxiety challenges and develop coping strategies',
      difficulty: 'Intermediate',
      icon: <Shield className="h-6 w-6" />,
      color: 'bg-blue-100 text-blue-800',
      reward: '+15 XP, +8 Gold',
      duration: '20-30 mins'
    },
    {
      id: 3,
      name: 'Mindfulness Arena',
      description: 'Master mindfulness techniques in an interactive environment',
      difficulty: 'Advanced',
      icon: <Zap className="h-6 w-6" />,
      color: 'bg-purple-100 text-purple-800',
      reward: '+20 XP, +12 Gold',
      duration: '30-45 mins'
    }
  ]

  const achievements = [
    { name: 'First Steps', description: 'Completed your first quest', unlocked: false },
    { name: 'Mindful Explorer', description: 'Completed 5 mindfulness exercises', unlocked: false },
    { name: 'Emotional Warrior', description: 'Mastered emotional regulation', unlocked: false }
  ]

  return (
    <div className="space-y-6">
      {/* Player Stats */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Gamepad2 className="h-5 w-5" />
            <span>Your RPG Profile</span>
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Level up by completing quests and challenges
          </p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">{playerStats.level}</div>
              <div className="text-sm text-muted-foreground">Level</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{playerStats.experience}</div>
              <div className="text-sm text-muted-foreground">XP</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{playerStats.health}</div>
              <div className="text-sm text-muted-foreground">Health</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{playerStats.mana}</div>
              <div className="text-sm text-muted-foreground">Mana</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">{playerStats.gold}</div>
              <div className="text-sm text-muted-foreground">Gold</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{playerStats.questsCompleted}</div>
              <div className="text-sm text-muted-foreground">Quests</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Available Games */}
      <Card>
        <CardHeader>
          <CardTitle>Available Quests</CardTitle>
          <p className="text-muted-foreground">
            Choose your adventure and grow through interactive experiences
          </p>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            {games.map((game) => (
              <Card key={game.id} className="p-4 hover:shadow-md transition-shadow cursor-pointer border-l-4 border-l-primary">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-lg flex items-center justify-center text-white">
                      {game.icon}
                    </div>
                    <div>
                      <h4 className="font-semibold">{game.name}</h4>
                      <p className="text-sm text-muted-foreground mb-1">{game.description}</p>
                      <div className="flex space-x-4 text-xs text-muted-foreground">
                        <span>Duration: {game.duration}</span>
                        <span>Reward: {game.reward}</span>
                      </div>
                      <Badge variant="outline" className="mt-2">
                        {game.difficulty}
                      </Badge>
                    </div>
                  </div>
                  <Button className="flex items-center space-x-2">
                    <Sword className="h-4 w-4" />
                    <span>Start Quest</span>
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Achievements */}
      <Card>
        <CardHeader>
          <CardTitle>Achievements</CardTitle>
          <p className="text-muted-foreground">Track your progress and unlock rewards</p>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3">
            {achievements.map((achievement, index) => (
              <div key={index} className={`flex items-center space-x-3 p-3 rounded-lg ${achievement.unlocked ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${achievement.unlocked ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-500'}`}>
                  {achievement.unlocked ? '✓' : '🔒'}
                </div>
                <div>
                  <h5 className="font-medium">{achievement.name}</h5>
                  <p className="text-sm text-muted-foreground">{achievement.description}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}