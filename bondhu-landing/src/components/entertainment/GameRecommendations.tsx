/**
 * Game Recommendations Component
 * Displays personalized game recommendations from backend agents
 */

import React from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Play, Heart, ThumbsDown, Share, ExternalLink, Gamepad2, Clock, Shield, Zap, Users } from 'lucide-react'
import type { GameRecommendation } from '@/lib/api-client'

interface GameRecommendationsProps {
    recommendations: GameRecommendation[]
    isLoading?: boolean
    onPlay?: (recommendation: GameRecommendation) => void
    onLike?: (recommendation: GameRecommendation) => void
    onDislike?: (recommendation: GameRecommendation) => void
    onShare?: (recommendation: GameRecommendation) => void
    currentlyPlaying?: string | null
}

export function GameRecommendations({
    recommendations,
    isLoading = false,
    onPlay,
    onLike,
    onDislike,
    onShare,
    currentlyPlaying
}: GameRecommendationsProps) {
    if (isLoading) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                        <Gamepad2 className="h-5 w-5" />
                        <span>Game Recommendations</span>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="animate-pulse">
                                <div className="aspect-square bg-muted rounded-lg mb-3"></div>
                                <div className="h-4 bg-muted rounded mb-2"></div>
                                <div className="h-3 bg-muted rounded w-2/3"></div>
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
                        <Gamepad2 className="h-5 w-5" />
                        <span>Game Recommendations</span>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-center py-8">
                        <Gamepad2 className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                        <p className="text-muted-foreground">No game recommendations available yet.</p>
                        <p className="text-sm text-muted-foreground mt-2">
                            Complete your personality analysis to get personalized game suggestions.
                        </p>
                    </div>
                </CardContent>
            </Card>
        )
    }

    const getDifficultyColor = (difficulty: string) => {
        switch (difficulty) {
            case 'easy': return 'text-green-600 bg-green-100 dark:bg-green-900/20'
            case 'medium': return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20'
            case 'hard': return 'text-red-600 bg-red-100 dark:bg-red-900/20'
            case 'adaptive': return 'text-blue-600 bg-blue-100 dark:bg-blue-900/20'
            default: return 'text-gray-600 bg-gray-100 dark:bg-gray-900/20'
        }
    }

    const getTypeColor = (type: string) => {
        switch (type) {
            case 'mobile': return 'text-purple-600 bg-purple-100 dark:bg-purple-900/20'
            case 'pc': return 'text-blue-600 bg-blue-100 dark:bg-blue-900/20'
            case 'console': return 'text-green-600 bg-green-100 dark:bg-green-900/20'
            case 'web': return 'text-orange-600 bg-orange-100 dark:bg-orange-900/20'
            case 'vr': return 'text-pink-600 bg-pink-100 dark:bg-pink-900/20'
            default: return 'text-gray-600 bg-gray-100 dark:bg-gray-900/20'
        }
    }

    const getConfidenceColor = (confidence: number) => {
        if (confidence >= 80) return 'border-green-500/30 bg-green-50/50 dark:bg-green-950/20'
        if (confidence >= 60) return 'border-blue-500/30 bg-blue-50/50 dark:bg-blue-950/20'
        return 'border-yellow-500/30 bg-yellow-50/50 dark:bg-yellow-950/20'
    }

    const formatPlayTime = (minutes?: number) => {
        if (!minutes) return null
        if (minutes < 60) return `${minutes}m`
        const hours = Math.floor(minutes / 60)
        if (hours < 24) return `${hours}h`
        const days = Math.floor(hours / 24)
        return `${days}d`
    }

    const getDifficultyIcon = (difficulty: string) => {
        switch (difficulty) {
            case 'easy': return <Shield className="h-3 w-3" />
            case 'medium': return <Zap className="h-3 w-3" />
            case 'hard': return <Users className="h-3 w-3" />
            case 'adaptive': return <Gamepad2 className="h-3 w-3" />
            default: return <Shield className="h-3 w-3" />
        }
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <Gamepad2 className="h-5 w-5" />
                        <span>Game Recommendations</span>
                    </div>
                    <Badge variant="outline" className="text-xs">
                        {recommendations.length} games
                    </Badge>
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {recommendations.map((recommendation, index) => (
                        <motion.div
                            key={`${recommendation.title}-${index}`}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className={`rounded-lg border p-4 ${getConfidenceColor(recommendation.confidence)}`}
                        >
                            {/* Game Icon/Preview */}
                            <div className="relative aspect-square bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900 rounded-lg mb-4 overflow-hidden group">
                                <div className="w-full h-full flex items-center justify-center">
                                    <Gamepad2 className="h-12 w-12 text-muted-foreground" />
                                </div>

                                {/* Play overlay */}
                                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center">
                                    {onPlay && (
                                        <Button
                                            size="sm"
                                            variant={currentlyPlaying === recommendation.title ? "default" : "secondary"}
                                            onClick={() => onPlay(recommendation)}
                                            className="opacity-0 group-hover:opacity-100 transition-opacity"
                                        >
                                            <Play className="h-4 w-4 mr-2" />
                                            {currentlyPlaying === recommendation.title ? 'Playing' : 'Play'}
                                        </Button>
                                    )}
                                </div>

                                {/* Play time estimate */}
                                {recommendation.estimated_play_time && (
                                    <div className="absolute top-2 right-2 bg-black/80 text-white text-xs px-2 py-1 rounded">
                                        <Clock className="h-3 w-3 inline mr-1" />
                                        {formatPlayTime(recommendation.estimated_play_time)}
                                    </div>
                                )}
                            </div>

                            {/* Content */}
                            <div className="space-y-3">
                                <div>
                                    <h4 className="font-semibold line-clamp-2 mb-1">{recommendation.title}</h4>
                                    {recommendation.developer && (
                                        <p className="text-sm text-muted-foreground">by {recommendation.developer}</p>
                                    )}
                                </div>

                                <div className="flex items-center space-x-2 flex-wrap gap-1">
                                    <Badge className={`text-xs ${getTypeColor(recommendation.type)}`}>
                                        {recommendation.type}
                                    </Badge>
                                    <Badge variant="outline" className="text-xs">
                                        {recommendation.genre}
                                    </Badge>
                                    <Badge className={`text-xs ${getDifficultyColor(recommendation.difficulty_level)}`}>
                                        {getDifficultyIcon(recommendation.difficulty_level)}
                                        <span className="ml-1">{recommendation.difficulty_level}</span>
                                    </Badge>
                                </div>

                                <div className="space-y-2">
                                    <div className="flex items-center space-x-2">
                                        <span className="text-xs font-medium text-muted-foreground">Play Style:</span>
                                        <Badge variant="secondary" className="text-xs">
                                            {recommendation.play_style}
                                        </Badge>
                                    </div>

                                    {recommendation.platform && (
                                        <div className="flex items-center space-x-2">
                                            <span className="text-xs font-medium text-muted-foreground">Platform:</span>
                                            <Badge variant="outline" className="text-xs">
                                                {recommendation.platform}
                                            </Badge>
                                        </div>
                                    )}
                                </div>

                                <p className="text-sm text-muted-foreground line-clamp-3">
                                    {recommendation.reasoning}
                                </p>

                                <div className="flex items-center justify-between">
                                    {recommendation.confidence >= 70 && (
                                        <div className="flex items-center text-xs text-green-600">
                                            <Zap className="h-3 w-3 mr-1" />
                                            High match
                                        </div>
                                    )}

                                    <div className="text-xs text-muted-foreground">
                                        {Math.round(recommendation.confidence)}% confidence
                                    </div>
                                </div>

                                {/* Actions */}
                                <div className="flex items-center justify-between pt-3 border-t">
                                    <div className="flex space-x-2">
                                        {onLike && (
                                            <Button
                                                size="sm"
                                                variant="ghost"
                                                onClick={() => onLike(recommendation)}
                                                className="h-8 px-2"
                                            >
                                                <Heart className="h-3 w-3 mr-1" />
                                                Like
                                            </Button>
                                        )}

                                        {onDislike && (
                                            <Button
                                                size="sm"
                                                variant="ghost"
                                                onClick={() => onDislike(recommendation)}
                                                className="h-8 px-2"
                                            >
                                                <ThumbsDown className="h-3 w-3 mr-1" />
                                                Dislike
                                            </Button>
                                        )}

                                        {onShare && (
                                            <Button
                                                size="sm"
                                                variant="ghost"
                                                onClick={() => onShare(recommendation)}
                                                className="h-8 px-2"
                                            >
                                                <Share className="h-3 w-3 mr-1" />
                                                Share
                                            </Button>
                                        )}
                                    </div>

                                    {(recommendation.steam_id || recommendation.play_store_url) && (
                                        <Button
                                            size="sm"
                                            variant="outline"
                                            onClick={() => {
                                                const url = recommendation.steam_id
                                                    ? `https://store.steampowered.com/app/${recommendation.steam_id}`
                                                    : recommendation.play_store_url
                                                if (url) window.open(url, '_blank')
                                            }}
                                            className="h-8 px-2"
                                        >
                                            <ExternalLink className="h-3 w-3 mr-1" />
                                            Get
                                        </Button>
                                    )}
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </CardContent>
        </Card>
    )
}

export default GameRecommendations