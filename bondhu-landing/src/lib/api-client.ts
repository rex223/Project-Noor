/**
 * API Client for Bondhu AI Backend
 * Handles all communication with the FastAPI backend running LangChain/LangGraph orchestration
 */

import { getApiBaseUrl } from './env-config'

export interface PersonalityAnalysisRequest {
    user_id: string
    requested_agents?: ('music' | 'video' | 'gaming')[]
    force_refresh?: boolean
    include_cross_modal?: boolean
    survey_responses?: Record<string, any>
    conversation_history?: Array<{
        speaker: string
        message: string
        timestamp: string
    }>
}

export interface PersonalityTrait {
    trait: string
    score: number
    confidence: number
    confidence_level: 'low' | 'medium' | 'high'
    data_points: number
    description?: string
}

export interface PersonalityAnalysisResponse {
    user_id: string
    analysis_id: string
    status: 'queued' | 'processing' | 'completed' | 'failed'
    progress?: number
    current_step?: string
    scores?: {
        openness: PersonalityTrait
        conscientiousness: PersonalityTrait
        extraversion: PersonalityTrait
        agreeableness: PersonalityTrait
        neuroticism: PersonalityTrait
    }
    overall_confidence: number
    data_sources: string[]
    processing_time?: number
    created_at: string
    completed_at?: string
    error_message?: string
    warnings?: string[]
}

export interface AgentStatusResponse {
    status: 'healthy' | 'degraded' | 'unhealthy'
    agents: {
        music: { status: string; last_check: string; error?: string }
        video: { status: string; last_check: string; error?: string }
        gaming: { status: string; last_check: string; error?: string }
        personality: { status: string; last_check: string; error?: string }
    }
    orchestrator: {
        status: string
        active_analyses: number
        queue_size: number
    }
}

export interface MusicRecommendation {
    type: 'song' | 'artist' | 'playlist' | 'genre'
    title: string
    artist?: string
    genre?: string
    mood: string
    energy_level: number
    reasoning: string
    confidence: number
    spotify_id?: string
    youtube_url?: string
    preview_url?: string
}

export interface VideoRecommendation {
    type: 'movie' | 'tv_show' | 'documentary' | 'youtube' | 'short_form'
    title: string
    creator?: string
    duration_minutes?: number
    genre: string
    mood_match: string
    reasoning: string
    confidence: number
    platform?: string
    imdb_id?: string
    youtube_url?: string
    thumbnail?: string
}

export interface GameRecommendation {
    type: 'mobile' | 'pc' | 'console' | 'web' | 'vr'
    title: string
    developer?: string
    genre: string
    play_style: string
    difficulty_level: 'easy' | 'medium' | 'hard' | 'adaptive'
    reasoning: string
    confidence: number
    platform?: string
    steam_id?: string
    play_store_url?: string
    estimated_play_time?: number
}

export interface EntertainmentRecommendationsResponse {
    user_id: string
    recommendations: {
        music: MusicRecommendation[]
        videos: VideoRecommendation[]
        games: GameRecommendation[]
    }
    generated_at: string
    context: {
        time_of_day: string
        day_of_week: string
        mood_detected?: string
        recent_activity: string[]
    }
    overall_confidence: number
    personalization_factors: {
        personality_weight: number
        activity_history_weight: number
        current_context_weight: number
    }
}

export interface APIError {
    error: string
    message: string
    status_code: number
    details?: Record<string, any>
}

// Chat interfaces
export interface ChatMessage {
    role: 'user' | 'assistant'
    content: string
    timestamp?: string
}

export interface ChatRequest {
    user_id: string
    message: string
    conversation_history?: ChatMessage[]
    session_id?: string
    personality_context?: boolean
}

export interface ChatResponse {
    message: string
    session_id: string
    timestamp: string
    mood_detected?: string
    sentiment_score?: number
}

export interface APIResponse<T> {
    success: boolean
    data: T | null
    message: string
    error_code?: string
    timestamp?: string
}

// Entertainment interaction interfaces
export interface InteractionRequest {
    content_id: string
    content_type: 'music' | 'video' | 'game'
    interaction_type: 'view' | 'play' | 'like' | 'dislike' | 'skip' | 'complete' | 'share'
    content_title?: string
    duration_seconds?: number
    completion_percentage?: number
    mood_before?: string
    mood_after?: string
    rating?: number
    context?: Record<string, any>
}

