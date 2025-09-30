/**
 * Advanced Progress Tracking Component for Bondhu AI Analysis
 * Provides detailed progress visualization with agent status and step tracking
 */

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
    Music,
    Video,
    Gamepad2,
    Brain,
    CheckCircle,
    Clock,
    AlertCircle,
    RefreshCw,
    TrendingUp,
    Zap
} from 'lucide-react'

export interface AnalysisStep {
    id: string
    name: string
    description: string
    status: 'pending' | 'active' | 'completed' | 'failed'
    progress: number
    agent?: 'music' | 'video' | 'gaming' | 'personality' | 'orchestrator'
    estimated_time?: number
    actual_time?: number
    error_message?: string
}

export interface ProgressTrackingProps {
    analysisId?: string
    overallProgress: number
    currentStep?: string
    steps: AnalysisStep[]
    status: 'idle' | 'queued' | 'processing' | 'completed' | 'failed'
    onCancel?: () => void
    onRetry?: () => void
    showDetails?: boolean
    compact?: boolean
    startTime?: Date
    estimatedDuration?: number
}

const agentIcons = {
    music: Music,
    video: Video,
    gaming: Gamepad2,
    personality: Brain,
    orchestrator: TrendingUp
}

const agentColors = {
    music: 'text-purple-600 bg-purple-100 dark:bg-purple-900/20',
    video: 'text-red-600 bg-red-100 dark:bg-red-900/20',
    gaming: 'text-blue-600 bg-blue-100 dark:bg-blue-900/20',
    personality: 'text-green-600 bg-green-100 dark:bg-green-900/20',
    orchestrator: 'text-orange-600 bg-orange-100 dark:bg-orange-900/20'
}

