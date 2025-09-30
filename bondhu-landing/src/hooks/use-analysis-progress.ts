/**
 * Custom hook for managing analysis progress tracking
 * Provides real-time updates, step management, and status monitoring
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { useBondhuAPI } from './use-bondhu-api'
import type { AnalysisStep } from '@/components/ui/progress-tracking'

export interface UseAnalysisProgressOptions {
    analysisId?: string
    pollInterval?: number
    maxRetries?: number
    onComplete?: (result: any) => void
    onError?: (error: Error) => void
    onStepUpdate?: (step: AnalysisStep) => void
}

export interface AnalysisProgressState {
    // Progress tracking
    overallProgress: number
    currentStep?: string
    steps: AnalysisStep[]
    status: 'idle' | 'queued' | 'processing' | 'completed' | 'failed'

    // Timing
    startTime?: Date
    endTime?: Date
    elapsedTime: number
    estimatedTimeRemaining?: number

    // Results
    result?: any
    error?: Error

    // Metadata
    analysisId?: string
    retryCount: number
}

const DEFAULT_STEPS: AnalysisStep[] = [
    {
        id: 'initialization',
        name: 'Initializing Analysis',
        description: 'Setting up analysis pipeline and validating inputs',
        status: 'pending',
        progress: 0,
        agent: 'orchestrator'
    },
    {
        id: 'music_analysis',
        name: 'Music Preference Analysis',
        description: 'Analyzing musical preferences and patterns',
        status: 'pending',
        progress: 0,
        agent: 'music'
    },
    {
        id: 'video_analysis',
        name: 'Video Content Analysis',
        description: 'Processing video consumption patterns',
        status: 'pending',
        progress: 0,
        agent: 'video'
    },
    {
        id: 'gaming_analysis',
        name: 'Gaming Behavior Analysis',
        description: 'Evaluating gaming preferences and style',
        status: 'pending',
        progress: 0,
        agent: 'gaming'
    },
    {
        id: 'personality_synthesis',
        name: 'Personality Synthesis',
        description: 'Integrating insights into comprehensive personality profile',
        status: 'pending',
        progress: 0,
        agent: 'personality'
    },
    {
        id: 'finalization',
        name: 'Finalizing Results',
        description: 'Generating recommendations and saving profile',
        status: 'pending',
        progress: 0,
        agent: 'orchestrator'
    }
]

export function useAnalysisProgress(options: UseAnalysisProgressOptions = {}) {
    const {
        analysisId,
        pollInterval = 2000,
        maxRetries = 3,
        onComplete,
        onError,
        onStepUpdate
    } = options

    const { getAnalysisStatus } = useBondhuAPI()
    const [state, setState] = useState<AnalysisProgressState>({
        overallProgress: 0,
        steps: DEFAULT_STEPS,
        status: 'idle',
        elapsedTime: 0,
        retryCount: 0
    })

    const pollIntervalRef = useRef<NodeJS.Timeout | null>(null)
    const elapsedTimeIntervalRef = useRef<NodeJS.Timeout | null>(null)

    // Calculate overall progress based on step completion
    const calculateOverallProgress = useCallback((steps: AnalysisStep[]): number => {
        const totalSteps = steps.length
        const completedSteps = steps.filter(step => step.status === 'completed').length
        const activeStep = steps.find(step => step.status === 'active')

        let progress = (completedSteps / totalSteps) * 100

        // Add partial progress from active step
        if (activeStep && activeStep.progress > 0) {
            progress += (activeStep.progress / totalSteps)
        }

        return Math.min(progress, 100)
    }, [])

    // Update step status and progress
    const updateStep = useCallback((stepId: string, updates: Partial<AnalysisStep>) => {
        setState(prev => {
            const newSteps = prev.steps.map(step =>
                step.id === stepId ? { ...step, ...updates } : step
            )

            const updatedStep = newSteps.find(step => step.id === stepId)
            if (updatedStep && onStepUpdate) {
                onStepUpdate(updatedStep)
            }

            return {
                ...prev,
                steps: newSteps,
                overallProgress: calculateOverallProgress(newSteps)
            }
        })
    }, [calculateOverallProgress, onStepUpdate])

    // Parse backend status response into step updates
    const parseBackendStatus = useCallback((backendStatus: any) => {
        if (!backendStatus) return

        const { stage, progress, agent_statuses, error } = backendStatus

        // Map backend stages to our step IDs
        const stageMapping: Record<string, string> = {
            'initializing': 'initialization',
            'music_analysis': 'music_analysis',
            'video_analysis': 'video_analysis',
            'gaming_analysis': 'gaming_analysis',
            'personality_synthesis': 'personality_synthesis',
            'finalizing': 'finalization'
        }

        const currentStepId = stageMapping[stage] || 'initialization'

        // Update step statuses based on current stage
        setState(prev => {
            const newSteps = prev.steps.map(step => {
                if (step.id === currentStepId) {
                    return {
                        ...step,
                        status: 'active' as const,
                        progress: progress || 0,
                        error_message: error
                    }
                } else if (prev.steps.findIndex(s => s.id === step.id) < prev.steps.findIndex(s => s.id === currentStepId)) {
                    return {
                        ...step,
                        status: 'completed' as const,
                        progress: 100
                    }
                } else {
                    return step
                }
            })

            return {
                ...prev,
                steps: newSteps,
                currentStep: prev.steps.find(s => s.id === currentStepId)?.name,
                overallProgress: calculateOverallProgress(newSteps)
            }
        })
    }, [calculateOverallProgress])

    // Poll for analysis status
    const pollStatus = useCallback(async () => {
        if (!analysisId || state.status === 'completed' || state.status === 'failed') {
            return
        }

        try {
            const status = await getAnalysisStatus(analysisId)

            if (status && status.status === 'completed') {
                setState(prev => ({
                    ...prev,
                    status: 'completed',
                    endTime: new Date(),
                    overallProgress: 100,
                    result: status.scores,
                    steps: prev.steps.map(step => ({ ...step, status: 'completed', progress: 100 }))
                }))

                if (onComplete) {
                    onComplete(status.scores)
                }
            } else if (status && status.status === 'failed') {
                setState(prev => ({
                    ...prev,
                    status: 'failed',
                    endTime: new Date(),
                    error: new Error(status.error_message || 'Analysis failed')
                }))

                if (onError) {
                    onError(new Error(status.error_message || 'Analysis failed'))
                }
            } else if (status && status.status === 'processing') {
                setState(prev => ({ ...prev, status: 'processing' }))
                parseBackendStatus(status)
            }
        } catch (error) {
            console.error('Error polling analysis status:', error)

            setState(prev => ({
                ...prev,
                retryCount: prev.retryCount + 1
            }))

            // Stop polling if max retries reached
            if (state.retryCount >= maxRetries) {
                setState(prev => ({
                    ...prev,
                    status: 'failed',
                    error: error as Error
                }))

                if (onError) {
                    onError(error as Error)
                }
            }
        }
    }, [analysisId, state.status, state.retryCount, maxRetries, getAnalysisStatus, parseBackendStatus, onComplete, onError])

    // Start analysis tracking
    const startTracking = useCallback((newAnalysisId: string) => {
        setState(prev => ({
            ...prev,
            analysisId: newAnalysisId,
            status: 'queued',
            startTime: new Date(),
            endTime: undefined,
            overallProgress: 0,
            steps: DEFAULT_STEPS,
            error: undefined,
            result: undefined,
            retryCount: 0
        }))
    }, [])

    // Stop analysis tracking
    const stopTracking = useCallback(() => {
        if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current)
        }
        if (elapsedTimeIntervalRef.current) {
            clearInterval(elapsedTimeIntervalRef.current)
        }
        setState(prev => ({ ...prev, status: 'idle' }))
    }, [])

    // Reset progress state
    const resetProgress = useCallback(() => {
        stopTracking()
        setState({
            overallProgress: 0,
            steps: DEFAULT_STEPS,
            status: 'idle',
            elapsedTime: 0,
            retryCount: 0
        })
    }, [stopTracking])

    // Setup polling when analysis starts
    useEffect(() => {
        if (analysisId && (state.status === 'queued' || state.status === 'processing')) {
            pollIntervalRef.current = setInterval(pollStatus, pollInterval)

            return () => {
                if (pollIntervalRef.current) {
                    clearInterval(pollIntervalRef.current)
                }
            }
        }
    }, [analysisId, state.status, pollInterval, pollStatus])

    // Track elapsed time
    useEffect(() => {
        if (state.startTime && state.status === 'processing') {
            elapsedTimeIntervalRef.current = setInterval(() => {
                setState(prev => ({
                    ...prev,
                    elapsedTime: Math.floor((Date.now() - (prev.startTime?.getTime() || 0)) / 1000)
                }))
            }, 1000)

            return () => {
                if (elapsedTimeIntervalRef.current) {
                    clearInterval(elapsedTimeIntervalRef.current)
                }
            }
        }
    }, [state.startTime, state.status])

    return {
        ...state,
        startTracking,
        stopTracking,
        resetProgress,
        updateStep,
        isTracking: state.status === 'queued' || state.status === 'processing'
    }
}

export default useAnalysisProgress