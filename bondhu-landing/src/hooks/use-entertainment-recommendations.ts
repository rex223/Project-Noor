/**
 * React Hook for Entertainment Recommendations
 * Manages fetching, caching, and refreshing of entertainment recommendations
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { useBondhuAPI } from './use-bondhu-api'
import type { EntertainmentRecommendationsResponse, MusicRecommendation, VideoRecommendation, GameRecommendation } from '@/lib/api-client'

export interface UseEntertainmentRecommendationsOptions {
    userId: string
    categories?: ('music' | 'videos' | 'games')[]
    limit_per_category?: number
    auto_refresh_interval?: number // minutes
    include_context?: boolean
    onRecommendationsLoaded?: (recommendations: EntertainmentRecommendationsResponse) => void
    onError?: (error: Error) => void
}

export interface UseEntertainmentRecommendationsReturn {
    // Data
    recommendations: EntertainmentRecommendationsResponse | null
    musicRecommendations: MusicRecommendation[]
    videoRecommendations: VideoRecommendation[]
    gameRecommendations: GameRecommendation[]

    // State
    isLoading: boolean
    error: Error | null
    lastUpdated: Date | null

    // Actions
    refreshRecommendations: (options?: { force?: boolean; mood_override?: string }) => Promise<void>
    recordInteraction: (interaction: {
        content_type: 'music' | 'video' | 'game'
        content_id: string
        interaction_type: 'view' | 'play' | 'like' | 'dislike' | 'skip' | 'complete' | 'share'
        content_title?: string
        duration_seconds?: number
        completion_percentage?: number
        rating?: number
        mood_before?: string
        mood_after?: string
        context?: Record<string, any>
    }) => Promise<boolean>

    // Utilities
    getRecommendationsByMood: (mood: string) => {
        music: MusicRecommendation[]
        videos: VideoRecommendation[]
        games: GameRecommendation[]
    }
    getTopRecommendations: (count?: number) => {
        music: MusicRecommendation[]
        videos: VideoRecommendation[]
        games: GameRecommendation[]
    }
}

export function useEntertainmentRecommendations(
    options: UseEntertainmentRecommendationsOptions
): UseEntertainmentRecommendationsReturn {
    const {
        userId,
        categories = ['music', 'videos', 'games'],
        limit_per_category = 10,
        auto_refresh_interval,
        include_context = true,
        onRecommendationsLoaded,
        onError
    } = options

    const { getEntertainmentRecommendations, recordEntertainmentInteraction } = useBondhuAPI()

    const [recommendations, setRecommendations] = useState<EntertainmentRecommendationsResponse | null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<Error | null>(null)
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

    const refreshTimeoutRef = useRef<NodeJS.Timeout | null>(null)

    // Extract individual recommendation arrays
    const musicRecommendations = recommendations?.recommendations.music || []
    const videoRecommendations = recommendations?.recommendations.videos || []
    const gameRecommendations = recommendations?.recommendations.games || []

    // Get current time context
    const getTimeContext = useCallback((): 'morning' | 'afternoon' | 'evening' | 'night' => {
        const hour = new Date().getHours()
        if (hour < 6) return 'night'
        if (hour < 12) return 'morning'
        if (hour < 18) return 'afternoon'
        if (hour < 22) return 'evening'
        return 'night'
    }, [])

    // Refresh recommendations
    const refreshRecommendations = useCallback(async (refreshOptions?: { force?: boolean; mood_override?: string }) => {
        if (!userId) return

        // Skip if recently loaded and not forced
        if (!refreshOptions?.force && lastUpdated && Date.now() - lastUpdated.getTime() < 60000) {
            return
        }

        setIsLoading(true)
        setError(null)

        try {
            const response = await getEntertainmentRecommendations(userId, {
                categories,
                limit_per_category,
                include_context,
                mood_override: refreshOptions?.mood_override,
                time_context: getTimeContext()
            })

            if (response) {
                setRecommendations(response)
                setLastUpdated(new Date())

                if (onRecommendationsLoaded) {
                    onRecommendationsLoaded(response)
                }
            }
        } catch (err) {
            const error = err as Error
            setError(error)

            if (onError) {
                onError(error)
            }
        } finally {
            setIsLoading(false)
        }
    }, [userId, categories, limit_per_category, include_context, getEntertainmentRecommendations, lastUpdated, getTimeContext, onRecommendationsLoaded, onError])

    // Record user interaction
    const recordInteraction = useCallback(async (interaction: {
        content_type: 'music' | 'video' | 'game'
        content_id: string
        interaction_type: 'view' | 'play' | 'like' | 'dislike' | 'skip' | 'complete' | 'share'
        content_title?: string
        duration_seconds?: number
        completion_percentage?: number
        rating?: number
        mood_before?: string
        mood_after?: string
        context?: Record<string, any>
    }): Promise<boolean> => {
        if (!userId) return false

        try {
            const result = await recordEntertainmentInteraction(userId, interaction)

            // If it's a significant interaction, refresh recommendations
            if (interaction.interaction_type === 'like' ||
                interaction.interaction_type === 'dislike' ||
                interaction.interaction_type === 'complete') {
                // Refresh after a delay to allow backend processing
                setTimeout(() => refreshRecommendations({ force: true }), 2000)
            }

            return result?.success || false
        } catch (err) {
            console.error('Failed to record interaction:', err)
            return false
        }
    }, [userId, recordEntertainmentInteraction, refreshRecommendations])

    // Get recommendations by mood
    const getRecommendationsByMood = useCallback((mood: string) => {
        return {
            music: musicRecommendations.filter(rec =>
                rec.mood.toLowerCase().includes(mood.toLowerCase())
            ),
            videos: videoRecommendations.filter(rec =>
                rec.mood_match.toLowerCase().includes(mood.toLowerCase())
            ),
            games: gameRecommendations.filter(rec =>
                rec.play_style.toLowerCase().includes(mood.toLowerCase())
            )
        }
    }, [musicRecommendations, videoRecommendations, gameRecommendations])

    // Get top recommendations by confidence
    const getTopRecommendations = useCallback((count: number = 3) => {
        return {
            music: musicRecommendations
                .sort((a, b) => b.confidence - a.confidence)
                .slice(0, count),
            videos: videoRecommendations
                .sort((a, b) => b.confidence - a.confidence)
                .slice(0, count),
            games: gameRecommendations
                .sort((a, b) => b.confidence - a.confidence)
                .slice(0, count)
        }
    }, [musicRecommendations, videoRecommendations, gameRecommendations])

    // Initial load
    useEffect(() => {
        if (userId) {
            refreshRecommendations()
        }
    }, [userId, refreshRecommendations])

    // Auto-refresh setup
    useEffect(() => {
        if (auto_refresh_interval && auto_refresh_interval > 0) {
            refreshTimeoutRef.current = setInterval(() => {
                refreshRecommendations()
            }, auto_refresh_interval * 60 * 1000) // Convert minutes to milliseconds

            return () => {
                if (refreshTimeoutRef.current) {
                    clearInterval(refreshTimeoutRef.current)
                }
            }
        }
    }, [auto_refresh_interval, refreshRecommendations])

    // Cleanup
    useEffect(() => {
        return () => {
            if (refreshTimeoutRef.current) {
                clearInterval(refreshTimeoutRef.current)
            }
        }
    }, [])

    return {
        recommendations,
        musicRecommendations,
        videoRecommendations,
        gameRecommendations,
        isLoading,
        error,
        lastUpdated,
        refreshRecommendations,
        recordInteraction,
        getRecommendationsByMood,
        getTopRecommendations
    }
}

export default useEntertainmentRecommendations