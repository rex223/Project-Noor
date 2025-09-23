"use client"

import { useState, useRef, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Slider } from '@/components/ui/slider'
import { Play, Pause, Volume2, VolumeX, Maximize, SkipBack, SkipForward, Settings, Heart, Share2 } from 'lucide-react'

interface VideoWatchData {
  contentId: string
  userId: string
  sessionId: string
  watchTime: number
  totalDuration: number
  completionRate: number
  interactions: VideoInteraction[]
  emotionalResponse: EmotionalResponse[]
  skipPatterns: SkipPattern[]
}

interface VideoInteraction {
  timestamp: number
  action: 'pause' | 'play' | 'seek' | 'replay' | 'comment' | 'like' | 'share'
  context?: string
}

interface EmotionalResponse {
  timestamp: number
  emotion: 'joy' | 'sadness' | 'anger' | 'fear' | 'surprise' | 'disgust' | 'neutral'
  intensity: number
  context: string
}

interface SkipPattern {
  startTime: number
  endTime: number
  reason?: 'boring' | 'too_difficult' | 'emotional' | 'time_constraint'
}

interface VideoContent {
  id: string
  title: string
  description: string
  category: 'mental_health' | 'entertainment' | 'educational'
  duration: number
  thumbnail: string
  url: string
  tags: string[]
}

interface VideoPlayerProps {
  video: VideoContent
  onWatchComplete: (data: VideoWatchData) => void
  onClose: () => void
}

