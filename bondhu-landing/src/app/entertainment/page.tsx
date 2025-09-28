"use client"

import { useEffect, useState, useCallback, useMemo, useRef } from "react"
import { useRouter } from "next/navigation"
import { createClient } from "@/lib/supabase/client"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { ArrowLeft, Play, Pause, Volume2, ChevronRight, Gamepad2, Camera, Headphones, TrendingUp, Clock, Star, Users } from "lucide-react"
import { Slider } from "@/components/ui/slider"
import { GlowingEffect } from "@/components/ui/glowing-effect"
import type { Profile } from "@/types/auth"
import { Logo } from "@/components/logo"
import { ThemeToggle } from "@/components/theme-toggle"
import Link from "next/link"

// Import the components that were in the dashboard
// These would need to be moved to separate files in a real app
const PuzzleMaster = ({ onGameComplete }: { onGameComplete: (data: any) => void }) => (
    <div className="p-8 text-center">
        <h3 className="text-xl font-bold mb-4">Puzzle Master Game</h3>
        <p className="text-muted-foreground mb-4">Game interface would be implemented here</p>
        <Button onClick={() => onGameComplete({
            gameId: 'puzzle_master',
            completionRate: 85,
            performance: { creativity: 75, speed: 80, accuracy: 90 },
            emotionalState: 'focused'
        })}>
            Complete Demo
        </Button>
    </div>
)

const MemoryPalace = ({ onGameComplete }: { onGameComplete: (data: any) => void }) => (
    <div className="p-8 text-center">
        <h3 className="text-xl font-bold mb-4">Memory Palace Game</h3>
        <p className="text-muted-foreground mb-4">Memory game interface would be implemented here</p>
        <Button onClick={() => onGameComplete({
            gameId: 'memory_palace',
            completionRate: 92,
            performance: { creativity: 60, speed: 85, accuracy: 95 },
            emotionalState: 'determined'
        })}>
            Complete Demo
        </Button>
    </div>
)

const ColorSymphony = ({ onGameComplete }: { onGameComplete: (data: any) => void }) => (
    <div className="p-8 text-center">
        <h3 className="text-xl font-bold mb-4">Color Symphony Game</h3>
        <p className="text-muted-foreground mb-4">Creative color game interface would be implemented here</p>
        <Button onClick={() => onGameComplete({
            gameId: 'color_symphony',
            completionRate: 78,
            performance: { creativity: 95, speed: 70, accuracy: 80 },
            emotionalState: 'creative'
        })}>
            Complete Demo
        </Button>
    </div>
)

const VideoPlayer = ({ video, onWatchComplete, onClose }: { video: any, onWatchComplete: (data: any) => void, onClose: () => void }) => (
    <div className="space-y-4">
        <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold">{video.title}</h3>
            <Button variant="outline" onClick={onClose}>Close Player</Button>
        </div>
        <div className="aspect-video bg-black rounded-lg flex items-center justify-center text-white">
            <div className="text-center">
                <div className="text-6xl mb-4">{video.thumbnail}</div>
                <p className="text-lg">{video.title}</p>
                <p className="text-sm opacity-75">Video player would be implemented here</p>
                <Button
                    className="mt-4"
                    onClick={() => onWatchComplete({
                        contentId: video.id,
                        watchTime: video.duration * 0.8,
                        completionRate: 80,
                        interactions: ['pause', 'rewind'],
                        skipPatterns: []
                    })}
                >
                    Mark as Watched
                </Button>
            </div>
        </div>
    </div>
)

// Enhanced AI Learning Engine with dynamic analysis
class EnhancedAILearningEngine {
    private supabase = createClient()
    private profileId: string | null = null

    constructor(profileId: string) {
        this.profileId = profileId
    }

    async addGameplayData(data: any) {
        try {
            // Store gameplay data with real-time analysis
            const analysisData = {
                profile_id: this.profileId,
                content_type: 'game',
                content_id: data.gameId,
                interaction_data: data,
                insights: this.analyzeGameplayPatterns(data),
                timestamp: new Date().toISOString(),
                emotional_state: data.emotionalState,
                performance_metrics: data.performance
            }

            // Store in Supabase (would need to create this table)
            console.log('Enhanced game analysis:', analysisData)

            // Return personalized recommendations
            return this.getPersonalizedGameRecommendations(data)
        } catch (error) {
            console.error('Error storing gameplay data:', error)
        }
    }

    async addVideoData(data: any) {
        try {
            const analysisData = {
                profile_id: this.profileId,
                content_type: 'video',
                content_id: data.contentId,
                watch_time: data.watchTime,
                completion_rate: data.completionRate,
                interaction_patterns: data.interactions,
                skip_patterns: data.skipPatterns,
                timestamp: new Date().toISOString()
            }

            console.log('Enhanced video analysis:', analysisData)
            return this.getPersonalizedVideoRecommendations(data)
        } catch (error) {
            console.error('Error storing video data:', error)
        }
    }

    async addMusicData(data: any) {
        try {
            const analysisData = {
                profile_id: this.profileId,
                content_type: 'music',
                mood: data.mood,
                listening_duration: data.duration,
                track_preferences: data.trackPreferences,
                skip_rate: data.skipRate,
                timestamp: new Date().toISOString()
            }

            console.log('Enhanced music analysis:', analysisData)
            return this.getPersonalizedMusicRecommendations(data)
        } catch (error) {
            console.error('Error storing music data:', error)
        }
    }

    private analyzeGameplayPatterns(data: any) {
        const insights = {
            problemSolvingStyle: this.determineProblemSolvingStyle(data.performance),
            stressResponse: this.analyzeStressResponse(data.performance, data.emotionalState),
            learningPreference: this.identifyLearningPreference(data),
            personalityTraits: this.extractPersonalityTraits(data)
        }
        return insights
    }

    private determineProblemSolvingStyle(performance: any) {
        if (performance.speed > 80 && performance.accuracy > 85) return 'analytical_fast'
        if (performance.creativity > 80) return 'creative_explorer'
        if (performance.accuracy > 90) return 'methodical_precise'
        return 'balanced_approach'
    }

    private analyzeStressResponse(performance: any, emotionalState: string) {
        const stressIndicators = {
            performance_drop: performance.accuracy < 70,
            time_pressure_effect: performance.speed < 50,
            emotional_response: emotionalState
        }
        return stressIndicators
    }

    private identifyLearningPreference(data: any) {
        // Analyze learning patterns from gameplay
        return {
            visual: data.gameId.includes('color') || data.gameId.includes('puzzle'),
            kinesthetic: data.performance.speed > 75,
            analytical: data.performance.accuracy > 85
        }
    }

    private extractPersonalityTraits(data: any) {
        return {
            openness: data.performance.creativity,
            conscientiousness: data.performance.accuracy,
            extraversion: data.completionRate > 90 ? 75 : 45,
            agreeableness: 65, // Would be determined by multiplayer interactions
            neuroticism: this.calculateNeuroticism(data.emotionalState, data.performance)
        }
    }

    private calculateNeuroticism(emotionalState: string, performance: any) {
        const stressKeywords = ['anxious', 'frustrated', 'overwhelmed']
        const isStressed = stressKeywords.some(keyword => emotionalState.includes(keyword))
        return isStressed ? Math.max(70, 100 - performance.accuracy) : Math.min(40, 60 - performance.accuracy / 2)
    }

    private getPersonalizedGameRecommendations(data: any) {
        // Dynamic game recommendations based on performance and preferences
        const recommendations = []

        if (data.performance.creativity > 80) {
            recommendations.push({
                type: 'creative_games',
                reason: 'High creativity score detected',
                games: ['color_symphony', 'artistic_expression', 'story_builder']
            })
        }

        if (data.performance.accuracy > 85) {
            recommendations.push({
                type: 'strategy_games',
                reason: 'Excellent precision and attention to detail',
                games: ['chess_master', 'logic_puzzles', 'pattern_recognition']
            })
        }

        return recommendations
    }

