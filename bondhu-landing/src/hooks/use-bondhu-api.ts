/**
 * React Hooks for Bondhu AI API Integration
 * Provides easy-to-use hooks for frontend components
 */

import { useState, useEffect, useCallback } from 'react'
import { bondhuAPI, PersonalityAnalysisRequest, PersonalityAnalysisResponse, AgentStatusResponse } from '@/lib/api-client'

export interface UsePersonalityAnalysisOptions {
    onProgress?: (response: PersonalityAnalysisResponse) => void
    onComplete?: (response: PersonalityAnalysisResponse) => void
    onError?: (error: Error) => void
    autoStart?: boolean
}

export interface UsePersonalityAnalysisReturn {
    triggerAnalysis: (request: PersonalityAnalysisRequest) => Promise<void>
    isLoading: boolean
    progress: number
    currentStep: string | null
    result: PersonalityAnalysisResponse | null
    error: Error | null
    reset: () => void
}

/**
 * Hook for triggering and monitoring personality analysis
 */
export function usePersonalityAnalysis(
    options: UsePersonalityAnalysisOptions = {}
): UsePersonalityAnalysisReturn {
    const [isLoading, setIsLoading] = useState(false)
    const [progress, setProgress] = useState(0)
    const [currentStep, setCurrentStep] = useState<string | null>(null)
    const [result, setResult] = useState<PersonalityAnalysisResponse | null>(null)
    const [error, setError] = useState<Error | null>(null)

    const reset = useCallback(() => {
        setIsLoading(false)
        setProgress(0)
        setCurrentStep(null)
        setResult(null)
        setError(null)
    }, [])

    const triggerAnalysis = useCallback(async (request: PersonalityAnalysisRequest) => {
        reset()
        setIsLoading(true)

        try {
            // Start the analysis
            const initialResponse = await bondhuAPI.triggerPersonalityAnalysis(request)

            // If analysis completed immediately (cached result)
            if (initialResponse.status === 'completed') {
                setResult(initialResponse)
                setProgress(100)
                setCurrentStep('Completed')
                options.onComplete?.(initialResponse)
                return
            }

            // Poll for completion
            const finalResponse = await bondhuAPI.pollAnalysisStatus(
                initialResponse.analysis_id,
                (progressResponse) => {
                    setProgress(progressResponse.progress || 0)
                    setCurrentStep(progressResponse.current_step || null)
                    options.onProgress?.(progressResponse)
                }
            )

            setResult(finalResponse)
            setProgress(100)
            setCurrentStep('Completed')
            options.onComplete?.(finalResponse)

        } catch (err) {
            const error = err instanceof Error ? err : new Error('Analysis failed')
            setError(error)
            options.onError?.(error)
        } finally {
            setIsLoading(false)
        }
    }, [options, reset])

    return {
        triggerAnalysis,
        isLoading,
        progress,
        currentStep,
        result,
        error,
        reset,
    }
}

/**
 * Hook for fetching existing personality profile
 */
export function usePersonalityProfile(userId: string | null) {
    const [profile, setProfile] = useState<PersonalityAnalysisResponse | null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<Error | null>(null)

    const fetchProfile = useCallback(async (includeHistory = false) => {
        if (!userId) return

        setIsLoading(true)
        setError(null)

        try {
            const response = await bondhuAPI.getPersonalityProfile(userId, includeHistory)
            setProfile(response)
        } catch (err) {
            const error = err instanceof Error ? err : new Error('Failed to fetch profile')
            setError(error)
        } finally {
            setIsLoading(false)
        }
    }, [userId])

    useEffect(() => {
        fetchProfile()
    }, [fetchProfile])

    return {
        profile,
        isLoading,
        error,
        refetch: fetchProfile,
    }
}

/**
 * Hook for monitoring agent system status
 */
export function useAgentStatus() {
    const [status, setStatus] = useState<AgentStatusResponse | null>(null)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<Error | null>(null)

    const fetchStatus = useCallback(async () => {
        setIsLoading(true)
        setError(null)

        try {
            const response = await bondhuAPI.getAgentStatus()
            setStatus(response)
        } catch (err) {
            const error = err instanceof Error ? err : new Error('Failed to fetch agent status')
            setError(error)
        } finally {
            setIsLoading(false)
        }
    }, [])

    useEffect(() => {
        fetchStatus()

        // Poll status every 30 seconds
        const interval = setInterval(fetchStatus, 30000)
        return () => clearInterval(interval)
    }, [fetchStatus])

    return {
        status,
        isLoading,
        error,
        refetch: fetchStatus,
    }
}

/**
 * Hook for connecting external services (e.g., Spotify)
 */
export function useServiceConnection() {
    const [isConnecting, setIsConnecting] = useState(false)
    const [error, setError] = useState<Error | null>(null)

    const connectSpotify = useCallback(async (userId: string) => {
        setIsConnecting(true)
        setError(null)

        try {
            const response = await bondhuAPI.connectSpotify(userId)

            // Open auth URL in new window
            window.open(response.auth_url, 'spotify-auth', 'width=500,height=600')

            return response.auth_url
        } catch (err) {
            const error = err instanceof Error ? err : new Error('Failed to connect Spotify')
            setError(error)
            throw error
        } finally {
            setIsConnecting(false)
        }
    }, [])

    return {
        connectSpotify,
        isConnecting,
        error,
    }
}

