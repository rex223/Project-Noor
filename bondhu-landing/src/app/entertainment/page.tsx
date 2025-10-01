/**
 * Enhanced Entertainment Hub Page
 * Connected to real backend agent recommendations
 */

"use client"

import { useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { createClient } from "@/lib/supabase/client"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ArrowLeft, RefreshCw, Sparkles, TrendingUp, Clock, User, Settings } from "lucide-react"
import type { Profile } from "@/types/auth"
import { Logo } from "@/components/logo"
import { ThemeToggle } from "@/components/theme-toggle"
import { useEntertainmentRecommendations } from "@/hooks/use-entertainment-recommendations"
import MusicRecommendations from "@/components/entertainment/MusicRecommendations"
import VideoRecommendations from "@/components/entertainment/VideoRecommendations"
import GameRecommendations from "@/components/entertainment/GameRecommendations"
import type { MusicRecommendation, VideoRecommendation, GameRecommendation } from "@/lib/api-client"

export default function EnhancedEntertainmentPage() {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [currentlyPlaying, setCurrentlyPlaying] = useState<string | null>(null)
  const [selectedMood, setSelectedMood] = useState<string | null>(null)
  const router = useRouter()
  const supabase = createClient()

  // Entertainment recommendations hook
  const {
    recommendations,
    musicRecommendations,
    videoRecommendations,
    gameRecommendations,
    isLoading: recommendationsLoading,
    error: recommendationsError,
    lastUpdated,
    refreshRecommendations,
    recordInteraction,
    getRecommendationsByMood,
    getTopRecommendations
  } = useEntertainmentRecommendations({
    userId: profile?.id || '',
    categories: ['music', 'videos', 'games'],
    limit_per_category: 12,
    auto_refresh_interval: 30, // Refresh every 30 minutes
    include_context: true,
    onRecommendationsLoaded: (recs) => {
      console.log('🎯 Loaded entertainment recommendations:', recs)
    },
    onError: (error) => {
      console.error('❌ Entertainment recommendations error:', error)
    }
  })

  // Load user profile
  useEffect(() => {
    const loadProfile = async () => {
      try {
        const { data: { session }, error: sessionError } = await supabase.auth.getSession()
        if (sessionError || !session) {
          router.push('/sign-in?redirectTo=/entertainment')
          return
        }

        const { data: profile, error: profileError } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', session.user.id)
          .single()

        if (profileError) {
          console.error('Profile fetch error:', profileError)
          return
        }

        setProfile(profile)
      } catch (error) {
        console.error('Authentication check failed:', error)
      } finally {
        setIsLoading(false)
      }
    }

    loadProfile()
  }, [supabase.auth, supabase, router])

  // Helper to get content ID from recommendation
  const getContentId = (rec: MusicRecommendation | VideoRecommendation | GameRecommendation): string => {
    if ('spotify_id' in rec && rec.spotify_id) return rec.spotify_id
    if ('youtube_url' in rec && rec.youtube_url) return rec.youtube_url
    if ('imdb_id' in rec && rec.imdb_id) return rec.imdb_id
    return rec.title
  }

  // Helper to get content type
  const getContentType = (rec: MusicRecommendation | VideoRecommendation | GameRecommendation): 'music' | 'video' | 'game' => {
    if ('spotify_id' in rec) return 'music'
    if ('youtube_url' in rec || 'imdb_id' in rec) return 'video'
    return 'game'
  }

  // Handle play actions
  const handlePlay = useCallback(async (recommendation: MusicRecommendation | VideoRecommendation | GameRecommendation) => {
    if (!profile?.id) return

    // Toggle play state
    const isCurrentlyPlaying = currentlyPlaying === recommendation.title
    const newPlayingState = isCurrentlyPlaying ? null : recommendation.title
    setCurrentlyPlaying(newPlayingState)

    // Record interaction - only when starting to play
    if (!isCurrentlyPlaying) {
      await recordInteraction({
        content_type: getContentType(recommendation),
        content_id: getContentId(recommendation),
        content_title: recommendation.title,
        interaction_type: 'play',
        context: { source: 'entertainment_hub' }
      })
    }
  }, [profile?.id, currentlyPlaying, recordInteraction])

  // Handle like actions
  const handleLike = useCallback(async (recommendation: MusicRecommendation | VideoRecommendation | GameRecommendation) => {
    if (!profile?.id) return

    await recordInteraction({
      content_type: getContentType(recommendation),
      content_id: getContentId(recommendation),
      content_title: recommendation.title,
      interaction_type: 'like',
      rating: 5,
      context: { source: 'entertainment_hub' }
    })
  }, [profile?.id, recordInteraction])

  // Handle dislike actions
  const handleDislike = useCallback(async (recommendation: MusicRecommendation | VideoRecommendation | GameRecommendation) => {
    if (!profile?.id) return

    await recordInteraction({
      content_type: getContentType(recommendation),
      content_id: getContentId(recommendation),
      content_title: recommendation.title,
      interaction_type: 'dislike',
      rating: 1,
      context: { source: 'entertainment_hub' }
    })
  }, [profile?.id, recordInteraction])

  // Handle share actions
  const handleShare = useCallback(async (recommendation: MusicRecommendation | VideoRecommendation | GameRecommendation) => {
    if (!profile?.id) return

    const contentType = getContentType(recommendation)

    // Create share text
    const shareText = `Check out this ${contentType === 'music' ? 'song' : contentType === 'video' ? 'video' : 'game'}: ${recommendation.title}`

    // Try to use Web Share API if available
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Bondhu AI Recommendation',
          text: shareText,
          url: window.location.href
        })

        await recordInteraction({
          content_type: contentType,
          content_id: getContentId(recommendation),
          content_title: recommendation.title,
          interaction_type: 'share',
          context: { source: 'entertainment_hub', method: 'web_share_api' }
        })
      } catch (err) {
        // User cancelled share
      }
    } else {
      // Fallback to clipboard
      try {
        await navigator.clipboard.writeText(shareText)
        // Could show a toast notification here

        await recordInteraction({
          content_type: contentType,
          content_id: getContentId(recommendation),
          content_title: recommendation.title,
          interaction_type: 'share',
          context: { source: 'entertainment_hub', method: 'clipboard' }
        })
      } catch (err) {
        console.error('Failed to copy to clipboard:', err)
      }
    }
  }, [profile?.id, recordInteraction])

  // Handle mood filter
  const handleMoodFilter = useCallback((mood: string) => {
    setSelectedMood(mood === selectedMood ? null : mood)
  }, [selectedMood])

  // Get filtered recommendations based on mood
  const filteredRecommendations = selectedMood
    ? getRecommendationsByMood(selectedMood)
    : {
      music: musicRecommendations,
      videos: videoRecommendations,
      games: gameRecommendations
    }

  // Get top recommendations for overview
  const topRecommendations = getTopRecommendations(3)

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
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            {/* Left Section */}
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" onClick={() => router.back()}>
                <ArrowLeft className="h-4 w-4 mr-1" />
                Back
              </Button>
              <Logo width={140} height={50} />
              <div className="hidden sm:block">
                <h1 className="text-lg font-semibold text-muted-foreground">Entertainment Hub</h1>
                {lastUpdated && (
                  <p className="text-xs text-muted-foreground">
                    Updated {lastUpdated.toLocaleTimeString()}
                  </p>
                )}
              </div>
            </div>

            {/* Right Section */}
            <div className="flex items-center space-x-3">
              <Button
                variant="outline"
                size="sm"
                onClick={() => refreshRecommendations({ force: true })}
                disabled={recommendationsLoading}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${recommendationsLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <ThemeToggle />
              <div className="flex items-center space-x-2">
                <User className="h-4 w-4" />
                <span className="text-sm font-medium">{profile.full_name}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-3xl md:text-4xl font-bold mb-4">
              Your Personalized Entertainment Hub
            </h1>
            <p className="text-lg text-muted-foreground mb-6">
              AI-curated recommendations based on your unique personality profile
            </p>

            {recommendations && (
              <div className="flex items-center justify-center space-x-6 text-sm text-muted-foreground">
                <div className="flex items-center space-x-2">
                  <Sparkles className="h-4 w-4" />
                  <span>{recommendations.overall_confidence}% match confidence</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Clock className="h-4 w-4" />
                  <span>Generated {recommendations.context.time_of_day}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <TrendingUp className="h-4 w-4" />
                  <span>{recommendations.context.recent_activity.length} recent activities</span>
                </div>
              </div>
            )}
          </motion.div>
        </div>

        {/* Quick Overview */}
        {!recommendationsLoading && (topRecommendations.music.length > 0 || topRecommendations.videos.length > 0 || topRecommendations.games.length > 0) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-8"
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Sparkles className="h-5 w-5" />
                  <span>Top Picks for You</span>
                </CardTitle>
                <p className="text-muted-foreground">
                  Your highest-rated recommendations across all categories
                </p>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {topRecommendations.music[0] && (
                    <div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20 rounded-lg">
                      <div className="flex items-center space-x-2 mb-3">
                        <Badge className="text-purple-600 bg-purple-100 dark:bg-purple-900/20">Music</Badge>
                        <Badge variant="outline">{Math.round(topRecommendations.music[0].confidence)}%</Badge>
                      </div>
                      <h4 className="font-semibold mb-1">{topRecommendations.music[0].title}</h4>
                      {topRecommendations.music[0].artist && (
                        <p className="text-sm text-muted-foreground mb-2">by {topRecommendations.music[0].artist}</p>
                      )}
                      <p className="text-xs text-muted-foreground">{topRecommendations.music[0].reasoning}</p>
                    </div>
                  )}

                  {topRecommendations.videos[0] && (
                    <div className="p-4 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/20 dark:to-cyan-950/20 rounded-lg">
                      <div className="flex items-center space-x-2 mb-3">
                        <Badge className="text-blue-600 bg-blue-100 dark:bg-blue-900/20">Video</Badge>
                        <Badge variant="outline">{Math.round(topRecommendations.videos[0].confidence)}%</Badge>
                      </div>
                      <h4 className="font-semibold mb-1">{topRecommendations.videos[0].title}</h4>
                      {topRecommendations.videos[0].creator && (
                        <p className="text-sm text-muted-foreground mb-2">by {topRecommendations.videos[0].creator}</p>
                      )}
                      <p className="text-xs text-muted-foreground">{topRecommendations.videos[0].reasoning}</p>
                    </div>
                  )}

                  {topRecommendations.games[0] && (
                    <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/20 dark:to-emerald-950/20 rounded-lg">
                      <div className="flex items-center space-x-2 mb-3">
                        <Badge className="text-green-600 bg-green-100 dark:bg-green-900/20">Game</Badge>
                        <Badge variant="outline">{Math.round(topRecommendations.games[0].confidence)}%</Badge>
                      </div>
                      <h4 className="font-semibold mb-1">{topRecommendations.games[0].title}</h4>
                      {topRecommendations.games[0].developer && (
                        <p className="text-sm text-muted-foreground mb-2">by {topRecommendations.games[0].developer}</p>
                      )}
                      <p className="text-xs text-muted-foreground">{topRecommendations.games[0].reasoning}</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Mood Filters */}
        {recommendations && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="mb-8"
          >
            <div className="flex items-center space-x-4 mb-4">
              <h3 className="font-semibold">Filter by Mood:</h3>
              <div className="flex space-x-2 flex-wrap">
                {['energetic', 'relaxing', 'focused', 'creative', 'social', 'adventurous'].map((mood) => (
                  <Button
                    key={mood}
                    variant={selectedMood === mood ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleMoodFilter(mood)}
                    className="capitalize"
                  >
                    {mood}
                  </Button>
                ))}
                {selectedMood && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedMood(null)}
                  >
                    Clear
                  </Button>
                )}
              </div>
            </div>
          </motion.div>
        )}

        {/* Recommendations Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Tabs defaultValue="music" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="music">
                Music ({filteredRecommendations.music.length})
              </TabsTrigger>
              <TabsTrigger value="videos">
                Videos ({filteredRecommendations.videos.length})
              </TabsTrigger>
              <TabsTrigger value="games">
                Games ({filteredRecommendations.games.length})
              </TabsTrigger>
            </TabsList>

            <TabsContent value="music" className="mt-6">
              <MusicRecommendations
                recommendations={filteredRecommendations.music}
                isLoading={recommendationsLoading}
                onPlay={handlePlay}
                onLike={handleLike}
                onDislike={handleDislike}
                onShare={handleShare}
                currentlyPlaying={currentlyPlaying}
              />
            </TabsContent>

            <TabsContent value="videos" className="mt-6">
              <VideoRecommendations
                recommendations={filteredRecommendations.videos}
                isLoading={recommendationsLoading}
                onPlay={handlePlay}
                onLike={handleLike}
                onDislike={handleDislike}
                onShare={handleShare}
                currentlyPlaying={currentlyPlaying}
              />
            </TabsContent>

            <TabsContent value="games" className="mt-6">
              <GameRecommendations
                recommendations={filteredRecommendations.games}
                isLoading={recommendationsLoading}
                onPlay={handlePlay}
                onLike={handleLike}
                onDislike={handleDislike}
                onShare={handleShare}
                currentlyPlaying={currentlyPlaying}
              />
            </TabsContent>
          </Tabs>
        </motion.div>

        {/* Error State */}
        {recommendationsError && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8"
          >
            <Card className="border-destructive">
              <CardContent className="pt-6">
                <div className="text-center">
                  <Settings className="h-12 w-12 mx-auto text-destructive mb-4" />
                  <h3 className="text-lg font-semibold text-destructive mb-2">
                    Unable to Load Recommendations
                  </h3>
                  <p className="text-muted-foreground mb-4">
                    {recommendationsError.message}
                  </p>
                  <Button
                    onClick={() => refreshRecommendations({ force: true })}
                    disabled={recommendationsLoading}
                  >
                    <RefreshCw className={`h-4 w-4 mr-2 ${recommendationsLoading ? 'animate-spin' : ''}`} />
                    Try Again
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </main>
    </div>
  )
}