export interface InteractionStats {
    total_interactions: number
    like_rate: number
    completion_rate: number
    most_engaged_content_type: string
    recent_mood_trend?: string
}

class BondhuAPIClient {
    private baseURL: string
    private timeout: number = 30000 // 30 seconds default

    constructor() {
        this.baseURL = getApiBaseUrl()
    }

    private async makeRequest<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const url = `${this.baseURL}${endpoint}`

        const defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        const config: RequestInit = {
            ...options,
            headers: {
                ...defaultHeaders,
                ...options.headers,
            },
        }

        // Add timeout using AbortController
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), this.timeout)

        try {
            const response = await fetch(url, {
                ...config,
                signal: controller.signal,
            })

            clearTimeout(timeoutId)

            if (!response.ok) {
                let errorData: APIError
                try {
                    errorData = await response.json()
                } catch {
                    errorData = {
                        error: 'API Error',
                        message: `HTTP ${response.status}: ${response.statusText}`,
                        status_code: response.status,
                    }
                }
                
                // Handle different error response formats
                const errorMessage = errorData.message || 
                                   (errorData as any).detail || // FastAPI returns 'detail' field
                                   errorData.error || 
                                   `HTTP ${response.status}: ${response.statusText}` ||
                                   'Unknown API error'
                
                // Log full error for debugging
                console.error('API Error Details:', {
                    status: response.status,
                    statusText: response.statusText,
                    errorData: errorData,
                    url: response.url
                })
                
                throw new Error(`API Error: ${errorMessage}`)
            }

            return await response.json()
        } catch (error) {
            clearTimeout(timeoutId)

            if (error instanceof Error && error.name === 'AbortError') {
                throw new Error('Request timeout - the analysis is taking longer than expected')
            }

            if (error instanceof TypeError && error.message.includes('fetch')) {
                throw new Error('Unable to connect to Bondhu AI backend. Please check if the service is running.')
            }

            throw error
        }
    }

    /**
     * Trigger personality analysis for a user
     */
    async triggerPersonalityAnalysis(
        request: PersonalityAnalysisRequest
    ): Promise<PersonalityAnalysisResponse> {
        return this.makeRequest<PersonalityAnalysisResponse>(
            '/api/v1/personality/analyze',
            {
                method: 'POST',
                body: JSON.stringify(request),
            }
        )
    }

    /**
     * Get personality profile for a user
     */
    async getPersonalityProfile(
        userId: string,
        includeHistory: boolean = false
    ): Promise<PersonalityAnalysisResponse> {
        const params = new URLSearchParams()
        if (includeHistory) {
            params.append('include_history', 'true')
        }

        const query = params.toString() ? `?${params.toString()}` : ''
        return this.makeRequest<PersonalityAnalysisResponse>(
            `/api/v1/personality/${userId}${query}`
        )
    }

    /**
     * Get analysis status by analysis ID
     */
    async getAnalysisStatus(analysisId: string): Promise<PersonalityAnalysisResponse> {
        return this.makeRequest<PersonalityAnalysisResponse>(
            `/api/v1/personality/status/${analysisId}`
        )
    }

    /**
     * Get agent system status
     */
    async getAgentStatus(): Promise<AgentStatusResponse> {
        return this.makeRequest<AgentStatusResponse>('/api/v1/agents/status')
    }

    /**
     * Get system health check
     */
    async getHealthCheck(): Promise<{
        status: string
        timestamp: string
        version: string
        components: Record<string, string>
    }> {
        return this.makeRequest('/health')
    }

    /**
     * Connect Spotify for music analysis
     */
    async connectSpotify(userId: string): Promise<{ auth_url: string }> {
        return this.makeRequest<{ auth_url: string }>(
            `/api/v1/agents/music/connect?user_id=${userId}`
        )
    }

    /**
     * Poll for analysis completion with automatic retries
     */
    async pollAnalysisStatus(
        analysisId: string,
        onProgress?: (response: PersonalityAnalysisResponse) => void,
        maxAttempts: number = 60, // 5 minutes with 5-second intervals
        intervalMs: number = 5000
    ): Promise<PersonalityAnalysisResponse> {
        let attempts = 0

        const poll = async (): Promise<PersonalityAnalysisResponse> => {
            attempts++

            try {
                const response = await this.getAnalysisStatus(analysisId)

                if (onProgress) {
                    onProgress(response)
                }

                if (response.status === 'completed') {
                    return response
                }

                if (response.status === 'failed') {
                    throw new Error(response.error_message || 'Analysis failed')
                }

                if (attempts >= maxAttempts) {
                    throw new Error('Analysis timeout - maximum polling attempts reached')
                }

                // Continue polling for 'queued' or 'processing' status
                await new Promise(resolve => setTimeout(resolve, intervalMs))
                return poll()

            } catch (error) {
                if (attempts >= maxAttempts) {
                    throw error
                }

                // Retry on network errors
                await new Promise(resolve => setTimeout(resolve, intervalMs))
                return poll()
            }
        }

        return poll()
    }

    /**
     * Get entertainment recommendations for a user
     */
    async getEntertainmentRecommendations(
        userId: string,
        options: {
            categories?: ('music' | 'videos' | 'games')[]
            limit_per_category?: number
            include_context?: boolean
            mood_override?: string
            time_context?: 'morning' | 'afternoon' | 'evening' | 'night'
        } = {}
    ): Promise<EntertainmentRecommendationsResponse> {
        const params = new URLSearchParams()

        if (options.categories?.length) {
            params.append('categories', options.categories.join(','))
        }
        if (options.limit_per_category) {
            params.append('limit_per_category', options.limit_per_category.toString())
        }
        if (options.include_context !== undefined) {
            params.append('include_context', options.include_context.toString())
        }
        if (options.mood_override) {
            params.append('mood_override', options.mood_override)
        }
        if (options.time_context) {
            params.append('time_context', options.time_context)
        }

        const queryString = params.toString()
        const endpoint = `/entertainment/recommendations/${userId}${queryString ? `?${queryString}` : ''}`

        return this.makeRequest<EntertainmentRecommendationsResponse>(endpoint, {
            method: 'GET'
        })
    }

    /**
     * Record user interaction with entertainment content
     */
    async recordEntertainmentInteraction(
        userId: string,
        interaction: {
            content_type: 'music' | 'video' | 'game'
            content_id: string
            interaction_type: 'play' | 'pause' | 'skip' | 'like' | 'dislike' | 'complete' | 'share'
            duration_seconds?: number
            completion_percentage?: number
            rating?: number
            context?: Record<string, any>
        }
    ): Promise<{ success: boolean; message: string }> {
        return this.makeRequest<{ success: boolean; message: string }>(`/entertainment/interactions/${userId}`, {
            method: 'POST',
            body: JSON.stringify(interaction)
        })
    }

    /**
     * Get user's entertainment activity history
     */
    async getEntertainmentHistory(
        userId: string,
        options: {
            days_back?: number
            content_types?: ('music' | 'video' | 'game')[]
            limit?: number
        } = {}
    ): Promise<{
        activities: Array<{
            timestamp: string
            content_type: string
            content_id: string
            content_title: string
            interaction_type: string
            duration_seconds?: number
            rating?: number
        }>
        summary: {
            total_interactions: number
            most_active_category: string
            average_session_duration: number
            favorite_genres: string[]
        }
    }> {
        const params = new URLSearchParams()

        if (options.days_back) {
            params.append('days_back', options.days_back.toString())
        }
        if (options.content_types?.length) {
            params.append('content_types', options.content_types.join(','))
        }
        if (options.limit) {
            params.append('limit', options.limit.toString())
        }

        const queryString = params.toString()
        const endpoint = `/entertainment/history/${userId}${queryString ? `?${queryString}` : ''}`

        return this.makeRequest(endpoint, { method: 'GET' })
    }

    /**
     * Send a chat message and get AI response
     */
    async sendChatMessage(request: ChatRequest): Promise<APIResponse<ChatResponse>> {
        return this.makeRequest<APIResponse<ChatResponse>>('/api/v1/chat/send', {
            method: 'POST',
            body: JSON.stringify(request)
        })
    }

    /**
     * Get chat history for a user
     */
    async getChatHistory(
        userId: string,
        options: {
            session_id?: string
            limit?: number
        } = {}
    ): Promise<APIResponse<ChatMessage[]>> {
        const params = new URLSearchParams()

        if (options.session_id) {
            params.append('session_id', options.session_id)
        }
        if (options.limit) {
            params.append('limit', options.limit.toString())
        }

        const queryString = params.toString()
        const endpoint = `/api/v1/chat/history/${userId}${queryString ? `?${queryString}` : ''}`

        return this.makeRequest<APIResponse<ChatMessage[]>>(endpoint, {
            method: 'GET'
        })
    }

    /**
     * Delete a chat session
     */
    async deleteChatSession(userId: string, sessionId: string): Promise<APIResponse<{ deleted: boolean }>> {
        return this.makeRequest<APIResponse<{ deleted: boolean }>>(`/api/v1/chat/history/${userId}/${sessionId}`, {
            method: 'DELETE'
        })
    }

    /**
     * Get personalized music recommendations from Spotify based on personality
     */
    async getMusicRecommendations(
        userId: string,
        options: {
            limit?: number
            mood?: string
            refresh?: boolean
        } = {}
    ): Promise<APIResponse<MusicRecommendation[]>> {
        const params = new URLSearchParams()

        if (options.limit) {
            params.append('limit', options.limit.toString())
        }
        if (options.mood) {
            params.append('mood', options.mood)
        }
        if (options.refresh !== undefined) {
            params.append('refresh', options.refresh.toString())
        }

        const queryString = params.toString()
        const endpoint = `/api/v1/entertainment/music/recommendations/${userId}${queryString ? `?${queryString}` : ''}`

        return this.makeRequest<APIResponse<MusicRecommendation[]>>(endpoint, {
            method: 'GET'
        })
    }

    /**
     * Get personalized video recommendations from YouTube based on personality
     */
    async getVideoRecommendations(
        userId: string,
        options: {
            limit?: number
            mood?: string
            refresh?: boolean
        } = {}
    ): Promise<APIResponse<VideoRecommendation[]>> {
        const params = new URLSearchParams()

        if (options.limit) {
            params.append('limit', options.limit.toString())
        }
        if (options.mood) {
            params.append('mood', options.mood)
        }
        if (options.refresh !== undefined) {
            params.append('refresh', options.refresh.toString())
        }

        const queryString = params.toString()
        const endpoint = `/api/v1/entertainment/video/recommendations/${userId}${queryString ? `?${queryString}` : ''}`

        return this.makeRequest<APIResponse<VideoRecommendation[]>>(endpoint, {
            method: 'GET'
        })
    }

    /**
     * Record user interaction with entertainment content for RL training
     */
    async recordInteraction(
        userId: string,
        interaction: InteractionRequest
    ): Promise<APIResponse<{ recorded: boolean }>> {
        return this.makeRequest<APIResponse<{ recorded: boolean }>>(
            `/api/v1/entertainment/interactions/${userId}`,
            {
                method: 'POST',
                body: JSON.stringify(interaction)
            }
        )
    }

    /**
     * Get user interaction statistics
     */
    async getInteractionStats(
        userId: string
    ): Promise<APIResponse<InteractionStats>> {
        return this.makeRequest<APIResponse<InteractionStats>>(
            `/api/v1/entertainment/interactions/${userId}/stats`,
            {
                method: 'GET'
            }
        )
    }

    /**
     * Trigger personality profile update for a user
     * Aggregates insights from chat and entertainment interactions
     */
    async updatePersonalityProfile(
        userId: string
    ): Promise<APIResponse<{
        updated: boolean
        insights_processed: number
        trait_changes: Record<string, number>
    }>> {
        return this.makeRequest(
            `/api/v1/chat/personality/update/${userId}`,
            {
                method: 'POST'
            }
        )
    }

    /**
     * Set custom timeout for requests
     */
    setTimeout(timeoutMs: number): void {
        this.timeout = timeoutMs
    }

    /**
     * Get current API base URL
     */
    getBaseURL(): string {
        return this.baseURL
    }
}

// Export singleton instance
export const bondhuAPI = new BondhuAPIClient()