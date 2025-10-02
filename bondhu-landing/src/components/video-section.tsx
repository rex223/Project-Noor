"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Play,
  ThumbsUp,
  ThumbsDown,
  ExternalLink,
  Clock,
  Eye,
  Users,
  TrendingUp,
  Sparkles,
  Heart,
  Share,
  Bookmark
} from "lucide-react"
import { apiClient } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"
import type { Profile } from "@/types/auth"

interface VideoRecommendation {
  id: string
  title: string
  description: string
  channel_title: string
  category_name: string
  duration_formatted: string
  view_count: number
  thumbnail_url: string
  watch_url: string
  embed_url: string
  personality_match: number
  recommendation_reason: string
  thumbnails: {
    default: string
    medium: string
    high: string
  }
}

interface VideoRecommendationsResponse {
  recommendations: VideoRecommendation[]
  videos_per_genre: Record<string, number>
  total_count: number
  personality_based: boolean
  user_id: string
  generated_at: string
  has_thumbnails: boolean
  has_watch_links: boolean
}

interface VideoSectionProps {
  profile: Profile
}

export default function VideoSection({ profile }: VideoSectionProps) {
  const [recommendations, setRecommendations] = useState<VideoRecommendation[]>([])
  const [trendingVideos, setTrendingVideos] = useState<VideoRecommendation[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'recommended' | 'trending'>('recommended')
  const [likedVideos, setLikedVideos] = useState<Set<string>>(new Set())
  const [dislikedVideos, setDislikedVideos] = useState<Set<string>>(new Set())
  const { toast } = useToast()

  // Load video recommendations on component mount
  useEffect(() => {
    loadVideoRecommendations()
    loadTrendingVideos()
  }, [profile.id])

  const loadVideoRecommendations = async () => {
    try {
      setLoading(true)
      const response = await apiClient.get<VideoRecommendationsResponse>(
        `/video/recommendations/${profile.id}?max_results=20`
      )
      setRecommendations(response.recommendations)

      toast({
        title: "Videos loaded!",
        description: `Found ${response.total_count} personalized recommendations`,
      })
    } catch (error) {
      console.error('Error loading video recommendations:', error)
      toast({
        title: "Error loading videos",
        description: "Failed to load personalized recommendations. Please try again.",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const loadTrendingVideos = async () => {
    try {
      const response = await apiClient.get<{ trending_videos: VideoRecommendation[] }>(
        `/video/trending/${profile.id}?max_results=15`
      )
      setTrendingVideos(response.trending_videos)
    } catch (error) {
      console.error('Error loading trending videos:', error)
    }
  }

  const handleVideoFeedback = async (videoId: string, feedbackType: 'like' | 'dislike' | 'watch' | 'share') => {
    try {
      await apiClient.post('/video/feedback', {
        user_id: profile.id,
        video_id: videoId,
        feedback_type: feedbackType,
        additional_data: {
          timestamp: new Date().toISOString(),
          source: activeTab
        }
      })

      // Update local state
      if (feedbackType === 'like') {
        setLikedVideos(prev => new Set([...prev, videoId]))
        setDislikedVideos(prev => {
          const newSet = new Set(prev)
          newSet.delete(videoId)
          return newSet
        })
      } else if (feedbackType === 'dislike') {
        setDislikedVideos(prev => new Set([...prev, videoId]))
        setLikedVideos(prev => {
          const newSet = new Set(prev)
          newSet.delete(videoId)
          return newSet
        })
      }

      toast({
        title: `Feedback recorded`,
        description: `Thanks for ${feedbackType === 'like' ? 'liking' : feedbackType === 'dislike' ? 'disliking' : feedbackType === 'watch' ? 'watching' : 'sharing'} this video!`,
      })
    } catch (error) {
      console.error('Error submitting feedback:', error)
      toast({
        title: "Error",
        description: "Failed to record feedback. Please try again.",
        variant: "destructive"
      })
    }
  }

  const handleWatchVideo = (video: VideoRecommendation) => {
    // Record watch feedback
    handleVideoFeedback(video.id, 'watch')

    // Open YouTube video in new tab
    window.open(video.watch_url, '_blank', 'noopener,noreferrer')
  }

  const formatViewCount = (count: number): string => {
    if (count >= 1000000) {
      return `${(count / 1000000).toFixed(1)}M views`
    } else if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}K views`
    }
    return `${count} views`
  }

  const VideoCard = ({ video, showTrendingBadge = false }: { video: VideoRecommendation, showTrendingBadge?: boolean }) => (
    <Card className="group hover:shadow-lg transition-all duration-300 overflow-hidden">
      <div className="relative">
        <img
          src={video.thumbnails.high || video.thumbnail_url}
          alt={video.title}
          className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
          onError={(e) => {
            // Fallback to medium thumbnail if high fails
            const target = e.target as HTMLImageElement
            target.src = video.thumbnails.medium || video.thumbnails.default
          }}
        />

        {/* Play overlay */}
        <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
          <Button
            size="lg"
            className="rounded-full bg-red-600 hover:bg-red-700 text-white"
            onClick={() => handleWatchVideo(video)}
          >
            <Play className="h-6 w-6 ml-1" fill="white" />
          </Button>
        </div>

        {/* Duration badge */}
        <Badge className="absolute bottom-2 right-2 bg-black/70 text-white">
          <Clock className="h-3 w-3 mr-1" />
          {video.duration_formatted}
        </Badge>

        {/* Trending badge */}
        {showTrendingBadge && (
          <Badge className="absolute top-2 left-2 bg-red-600 text-white">
            <TrendingUp className="h-3 w-3 mr-1" />
            Trending
          </Badge>
        )}

        {/* Personality match badge */}
        <Badge className="absolute top-2 right-2 bg-purple-600 text-white">
          <Sparkles className="h-3 w-3 mr-1" />
          {video.personality_match}% match
        </Badge>
      </div>

      <CardContent className="p-4">
        <h3 className="font-semibold text-sm line-clamp-2 mb-2 group-hover:text-purple-600 transition-colors">
          {video.title}
        </h3>

        <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
          <Users className="h-3 w-3" />
          <span>{video.channel_title}</span>
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground mb-3">
          <Eye className="h-3 w-3" />
          <span>{formatViewCount(video.view_count)}</span>
          <Badge variant="outline" className="text-xs">
            {video.category_name}
          </Badge>
        </div>

        <p className="text-xs text-muted-foreground mb-3 line-clamp-2">
          {video.recommendation_reason}
        </p>

        {/* Action buttons */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1">
            <Button
              size="sm"
              variant={likedVideos.has(video.id) ? "default" : "outline"}
              onClick={() => handleVideoFeedback(video.id, 'like')}
              className="h-8 px-2"
            >
              <ThumbsUp className={`h-3 w-3 ${likedVideos.has(video.id) ? 'fill-current' : ''}`} />
            </Button>

            <Button
              size="sm"
              variant={dislikedVideos.has(video.id) ? "default" : "outline"}
              onClick={() => handleVideoFeedback(video.id, 'dislike')}
              className="h-8 px-2"
            >
              <ThumbsDown className={`h-3 w-3 ${dislikedVideos.has(video.id) ? 'fill-current' : ''}`} />
            </Button>

            <Button
              size="sm"
              variant="outline"
              onClick={() => handleVideoFeedback(video.id, 'share')}
              className="h-8 px-2"
            >
              <Share className="h-3 w-3" />
            </Button>
          </div>

          <Button
            size="sm"
            onClick={() => handleWatchVideo(video)}
            className="h-8 px-3 bg-red-600 hover:bg-red-700 text-white"
          >
            <ExternalLink className="h-3 w-3 mr-1" />
            Watch
          </Button>
        </div>
      </CardContent>
    </Card>
  )

  const LoadingSkeleton = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {Array.from({ length: 8 }).map((_, i) => (
        <Card key={i}>
          <Skeleton className="h-48 w-full" />
          <CardContent className="p-4">
            <Skeleton className="h-4 w-3/4 mb-2" />
            <Skeleton className="h-3 w-1/2 mb-2" />
            <Skeleton className="h-3 w-full mb-3" />
            <div className="flex justify-between items-center">
              <div className="flex gap-1">
                <Skeleton className="h-6 w-8" />
                <Skeleton className="h-6 w-8" />
                <Skeleton className="h-6 w-8" />
              </div>
              <Skeleton className="h-6 w-16" />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold mb-2">Video Recommendations</h2>
          <p className="text-muted-foreground">
            Personalized videos based on your unique personality profile
          </p>
        </div>

        <Button
          onClick={loadVideoRecommendations}
          disabled={loading}
          variant="outline"
        >
          <Sparkles className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as typeof activeTab)}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="recommended" className="flex items-center gap-2">
            <Heart className="h-4 w-4" />
            For You ({recommendations.length})
          </TabsTrigger>
          <TabsTrigger value="trending" className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Trending ({trendingVideos.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="recommended">
          {loading ? (
            <LoadingSkeleton />
          ) : recommendations.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {recommendations.map((video) => (
                <VideoCard key={video.id} video={video} />
              ))}
            </div>
          ) : (
            <Card className="p-8 text-center">
              <div className="text-muted-foreground mb-4">
                <Play className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <h3 className="text-lg font-medium mb-2">No recommendations yet</h3>
                <p>Complete your personality assessment to get personalized video recommendations!</p>
              </div>
              <Button onClick={loadVideoRecommendations}>
                Try Again
              </Button>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="trending">
          {trendingVideos.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {trendingVideos.map((video) => (
                <VideoCard key={video.id} video={video} showTrendingBadge />
              ))}
            </div>
          ) : (
            <Card className="p-8 text-center">
              <div className="text-muted-foreground">
                <TrendingUp className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <h3 className="text-lg font-medium mb-2">Loading trending videos...</h3>
                <p>Fetching the latest trending content matched to your personality.</p>
              </div>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}