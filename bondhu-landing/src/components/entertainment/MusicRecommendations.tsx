/**
 * Music Recommendations Component
 * Displays personalized music recommendations from backend agents
 */

import React from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Play, Pause, Heart, Share, ExternalLink, Headphones, TrendingUp } from 'lucide-react'
import type { MusicRecommendation } from '@/lib/api-client'

interface MusicRecommendationsProps {
    recommendations: MusicRecommendation[]
    isLoading?: boolean
    onPlay?: (recommendation: MusicRecommendation) => void
    onLike?: (recommendation: MusicRecommendation) => void
    onShare?: (recommendation: MusicRecommendation) => void
    currentlyPlaying?: string | null
}

export function MusicRecommendations({
    recommendations,
    isLoading = false,
    onPlay,
    onLike,
    onShare,
    currentlyPlaying
}: MusicRecommendationsProps) {
    if (isLoading) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                        <Headphones className="h-5 w-5" />
                        <span>Music Recommendations</span>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="animate-pulse">
                                <div className="h-16 bg-muted rounded-lg"></div>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>
        )
    }

    if (!recommendations.length) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                        <Headphones className="h-5 w-5" />
                        <span>Music Recommendations</span>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-center py-8">
                        <Headphones className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                        <p className="text-muted-foreground">No music recommendations available yet.</p>
                        <p className="text-sm text-muted-foreground mt-2">
                            Complete your personality analysis to get personalized music suggestions.
                        </p>
                    </div>
                </CardContent>
            </Card>
        )
    }

    const getEnergyColor = (energy: number) => {
        if (energy >= 80) return 'text-red-600 bg-red-100 dark:bg-red-900/20'
        if (energy >= 60) return 'text-orange-600 bg-orange-100 dark:bg-orange-900/20'
        if (energy >= 40) return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20'
        if (energy >= 20) return 'text-green-600 bg-green-100 dark:bg-green-900/20'
        return 'text-blue-600 bg-blue-100 dark:bg-blue-900/20'
    }

    const getConfidenceColor = (confidence: number) => {
        if (confidence >= 80) return 'border-green-500/30 bg-green-50/50 dark:bg-green-950/20'
        if (confidence >= 60) return 'border-blue-500/30 bg-blue-50/50 dark:bg-blue-950/20'
        return 'border-yellow-500/30 bg-yellow-50/50 dark:bg-yellow-950/20'
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <Headphones className="h-5 w-5" />
                        <span>Music Recommendations</span>
                    </div>
                    <Badge variant="outline" className="text-xs">
                        {recommendations.length} songs
                    </Badge>
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {recommendations.map((recommendation, index) => (
                        <motion.div
                            key={`${recommendation.title}-${index}`}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className={`p-4 rounded-lg border ${getConfidenceColor(recommendation.confidence)}`}
                        >
                            <div className="flex items-start justify-between">
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center space-x-2 mb-2">
                                        <h4 className="font-semibold truncate">{recommendation.title}</h4>
                                        {recommendation.artist && (
                                            <span className="text-sm text-muted-foreground">by {recommendation.artist}</span>
                                        )}
                                    </div>

                                    <div className="flex items-center space-x-2 mb-3">
                                        <Badge variant="secondary" className="text-xs">
                                            {recommendation.type}
                                        </Badge>
                                        {recommendation.genre && (
                                            <Badge variant="outline" className="text-xs">
                                                {recommendation.genre}
                                            </Badge>
                                        )}
                                        <Badge className={`text-xs ${getEnergyColor(recommendation.energy_level)}`}>
                                            {recommendation.energy_level}% energy
                                        </Badge>
                                    </div>

                                    <p className="text-sm text-muted-foreground mb-3">
                                        {recommendation.reasoning}
                                    </p>

                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center space-x-2">
                                            <Badge variant="outline" className="text-xs">
                                                {recommendation.mood}
                                            </Badge>
                                            {recommendation.confidence >= 70 && (
                                                <Badge variant="default" className="text-xs">
                                                    <TrendingUp className="h-3 w-3 mr-1" />
                                                    High match
                                                </Badge>
                                            )}
                                        </div>

                                        <div className="text-xs text-muted-foreground">
                                            {Math.round(recommendation.confidence)}% confidence
                                        </div>
                                    </div>
                                </div>

                                <div className="flex flex-col space-y-2 ml-4">
                                    {onPlay && (
                                        <Button
                                            size="sm"
                                            variant={currentlyPlaying === recommendation.title ? "default" : "outline"}
                                            onClick={() => onPlay(recommendation)}
                                            className="h-8 w-8 p-0"
                                        >
                                            {currentlyPlaying === recommendation.title ? (
                                                <Pause className="h-4 w-4" />
                                            ) : (
                                                <Play className="h-4 w-4" />
                                            )}
                                        </Button>
                                    )}

                                    <div className="flex space-x-1">
                                        {onLike && (
                                            <Button
                                                size="sm"
                                                variant="ghost"
                                                onClick={() => onLike(recommendation)}
                                                className="h-8 w-8 p-0"
                                            >
                                                <Heart className="h-3 w-3" />
                                            </Button>
                                        )}

                                        {onShare && (
                                            <Button
                                                size="sm"
                                                variant="ghost"
                                                onClick={() => onShare(recommendation)}
                                                className="h-8 w-8 p-0"
                                            >
                                                <Share className="h-3 w-3" />
                                            </Button>
                                        )}

                                        {(recommendation.spotify_id || recommendation.youtube_url) && (
                                            <Button
                                                size="sm"
                                                variant="ghost"
                                                onClick={() => {
                                                    const url = recommendation.spotify_id
                                                        ? `https://open.spotify.com/track/${recommendation.spotify_id}`
                                                        : recommendation.youtube_url
                                                    if (url) window.open(url, '_blank')
                                                }}
                                                className="h-8 w-8 p-0"
                                            >
                                                <ExternalLink className="h-3 w-3" />
                                            </Button>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </CardContent>
        </Card>
    )
}

export default MusicRecommendations