export function ProgressTracking({
    analysisId,
    overallProgress,
    currentStep,
    steps,
    status,
    onCancel,
    onRetry,
    showDetails = true,
    compact = false,
    startTime,
    estimatedDuration = 300 // 5 minutes default
}: ProgressTrackingProps) {
    const [elapsedTime, setElapsedTime] = useState(0)
    const [estimatedTimeRemaining, setEstimatedTimeRemaining] = useState(estimatedDuration)

    // Update elapsed time
    useEffect(() => {
        if (!startTime || status === 'completed' || status === 'failed') return

        const interval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - startTime.getTime()) / 1000)
            setElapsedTime(elapsed)

            // Estimate remaining time based on progress
            if (overallProgress > 0) {
                const totalEstimated = (elapsed / overallProgress) * 100
                const remaining = Math.max(0, totalEstimated - elapsed)
                setEstimatedTimeRemaining(remaining)
            }
        }, 1000)

        return () => clearInterval(interval)
    }, [startTime, overallProgress, status])

    const formatTime = (seconds: number): string => {
        const mins = Math.floor(seconds / 60)
        const secs = seconds % 60
        return `${mins}:${secs.toString().padStart(2, '0')}`
    }

    const getStatusColor = (stepStatus: string) => {
        switch (stepStatus) {
            case 'completed': return 'text-green-600 bg-green-100 dark:bg-green-900/20'
            case 'active': return 'text-blue-600 bg-blue-100 dark:bg-blue-900/20'
            case 'failed': return 'text-red-600 bg-red-100 dark:bg-red-900/20'
            default: return 'text-gray-600 bg-gray-100 dark:bg-gray-900/20'
        }
    }

    const getStatusIcon = (stepStatus: string) => {
        switch (stepStatus) {
            case 'completed': return CheckCircle
            case 'active': return RefreshCw
            case 'failed': return AlertCircle
            default: return Clock
        }
    }

    if (compact) {
        return (
            <div className="flex items-center space-x-3 p-3 bg-muted/50 rounded-lg">
                <div className="w-8 h-8 relative">
                    <motion.div
                        animate={{ rotate: status === 'processing' ? 360 : 0 }}
                        transition={{ duration: 2, repeat: status === 'processing' ? Infinity : 0, ease: "linear" }}
                        className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full"
                    />
                </div>
                <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium">{currentStep || 'Initializing...'}</span>
                        <span className="text-sm text-muted-foreground">{Math.round(overallProgress)}%</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                        <motion.div
                            className="bg-primary h-2 rounded-full"
                            initial={{ width: 0 }}
                            animate={{ width: `${overallProgress}%` }}
                            transition={{ duration: 0.5 }}
                        />
                    </div>
                </div>
                {elapsedTime > 0 && (
                    <div className="text-xs text-muted-foreground">
                        {formatTime(elapsedTime)}
                    </div>
                )}
            </div>
        )
    }

    return (
        <Card className="w-full max-w-2xl mx-auto">
            <CardHeader className="pb-4">
                <div className="flex items-center justify-between">
                    <div>
                        <CardTitle className="flex items-center space-x-2">
                            <Zap className="h-5 w-5 text-primary" />
                            <span>AI Analysis in Progress</span>
                            {analysisId && (
                                <Badge variant="outline" className="font-mono text-xs">
                                    {analysisId.slice(0, 8)}...
                                </Badge>
                            )}
                        </CardTitle>
                        <p className="text-sm text-muted-foreground mt-1">
                            Running comprehensive personality analysis across multiple agents
                        </p>
                    </div>
                    <div className="text-right">
                        <div className="text-2xl font-bold text-primary">
                            {Math.round(overallProgress)}%
                        </div>
                        {elapsedTime > 0 && (
                            <div className="text-xs text-muted-foreground">
                                {formatTime(elapsedTime)} elapsed
                            </div>
                        )}
                    </div>
                </div>
            </CardHeader>

            <CardContent className="space-y-6">
                {/* Overall Progress Bar */}
                <div className="space-y-2">
                    <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Overall Progress</span>
                        <div className="flex items-center space-x-2">
                            {estimatedTimeRemaining > 0 && overallProgress < 100 && (
                                <span className="text-xs text-muted-foreground">
                                    ~{formatTime(estimatedTimeRemaining)} remaining
                                </span>
                            )}
                        </div>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-3">
                        <motion.div
                            className="bg-gradient-to-r from-primary/80 to-primary h-3 rounded-full relative overflow-hidden"
                            initial={{ width: 0 }}
                            animate={{ width: `${overallProgress}%` }}
                            transition={{ duration: 0.8, ease: "easeOut" }}
                        >
                            {status === 'processing' && (
                                <motion.div
                                    className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
                                    animate={{ x: [-100, 200] }}
                                    transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                                />
                            )}
                        </motion.div>
                    </div>
                </div>

                {/* Current Step Highlight */}
                {currentStep && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="p-3 bg-primary/5 border border-primary/20 rounded-lg"
                    >
                        <div className="flex items-center space-x-3">
                            <motion.div
                                animate={{ rotate: 360 }}
                                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                                className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full"
                            />
                            <div>
                                <div className="font-medium text-primary">Currently Processing</div>
                                <div className="text-sm text-muted-foreground">{currentStep}</div>
                            </div>
                        </div>
                    </motion.div>
                )}

                {/* Detailed Step Progress */}
                {showDetails && steps.length > 0 && (
                    <div className="space-y-3">
                        <h4 className="text-sm font-medium text-muted-foreground">Analysis Steps</h4>
                        <div className="space-y-2">
                            {steps.map((step, index) => {
                                const StatusIcon = getStatusIcon(step.status)
                                const AgentIcon = step.agent ? agentIcons[step.agent] : Brain

                                return (
                                    <motion.div
                                        key={step.id}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: index * 0.1 }}
                                        className={`flex items-center justify-between p-3 rounded-lg border ${step.status === 'active'
                                                ? 'border-primary/30 bg-primary/5'
                                                : 'border-border bg-muted/30'
                                            }`}
                                    >
                                        <div className="flex items-center space-x-3">
                                            <div className={`p-2 rounded-full ${step.agent ? agentColors[step.agent] : 'text-gray-600 bg-gray-100'}`}>
                                                <AgentIcon className="h-4 w-4" />
                                            </div>
                                            <div>
                                                <div className="font-medium text-sm">{step.name}</div>
                                                <div className="text-xs text-muted-foreground">{step.description}</div>
                                                {step.error_message && (
                                                    <div className="text-xs text-red-600 mt-1">{step.error_message}</div>
                                                )}
                                            </div>
                                        </div>

                                        <div className="flex items-center space-x-2">
                                            {step.status === 'active' && step.progress > 0 && (
                                                <div className="text-xs text-muted-foreground">
                                                    {step.progress}%
                                                </div>
                                            )}
                                            <div className={`p-1 rounded-full ${getStatusColor(step.status)}`}>
                                                <StatusIcon className={`h-3 w-3 ${step.status === 'active' ? 'animate-spin' : ''}`} />
                                            </div>
                                        </div>
                                    </motion.div>
                                )
                            })}
                        </div>
                    </div>
                )}

                {/* Action Buttons */}
                <div className="flex justify-between items-center pt-4 border-t">
                    <div className="flex items-center space-x-2">
                        {status === 'failed' && onRetry && (
                            <Button onClick={onRetry} size="sm" variant="outline">
                                <RefreshCw className="h-4 w-4 mr-2" />
                                Retry Analysis
                            </Button>
                        )}
                    </div>

                    <div className="flex items-center space-x-2">
                        {status === 'processing' && onCancel && (
                            <Button onClick={onCancel} size="sm" variant="ghost">
                                Cancel
                            </Button>
                        )}

                        <Badge variant={
                            status === 'completed' ? 'default' :
                                status === 'failed' ? 'destructive' :
                                    status === 'processing' ? 'secondary' : 'outline'
                        }>
                            {status === 'completed' ? '✓ Complete' :
                                status === 'failed' ? '✗ Failed' :
                                    status === 'processing' ? '⚡ Processing' :
                                        status === 'queued' ? '⏳ Queued' : '💤 Idle'}
                        </Badge>
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}

export default ProgressTracking