export function VideoPlayer({ video, onWatchComplete, onClose }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(1)
  const [isMuted, setIsMuted] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [showControls, setShowControls] = useState(true)
  const [playbackRate, setPlaybackRate] = useState(1)
  const [isBuffering, setIsBuffering] = useState(false)

  // Analytics
  const [watchStartTime] = useState(new Date())
  const [sessionId] = useState(() => Math.random().toString(36).substr(2, 9))
  const [interactions, setInteractions] = useState<VideoInteraction[]>([])
  const [skipPatterns, setSkipPatterns] = useState<SkipPattern[]>([])
  const [lastSeekTime, setLastSeekTime] = useState<number | null>(null)
  const [totalWatchTime, setTotalWatchTime] = useState(0)
  const [isLiked, setIsLiked] = useState(false)

  const controlsTimeoutRef = useRef<NodeJS.Timeout>()

  // Format time display
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  // Handle video events
  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration)
    }
  }

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime)
      setTotalWatchTime(prev => prev + 0.1) // Approximate watch time tracking
    }
  }

  const handlePlay = () => {
    setIsPlaying(true)
    addInteraction('play', `Resumed at ${formatTime(currentTime)}`)
  }

  const handlePause = () => {
    setIsPlaying(false)
    addInteraction('pause', `Paused at ${formatTime(currentTime)}`)
  }

  const handleWaiting = () => {
    setIsBuffering(true)
  }

  const handleCanPlay = () => {
    setIsBuffering(false)
  }

  const handleEnded = () => {
    setIsPlaying(false)
    completeWatching()
  }

  // Add interaction to analytics
  const addInteraction = useCallback((action: VideoInteraction['action'], context?: string) => {
    const interaction: VideoInteraction = {
      timestamp: currentTime,
      action,
      context
    }
    setInteractions(prev => [...prev, interaction])
  }, [currentTime])

  // Play/Pause toggle
  const togglePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause()
      } else {
        videoRef.current.play()
      }
    }
  }

  // Seek to specific time
  const seekTo = (time: number) => {
    if (videoRef.current) {
      const oldTime = currentTime
      videoRef.current.currentTime = time
      setCurrentTime(time)
      
      // Track seeking patterns
      if (lastSeekTime !== null && Math.abs(time - lastSeekTime) > 10) {
        const skipPattern: SkipPattern = {
          startTime: Math.min(oldTime, time),
          endTime: Math.max(oldTime, time),
          reason: time > oldTime ? 'boring' : undefined
        }
        setSkipPatterns(prev => [...prev, skipPattern])
      }
      
      setLastSeekTime(time)
      addInteraction('seek', `Seeked to ${formatTime(time)}`)
    }
  }

  // Volume control
  const handleVolumeChange = (newVolume: number[]) => {
    const vol = newVolume[0]
    setVolume(vol)
    if (videoRef.current) {
      videoRef.current.volume = vol
    }
    if (vol === 0 && !isMuted) {
      setIsMuted(true)
    } else if (vol > 0 && isMuted) {
      setIsMuted(false)
    }
  }

  // Mute toggle
  const toggleMute = () => {
    if (videoRef.current) {
      const newMuted = !isMuted
      setIsMuted(newMuted)
      videoRef.current.muted = newMuted
      addInteraction(newMuted ? 'pause' : 'play', `Audio ${newMuted ? 'muted' : 'unmuted'}`)
    }
  }

  // Skip forward/backward
  const skipForward = () => {
    seekTo(Math.min(currentTime + 10, duration))
  }

  const skipBackward = () => {
    seekTo(Math.max(currentTime - 10, 0))
  }

  // Playback speed
  const changePlaybackRate = (rate: number) => {
    if (videoRef.current) {
      videoRef.current.playbackRate = rate
      setPlaybackRate(rate)
      addInteraction('play', `Changed speed to ${rate}x`)
    }
  }

  // Fullscreen toggle
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      videoRef.current?.requestFullscreen()
      setIsFullscreen(true)
    } else {
      document.exitFullscreen()
      setIsFullscreen(false)
    }
  }

  // Like video
  const toggleLike = () => {
    setIsLiked(!isLiked)
    addInteraction('like', isLiked ? 'Unliked video' : 'Liked video')
  }

  // Share video
  const shareVideo = () => {
    addInteraction('share', 'Shared video')
    // Implement sharing logic here
  }

  // Complete watching session
  const completeWatching = useCallback(() => {
    const watchData: VideoWatchData = {
      contentId: video.id,
      userId: 'current_user',
      sessionId,
      watchTime: totalWatchTime,
      totalDuration: duration,
      completionRate: (currentTime / duration) * 100,
      interactions,
      emotionalResponse: [], // This could be enhanced with facial recognition or user feedback
      skipPatterns
    }
    
    onWatchComplete(watchData)
  }, [video.id, sessionId, totalWatchTime, duration, currentTime, interactions, skipPatterns, onWatchComplete])

  // Auto-hide controls
  const resetControlsTimeout = () => {
    setShowControls(true)
    if (controlsTimeoutRef.current) {
      clearTimeout(controlsTimeoutRef.current)
    }
    controlsTimeoutRef.current = setTimeout(() => {
      if (isPlaying) {
        setShowControls(false)
      }
    }, 3000)
  }

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      switch (e.code) {
        case 'Space':
          e.preventDefault()
          togglePlayPause()
          break
        case 'ArrowLeft':
          e.preventDefault()
          skipBackward()
          break
        case 'ArrowRight':
          e.preventDefault()
          skipForward()
          break
        case 'KeyM':
          e.preventDefault()
          toggleMute()
          break
        case 'KeyF':
          e.preventDefault()
          toggleFullscreen()
          break
      }
    }

    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [isPlaying])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (controlsTimeoutRef.current) {
        clearTimeout(controlsTimeoutRef.current)
      }
      // Send final analytics if video was watched
      if (totalWatchTime > 30) {
        completeWatching()
      }
    }
  }, [totalWatchTime, completeWatching])

  return (
    <Card className="w-full max-w-4xl mx-auto bg-black text-white">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-white">{video.title}</CardTitle>
          <Button variant="ghost" onClick={onClose} className="text-white hover:bg-gray-800">
            ×
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div 
          className="relative aspect-video bg-black"
          onMouseMove={resetControlsTimeout}
          onMouseLeave={() => setShowControls(false)}
        >
          <video
            ref={videoRef}
            className="w-full h-full"
            onLoadedMetadata={handleLoadedMetadata}
            onTimeUpdate={handleTimeUpdate}
            onPlay={handlePlay}
            onPause={handlePause}
            onEnded={handleEnded}
            onWaiting={handleWaiting}
            onCanPlay={handleCanPlay}
            onClick={togglePlayPause}
          >
            <source src={video.url} type="video/mp4" />
            Your browser does not support the video tag.
          </video>

          {/* Loading spinner */}
          {isBuffering && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white"></div>
            </div>
          )}

          {/* Play button overlay */}
          {!isPlaying && !isBuffering && (
            <div className="absolute inset-0 flex items-center justify-center">
              <Button
                size="lg"
                className="rounded-full w-20 h-20 bg-white/20 hover:bg-white/30 backdrop-blur"
                onClick={togglePlayPause}
              >
                <Play className="h-8 w-8 text-white ml-1" />
              </Button>
            </div>
          )}

          {/* Video Controls */}
          {showControls && (
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
              {/* Progress Bar */}
              <div className="mb-4">
                <Slider
                  value={[currentTime]}
                  max={duration}
                  step={0.1}
                  onValueChange={([time]) => seekTo(time)}
                  className="w-full"
                />
                <div className="flex justify-between text-sm mt-1">
                  <span>{formatTime(currentTime)}</span>
                  <span>{formatTime(duration)}</span>
                </div>
              </div>

              {/* Control Buttons */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Button variant="ghost" size="sm" onClick={skipBackward}>
                    <SkipBack className="h-4 w-4" />
                  </Button>
                  
                  <Button variant="ghost" size="sm" onClick={togglePlayPause}>
                    {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                  </Button>
                  
                  <Button variant="ghost" size="sm" onClick={skipForward}>
                    <SkipForward className="h-4 w-4" />
                  </Button>

                  <div className="flex items-center space-x-2 ml-4">
                    <Button variant="ghost" size="sm" onClick={toggleMute}>
                      {isMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
                    </Button>
                    
                    <div className="w-20">
                      <Slider
                        value={[volume]}
                        max={1}
                        step={0.1}
                        onValueChange={handleVolumeChange}
                      />
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={toggleLike}
                    className={isLiked ? 'text-red-500' : ''}
                  >
                    <Heart className={`h-4 w-4 ${isLiked ? 'fill-current' : ''}`} />
                  </Button>
                  
                  <Button variant="ghost" size="sm" onClick={shareVideo}>
                    <Share2 className="h-4 w-4" />
                  </Button>

                  {/* Speed Control */}
                  <select
                    value={playbackRate}
                    onChange={(e) => changePlaybackRate(Number(e.target.value))}
                    className="bg-transparent text-white text-sm border border-gray-600 rounded px-2 py-1"
                  >
                    <option value={0.5}>0.5x</option>
                    <option value={0.75}>0.75x</option>
                    <option value={1}>1x</option>
                    <option value={1.25}>1.25x</option>
                    <option value={1.5}>1.5x</option>
                    <option value={2}>2x</option>
                  </select>

                  <Button variant="ghost" size="sm" onClick={toggleFullscreen}>
                    <Maximize className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Video Info */}
        <div className="p-4 bg-gray-900">
          <div className="flex flex-wrap gap-2 mb-2">
            {video.tags.map(tag => (
              <Badge key={tag} variant="secondary" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
          <p className="text-sm text-gray-300">{video.description}</p>
          
          {/* Analytics Preview */}
          <div className="mt-4 text-xs text-gray-400 space-y-1">
            <p>Watch Progress: {Math.round((currentTime / duration) * 100)}%</p>
            <p>Interactions: {interactions.length}</p>
            <p>Skip Events: {skipPatterns.length}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
