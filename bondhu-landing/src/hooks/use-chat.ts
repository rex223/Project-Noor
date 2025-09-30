/**
 * React Hook for Chat API Integration
 * Manages chat messages, API calls, and conversation state
 */

import { useState, useCallback } from 'react'
import { bondhuAPI, ChatMessageRequest, ChatResponse, ChatMessage } from '@/lib/api-client'

interface UseChatOptions {
    userId: string
    sessionId?: string
}

interface UseChatReturn {
    messages: ChatMessage[]
    isLoading: boolean
    error: string | null
    sendMessage: (message: string, context?: Record<string, any>) => Promise<void>
    clearMessages: () => void
    refreshHistory: () => Promise<void>
}

export function useChat({ userId, sessionId }: UseChatOptions): UseChatReturn {
    const [messages, setMessages] = useState<ChatMessage[]>([])
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const sendMessage = useCallback(async (message: string, context?: Record<string, any>) => {
        if (!message.trim()) return

        setIsLoading(true)
        setError(null)

        try {
            const request: ChatMessageRequest = {
                user_id: userId,
                message: message.trim(),
                session_id: sessionId,
                context: context || {}
            }

            const response = await bondhuAPI.sendChatMessage(request)

            if (response.success && response.data) {
                // Add both user message and AI response to the conversation
                setMessages(prev => [
                    ...prev,
                    response.data.user_message,
                    response.data.ai_response
                ])
            } else {
                throw new Error(response.message || 'Failed to send message')
            }

        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to send message'
            setError(errorMessage)
            console.error('Chat error:', err)
        } finally {
            setIsLoading(false)
        }
    }, [userId, sessionId])

    const clearMessages = useCallback(() => {
        setMessages([])
        setError(null)
    }, [])

    const refreshHistory = useCallback(async () => {
        try {
            setError(null)
            const response = await bondhuAPI.getChatHistory(userId, sessionId, 50)
            
            if (response.success && response.data) {
                // Sort by timestamp to ensure proper order
                const sortedMessages = response.data.sort((a, b) => {
                    const timeA = a.timestamp ? new Date(a.timestamp).getTime() : 0
                    const timeB = b.timestamp ? new Date(b.timestamp).getTime() : 0
                    return timeA - timeB
                })
                setMessages(sortedMessages)
            }
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to load chat history'
            setError(errorMessage)
            console.error('Chat history error:', err)
        }
    }, [userId, sessionId])

    return {
        messages,
        isLoading,
        error,
        sendMessage,
        clearMessages,
        refreshHistory
    }
}

/**
 * Hook for managing chat session state
 */
export function useChatSession() {
    const [sessionId, setSessionId] = useState<string>(() => {
        // Generate a new session ID or use existing one from localStorage
        const existingSession = localStorage.getItem('chat-session-id')
        if (existingSession) {
            return existingSession
        }
        
        const newSession = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
        localStorage.setItem('chat-session-id', newSession)
        return newSession
    })

    const startNewSession = useCallback(() => {
        const newSession = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
        setSessionId(newSession)
        localStorage.setItem('chat-session-id', newSession)
    }, [])

    const clearSession = useCallback(() => {
        localStorage.removeItem('chat-session-id')
        startNewSession()
    }, [startNewSession])

    return {
        sessionId,
        startNewSession,
        clearSession
    }
}