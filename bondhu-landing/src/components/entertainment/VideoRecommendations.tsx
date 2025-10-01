/**
 * Video Recommendations Component
 * Displays personalized video recommendations from backend agents
 */

import React from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Play, Heart, ThumbsDown, Share, ExternalLink, Video, Clock, Star } from 'lucide-react'
import type { VideoRecommendation } from '@/lib/api-client'

interface VideoRecommendationsProps {
    recommendations: VideoRecommendation[]
    isLoading?: boolean
    onPlay?: (recommendation: VideoRecommendation) => void
    onLike?: (recommendation: VideoRecommendation) => void
    onDislike?: (recommendation: VideoRecommendation) => void
    onShare?: (recommendation: VideoRecommendation) => void
    currentlyPlaying?: string | null
}

export function VideoRecommendations({
    recommendations,
    isLoading = false,
    onPlay,
    onLike,
    onDislike,
    onShare,
    currentlyPlaying
}: VideoRecommendationsProps) {
    if (isLoading) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                        <Video className="h-5 w-5" />
                        <span>Video Recommendations</span>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {[1, 2, 3, 4].map((i) => (
                            <div key={i} className="animate-pulse">
                                <div className="aspect-video bg-muted rounded-lg mb-2"></div>
                                <div className="h-4 bg-muted rounded mb-1"></div>
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
                        <Video className="h-5 w-5" />
                        <span>Video Recommendations</span>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-center py-8">
                        <Video className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                        <p className="text-muted-foreground">No video recommendations available yet.</p>
                        <p className="text-sm text-muted-foreground mt-2">
                            Complete your personality analysis to get personalized video suggestions.
                        </p>
                    </div>
                </CardContent>
            </Card>
        )
    }

    const formatDuration = (minutes?: number) => {
        if (!minutes) return null
        if (minutes < 60) return `${minutes}m`
        const hours = Math.floor(minutes / 60)
        const remainingMinutes = minutes % 60
        return `${hours}h ${remainingMinutes}m`
    }

    const getTypeColor = (type: string) => {
        switch (type) {
            case 'movie': return 'text-red-600 bg-red-100 dark:bg-red-900/20'
            case 'tv_show': return 'text-blue-600 bg-blue-100 dark:bg-blue-900/20'
            case 'documentary': return 'text-green-600 bg-green-100 dark:bg-green-900/20'
            case 'youtube': return 'text-orange-600 bg-orange-100 dark:bg-orange-900/20'
            case 'short_form': return 'text-purple-600 bg-purple-100 dark:bg-purple-900/20'
            default: return 'text-gray-600 bg-gray-100 dark:bg-gray-900/20'
        }
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
                        <Video className="h-5 w-5" />
                        <span>Video Recommendations</span>
                    </div>
                    <Badge variant="outline" className="text-xs">
                        {recommendations.length} videos
                    </Badge>
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {recommendations.map((recommendation, index) => (
                        <motion.div
                            key={`${recommendation.title}-${index}`}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className={`rounded-lg border p-4 ${getConfidenceColor(recommendation.confidence)}`}
                        >
                            {/* Thumbnail/Preview Area */}
                            <div className="relative aspect-video bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900 rounded-lg mb-3 overflow-hidden group">
                                {recommendation.thumbnail ? (
                                    <img
                                        src={recommendation.thumbnail}
                                        alt={recommendation.title}
                                        className="w-full h-full object-cover"
                                    />
                                ) : (
                                    <div className="w-full h-full flex items-center justify-center">
                                        <Video className="h-8 w-8 text-muted-foreground" />
                                    </div>
                                )}

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

                                {/* Duration badge */}
                                {recommendation.duration_minutes && (
                                    <div className="absolute bottom-2 right-2 bg-black/80 text-white text-xs px-2 py-1 rounded">
                                        <Clock className="h-3 w-3 inline mr-1" />
                                        {formatDuration(recommendation.duration_minutes)}
                                    </div>
                                )}
                            </div>

                            {/* Content */}
                            <div className="space-y-3">
                                <div>
                                    <h4 className="font-semibold line-clamp-2 mb-1">{recommendation.title}</h4>
                                    {recommendation.creator && (
                                        <p className="text-sm text-muted-foreground">by {recommendation.creator}</p>
                                    )}
                                </div>

                                <div className="flex items-center space-x-2 flex-wrap">
                                    <Badge className={`text-xs ${getTypeColor(recommendation.type)}`}>
                                        {recommendation.type.replace('_', ' ')}
                                    </Badge>
                                    <Badge variant="outline" className="text-xs">
                                        {recommendation.genre}
                                    </Badge>
                                    {recommendation.platform && (
                                        <Badge variant="secondary" className="text-xs">
                                            {recommendation.platform}
                                        </Badge>
                                    )}
                                </div>

                                <p className="text-sm text-muted-foreground line-clamp-2">
                                    {recommendation.reasoning}
                                </p>

                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-2">
                                        <Badge variant="outline" className="text-xs">
                                            {recommendation.mood_match}
                                        </Badge>
                                        {recommendation.confidence >= 70 && (
                                            <div className="flex items-center text-xs text-green-600">
                                                <Star className="h-3 w-3 mr-1" />
                                                High match
                                            </div>
                                        )}
                                    </div>

                                    <div className="text-xs text-muted-foreground">
                                        {Math.round(recommendation.confidence)}% confidence
                                    </div>
                                </div>

                                {/* Actions */}
                                <div className="flex items-center justify-between pt-2 border-t">
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

                                    {(recommendation.youtube_url || recommendation.imdb_id) && (
                                        <Button
                                            size="sm"
                                            variant="outline"
                                            onClick={() => {
                                                const url = recommendation.youtube_url ||
                                                    (recommendation.imdb_id ? `https://www.imdb.com/title/${recommendation.imdb_id}` : null)
                                                if (url) window.open(url, '_blank')
                                            }}
                                            className="h-8 px-2"
                                        >
                                            <ExternalLink className="h-3 w-3 mr-1" />
                                            Watch
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

export default VideoRecommendations