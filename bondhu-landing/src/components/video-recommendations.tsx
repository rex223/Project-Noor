/**
 * Enhanced Video Recommendation Components with YouTube Integration
 * Provides personalized video suggestions with like/dislike feedback and personality learning
 */

import * as React from 'react'
import { useState, useEffect, useCallback, useMemo } from 'react'
import Image from 'next/image'
import { apiClient, ApiError } from '../lib/api-client'
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { Button } from "./ui/button"
import { Badge } from "./ui/badge"
import { Progress } from "./ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs"
import { Alert, AlertDescription } from "./ui/alert"
import {
    ThumbsUp, ThumbsDown, Play, ExternalLink, RefreshCw,
    Clock, TrendingUp, Sparkles, Brain, Target,
    Share2
} from 'lucide-react'
import { toast } from 'sonner'

interface VideoData {
    id: string
    title: string
    description: string
    channel_title: string
    duration_formatted: string
    duration_seconds: number
    view_count: number
    like_count: number
    thumbnail_url: string
    youtube_url: string
    category_name: string
    content_themes: string[]
    personality_score: number
    rl_score: number
    combined_score: number
    source: 'personalized' | 'trending'
    engagement_score: number
    personality_indicators: { [key: string]: number }
    genre?: string
    genre_rank?: number
    genre_combined_score?: number
}

interface VideoFeedback {
    video_id: string
    feedback_type: 'like' | 'dislike' | 'watch' | 'skip' | 'share' | 'comment'
    watch_time?: number
    total_duration?: number
    interactions?: string[]
    time_to_click?: number
    // Additional metadata for watch history storage
    video_title?: string
    channel_title?: string
    category_name?: string
}

interface GenreCluster {
    genre: string
    cluster_rank: number
    history_score: number
    personality_score: number
    combined_score: number
    reason: string
    videos: VideoData[]
}

interface VideoRecommendationPayload {
    recommendations?: VideoData[]
    trending_videos?: VideoData[]
    genre_clusters?: GenreCluster[]
    total_count?: number
    [key: string]: unknown
}

interface VideoRecommendationApiResponse {
    success: boolean
    data?: VideoRecommendationPayload
    message?: string
}

interface PersonalityProfile {
    openness: number
    conscientiousness: number
    extraversion: number
    agreeableness: number
    neuroticism: number
}

interface VideoRecommendationsProps {
    userId: string
    personalityProfile: PersonalityProfile
    onVideoInteraction: (video: VideoData, interaction: string) => void
}

