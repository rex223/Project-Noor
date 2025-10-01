/**
 * Personality Update Status Component
 * Shows when personality was last updated and allows manual trigger
 */

'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { RefreshCw, TrendingUp, Clock, CheckCircle, AlertCircle } from 'lucide-react'
import { bondhuAPI } from '@/lib/api-client'
import { useAuth } from '@/hooks/use-auth'

interface PersonalityUpdateStatus {
    lastUpdated: Date | null
    insightsProcessed: number
    isUpdating: boolean
    error: string | null
    traitChanges: Record<string, number> | null
}

export function PersonalityUpdateStatus() {
    const { user } = useAuth()
    const [status, setStatus] = useState<PersonalityUpdateStatus>({
        lastUpdated: null,
        insightsProcessed: 0,
        isUpdating: false,
        error: null,
        traitChanges: null
    })

    const handleManualUpdate = async () => {
        if (!user?.id) return

        setStatus(prev => ({ ...prev, isUpdating: true, error: null }))

        try {
            const response = await bondhuAPI.updatePersonalityProfile(user.id)

            if (response.success && response.data) {
                setStatus({
                    lastUpdated: new Date(),
                    insightsProcessed: response.data.insights_processed,
                    isUpdating: false,
                    error: null,
                    traitChanges: response.data.trait_changes
                })
            } else {
                setStatus(prev => ({
                    ...prev,
                    isUpdating: false,
                    error: response.message || 'Update failed'
                }))
            }
        } catch (error) {
            setStatus(prev => ({
                ...prev,
                isUpdating: false,
                error: error instanceof Error ? error.message : 'Unknown error'
            }))
        }
    }

    const formatTraitChange = (value: number): string => {
        const sign = value >= 0 ? '+' : ''
        return `${sign}${value.toFixed(1)}`
    }

    const getTraitChangeColor = (value: number): string => {
        if (Math.abs(value) < 0.1) return 'text-muted-foreground'
        return value > 0 ? 'text-green-600' : 'text-red-600'
    }

    if (!user) return null

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <TrendingUp className="h-5 w-5" />
                        <span>Personality Learning</span>
                    </div>
                    <Button
                        size="sm"
                        variant="outline"
                        onClick={handleManualUpdate}
                        disabled={status.isUpdating}
                    >
                        <RefreshCw className={`h-4 w-4 mr-2 ${status.isUpdating ? 'animate-spin' : ''}`} />
                        Update Now
                    </Button>
                </CardTitle>
                <CardDescription>
                    Your personality profile automatically updates based on your interactions
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                {/* Last Update Info */}
                <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                    <div className="flex items-center space-x-2">
                        <Clock className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm font-medium">Last Updated</span>
                    </div>
                    <span className="text-sm text-muted-foreground">
                        {status.lastUpdated
                            ? status.lastUpdated.toLocaleString()
                            : 'Scheduled for 2:00 AM daily'
                        }
                    </span>
                </div>

                {/* Insights Processed */}
                {status.insightsProcessed > 0 && (
                    <div className="flex items-center justify-between p-3 rounded-lg bg-blue-50 dark:bg-blue-950/20">
                        <div className="flex items-center space-x-2">
                            <CheckCircle className="h-4 w-4 text-blue-600" />
                            <span className="text-sm font-medium">Insights Processed</span>
                        </div>
                        <Badge variant="secondary">{status.insightsProcessed}</Badge>
                    </div>
                )}

                {/* Trait Changes */}
                {status.traitChanges && Object.keys(status.traitChanges).length > 0 && (
                    <div className="space-y-2">
                        <p className="text-sm font-medium">Recent Changes:</p>
                        <div className="grid grid-cols-2 gap-2">
                            {Object.entries(status.traitChanges).map(([trait, change]) => (
                                <div
                                    key={trait}
                                    className="flex items-center justify-between p-2 rounded-md bg-muted/30"
                                >
                                    <span className="text-xs capitalize">{trait}</span>
                                    <span className={`text-xs font-mono ${getTraitChangeColor(change)}`}>
                                        {formatTraitChange(change)}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Error State */}
                {status.error && (
                    <div className="flex items-start space-x-2 p-3 rounded-lg bg-red-50 dark:bg-red-950/20">
                        <AlertCircle className="h-4 w-4 text-red-600 mt-0.5" />
                        <div className="flex-1">
                            <p className="text-sm font-medium text-red-600">Update Failed</p>
                            <p className="text-xs text-red-600/80 mt-1">{status.error}</p>
                        </div>
                    </div>
                )}

                {/* Info Text */}
                <p className="text-xs text-muted-foreground">
                    Your personality profile updates automatically every night at 2 AM based on your chat
                    conversations and entertainment preferences from the past 30 days.
                </p>
            </CardContent>
        </Card>
    )
}

export default PersonalityUpdateStatus