/**
 * Main Bondhu API Hook
 * Combines all API functionality into a single convenient hook
 */
export function useBondhuAPI() {
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<Error | null>(null)

    const analyzePersonality = useCallback(async (request: PersonalityAnalysisRequest) => {
        setIsLoading(true)
        setError(null)

        try {
            const response = await bondhuAPI.triggerPersonalityAnalysis(request)
            return response
        } catch (err) {
            const error = err instanceof Error ? err : new Error('Analysis failed')
            setError(error)
            throw error
        } finally {
            setIsLoading(false)
        }
    }, [])

    const getPersonalityProfile = useCallback(async (userId: string) => {
        setIsLoading(true)
        setError(null)

        try {
            const response = await bondhuAPI.getPersonalityProfile(userId)
            return response
        } catch (err) {
            const error = err instanceof Error ? err : new Error('Failed to get profile')
            setError(error)
            throw error
        } finally {
            setIsLoading(false)
        }
    }, [])

    const getAnalysisStatus = useCallback(async (analysisId: string) => {
        try {
            const response = await bondhuAPI.getAnalysisStatus(analysisId)
            return response
        } catch (err) {
            // Don't set loading/error state for status checks as they're background operations
            console.warn('Status check failed:', err)
            return null
        }
    }, [])

    const getAgentStatus = useCallback(async () => {
        try {
            const response = await bondhuAPI.getAgentStatus()
            return response
        } catch (err) {
            console.warn('Agent status check failed:', err)
            return null
        }
    }, [])

    // Entertainment recommendation functions
    const getEntertainmentRecommendations = useCallback(async (
        userId: string,
        options?: {
            categories?: ('music' | 'videos' | 'games')[]
            limit_per_category?: number
            include_context?: boolean
            mood_override?: string
            time_context?: 'morning' | 'afternoon' | 'evening' | 'night'
        }
    ) => {
        try {
            // Call individual category endpoints for real data
            const results: any = {
                user_id: userId,
                recommendations: {
                    music: [],
                    videos: [],
                    games: []
                },
                generated_at: new Date().toISOString(),
                context: {
                    time_of_day: options?.time_context || 'afternoon',
                    day_of_week: new Date().toLocaleDateString('en-US', { weekday: 'long' }),
                    mood_detected: options?.mood_override,
                    recent_activity: []
                },
                overall_confidence: 0,
                personalization_factors: {
                    personality_weight: 0.6,
                    activity_history_weight: 0.3,
                    current_context_weight: 0.1
                }
            }

            const categories = options?.categories || ['music', 'videos', 'games']
            const limit = options?.limit_per_category || 12

            // Fetch music recommendations if requested
            if (categories.includes('music')) {
                try {
                    const musicResponse = await bondhuAPI.getMusicRecommendations(userId, {
                        limit,
                        mood: options?.mood_override,
                        refresh: false
                    })

                    if (musicResponse.success && musicResponse.data) {
                        results.recommendations.music = musicResponse.data
                    }
                } catch (err) {
                    console.error('Music recommendations failed:', err)
                }
            }

            // Fetch video recommendations if requested
            if (categories.includes('videos')) {
                try {
                    const videoResponse = await bondhuAPI.getVideoRecommendations(userId, {
                        limit,
                        mood: options?.mood_override,
                        refresh: false
                    })

                    if (videoResponse.success && videoResponse.data) {
                        results.recommendations.videos = videoResponse.data
                    }
                } catch (err) {
                    console.error('Video recommendations failed:', err)
                }
            }

            // TODO: Add games recommendations when endpoint is implemented

            return results
        } catch (err) {
            console.error('Entertainment recommendations failed:', err)
            setError(err as Error)
            return null
        }
    }, [])

    const recordEntertainmentInteraction = useCallback(async (
        userId: string,
        interaction: {
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
        }
    ) => {
        try {
            const response = await bondhuAPI.recordInteraction(userId, interaction)
            return response
        } catch (err) {
            console.error('Recording interaction failed:', err)
            return { success: false, data: null, message: 'Failed to record interaction' }
        }
    }, [])

    const getEntertainmentHistory = useCallback(async (
        userId: string,
        options?: {
            days_back?: number
            content_types?: ('music' | 'video' | 'game')[]
            limit?: number
        }
    ) => {
        try {
            const response = await bondhuAPI.getEntertainmentHistory(userId, options)
            return response
        } catch (err) {
            console.error('Entertainment history failed:', err)
            return null
        }
    }, [])

    return {
        // Analysis functions
        analyzePersonality,
        getPersonalityProfile,
        getAnalysisStatus,
        getAgentStatus,

        // Entertainment functions
        getEntertainmentRecommendations,
        recordEntertainmentInteraction,
        getEntertainmentHistory,

        // State
        isLoading,
        error,

        // Individual hooks for more specific use cases
        usePersonalityAnalysis,
        usePersonalityProfile,
        useAgentStatus,
        useServiceConnection,
    }
}