    private getPersonalizedVideoRecommendations(data: any) {
        const recommendations = []

        if (data.completionRate > 80) {
            recommendations.push({
                type: 'deep_content',
                reason: 'High engagement with educational content',
                categories: ['advanced_psychology', 'neuroscience', 'philosophy']
            })
        }

        if (data.skipPatterns.length > 3) {
            recommendations.push({
                type: 'bite_sized_content',
                reason: 'Preference for shorter, focused content',
                categories: ['quick_tips', 'micro_learning', 'summary_videos']
            })
        }

        return recommendations
    }

    private getPersonalizedMusicRecommendations(data: any) {
        const recommendations = []

        // Analyze listening patterns for mood correlation
        const moodPreferences = this.analyzeMoodPatterns(data)

        recommendations.push({
            type: 'mood_based',
            currentMood: data.mood,
            suggestedMoods: this.getComplementaryMoods(data.mood),
            playlists: this.generateDynamicPlaylists(moodPreferences)
        })

        return recommendations
    }

    private analyzeMoodPatterns(data: any) {
        // This would analyze historical mood data
        return {
            mostFrequent: data.mood,
            timeOfDay: new Date().getHours() > 18 ? 'evening' : 'day',
            weekday: new Date().getDay() < 6
        }
    }

    private getComplementaryMoods(currentMood: string) {
        const moodMap: { [key: string]: string[] } = {
            'Focus': ['Relax', 'Creative'],
            'Relax': ['Energy', 'Creative'],
            'Energy': ['Focus', 'Relax'],
            'Creative': ['Focus', 'Energy']
        }
        return moodMap[currentMood] || []
    }

    private generateDynamicPlaylists(moodPreferences: any) {
        // Generate playlists based on user preferences and time context
        const timeOfDay = new Date().getHours()
        const isWeekend = [0, 6].includes(new Date().getDay())

        return {
            contextual: `${isWeekend ? 'Weekend' : 'Weekday'} ${timeOfDay > 18 ? 'Evening' : 'Morning'} Vibes`,
            personal: `Your ${moodPreferences.mostFrequent} Mix`,
            discovery: 'New Sounds for You'
        }
    }
}