// Enhanced Video Card Component
const VideoCard: React.FC<{
    video: VideoData
    onFeedback: (feedback: VideoFeedback) => void
    onWatchClick: (video: VideoData) => void
}> = ({ video, onFeedback, onWatchClick }) => {
    const [isLiked, setIsLiked] = useState<boolean | null>(null)
    const [watchStartTime, setWatchStartTime] = useState<number | null>(null)

    const formatViewCount = (count: number): string => {
        if (count >= 1000000) {
            return `${(count / 1000000).toFixed(1)}M views`
        } else if (count >= 1000) {
            return `${(count / 1000).toFixed(1)}K views`
        }
        return `${count} views`
    }

    const handleLike = useCallback(async (liked: boolean) => {
        const clickTime = watchStartTime ? (Date.now() - watchStartTime) / 1000 : undefined

        setIsLiked(liked)

        const feedback: VideoFeedback = {
            video_id: video.id,
            feedback_type: liked ? 'like' : 'dislike',
            time_to_click: clickTime
        }

        await onFeedback(feedback)

        toast.success(liked ? 'Video liked! This helps improve your recommendations.' : 'Feedback noted. We\'ll show you less content like this.')
    }, [video.id, watchStartTime, onFeedback])

    const handleWatch = useCallback(() => {
        setWatchStartTime(Date.now())
        onWatchClick(video)

        // Track watch interaction
        const feedback: VideoFeedback = {
            video_id: video.id,
            feedback_type: 'watch',
            total_duration: video.duration_seconds
        }
        onFeedback(feedback)
    }, [video, onWatchClick, onFeedback])

    const handleShare = useCallback(async () => {
        try {
            await navigator.share({
                title: video.title,
                text: `Check out this video: ${video.title}`,
                url: video.youtube_url
            })

            const feedback: VideoFeedback = {
                video_id: video.id,
                feedback_type: 'share'
            }
            onFeedback(feedback)
        } catch (shareError) {
            console.error('Falling back to clipboard copy for share', shareError)
            // Fallback to clipboard
            navigator.clipboard.writeText(video.youtube_url)
            toast.success('Video link copied to clipboard!')
        }
    }, [video, onFeedback])

    return (
        <Card className="group hover:shadow-lg transition-all duration-300 border-2 hover:border-primary/20">
            <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                        <CardTitle className="text-lg font-semibold leading-tight mb-2 line-clamp-2">
                            {video.title}
                        </CardTitle>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                            <span className="font-medium">{video.channel_title}</span>
                            <span>•</span>
                            <span>{formatViewCount(video.view_count)}</span>
                            <span>•</span>
                            <div className="flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                <span>{video.duration_formatted}</span>
                            </div>
                        </div>
                    </div>

                    {/* Source Badge */}
                    <Badge
                        variant={video.source === 'personalized' ? 'default' : 'secondary'}
                        className="ml-2"
                    >
                        {video.source === 'personalized' ? (
                            <><Sparkles className="h-3 w-3 mr-1" /> For You</>
                        ) : (
                            <><TrendingUp className="h-3 w-3 mr-1" /> Trending</>
                        )}
                    </Badge>
                </div>
            </CardHeader>

            <CardContent className="space-y-4">
                {/* Thumbnail */}
                <div className="relative aspect-video rounded-lg overflow-hidden bg-muted">
                    {video.thumbnail_url ? (
                        <Image
                            src={video.thumbnail_url}
                            alt={video.title}
                            fill
                            sizes="(max-width: 768px) 100vw, (max-width: 1280px) 50vw, 400px"
                            className="object-cover"
                            priority={video.source === 'personalized'}
                            unoptimized
                        />
                    ) : (
                        <div className="w-full h-full flex items-center justify-center text-6xl">
                            🎥
                        </div>
                    )}

                    {/* Play Overlay */}
                    <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                        <Button
                            size="lg"
                            onClick={handleWatch}
                            className="bg-white/90 text-black hover:bg-white"
                        >
                            <Play className="h-5 w-5 mr-2" />
                            Watch Now
                        </Button>
                    </div>
                </div>

                {/* Video Description */}
                <div className="text-sm text-muted-foreground line-clamp-2">
                    {video.description}
                </div>

                {/* Content Themes */}
                {video.content_themes.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                        {video.content_themes.slice(0, 3).map((theme) => (
                            <Badge key={theme} variant="outline" className="text-xs">
                                {theme.replace('_', ' ')}
                            </Badge>
                        ))}
                    </div>
                )}

                {/* Personality Match Score */}
                <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-1">
                            <Brain className="h-4 w-4 text-primary" />
                            <span className="font-medium">Personality Match</span>
                        </div>
                        <span className="text-primary font-semibold">
                            {Math.round(video.combined_score * 100)}%
                        </span>
                    </div>
                    <Progress value={video.combined_score * 100} className="h-2" />
                </div>

                {/* Action Buttons */}
                <div className="flex items-center justify-between pt-2">
                    <div className="flex items-center gap-2">
                        <Button
                            variant={isLiked === true ? "default" : "outline"}
                            size="sm"
                            onClick={() => handleLike(true)}
                            className="transition-colors"
                        >
                            <ThumbsUp className="h-4 w-4 mr-1" />
                            Like
                        </Button>

                        <Button
                            variant={isLiked === false ? "destructive" : "outline"}
                            size="sm"
                            onClick={() => handleLike(false)}
                            className="transition-colors"
                        >
                            <ThumbsDown className="h-4 w-4 mr-1" />
                            Dislike
                        </Button>
                    </div>

                    <div className="flex items-center gap-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={handleShare}
                        >
                            <Share2 className="h-4 w-4" />
                        </Button>

                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => window.open(video.youtube_url, '_blank')}
                        >
                            <ExternalLink className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}