export default function EntertainmentHubPage() {
    const [profile, setProfile] = useState<Profile | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const [userPreferences, setUserPreferences] = useState<any>(null)
    const [activityHistory, setActivityHistory] = useState<any[]>([])
    const [personalizedRecommendations, setPersonalizedRecommendations] = useState<any>(null)
    const router = useRouter()
    const supabase = createClient()
    const aiEngine = useRef<EnhancedAILearningEngine | null>(null)

    // Function to add activity to main history - this will update the stats
    const addActivityToHistory = useCallback((activity: any) => {
        setActivityHistory(prev => [...prev, activity])
    }, [])

    // Memoized user stats calculation
    const userStats = useMemo(() => {
        if (!activityHistory.length) return null

        const gamesPlayed = activityHistory.filter(a => a.type === 'game').length
        const videosWatched = activityHistory.filter(a => a.type === 'video').length
        const musicListened = activityHistory.filter(a => a.type === 'music').length
        const totalTime = activityHistory.reduce((acc, a) => acc + (a.duration || 0), 0)

        return {
            gamesPlayed,
            videosWatched,
            musicListened,
            totalTime: Math.round(totalTime / 60), // Convert to minutes
            streak: calculateStreak(activityHistory),
            favoriteCategory: getFavoriteCategory(activityHistory)
        }
    }, [activityHistory])

    // Dynamic content loading based on user behavior
    const loadUserData = useCallback(async (userId: string) => {
        try {
            // Initialize AI engine
            aiEngine.current = new EnhancedAILearningEngine(userId)

            // Load user preferences (would come from database)
            const preferences = await loadUserPreferences(userId)
            setUserPreferences(preferences)

            // Load activity history
            const history = await loadActivityHistory(userId)
            setActivityHistory(history)

            // Generate personalized recommendations
            const recommendations = await generatePersonalizedContent(userId, preferences, history)
            setPersonalizedRecommendations(recommendations)

        } catch (error) {
            console.error('Error loading user data:', error)
        }
    }, [])

    useEffect(() => {
        const getProfile = async () => {
            try {
                const { data: { user } } = await supabase.auth.getUser()

                if (!user) {
                    router.push('/sign-in')
                    return
                }

                const { data: profileData, error } = await supabase
                    .from('profiles')
                    .select('*')
                    .eq('id', user.id)
                    .single()

                if (error) {
                    console.error('Error fetching profile:', error)
                    return
                }

                setProfile(profileData)

                // Load additional user data for personalization
                await loadUserData(user.id)

            } catch (error) {
                console.error('Error:', error)
            } finally {
                setIsLoading(false)
            }
        }

        getProfile()
    }, [supabase, router, loadUserData])

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
            </div>
        )
    }

    if (!profile) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <h1 className="text-2xl font-bold mb-4">Profile not found</h1>
                    <Button onClick={() => router.push('/sign-in')}>
                        Return to Sign In
                    </Button>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-background via-background to-secondary/20">
            {/* Header */}
            <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex h-16 items-center justify-between">
                        {/* Logo and Back Button */}
                        <div className="flex items-center space-x-4">
                            <Button variant="ghost" size="sm" onClick={() => router.back()}>
                                <ArrowLeft className="h-4 w-4 mr-1" />
                                Back to Dashboard
                            </Button>
                            <Link href="/" className="flex items-center">
                                <Logo width={140} height={50} />
                            </Link>
                            <div className="hidden sm:block">
                                <h1 className="text-lg font-semibold text-muted-foreground">Entertainment Hub</h1>
                            </div>
                        </div>

                        {/* Right Section */}
                        <div className="flex items-center space-x-3">
                            <ThemeToggle />
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="container mx-auto px-4 py-6 max-w-7xl">
                {/* Breadcrumb Navigation */}
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                        <button
                            onClick={() => router.push('/dashboard')}
                            className="hover:text-foreground transition-colors"
                        >
                            Dashboard
                        </button>
                        <ChevronRight className="h-4 w-4" />
                        <span className="text-foreground font-medium">Entertainment Hub</span>
                    </div>
                </div>

                {/* Hero Section */}
                <div className="mb-8">
                    <Card className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20 border-purple-200 dark:border-purple-800">
                        <CardContent className="p-8">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-6">
                                    <Avatar className="h-20 w-20 border-4 border-white shadow-lg">
                                        <AvatarFallback className="text-2xl bg-gradient-to-br from-purple-500 to-pink-500 text-white">
                                            {profile.full_name?.split(' ').map(n => n[0]).join('') || 'U'}
                                        </AvatarFallback>
                                    </Avatar>
                                    <div>
                                        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                                            Entertainment Hub
                                        </h1>
                                        <p className="text-muted-foreground text-lg">
                                            Explore games, videos, and music while Bondhu learns about your personality
                                        </p>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">
                                        🎮
                                    </div>
                                    <div className="text-sm text-muted-foreground">
                                        Interactive Content
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* User Stats Dashboard */}
                {userStats && (
                    <Card className="mb-6 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-950/20 dark:to-purple-950/20">
                        <CardContent className="p-6">
                            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                                        {userStats.gamesPlayed}
                                    </div>
                                    <div className="text-sm text-muted-foreground">Games Played</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                                        {userStats.videosWatched}
                                    </div>
                                    <div className="text-sm text-muted-foreground">Videos Watched</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-pink-600 dark:text-pink-400">
                                        {userStats.musicListened}
                                    </div>
                                    <div className="text-sm text-muted-foreground">Music Sessions</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                                        {userStats.totalTime}m
                                    </div>
                                    <div className="text-sm text-muted-foreground">Total Time</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                                        {userStats.streak}
                                    </div>
                                    <div className="text-sm text-muted-foreground">Day Streak</div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* Personalized Recommendations */}
                {personalizedRecommendations && (
                    <Card className="mb-6">
                        <CardHeader>
                            <CardTitle className="flex items-center space-x-2">
                                <TrendingUp className="h-5 w-5" />
                                <span>Recommended for You</span>
                            </CardTitle>
                            <p className="text-muted-foreground">
                                Based on your personality insights and activity patterns
                            </p>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                {personalizedRecommendations.games?.slice(0, 1).map((game: any, index: number) => (
                                    <div key={index} className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/20 dark:to-emerald-950/20 rounded-lg">
                                        <div className="flex items-center space-x-2 mb-2">
                                            <Gamepad2 className="h-4 w-4 text-green-600" />
                                            <span className="font-medium text-sm">Game</span>
                                        </div>
                                        <h4 className="font-semibold mb-1">{game.name}</h4>
                                        <p className="text-xs text-muted-foreground">{game.reason}</p>
                                    </div>
                                ))}
                                {personalizedRecommendations.videos?.slice(0, 1).map((video: any, index: number) => (
                                    <div key={index} className="p-4 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/20 dark:to-cyan-950/20 rounded-lg">
                                        <div className="flex items-center space-x-2 mb-2">
                                            <Camera className="h-4 w-4 text-blue-600" />
                                            <span className="font-medium text-sm">Video</span>
                                        </div>
                                        <h4 className="font-semibold mb-1">{video.title}</h4>
                                        <p className="text-xs text-muted-foreground">{video.reason}</p>
                                    </div>
                                ))}
                                {personalizedRecommendations.music?.slice(0, 1).map((music: any, index: number) => (
                                    <div key={index} className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20 rounded-lg">
                                        <div className="flex items-center space-x-2 mb-2">
                                            <Headphones className="h-4 w-4 text-purple-600" />
                                            <span className="font-medium text-sm">Music</span>
                                        </div>
                                        <h4 className="font-semibold mb-1">{music.playlist}</h4>
                                        <p className="text-xs text-muted-foreground">{music.reason}</p>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* Entertainment Content */}
                <EntertainmentHub
                    profile={profile}
                    userPreferences={userPreferences}
                    aiEngine={aiEngine.current}
                    personalizedRecommendations={personalizedRecommendations}
                    addActivityToHistory={addActivityToHistory}
                />
            </main>
        </div>
    )
}

// Helper functions for dynamic data loading
async function loadUserPreferences(userId: string) {
    // Mock implementation - would load from Supabase
    return {
        favoriteGameTypes: ['puzzle', 'strategy'],
        preferredVideoLength: 'medium', // short, medium, long
        musicMoods: ['Focus', 'Relax'],
        playingTime: 'evening',
        difficulty: 'medium'
    }
}

async function loadActivityHistory(userId: string) {
    // Mock implementation - would load recent activity from Supabase
    const mockHistory = [
        { type: 'game', name: 'Puzzle Master', duration: 900, timestamp: new Date().toISOString(), performance: { accuracy: 85 } },
        { type: 'video', name: 'Breathing Exercise', duration: 300, timestamp: new Date().toISOString() },
        { type: 'music', mood: 'Focus', duration: 1800, timestamp: new Date().toISOString() }
    ]
    return mockHistory
}

async function generatePersonalizedContent(userId: string, preferences: any, history: any[]) {
    // AI-powered content generation based on user data
    const recommendations = {
        games: [
            {
                name: 'Advanced Pattern Recognition',
                reason: 'Based on your high accuracy in puzzle games',
                type: 'puzzle',
                difficulty: 'hard'
            }
        ],
        videos: [
            {
                title: 'Deep Focus Techniques',
                reason: 'You frequently use focus music',
                category: 'wellness',
                duration: 600
            }
        ],
        music: [
            {
                playlist: 'Your Evening Focus Mix',
                reason: 'Optimized for your evening focus sessions',
                mood: 'Focus',
                tracks: 15
            }
        ]
    }

    return recommendations
}

function calculateStreak(history: any[]) {
    // Calculate consecutive days of engagement
    const today = new Date()
    let streak = 0

    for (let i = 0; i < 30; i++) {
        const checkDate = new Date(today)
        checkDate.setDate(today.getDate() - i)

        const hasActivity = history.some(activity => {
            const activityDate = new Date(activity.timestamp)
            return activityDate.toDateString() === checkDate.toDateString()
        })

        if (hasActivity) {
            streak++
        } else if (i > 0) {
            break
        }
    }

    return streak
}

function getFavoriteCategory(history: any[]) {
    const categories = history.reduce((acc, activity) => {
        acc[activity.type] = (acc[activity.type] || 0) + 1
        return acc
    }, {})

    return Object.keys(categories).reduce((a, b) => categories[a] > categories[b] ? a : b)
}

// Enhanced Entertainment Hub Component with dynamic features
function EntertainmentHub({
    profile,
    userPreferences,
    aiEngine,
    personalizedRecommendations,
    addActivityToHistory
}: {
    profile: Profile
    userPreferences: any
    aiEngine: EnhancedAILearningEngine | null
    personalizedRecommendations: any
    addActivityToHistory: (activity: any) => void
}) {
    const [activeSection, setActiveSection] = useState(() => {
        // Dynamic default section based on user preferences or time of day
        const hour = new Date().getHours()
        if (hour < 12) return userPreferences?.morningPreference || 'games'
        if (hour < 18) return userPreferences?.afternoonPreference || 'videos'
        return userPreferences?.eveningPreference || 'music'
    })
    // Real-time mood inference function
    const inferCurrentMood = useCallback(() => {
        const hour = new Date().getHours()
        const day = new Date().getDay()

        // Time-based mood inference
        if (hour >= 9 && hour <= 17 && day >= 1 && day <= 5) return 'Focus'
        if (hour >= 18 || day === 0 || day === 6) return 'Relax'
        if (hour >= 6 && hour <= 9) return 'Energy'
        return 'Creative'
    }, [])

    const [currentMood, setCurrentMood] = useState(() => {
        // Infer current mood from time and recent activity inline
        const hour = new Date().getHours()
        const day = new Date().getDay()

        // Time-based mood inference
        if (hour >= 9 && hour <= 17 && day >= 1 && day <= 5) return 'Focus'
        if (hour >= 18 || day === 0 || day === 6) return 'Relax'
        if (hour >= 6 && hour <= 9) return 'Energy'
        return 'Creative'
    })
    const [recentActivity, setRecentActivity] = useState<any[]>([])

    // Update mood dynamically
    useEffect(() => {
        const interval = setInterval(() => {
            const newMood = inferCurrentMood()
            if (newMood !== currentMood) {
                setCurrentMood(newMood)
            }
        }, 60000) // Check every minute

        return () => clearInterval(interval)
    }, [currentMood, inferCurrentMood])

    return (
        <div className="space-y-6">
            {/* Entertainment Navigation */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                        <Play className="h-5 w-5" />
                        <span>Choose Your Experience</span>
                    </CardTitle>
                    <p className="text-muted-foreground">
                        Select what type of content you'd like to explore today
                    </p>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-3 gap-4 mb-6">
                        <Button
                            variant="ghost"
                            onClick={() => setActiveSection('games')}
                            className={`h-16 flex flex-col justify-center items-center space-y-1.5 relative overflow-hidden transition-all duration-500 group border-0 ${activeSection === 'games'
                                    ? 'bg-green-500/20 backdrop-blur-xl border border-green-400/30 shadow-lg shadow-green-500/20 dark:shadow-green-400/15'
                                    : 'bg-white/10 dark:bg-white/5 backdrop-blur-lg border border-white/20 dark:border-white/10 hover:bg-green-500/10 hover:border-green-400/20 hover:shadow-md hover:shadow-green-500/10'
                                }`}
                        >
                            <GlowingEffect disabled={false} proximity={120} spread={35} blur={1.5} />

                            {/* Liquid glass morphing background */}
                            <div className={`absolute inset-0 transition-all duration-700 ease-out ${activeSection === 'games'
                                    ? 'bg-gradient-to-br from-green-400/30 via-emerald-500/20 to-green-600/30'
                                    : 'bg-gradient-to-br from-white/5 via-green-500/5 to-white/10 group-hover:from-green-400/10 group-hover:via-emerald-500/10 group-hover:to-green-600/15'
                                }`} />

                            {/* Animated liquid blob */}
                            <div className={`absolute w-32 h-32 -top-8 -left-8 rounded-full transition-all duration-1000 ease-in-out ${activeSection === 'games'
                                    ? 'bg-green-400/30 blur-xl animate-pulse'
                                    : 'bg-green-500/10 blur-2xl group-hover:bg-green-400/20 group-hover:scale-110'
                                }`} />

                            {/* Glass reflection effect */}
                            <div className="absolute inset-0 bg-gradient-to-br from-white/20 via-transparent to-transparent opacity-50" />

                            <Gamepad2 className={`h-5 w-5 transition-all duration-300 group-hover:scale-110 relative z-10 ${activeSection === 'games'
                                    ? 'text-green-100 drop-shadow-sm filter brightness-110'
                                    : 'text-green-600 dark:text-green-400 group-hover:text-green-500 dark:group-hover:text-green-300'
                                }`} />
                            <span className={`text-xs font-semibold transition-all duration-300 relative z-10 ${activeSection === 'games'
                                    ? 'text-green-50 drop-shadow-sm filter brightness-110'
                                    : 'text-green-700 dark:text-green-300 group-hover:text-green-600 dark:group-hover:text-green-200'
                                }`}>Games</span>
                        </Button>

                        <Button
                            variant="ghost"
                            onClick={() => setActiveSection('videos')}
                            className={`h-16 flex flex-col justify-center items-center space-y-1.5 relative overflow-hidden transition-all duration-500 group border-0 ${activeSection === 'videos'
                                    ? 'bg-blue-500/20 backdrop-blur-xl border border-blue-400/30 shadow-lg shadow-blue-500/20 dark:shadow-blue-400/15'
                                    : 'bg-white/10 dark:bg-white/5 backdrop-blur-lg border border-white/20 dark:border-white/10 hover:bg-blue-500/10 hover:border-blue-400/20 hover:shadow-md hover:shadow-blue-500/10'
                                }`}
                        >
                            <GlowingEffect disabled={false} proximity={120} spread={35} blur={1.5} />

                            {/* Liquid glass morphing background */}
                            <div className={`absolute inset-0 transition-all duration-700 ease-out ${activeSection === 'videos'
                                    ? 'bg-gradient-to-br from-blue-400/30 via-cyan-500/20 to-blue-600/30'
                                    : 'bg-gradient-to-br from-white/5 via-blue-500/5 to-white/10 group-hover:from-blue-400/10 group-hover:via-cyan-500/10 group-hover:to-blue-600/15'
                                }`} />

                            {/* Animated liquid blob */}
                            <div className={`absolute w-32 h-32 -top-8 -right-8 rounded-full transition-all duration-1000 ease-in-out ${activeSection === 'videos'
                                    ? 'bg-blue-400/30 blur-xl animate-pulse'
                                    : 'bg-blue-500/10 blur-2xl group-hover:bg-blue-400/20 group-hover:scale-110'
                                }`} />

                            {/* Glass reflection effect */}
                            <div className="absolute inset-0 bg-gradient-to-br from-white/20 via-transparent to-transparent opacity-50" />

                            <Camera className={`h-5 w-5 transition-all duration-300 group-hover:scale-110 relative z-10 ${activeSection === 'videos'
                                    ? 'text-blue-100 drop-shadow-sm filter brightness-110'
                                    : 'text-blue-600 dark:text-blue-400 group-hover:text-blue-500 dark:group-hover:text-blue-300'
                                }`} />
                            <span className={`text-xs font-semibold transition-all duration-300 relative z-10 ${activeSection === 'videos'
                                    ? 'text-blue-50 drop-shadow-sm filter brightness-110'
                                    : 'text-blue-700 dark:text-blue-300 group-hover:text-blue-600 dark:group-hover:text-blue-200'
                                }`}>Videos</span>
                        </Button>

                        <Button
                            variant="ghost"
                            onClick={() => setActiveSection('music')}
                            className={`h-16 flex flex-col justify-center items-center space-y-1.5 relative overflow-hidden transition-all duration-500 group border-0 ${activeSection === 'music'
                                    ? 'bg-purple-500/20 backdrop-blur-xl border border-purple-400/30 shadow-lg shadow-purple-500/20 dark:shadow-purple-400/15'
                                    : 'bg-white/10 dark:bg-white/5 backdrop-blur-lg border border-white/20 dark:border-white/10 hover:bg-purple-500/10 hover:border-purple-400/20 hover:shadow-md hover:shadow-purple-500/10'
                                }`}
                        >
                            <GlowingEffect disabled={false} proximity={120} spread={35} blur={1.5} />

                            {/* Liquid glass morphing background */}
                            <div className={`absolute inset-0 transition-all duration-700 ease-out ${activeSection === 'music'
                                    ? 'bg-gradient-to-br from-purple-400/30 via-pink-500/20 to-purple-600/30'
                                    : 'bg-gradient-to-br from-white/5 via-purple-500/5 to-white/10 group-hover:from-purple-400/10 group-hover:via-pink-500/10 group-hover:to-purple-600/15'
                                }`} />

                            {/* Animated liquid blob */}
                            <div className={`absolute w-32 h-32 -bottom-8 -left-8 rounded-full transition-all duration-1000 ease-in-out ${activeSection === 'music'
                                    ? 'bg-purple-400/30 blur-xl animate-pulse'
                                    : 'bg-purple-500/10 blur-2xl group-hover:bg-purple-400/20 group-hover:scale-110'
                                }`} />

                            {/* Glass reflection effect */}
                            <div className="absolute inset-0 bg-gradient-to-br from-white/20 via-transparent to-transparent opacity-50" />

                            <Headphones className={`h-5 w-5 transition-all duration-300 group-hover:scale-110 relative z-10 ${activeSection === 'music'
                                    ? 'text-purple-100 drop-shadow-sm filter brightness-110'
                                    : 'text-purple-600 dark:text-purple-400 group-hover:text-purple-500 dark:group-hover:text-purple-300'
                                }`} />
                            <span className={`text-xs font-semibold transition-all duration-300 relative z-10 ${activeSection === 'music'
                                    ? 'text-purple-50 drop-shadow-sm filter brightness-110'
                                    : 'text-purple-700 dark:text-purple-300 group-hover:text-purple-600 dark:group-hover:text-purple-200'
                                }`}>Music</span>
                        </Button>
                    </div>

                    {/* Dynamic Content Area */}
                    {activeSection === 'games' && (
                        <GamingSection
                            profile={profile}
                            userPreferences={userPreferences}
                            aiEngine={aiEngine}
                            recommendations={personalizedRecommendations?.games}
                            addActivityToHistory={addActivityToHistory}
                        />
                    )}
                    {activeSection === 'videos' && (
                        <VideoSection
                            profile={profile}
                            userPreferences={userPreferences}
                            aiEngine={aiEngine}
                            recommendations={personalizedRecommendations?.videos}
                            addActivityToHistory={addActivityToHistory}
                        />
                    )}
                    {activeSection === 'music' && (
                        <MusicSection
                            profile={profile}
                            currentMood={currentMood}
                            userPreferences={userPreferences}
                            aiEngine={aiEngine}
                            recommendations={personalizedRecommendations?.music}
                            addActivityToHistory={addActivityToHistory}
                        />
                    )}
                </CardContent>
            </Card>
        </div>
    )
}

// Copy the rest of the components from dashboard (GamingSection, VideoSection, MusicSection)
// I'll include simplified versions here due to space constraints

function GamingSection({
    profile,
    userPreferences,
    aiEngine,
    recommendations,
    addActivityToHistory
}: {
    profile: Profile
    userPreferences: any
    aiEngine: EnhancedAILearningEngine | null
    recommendations?: any[]
    addActivityToHistory: (activity: any) => void
}) {
    const [selectedGame, setSelectedGame] = useState<string | null>(null)
    const [gameResults, setGameResults] = useState<any[]>([])
    const [gameStats, setGameStats] = useState<{
        [key: string]: {
            completions?: number
            averageScore?: number
            bestScore?: number
            startTime?: number
            endTime?: number
            attempts?: number
        }
    }>({})

    // Dynamic game library based on user preferences and skill level
    const availableGames = useMemo(() => {
        const baseGames = [
            {
                id: 'puzzle_master',
                name: 'Puzzle Master',
                category: 'Puzzle',
                description: 'Test your spatial reasoning and pattern recognition',
                icon: '🧩',
                difficulty: 'Medium',
                insights: ['Problem-solving approach', 'Spatial reasoning', 'Persistence patterns'],
                duration: '10-15 min',
                component: PuzzleMaster,
                popularity: 85,
                recentPlays: 12
            },
            {
                id: 'memory_palace',
                name: 'Memory Palace',
                category: 'Strategy',
                description: 'Enhance memory and strategic thinking',
                icon: '🧠',
                difficulty: 'Easy',
                insights: ['Memory patterns', 'Strategic planning', 'Attention to detail'],
                duration: '5-10 min',
                component: MemoryPalace,
                popularity: 92,
                recentPlays: 8
            },
            {
                id: 'color_symphony',
                name: 'Color Symphony',
                category: 'Creative',
                description: 'Express creativity through color and pattern',
                icon: '🎨',
                difficulty: 'Easy',
                insights: ['Creative expression', 'Aesthetic preferences', 'Emotional associations'],
                duration: '15-20 min',
                component: ColorSymphony,
                popularity: 78,
                recentPlays: 15
            }
        ]

        // Filter and sort based on user preferences
        return baseGames
            .filter(game => {
                if (!userPreferences?.favoriteGameTypes) return true
                return userPreferences.favoriteGameTypes.includes(game.category.toLowerCase())
            })
            .sort((a, b) => {
                // Prioritize based on recommendations and popularity
                if (recommendations?.some(r => r.type === a.category.toLowerCase())) return -1
                if (recommendations?.some(r => r.type === b.category.toLowerCase())) return 1
                return b.popularity - a.popularity
            })
    }, [userPreferences, recommendations])

    const handleGameComplete = useCallback(async (gameData: any) => {
        // Enhanced game completion handling
        const enhancedData = {
            ...gameData,
            userId: profile.id,
            timestamp: new Date().toISOString(),
            sessionDuration: Date.now() - (gameStats[gameData.gameId]?.startTime || Date.now())
        }

        setGameResults(prev => [...prev, enhancedData])
        setSelectedGame(null)

        // Add to main activity history for stats dashboard
        const activityData = {
            type: 'game',
            name: gameData.gameId,
            duration: enhancedData.sessionDuration / 1000, // Convert to seconds
            timestamp: enhancedData.timestamp,
            performance: gameData.performance,
            completionRate: gameData.completionRate
        }
        addActivityToHistory(activityData)

        // Update game stats
        setGameStats(prev => ({
            ...prev,
            [gameData.gameId]: {
                ...prev[gameData.gameId],
                completions: (prev[gameData.gameId]?.completions || 0) + 1,
                averageScore: calculateAverageScore(prev[gameData.gameId], gameData),
                bestScore: Math.max(prev[gameData.gameId]?.bestScore || 0, gameData.completionRate),
                endTime: Date.now()
            }
        }))

        // Send to AI engine for analysis
        if (aiEngine) {
            await aiEngine.addGameplayData(enhancedData)
        }
    }, [profile.id, gameStats, aiEngine, addActivityToHistory])

    const startGame = useCallback((gameId: string) => {
        setSelectedGame(gameId)
        setGameStats(prev => ({
            ...prev,
            [gameId]: {
                ...prev[gameId],
                startTime: Date.now(),
                attempts: (prev[gameId]?.attempts || 0) + 1
            }
        }))
    }, [])

    const calculateAverageScore = (existingStats: any, newData: any) => {
        if (!existingStats?.averageScore) return newData.completionRate
        const totalGames = existingStats.completions || 0
        return ((existingStats.averageScore * totalGames) + newData.completionRate) / (totalGames + 1)
    }

    const selectedGameData = availableGames.find(game => game.id === selectedGame)

    if (selectedGame && selectedGameData) {
        const GameComponent = selectedGameData.component
        return (
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <h3 className="font-semibold">Playing: {selectedGameData.name}</h3>
                    <Button variant="outline" onClick={() => setSelectedGame(null)}>
                        Back to Games
                    </Button>
                </div>
                <GameComponent onGameComplete={handleGameComplete} />
            </div>
        )
    }

    return (
        <div className="space-y-4">
            {/* Game Performance Summary */}
            {Object.keys(gameStats).length > 0 && (
                <Card className="mb-4 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-950/20 dark:to-emerald-950/20">
                    <CardHeader>
                        <CardTitle className="text-lg">Your Gaming Progress</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            {Object.entries(gameStats).map(([gameId, stats]: [string, any]) => {
                                const game = availableGames.find(g => g.id === gameId)
                                return (
                                    <div key={gameId} className="p-3 bg-white dark:bg-gray-800 rounded-lg">
                                        <div className="flex items-center space-x-2 mb-2">
                                            <span className="text-lg">{game?.icon}</span>
                                            <span className="font-medium text-sm">{game?.name}</span>
                                        </div>
                                        <div className="space-y-1 text-xs text-muted-foreground">
                                            <div>Games: {stats.completions || 0}</div>
                                            <div>Best: {stats.bestScore || 0}%</div>
                                            <div>Avg: {Math.round(stats.averageScore || 0)}%</div>
                                        </div>
                                    </div>
                                )
                            })}
                        </div>
                    </CardContent>
                </Card>
            )}

            <div className="grid gap-4">
                {availableGames.map((game) => {
                    const stats = gameStats[game.id]
                    const isRecommended = recommendations?.some(r => r.games?.includes(game.id))

                    return (
                        <Card key={game.id} className={`p-4 hover:shadow-md transition-shadow cursor-pointer relative ${isRecommended ? 'ring-2 ring-green-400 bg-green-50 dark:bg-green-950/10' : ''
                            }`}>
                            <GlowingEffect disabled={false} proximity={150} spread={40} blur={2} />

                            {/* Recommendation Badge */}
                            {isRecommended && (
                                <div className="absolute -top-2 -right-2 z-20">
                                    <Badge className="bg-green-500 text-white">
                                        <Star className="h-3 w-3 mr-1" />
                                        Recommended
                                    </Badge>
                                </div>
                            )}

                            <div className="flex items-center justify-between relative z-10">
                                <div className="flex items-center space-x-4">
                                    <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center text-2xl">
                                        {game.icon}
                                    </div>
                                    <div className="flex-1">
                                        <div className="flex items-center space-x-2 mb-1">
                                            <h4 className="font-semibold">{game.name}</h4>
                                            {game.recentPlays && (
                                                <Badge variant="outline" className="text-xs">
                                                    <Users className="h-3 w-3 mr-1" />
                                                    {game.recentPlays}
                                                </Badge>
                                            )}
                                        </div>
                                        <p className="text-sm text-muted-foreground mb-2">{game.description}</p>
                                        <div className="flex flex-wrap gap-1 mb-2">
                                            {game.insights.map((insight, index) => (
                                                <Badge key={index} variant="secondary" className="text-xs">
                                                    {insight}
                                                </Badge>
                                            ))}
                                        </div>
                                        <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                                            <span className="flex items-center">
                                                <Clock className="h-3 w-3 mr-1" />
                                                {game.duration}
                                            </span>
                                            <span>Difficulty: {game.difficulty}</span>
                                            <span>❤️ {game.popularity}%</span>
                                            {stats && (
                                                <span className="text-green-600 dark:text-green-400">
                                                    Best: {stats.bestScore}%
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                </div>
                                <Button onClick={() => startGame(game.id)} className="flex-shrink-0">
                                    <Play className="h-4 w-4 mr-2" />
                                    {stats?.completions ? 'Play Again' : 'Play'}
                                </Button>
                            </div>
                        </Card>
                    )
                })}
            </div>
        </div>
    )
}

function VideoSection({
    profile,
    userPreferences,
    aiEngine,
    recommendations,
    addActivityToHistory
}: {
    profile: Profile
    userPreferences: any
    aiEngine: EnhancedAILearningEngine | null
    recommendations?: any[]
    addActivityToHistory: (activity: any) => void
}) {
    const [selectedCategory, setSelectedCategory] = useState(() => {
        // Dynamic default category based on user preferences or time
        return userPreferences?.preferredVideoCategory || 'mental_health'
    })
    const [selectedVideo, setSelectedVideo] = useState<any | null>(null)
    const [watchHistory, setWatchHistory] = useState<any[]>([])
    const [videoProgress, setVideoProgress] = useState<{ [key: string]: number }>({})

    const categories = [
        { id: 'mental_health', name: 'Wellness', icon: '🧘', color: 'bg-green-100 text-green-800' },
        { id: 'educational', name: 'Learning', icon: '📚', color: 'bg-blue-100 text-blue-800' },
        { id: 'entertainment', name: 'Fun', icon: '🎭', color: 'bg-purple-100 text-purple-800' }
    ]

    // Dynamic video library with personalization
    const availableVideos = useMemo(() => {
        const baseVideos = [
            {
                id: '1',
                title: '5-Minute Breathing Exercise',
                description: 'Learn powerful breathing techniques to manage stress and anxiety.',
                category: 'mental_health',
                duration: 323,
                thumbnail: '🌿',
                tags: ['breathing', 'anxiety', 'mindfulness'],
                insights: ['Stress response', 'Mindfulness engagement', 'Focus duration'],
                difficulty: 'beginner',
                views: 1250,
                rating: 4.8,
                instructor: 'Dr. Sarah Chen'
            },
            {
                id: '2',
                title: 'Understanding Emotions',
                description: 'Explore the science behind emotions and healthy processing.',
                category: 'educational',
                duration: 765,
                thumbnail: '🧠',
                tags: ['emotions', 'psychology', 'self-awareness'],
                insights: ['Learning style', 'Attention span', 'Concept retention'],
                difficulty: 'intermediate',
                views: 892,
                rating: 4.6,
                instructor: 'Prof. Michael Torres'
            },
            {
                id: '3',
                title: 'Quick Stress Relief',
                description: 'Instant techniques for managing overwhelming moments.',
                category: 'mental_health',
                duration: 180,
                thumbnail: '⚡',
                tags: ['stress', 'quick-relief', 'workplace'],
                insights: ['Stress management', 'Coping strategies', 'Emotional regulation'],
                difficulty: 'beginner',
                views: 2100,
                rating: 4.9,
                instructor: 'Lisa Rodriguez'
            }
        ]

        // Filter based on preferences and sort by relevance
        return baseVideos
            .filter(video => {
                if (userPreferences?.preferredVideoLength === 'short' && video.duration > 600) return false
                if (userPreferences?.preferredVideoLength === 'long' && video.duration < 600) return false
                return true
            })
            .sort((a, b) => {
                // Prioritize recommended content
                const aRecommended = recommendations?.some(r => r.contentId === a.id)
                const bRecommended = recommendations?.some(r => r.contentId === b.id)
                if (aRecommended && !bRecommended) return -1
                if (!aRecommended && bRecommended) return 1

                // Then by rating and views
                return (b.rating * Math.log(b.views)) - (a.rating * Math.log(a.views))
            })
    }, [userPreferences, recommendations])

    const handleVideoComplete = useCallback(async (watchData: any) => {
        const enhancedData = {
            ...watchData,
            userId: profile.id,
            timestamp: new Date().toISOString(),
            category: selectedCategory
        }

        setSelectedVideo(null)
        setWatchHistory(prev => [...prev, enhancedData])

        // Add to main activity history for stats dashboard
        const activityData = {
            type: 'video',
            name: watchData.contentId,
            duration: watchData.watchTime, // Watch time in seconds
            timestamp: enhancedData.timestamp,
            category: selectedCategory,
            completionRate: watchData.completionRate
        }
        addActivityToHistory(activityData)

        // Update progress
        setVideoProgress(prev => ({
            ...prev,
            [watchData.contentId]: 100
        }))

        if (aiEngine) {
            await aiEngine.addVideoData(enhancedData)
        }
    }, [profile.id, selectedCategory, aiEngine, addActivityToHistory])

    const handleVideoProgress = useCallback((videoId: string, progress: number) => {
        setVideoProgress(prev => ({
            ...prev,
            [videoId]: progress
        }))
    }, [])

    const formatDuration = (seconds: number) => {
        const mins = Math.floor(seconds / 60)
        const secs = seconds % 60
        return `${mins}:${secs.toString().padStart(2, '0')}`
    }

    if (selectedVideo) {
        return (
            <VideoPlayer
                video={selectedVideo}
                onWatchComplete={handleVideoComplete}
                onClose={() => setSelectedVideo(null)}
            />
        )
    }

    return (
        <div className="space-y-4">
            {/* Watch Progress Summary */}
            {watchHistory.length > 0 && (
                <Card className="mb-4 bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-950/20 dark:to-cyan-950/20">
                    <CardHeader>
                        <CardTitle className="text-lg">Your Learning Journey</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                            <div>
                                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                                    {watchHistory.length}
                                </div>
                                <div className="text-sm text-muted-foreground">Videos Watched</div>
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-cyan-600 dark:text-cyan-400">
                                    {Math.round(watchHistory.reduce((acc, w) => acc + w.watchTime, 0) / 60)}m
                                </div>
                                <div className="text-sm text-muted-foreground">Learning Time</div>
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                                    {Math.round(watchHistory.reduce((acc, w) => acc + w.completionRate, 0) / watchHistory.length)}%
                                </div>
                                <div className="text-sm text-muted-foreground">Avg Completion</div>
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                                    {new Set(watchHistory.map(w => w.category)).size}
                                </div>
                                <div className="text-sm text-muted-foreground">Topics Explored</div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}

            <div className="flex flex-wrap gap-2 mb-4">
                {categories.map((category) => {
                    const categoryVideos = availableVideos.filter(v => v.category === category.id)
                    const watchedCount = watchHistory.filter(w => w.category === category.id).length

                    return (
                        <Button
                            key={category.id}
                            variant={selectedCategory === category.id ? 'default' : 'outline'}
                            onClick={() => setSelectedCategory(category.id)}
                            size="sm"
                            className="relative"
                        >
                            <span className="mr-2">{category.icon}</span>
                            {category.name}
                            {watchedCount > 0 && (
                                <Badge variant="secondary" className="ml-2 text-xs">
                                    {watchedCount}
                                </Badge>
                            )}
                        </Button>
                    )
                })}
            </div>

            <div className="grid gap-4">
                {availableVideos.filter(v => v.category === selectedCategory).map((video) => {
                    const progress = videoProgress[video.id] || 0
                    const isRecommended = recommendations?.some(r => r.contentId === video.id)
                    const hasWatched = watchHistory.some(w => w.contentId === video.id)

                    return (
                        <Card key={video.id} className={`p-4 hover:shadow-md transition-shadow cursor-pointer relative ${isRecommended ? 'ring-2 ring-blue-400 bg-blue-50 dark:bg-blue-950/10' : ''
                            }`}>
                            <GlowingEffect disabled={false} proximity={150} spread={40} blur={2} />

                            {/* Recommendation Badge */}
                            {isRecommended && (
                                <div className="absolute -top-2 -right-2 z-20">
                                    <Badge className="bg-blue-500 text-white">
                                        <Star className="h-3 w-3 mr-1" />
                                        For You
                                    </Badge>
                                </div>
                            )}

                            {/* Progress Bar */}
                            {progress > 0 && (
                                <div className="absolute top-0 left-0 right-0 h-1 bg-gray-200 dark:bg-gray-700 rounded-t-lg overflow-hidden">
                                    <div
                                        className="h-full bg-blue-500 transition-all duration-300"
                                        style={{ width: `${progress}%` }}
                                    />
                                </div>
                            )}

                            <div className="flex items-center space-x-4 relative z-10">
                                <div className="w-20 h-16 bg-gradient-to-r from-red-500 to-orange-500 rounded-lg flex items-center justify-center text-3xl flex-shrink-0 relative">
                                    {video.thumbnail}
                                    {hasWatched && (
                                        <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                                            <span className="text-white text-xs">✓</span>
                                        </div>
                                    )}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center space-x-2 mb-1">
                                        <h4 className="font-medium text-lg">{video.title}</h4>
                                        {video.rating && (
                                            <div className="flex items-center space-x-1">
                                                <Star className="h-3 w-3 text-yellow-500 fill-current" />
                                                <span className="text-xs text-muted-foreground">{video.rating}</span>
                                            </div>
                                        )}
                                    </div>
                                    <p className="text-sm text-muted-foreground mb-2">{video.description}</p>
                                    <div className="flex items-center space-x-4 text-sm text-muted-foreground mb-2">
                                        <span className="flex items-center">
                                            <Clock className="h-3 w-3 mr-1" />
                                            {formatDuration(video.duration)}
                                        </span>
                                        <span className="flex items-center">
                                            <Users className="h-3 w-3 mr-1" />
                                            {video.views}
                                        </span>
                                        <span>By {video.instructor}</span>
                                    </div>
                                    <div className="flex flex-wrap gap-1">
                                        {video.tags.map((tag, index) => (
                                            <Badge key={index} variant="secondary" className="text-xs">
                                                {tag}
                                            </Badge>
                                        ))}
                                    </div>
                                </div>
                                <Button onClick={() => setSelectedVideo(video)} className="flex-shrink-0">
                                    <Play className="h-4 w-4 mr-2" />
                                    {hasWatched ? 'Rewatch' : 'Watch'}
                                </Button>
                            </div>
                        </Card>
                    )
                })}
            </div>
        </div>
    )
}

function MusicSection({
    profile,
    currentMood,
    userPreferences,
    aiEngine,
    recommendations,
    addActivityToHistory
}: {
    profile: Profile
    currentMood: string
    userPreferences: any
    aiEngine: EnhancedAILearningEngine | null
    recommendations?: any[]
    addActivityToHistory: (activity: any) => void
}) {
    const [selectedMood, setSelectedMood] = useState(currentMood || 'Focus')
    const [currentTrack, setCurrentTrack] = useState<any | null>(null)
    const [isPlaying, setIsPlaying] = useState(false)
    const [listeningHistory, setListeningHistory] = useState<any[]>([])
    const [playlistProgress, setPlaylistProgress] = useState<{ [key: string]: number }>({})

    // Dynamic mood detection and suggestions
    const moods = useMemo(() => {
        const baseMoods = [
            { name: 'Focus', emoji: '🎯', description: 'Deep work and concentration', color: 'from-blue-500 to-indigo-500' },
            { name: 'Relax', emoji: '🌊', description: 'Calm and peaceful', color: 'from-green-500 to-teal-500' },
            { name: 'Energy', emoji: '⚡', description: 'Upbeat and motivating', color: 'from-red-500 to-pink-500' },
            { name: 'Creative', emoji: '🎨', description: 'Inspiration and flow', color: 'from-purple-500 to-pink-500' }
        ]

        // Add user's favorite moods to the top
        const userFavorites = userPreferences?.musicMoods || []
        return baseMoods.sort((a, b) => {
            const aIsFavorite = userFavorites.includes(a.name)
            const bIsFavorite = userFavorites.includes(b.name)
            if (aIsFavorite && !bIsFavorite) return -1
            if (!aIsFavorite && bIsFavorite) return 1
            return 0
        })
    }, [userPreferences])

    // Dynamic playlist generation
    const availablePlaylists = useMemo(() => {
        const hour = new Date().getHours()
        const day = new Date().getDay()
        const isWeekend = [0, 6].includes(day)

        const basePlaylists = [
            {
                id: 1,
                name: 'Deep Focus Flow',
                mood: 'Focus',
                tracks: 24,
                duration: '1h 45m',
                cover: '🎵',
                popularity: 95,
                personalizedFor: 'work sessions',
                context: hour >= 9 && hour <= 17 ? 'workday' : 'evening',
                tracks_list: [
                    { id: 1, title: 'Concentrated Mind', artist: 'Focus Collective', duration: 240, plays: 120 },
                    { id: 2, title: 'Neural Networks', artist: 'Brain Waves', duration: 300, plays: 89 },
                    { id: 3, title: 'Flow State', artist: 'Productivity Labs', duration: 280, plays: 156 }
                ]
            },
            {
                id: 2,
                name: 'Evening Unwind',
                mood: 'Relax',
                tracks: 18,
                duration: '1h 12m',
                cover: '🌙',
                popularity: 88,
                personalizedFor: 'relaxation',
                context: hour >= 18 ? 'evening' : 'anytime',
                tracks_list: [
                    { id: 4, title: 'Gentle Waves', artist: 'Nature Sounds', duration: 220, plays: 95 },
                    { id: 5, title: 'Mindful Breathing', artist: 'Calm Collective', duration: 180, plays: 112 }
                ]
            },
            {
                id: 3,
                name: 'Creative Spark',
                mood: 'Creative',
                tracks: 32,
                duration: '2h 5m',
                cover: '✨',
                popularity: 92,
                personalizedFor: 'creative work',
                context: 'inspiration',
                tracks_list: [
                    { id: 6, title: 'Innovation Frequency', artist: 'Creative Minds', duration: 245, plays: 78 },
                    { id: 7, title: 'Artistic Flow', artist: 'Inspiration Inc', duration: 290, plays: 134 }
                ]
            }
        ]

        // Filter and sort based on current context and preferences
        return basePlaylists
            .filter(playlist => {
                if (selectedMood && playlist.mood !== selectedMood) return false
                return true
            })
            .sort((a, b) => {
                // Prioritize contextually relevant playlists
                const aContextMatch = a.context === (isWeekend ? 'weekend' : 'workday')
                const bContextMatch = b.context === (isWeekend ? 'weekend' : 'workday')
                if (aContextMatch && !bContextMatch) return -1
                if (!aContextMatch && bContextMatch) return 1

                // Then by popularity and user history
                return b.popularity - a.popularity
            })
    }, [selectedMood])

    const handlePlaylistComplete = useCallback(async (listenData: any) => {
        const enhancedData = {
            ...listenData,
            userId: profile.id,
            timestamp: new Date().toISOString(),
            context: determineListeningContext(),
            mood: selectedMood
        }

        setListeningHistory(prev => [...prev, enhancedData])

        // Add to main activity history for stats dashboard
        const activityData = {
            type: 'music',
            name: listenData.playlistId || 'playlist',
            duration: listenData.duration || 0, // Duration in seconds
            timestamp: enhancedData.timestamp,
            mood: selectedMood,
            context: enhancedData.context
        }
        addActivityToHistory(activityData)

        if (aiEngine) {
            await aiEngine.addMusicData(enhancedData)
        }
    }, [profile.id, selectedMood, aiEngine, addActivityToHistory])

    const determineListeningContext = () => {
        const hour = new Date().getHours()
        if (hour >= 6 && hour <= 11) return 'morning'
        if (hour >= 12 && hour <= 17) return 'afternoon'
        if (hour >= 18 && hour <= 22) return 'evening'
        return 'night'
    }

    const handleMoodChange = useCallback((mood: string) => {
        setSelectedMood(mood)
        // Track mood changes for AI learning
        if (aiEngine) {
            aiEngine.addMusicData({
                type: 'mood_change',
                fromMood: selectedMood,
                toMood: mood,
                timestamp: new Date().toISOString(),
                context: determineListeningContext()
            })
        }
    }, [selectedMood, aiEngine])

    // Real-time mood suggestions based on time and activity
    useEffect(() => {
        if (currentMood && currentMood !== selectedMood) {
            setSelectedMood(currentMood)
        }
    }, [currentMood, selectedMood])

    return (
        <div className="space-y-6">
            {/* Listening Stats */}
            {listeningHistory.length > 0 && (
                <Card className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20">
                    <CardHeader>
                        <CardTitle className="text-lg">Your Music Journey</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                            <div>
                                <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                                    {listeningHistory.length}
                                </div>
                                <div className="text-sm text-muted-foreground">Sessions</div>
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-pink-600 dark:text-pink-400">
                                    {Math.round(listeningHistory.reduce((acc, h) => acc + (h.duration || 0), 0) / 3600)}h
                                </div>
                                <div className="text-sm text-muted-foreground">Listening Time</div>
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                                    {new Set(listeningHistory.map(h => h.mood)).size}
                                </div>
                                <div className="text-sm text-muted-foreground">Moods Explored</div>
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                                    {selectedMood}
                                </div>
                                <div className="text-sm text-muted-foreground">Current Mood</div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Smart Mood Selection */}
            <Card>
                <CardHeader>
                    <CardTitle>Choose Your Mood</CardTitle>
                    <p className="text-muted-foreground">
                        AI-suggested based on time: {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {moods.map((mood) => {
                            const isRecommended = mood.name === currentMood
                            const hasHistory = listeningHistory.some(h => h.mood === mood.name)

                            return (
                                <div
                                    key={mood.name}
                                    onClick={() => handleMoodChange(mood.name)}
                                    className={`
                    relative overflow-hidden rounded-xl p-6 cursor-pointer transition-all duration-300 group
                    ${selectedMood === mood.name
                                            ? `bg-gradient-to-br ${mood.color} text-white shadow-lg scale-105`
                                            : 'bg-white dark:bg-card hover:bg-gray-50 dark:hover:bg-gray-800 border hover:shadow-md'
                                        }
                  `}
                                >
                                    {isRecommended && (
                                        <div className="absolute -top-1 -right-1">
                                            <Badge className="bg-yellow-500 text-white text-xs">
                                                <Star className="h-2 w-2 mr-1" />
                                                AI Pick
                                            </Badge>
                                        </div>
                                    )}

                                    <div className="text-center space-y-2">
                                        <div className="text-3xl">{mood.emoji}</div>
                                        <h3 className="font-semibold">{mood.name}</h3>
                                        <p className="text-xs opacity-80">{mood.description}</p>
                                        {hasHistory && (
                                            <div className="text-xs text-green-600 dark:text-green-400">
                                                ✓ Previously enjoyed
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                </CardContent>
            </Card>

            {/* Dynamic Playlists */}
            {selectedMood && (
                <div className="grid gap-4">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold">
                            {selectedMood} Playlists
                        </h3>
                        <Badge variant="outline">
                            {availablePlaylists.length} available
                        </Badge>
                    </div>

                    {availablePlaylists.map((playlist) => {
                        const progress = playlistProgress[playlist.id] || 0
                        const isRecommended = recommendations?.some(r => r.playlistId === playlist.id)

                        return (
                            <Card key={playlist.id} className={`p-4 relative ${isRecommended ? 'ring-2 ring-purple-400 bg-purple-50 dark:bg-purple-950/10' : ''
                                }`}>
                                <GlowingEffect disabled={false} proximity={150} spread={40} blur={2} />

                                {isRecommended && (
                                    <div className="absolute -top-2 -right-2 z-20">
                                        <Badge className="bg-purple-500 text-white">
                                            <Star className="h-3 w-3 mr-1" />
                                            Recommended
                                        </Badge>
                                    </div>
                                )}

                                {progress > 0 && (
                                    <div className="absolute top-0 left-0 right-0 h-1 bg-gray-200 dark:bg-gray-700 rounded-t-lg overflow-hidden">
                                        <div
                                            className="h-full bg-purple-500 transition-all duration-300"
                                            style={{ width: `${progress}%` }}
                                        />
                                    </div>
                                )}

                                <div className="flex items-center space-x-4 relative z-10">
                                    <div className={`w-16 h-16 bg-gradient-to-r ${playlist.mood === 'Focus' ? 'from-blue-500 to-indigo-500' :
                                        playlist.mood === 'Relax' ? 'from-green-500 to-teal-500' :
                                            playlist.mood === 'Energy' ? 'from-red-500 to-pink-500' :
                                                'from-purple-500 to-pink-500'} rounded-lg flex items-center justify-center text-2xl`}>
                                        {playlist.cover}
                                    </div>
                                    <div className="flex-1">
                                        <div className="flex items-center space-x-2 mb-1">
                                            <h4 className="font-medium">{playlist.name}</h4>
                                            <Badge variant="outline" className="text-xs">
                                                {playlist.popularity}% match
                                            </Badge>
                                        </div>
                                        <p className="text-sm text-muted-foreground mb-2">
                                            {playlist.tracks} tracks • {playlist.duration} • {playlist.personalizedFor}
                                        </p>
                                        <div className="text-xs text-muted-foreground">
                                            Perfect for {playlist.context} • Most popular track played {Math.max(...playlist.tracks_list.map(t => t.plays))} times
                                        </div>
                                    </div>
                                    <div className="flex flex-col space-y-2">
                                        <Button
                                            onClick={() => {
                                                setCurrentTrack(playlist)
                                                // Simulate listening session with playlist duration
                                                const estimatedDuration = playlist.tracks * 240 // Estimate 4 minutes per track
                                                handlePlaylistComplete({
                                                    playlistId: playlist.id,
                                                    mood: selectedMood,
                                                    duration: estimatedDuration, // Estimated listening time in seconds
                                                    context: determineListeningContext()
                                                })
                                            }}
                                            className="flex-shrink-0"
                                        >
                                            <Play className="h-4 w-4 mr-2" />
                                            Play
                                        </Button>
                                        {playlist.tracks_list.length > 0 && (
                                            <Button variant="outline" size="sm">
                                                <Volume2 className="h-3 w-3 mr-1" />
                                                Preview
                                            </Button>
                                        )}
                                    </div>
                                </div>
                            </Card>
                        )
                    })}
                </div>
            )}

            {/* Currently Playing */}
            {currentTrack && (
                <Card className="bg-gradient-to-r from-purple-600 to-pink-600 text-white">
                    <CardContent className="p-6">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-4">
                                <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center text-xl">
                                    {currentTrack.cover}
                                </div>
                                <div>
                                    <h4 className="font-semibold">{currentTrack.name}</h4>
                                    <p className="text-sm opacity-80">Now playing • {selectedMood} mood</p>
                                </div>
                            </div>
                            <div className="flex items-center space-x-2">
                                <Button variant="ghost" size="sm" className="text-white hover:bg-white/20">
                                    <Pause className="h-4 w-4" />
                                </Button>
                                <Button variant="ghost" size="sm" className="text-white hover:bg-white/20">
                                    <Volume2 className="h-4 w-4" />
                                </Button>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    )
}