// Main Video Recommendations Component
const VideoRecommendations: React.FC<VideoRecommendationsProps> = ({
    userId,
    personalityProfile,
    onVideoInteraction
}) => {
    const [recommendations, setRecommendations] = useState<VideoData[]>([])
    const [trendingVideos, setTrendingVideos] = useState<VideoData[]>([])
    const [genreClusters, setGenreClusters] = useState<GenreCluster[]>([])
    const [loading, setLoading] = useState(false)
    const [refreshing, setRefreshing] = useState(false)
    const [lastRefresh, setLastRefresh] = useState<Date | null>(null)
    const [activeTab, setActiveTab] = useState<'foryou' | 'trending'>('foryou')
    const [stats, setStats] = useState<Record<string, number> | null>(null)

    const dominantTrait = useMemo(() => {
        const entries = Object.entries(personalityProfile ?? {})
        if (!entries.length) {
            return null
        }

        const [trait, score] = entries.sort((a, b) => Number(b[1]) - Number(a[1]))[0]
        return { trait, score }
    }, [personalityProfile])

    const formatTraitLabel = useCallback((trait: string) =>
        trait.replace(/_/g, ' ').toLowerCase(), [])

    const fetchRecommendations = useCallback(async (forceRefresh = false) => {
        if (!userId) return

        setLoading(true)
        if (forceRefresh) setRefreshing(true)

        try {
            const apiResponse = await apiClient.post<VideoRecommendationApiResponse>(
                `/video/recommendations/${userId}`,
                {
                    max_results: 20,
                    force_refresh: forceRefresh,
                    include_trending: true
                }
            )

            const payload: VideoRecommendationPayload = apiResponse.data ?? {}

            const videos = Array.isArray(payload.recommendations)
                ? (payload.recommendations as VideoData[])
                : []
            const clusters = Array.isArray(payload.genre_clusters)
                ? (payload.genre_clusters as GenreCluster[])
                : []

            setGenreClusters(clusters)

            // Separate personalized and trending videos
            const personalizedVideos = clusters.length
                ? clusters.flatMap((cluster) => cluster.videos)
                : videos.filter((v: VideoData) => v.source === 'personalized')

            const uniquePersonalized = Array.from(
                new Map(
                    personalizedVideos.map((video) => [video.id ?? video.youtube_url, video])
                ).values()
            )

            const trendingVids = videos.filter((v: VideoData) => v.source === 'trending')

            setRecommendations(uniquePersonalized)
            setTrendingVideos(trendingVids)
            setLastRefresh(new Date())

            // Fetch RL statistics
            const statsResponse = await apiClient.get<{ data?: { rl_statistics?: unknown } }>(
                `/video/rl-stats/${userId}`
            )
            const rlStats = statsResponse.data?.rl_statistics
            if (rlStats && typeof rlStats === 'object') {
                setStats(rlStats as Record<string, number>)
            } else {
                setStats(null)
            }

        } catch (error) {
            console.error('Error fetching recommendations:', error)
            if (error instanceof ApiError) {
                toast.error(error.details?.detail || error.message)
            } else {
                toast.error('Failed to load video recommendations')
            }
        } finally {
            setLoading(false)
            setRefreshing(false)
        }
    }, [userId])

    const handleVideoFeedback = useCallback(async (feedback: VideoFeedback) => {
        try {
            await apiClient.post(`/video/feedback/${userId}`, feedback)

            // Update video interaction callback
            const video = [...recommendations, ...trendingVideos].find(v => v.id === feedback.video_id)
            if (video) {
                onVideoInteraction(video, feedback.feedback_type)
            }

        } catch (error) {
            console.error('Error processing feedback:', error)
            toast.error('Failed to process feedback')
        }
    }, [userId, recommendations, trendingVideos, onVideoInteraction])

    const handleWatchVideo = useCallback((video: VideoData) => {
        // Open YouTube video in new tab
        window.open(video.youtube_url, '_blank')

        // Track watch event with full video metadata for proper history storage
        const feedback: VideoFeedback = {
            video_id: video.id,
            feedback_type: 'watch',
            total_duration: video.duration_seconds,
            // Include video metadata for database storage
            video_title: video.title,
            channel_title: video.channel_title,
            category_name: video.category_name,
            watch_time: video.duration_seconds // Assume full watch for now
        }
        handleVideoFeedback(feedback)
    }, [handleVideoFeedback])

    const handleManualRefresh = useCallback(async () => {
        if (!userId) return

        setRefreshing(true)
        try {
            // Use the scheduler's manual refresh endpoint
            const response = await apiClient.post<{
                data?: {
                    refresh_completed?: boolean
                }
            }>(`/video/refresh-recommendations/${userId}`)

            if (response.data?.refresh_completed) {
                await fetchRecommendations(false)
                toast.success('Recommendations refreshed successfully!')
            } else {
                toast.success('Refresh triggered! New recommendations will appear shortly.')
                setTimeout(() => fetchRecommendations(false), 2000)
            }
        } catch (error) {
            console.error('Error refreshing recommendations:', error)
            if (error instanceof ApiError) {
                toast.error(error.details?.detail || error.message)
            } else {
                toast.error('Failed to refresh recommendations')
            }
            // Fallback to local refresh
            await fetchRecommendations(true)
        } finally {
            setRefreshing(false)
        }
    }, [userId, fetchRecommendations])

    // Register user for automatic refresh and check scheduler status
    useEffect(() => {
        if (!userId) return

        let isActive = true
        let intervalId: ReturnType<typeof setInterval> | null = null

        const setupAutoRefresh = async () => {
            try {
                await apiClient.post(`/video/scheduler/register/${userId}`)

                const statusData = await apiClient.get<{ data?: { next_refresh?: string } }>(
                    '/video/scheduler-status'
                )
                const nextRefresh = statusData.data?.next_refresh
                if (!nextRefresh || !isActive) return

                intervalId = setInterval(() => {
                    const now = new Date()
                    const refreshTime = new Date(nextRefresh)

                    if (
                        now >= refreshTime &&
                        lastRefresh &&
                        (now.getTime() - lastRefresh.getTime()) >= 7.5 * 60 * 60 * 1000
                    ) {
                        fetchRecommendations(true)
                    }
                }, 10 * 60 * 1000)
            } catch (scheduleError) {
                console.error('Error setting up auto-refresh:', scheduleError)
            }
        }

        setupAutoRefresh()

        return () => {
            isActive = false
            if (intervalId) {
                clearInterval(intervalId)
            }
        }
    }, [userId, lastRefresh, fetchRecommendations])

    // Initial load
    useEffect(() => {
        fetchRecommendations()
    }, [fetchRecommendations])

    const personalizedVideos = useMemo(() => {
        if (genreClusters.length > 0) {
            return genreClusters.flatMap((cluster) => cluster.videos)
        }
        return recommendations
    }, [genreClusters, recommendations])
    const trending = useMemo(() => trendingVideos, [trendingVideos])

    return (
        <div className="space-y-6">
            {/* Header with Refresh Button */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold mb-2">Video Recommendations</h2>
                    <p className="text-muted-foreground">
                        Personalized content based on your personality and preferences
                    </p>
                    {dominantTrait && (
                        <p className="text-sm text-muted-foreground mt-1">
                            Spotlighting genres that resonate with your {formatTraitLabel(dominantTrait.trait)} energy
                        </p>
                    )}
                </div>

                <div className="flex items-center gap-3">
                    {lastRefresh && (
                        <p className="text-sm text-muted-foreground">
                            Last updated: {lastRefresh.toLocaleTimeString()}
                        </p>
                    )}

                    <Button
                        variant="outline"
                        onClick={handleManualRefresh}
                        disabled={refreshing}
                        className="flex items-center gap-2"
                    >
                        <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
                        {refreshing ? 'Refreshing...' : 'Refresh'}
                    </Button>
                </div>
            </div>

            {/* Learning Statistics */}
            {stats && (
                <Alert>
                    <Brain className="h-4 w-4" />
                    <AlertDescription>
                        <div className="flex items-center gap-4 text-sm">
                            <span>Learning Progress: <strong>{stats.training_episodes}</strong> interactions</span>
                            <span>Average Engagement: <strong>{(stats.average_reward * 100).toFixed(1)}%</strong></span>
                            <span>Recommendations Accuracy: <strong>{((1 - stats.epsilon) * 100).toFixed(1)}%</strong></span>
                        </div>
                    </AlertDescription>
                </Alert>
            )}

            {/* Tabs for Different Video Sources */}
            <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'foryou' | 'trending')}>
                <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="foryou" className="flex items-center gap-2">
                        <Target className="h-4 w-4" />
                        For You ({personalizedVideos.length})
                    </TabsTrigger>
                    <TabsTrigger value="trending" className="flex items-center gap-2">
                        <TrendingUp className="h-4 w-4" />
                        Trending ({trending.length})
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="foryou" className="mt-6">
                    {loading && personalizedVideos.length === 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {[...Array(6)].map((_, i) => (
                                <Card key={i} className="animate-pulse">
                                    <CardHeader className="space-y-2">
                                        <div className="h-4 bg-muted rounded w-3/4"></div>
                                        <div className="h-3 bg-muted rounded w-1/2"></div>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="aspect-video bg-muted rounded mb-4"></div>
                                        <div className="space-y-2">
                                            <div className="h-3 bg-muted rounded"></div>
                                            <div className="h-3 bg-muted rounded w-2/3"></div>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    ) : genreClusters.length > 0 ? (
                        <div className="space-y-10">
                            {genreClusters.map((cluster) => (
                                <div key={`${cluster.genre}-${cluster.cluster_rank}`} className="space-y-4">
                                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                                        <div>
                                            <div className="flex items-center gap-2">
                                                <Sparkles className="h-4 w-4 text-primary" />
                                                <h3 className="text-xl font-semibold">{cluster.genre}</h3>
                                            </div>
                                            <p className="text-sm text-muted-foreground mt-1">
                                                {cluster.reason}
                                            </p>
                                        </div>
                                        <div className="flex flex-wrap gap-2">
                                            <Badge variant="secondary">Match {Math.round(cluster.combined_score * 100)}%</Badge>
                                            <Badge variant="outline">History {Math.round(cluster.history_score * 100)}%</Badge>
                                            <Badge variant="outline">Persona {Math.round(cluster.personality_score * 100)}%</Badge>
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                        {cluster.videos.map((video) => (
                                            <VideoCard
                                                key={video.id || `${cluster.genre}-${video.youtube_url}`}
                                                video={video}
                                                onFeedback={handleVideoFeedback}
                                                onWatchClick={handleWatchVideo}
                                            />
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : personalizedVideos.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {personalizedVideos.map((video) => (
                                <VideoCard
                                    key={video.id}
                                    video={video}
                                    onFeedback={handleVideoFeedback}
                                    onWatchClick={handleWatchVideo}
                                />
                            ))}
                        </div>
                    ) : (
                        <Card>
                            <CardContent className="p-8 text-center">
                                <div className="text-4xl mb-4">🎬</div>
                                <h3 className="text-lg font-semibold mb-2">No Personalized Videos Yet</h3>
                                <p className="text-muted-foreground mb-4">
                                    Start interacting with videos to get personalized recommendations!
                                </p>
                                <Button onClick={() => setActiveTab('trending')}>
                                    Browse Trending Videos
                                </Button>
                            </CardContent>
                        </Card>
                    )}
                </TabsContent>

                <TabsContent value="trending" className="mt-6">
                    {trending.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {trending.map((video) => (
                                <VideoCard
                                    key={video.id}
                                    video={video}
                                    onFeedback={handleVideoFeedback}
                                    onWatchClick={handleWatchVideo}
                                />
                            ))}
                        </div>
                    ) : (
                        <Card>
                            <CardContent className="p-8 text-center">
                                <div className="text-4xl mb-4">📈</div>
                                <h3 className="text-lg font-semibold mb-2">Loading Trending Videos</h3>
                                <p className="text-muted-foreground">
                                    Fetching the latest trending content...
                                </p>
                            </CardContent>
                        </Card>
                    )}
                </TabsContent>
            </Tabs>
        </div>
    )
}

export default VideoRecommendations