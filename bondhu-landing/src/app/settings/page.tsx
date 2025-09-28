"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { createClient } from "@/lib/supabase/client"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, ChevronRight, Settings, User } from "lucide-react"
import { GlowingEffect } from "@/components/ui/glowing-effect"
import type { Profile } from "@/types/auth"
import { Logo } from "@/components/logo"
import { ThemeToggle } from "@/components/theme-toggle"
import { aiLearningEngine } from "@/lib/ai-learning-engine"
import Link from "next/link"

export default function SettingsPage() {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [deactivateStatus, setDeactivateStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [escapeStatus, setEscapeStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [isDisappearing, setIsDisappearing] = useState(false)
  const [nameChangeStatus, setNameChangeStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [avatarUploadStatus, setAvatarUploadStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [newName, setNewName] = useState('')
  const router = useRouter()
  const supabase = createClient()

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
      } catch (error) {
        console.error('Error:', error)
      } finally {
        setIsLoading(false)
      }
    }

    getProfile()
  }, [supabase, router])

  const handleDeactivateAccount = async () => {
    if (!confirm('Are you sure you want to deactivate your account? Your data will be preserved for 30 days and you can reactivate anytime.')) {
      return
    }

    setDeactivateStatus('loading')
    try {
      // Update user profile to mark as deactivated
      const { error } = await supabase
        .from('profiles')
        .update({ 
          is_active: false,
          deactivated_at: new Date().toISOString()
        })
        .eq('id', profile?.id)

      if (error) {
        throw error
      }

      setDeactivateStatus('success')
      
      // Sign out user after deactivation
      setTimeout(async () => {
        await supabase.auth.signOut()
        router.push('/sign-in?message=Account deactivated successfully')
      }, 2000)

    } catch (error) {
      console.error('Deactivation failed:', error)
      setDeactivateStatus('error')
      setTimeout(() => setDeactivateStatus('idle'), 3000)
    }
  }

  const handleEscapeMatrix = async () => {
    if (!confirm('⚠️ ESCAPE THE MATRIX ⚠️\n\nThis will PERMANENTLY delete:\n• All your data\n• Your account\n• Everything from all systems\n\nThis cannot be undone. Are you absolutely sure?')) {
      return
    }

    // Proper text input dialog
    const confirmationText = prompt('Last chance! This action is IRREVERSIBLE.\n\nType "ESCAPE" (in capital letters) to confirm you want to delete everything forever:')
    
    if (confirmationText !== 'ESCAPE') {
      if (confirmationText !== null) { // User didn't cancel
        alert('❌ Confirmation failed. You must type "ESCAPE" exactly to proceed.')
      }
      return
    }

    setEscapeStatus('loading')
    setIsDisappearing(true)

    try {
      // Start the deletion process
      setTimeout(async () => {
        try {
          // First sign out the user to invalidate session
          await supabase.auth.signOut()
          
          // Delete all user data from profiles table
          const { error: profileError } = await supabase
            .from('profiles')
            .delete()
            .eq('id', profile?.id)

          if (profileError) {
            console.error('Profile deletion error:', profileError)
          }

          // Call server-side API to delete user from Supabase Auth
          try {
            const response = await fetch('/api/delete-user', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ userId: profile?.id })
            })

            if (!response.ok) {
              console.error('Failed to delete user from auth system')
            }
          } catch (apiError) {
            console.error('API call failed:', apiError)
          }
          
          // Clear all local storage and cached data
          localStorage.clear()
          sessionStorage.clear()
          
          // Clear all cookies
          document.cookie.split(";").forEach((c) => {
            document.cookie = c
              .replace(/^ +/, "")
              .replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/")
          })
          
          setEscapeStatus('success')
          
          // Redirect after animation completes
          setTimeout(() => {
            window.location.href = '/sign-in?message=Successfully escaped the matrix! 🎭✨'
          }, 2000)
          
        } catch (deletionError) {
          console.error('Matrix escape deletion failed:', deletionError)
          setEscapeStatus('error')
          setIsDisappearing(false)
          setTimeout(() => setEscapeStatus('idle'), 3000)
        }
      }, 3000) // Wait for disappearing animation
      
    } catch (error) {
      console.error('Matrix escape failed:', error)
      setEscapeStatus('error')
      setIsDisappearing(false)
      setTimeout(() => setEscapeStatus('idle'), 3000)
    }
  }

  const handleNameChange = async () => {
    if (!newName.trim()) {
      alert('Please enter a new name')
      return
    }

    if (newName.trim() === profile?.full_name) {
      alert('New name cannot be the same as current name')
      return
    }

    // Check if user can change name (30-day cooldown)
    const lastNameChange = profile?.last_name_change
    if (lastNameChange) {
      const lastChangeDate = new Date(lastNameChange)
      const daysSinceLastChange = Math.floor((Date.now() - lastChangeDate.getTime()) / (1000 * 60 * 60 * 24))
      
      if (daysSinceLastChange < 30) {
        const remainingDays = 30 - daysSinceLastChange
        alert(`You can change your name again in ${remainingDays} days. Last change was ${daysSinceLastChange} days ago.`)
        return
      }
    }

    if (!confirm(`Are you sure you want to change your name from "${profile?.full_name}" to "${newName.trim()}"?\n\nYou won't be able to change it again for 30 days.`)) {
      return
    }

    setNameChangeStatus('loading')
    try {
      const { error } = await supabase
        .from('profiles')
        .update({ 
          full_name: newName.trim(),
          last_name_change: new Date().toISOString()
        })
        .eq('id', profile?.id)

      if (error) {
        throw error
      }

      // Update local profile state
      setProfile(prev => prev ? {
        ...prev,
        full_name: newName.trim(),
        last_name_change: new Date().toISOString()
      } : null)

      setNameChangeStatus('success')
      setNewName('')
      setTimeout(() => setNameChangeStatus('idle'), 3000)

    } catch (error) {
      console.error('Name change failed:', error)
      setNameChangeStatus('error')
      setTimeout(() => setNameChangeStatus('idle'), 3000)
    }
  }

  const handleAvatarUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please select a valid image file')
      return
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('Image size must be less than 5MB')
      return
    }

    setAvatarUploadStatus('loading')
    try {
      // Create unique filename
      const fileExt = file.name.split('.').pop()
      const fileName = `${profile?.id}-${Date.now()}.${fileExt}`

      // Upload to Supabase storage
      const { error: uploadError } = await supabase.storage
        .from('avatars')
        .upload(fileName, file, {
          upsert: true
        })

      if (uploadError) {
        throw uploadError
      }

      // Get public URL
      const { data: { publicUrl } } = supabase.storage
        .from('avatars')
        .getPublicUrl(fileName)

      // Update profile with new avatar URL
      const { error: updateError } = await supabase
        .from('profiles')
        .update({ avatar_url: publicUrl })
        .eq('id', profile?.id)

      if (updateError) {
        throw updateError
      }

      // Update local profile state
      setProfile(prev => prev ? {
        ...prev,
        avatar_url: publicUrl
      } : null)

      setAvatarUploadStatus('success')
      setTimeout(() => setAvatarUploadStatus('idle'), 3000)

    } catch (error) {
      console.error('Avatar upload failed:', error)
      setAvatarUploadStatus('error')
      setTimeout(() => setAvatarUploadStatus('idle'), 3000)
    }
  }

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
    <div className={`min-h-screen bg-gradient-to-br from-background via-background to-secondary/20 relative ${isDisappearing ? 'animate-pulse' : ''}`}>
      {/* Thanos Snap Disappearing Animation Overlay */}
      {isDisappearing && (
        <div className="fixed inset-0 z-50 pointer-events-none">
          <div className="absolute inset-0 bg-black/20"></div>
          {/* Dust particles animation */}
          {Array.from({ length: 20 }).map((_, i) => (
            <div
              key={i}
              className={`absolute w-2 h-2 bg-gray-400 rounded-full animate-bounce opacity-70`}
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 2}s`,
                animationDuration: `${1 + Math.random() * 2}s`
              }}
            />
          ))}
          {/* Fade out effect */}
          <div className="absolute inset-0 bg-white transition-opacity duration-3000 ease-in-out opacity-100" />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center text-gray-700 z-10">
              <div className="text-6xl mb-4 animate-bounce">💨</div>
              <h2 className="text-2xl font-bold mb-2 animate-pulse">Escaping the Matrix...</h2>
              <p className="text-lg opacity-70">Your digital existence is being erased...</p>
            </div>
          </div>
        </div>
      )}
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
                <h1 className="text-lg font-semibold text-muted-foreground">Privacy & Settings</h1>
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
      <main className="container mx-auto px-4 py-6 max-w-4xl">
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
            <span className="text-foreground font-medium">Privacy & Settings</span>
          </div>
        </div>

        {/* Hero Section */}
        <div className="mb-8">
          <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20 border-blue-200 dark:border-blue-800">
            <CardContent className="p-8">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-6">
                  <Avatar className="h-20 w-20 border-4 border-white shadow-lg">
                    <AvatarFallback className="text-2xl bg-gradient-to-br from-blue-500 to-indigo-500 text-white">
                      {profile.full_name?.split(' ').map(n => n[0]).join('') || 'U'}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                      Privacy & Settings
                    </h1>
                    <p className="text-muted-foreground text-lg">
                      Manage your data, privacy preferences, and account settings
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                    <Settings className="h-12 w-12" />
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Your Control Center
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Settings Content */}
        <SettingsPanel 
          profile={profile} 
          deactivateStatus={deactivateStatus}
          escapeStatus={escapeStatus}
          isDisappearing={isDisappearing}
          nameChangeStatus={nameChangeStatus}
          avatarUploadStatus={avatarUploadStatus}
          newName={newName}
          setNewName={setNewName}
          handleDeactivateAccount={handleDeactivateAccount}
          handleEscapeMatrix={handleEscapeMatrix}
          handleNameChange={handleNameChange}
          handleAvatarUpload={handleAvatarUpload}
        />
      </main>
    </div>
  )
}

// Settings Panel Component (moved from dashboard)
function SettingsPanel({ 
  profile, 
  deactivateStatus, 
  escapeStatus, 
  isDisappearing,
  nameChangeStatus,
  avatarUploadStatus,
  newName,
  setNewName,
  handleDeactivateAccount, 
  handleEscapeMatrix,
  handleNameChange,
  handleAvatarUpload
}: { 
  profile: Profile;
  deactivateStatus: 'idle' | 'loading' | 'success' | 'error';
  escapeStatus: 'idle' | 'loading' | 'success' | 'error';
  isDisappearing: boolean;
  nameChangeStatus: 'idle' | 'loading' | 'success' | 'error';
  avatarUploadStatus: 'idle' | 'loading' | 'success' | 'error';
  newName: string;
  setNewName: (name: string) => void;
  handleDeactivateAccount: () => void;
  handleEscapeMatrix: () => void;
  handleNameChange: () => void;
  handleAvatarUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
}) {
  const [dataSettings, setDataSettings] = useState({
    gamingData: true,
    videoData: true,
    musicData: true,
    personalityAnalytics: true,
    aiRecommendations: true,
    crossModalInsights: true,
    dataRetention: 365, // days
    shareAnonymized: false,
    exportFormat: 'json'
  })

  const [exportStatus, setExportStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [deleteStatus, setDeleteStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')

  const handleSettingChange = (setting: string, value: boolean | number | string) => {
    setDataSettings(prev => ({ ...prev, [setting]: value }))
    // In real app, this would sync with backend
    console.log('Updated setting:', setting, value)
  }

  const handleExportData = async () => {
    setExportStatus('loading')
    try {
      // Get all data from AI learning engine
      const exportData = aiLearningEngine.exportForExternalAnalysis()
      
      // Add user profile data
      const fullExport = {
        profile: {
          id: profile.id,
          full_name: profile.full_name,
          created_at: profile.created_at,
          personality_data: profile.personality_data
        },
        entertainmentData: exportData,
        settings: dataSettings,
        exportDate: new Date().toISOString()
      }

      // Create and download file
      const blob = new Blob([JSON.stringify(fullExport, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `bondhu-data-export-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      setExportStatus('success')
      setTimeout(() => setExportStatus('idle'), 3000)
    } catch (error) {
      console.error('Export failed:', error)
      setExportStatus('error')
      setTimeout(() => setExportStatus('idle'), 3000)
    }
  }

  const handleDeleteData = async (dataType: 'gaming' | 'video' | 'music' | 'all') => {
    if (!confirm(`Are you sure you want to delete all ${dataType} data? This action cannot be undone.`)) {
      return
    }

    setDeleteStatus('loading')
    try {
      // In real app, this would call backend API
      console.log('Deleting data type:', dataType)
      
      // For demo, we'll clear the AI learning engine data
      if (dataType === 'all') {
        // Would reset the entire learning engine
        console.log('All entertainment data deleted')
      }

      setDeleteStatus('success')
      setTimeout(() => setDeleteStatus('idle'), 3000)
    } catch (error) {
      console.error('Delete failed:', error)
      setDeleteStatus('error')
      setTimeout(() => setDeleteStatus('idle'), 3000)
    }
  }

  return (
    <div className="space-y-6">
      {/* Profile Settings */}
      <Card className="relative">
        <GlowingEffect disabled={false} proximity={150} spread={40} blur={2} />
        <CardHeader className="relative z-10">
          <CardTitle className="flex items-center space-x-2">
            <User className="h-5 w-5" />
            <span>Profile Settings</span>
          </CardTitle>
          <p className="text-muted-foreground">
            Customize your profile appearance and personal information
          </p>
        </CardHeader>
        <CardContent className="relative z-10">
          <div className="space-y-6">
            {/* Avatar Upload */}
            <div>
              <h4 className="font-medium mb-4">Profile Picture</h4>
              <div className="flex items-center space-x-4">
                <div className="relative">
                  <Avatar className="h-20 w-20">
                    {profile.avatar_url ? (
                      <img 
                        src={profile.avatar_url} 
                        alt="Profile" 
                        className="w-full h-full object-cover rounded-full"
                      />
                    ) : (
                      <AvatarFallback className="text-2xl bg-gradient-to-br from-blue-500 to-purple-500 text-white">
                        {profile.full_name?.split(' ').map(n => n[0]).join('') || 'U'}
                      </AvatarFallback>
                    )}
                  </Avatar>
                  {avatarUploadStatus === 'loading' && (
                    <div className="absolute inset-0 bg-black/50 rounded-full flex items-center justify-center">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                    </div>
                  )}
                </div>
                <div className="flex-1">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleAvatarUpload}
                    className="hidden"
                    id="avatar-upload"
                    disabled={avatarUploadStatus === 'loading'}
                  />
                  <label
                    htmlFor="avatar-upload"
                    className={`inline-flex items-center px-4 py-2 rounded-md text-sm font-medium cursor-pointer transition-colors ${
                      avatarUploadStatus === 'loading'
                        ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                        : 'bg-primary text-primary-foreground hover:bg-primary/90'
                    }`}
                  >
                    {avatarUploadStatus === 'loading' ? 'Uploading...' : 
                     avatarUploadStatus === 'success' ? 'Uploaded!' : 
                     'Change Avatar'}
                  </label>
                  <p className="text-xs text-muted-foreground mt-2">
                    Upload a new profile picture (Max 5MB, JPG/PNG/GIF)
                  </p>
                </div>
              </div>
            </div>

            {/* Name Change */}
            <div>
              <h4 className="font-medium mb-4">Display Name</h4>
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Current Name</label>
                  <div className="mt-1 p-3 bg-muted rounded-md">
                    <span className="font-medium">{profile.full_name}</span>
                  </div>
                </div>

                {(() => {
                  const lastNameChange = profile.last_name_change
                  const canChangeName = !lastNameChange || 
                    Math.floor((Date.now() - new Date(lastNameChange).getTime()) / (1000 * 60 * 60 * 24)) >= 30
                  
                  const daysSinceLastChange = lastNameChange ? 
                    Math.floor((Date.now() - new Date(lastNameChange).getTime()) / (1000 * 60 * 60 * 24)) : null
                  
                  const remainingDays = daysSinceLastChange !== null ? Math.max(0, 30 - daysSinceLastChange) : 0

                  return (
                    <div>
                      <label className="text-sm font-medium">New Name</label>
                      <div className="mt-1 flex space-x-2">
                        <input
                          type="text"
                          value={newName}
                          onChange={(e) => setNewName(e.target.value)}
                          placeholder="Enter new display name"
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                          disabled={!canChangeName || nameChangeStatus === 'loading'}
                        />
                        <Button
                          onClick={handleNameChange}
                          disabled={!canChangeName || !newName.trim() || nameChangeStatus === 'loading'}
                          size="sm"
                        >
                          {nameChangeStatus === 'loading' ? 'Updating...' : 
                           nameChangeStatus === 'success' ? 'Updated!' : 
                           'Change Name'}
                        </Button>
                      </div>
                      
                      {!canChangeName && remainingDays > 0 && (
                        <p className="text-xs text-amber-600 mt-2">
                          ⏳ You can change your name again in {remainingDays} days
                        </p>
                      )}
                      
                      {canChangeName && (
                        <p className="text-xs text-muted-foreground mt-2">
                          You can change your name once every 30 days
                        </p>
                      )}

                      {lastNameChange && (
                        <p className="text-xs text-muted-foreground mt-1">
                          Last changed: {new Date(lastNameChange).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  )
                })()}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Privacy Controls */}
      <Card className="relative">
        <GlowingEffect disabled={false} proximity={150} spread={40} blur={2} />
        <CardHeader className="relative z-10">
          <CardTitle className="flex items-center space-x-2">
            <Settings className="h-5 w-5" />
            <span>Privacy & Data Controls</span>
          </CardTitle>
          <p className="text-muted-foreground">
            Manage how Bondhu collects and uses your data for personalization
          </p>
        </CardHeader>
        <CardContent className="relative z-10">
          <div className="space-y-6">
            {/* Entertainment Data Collection */}
            <div>
              <h4 className="font-medium mb-4">Entertainment Data Collection</h4>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="font-medium">Gaming Analytics</h5>
                    <p className="text-sm text-muted-foreground">Track game choices, performance, and playing patterns</p>
                  </div>
                  <Button
                    variant={dataSettings.gamingData ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleSettingChange('gamingData', !dataSettings.gamingData)}
                  >
                    {dataSettings.gamingData ? 'Enabled' : 'Disabled'}
                  </Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="font-medium">Video Viewing Analytics</h5>
                    <p className="text-sm text-muted-foreground">Monitor watch time, completion rates, and content preferences</p>
                  </div>
                  <Button
                    variant={dataSettings.videoData ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleSettingChange('videoData', !dataSettings.videoData)}
                  >
                    {dataSettings.videoData ? 'Enabled' : 'Disabled'}
                  </Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="font-medium">Music Listening Analytics</h5>
                    <p className="text-sm text-muted-foreground">Analyze listening habits, mood patterns, and genre preferences</p>
                  </div>
                  <Button
                    variant={dataSettings.musicData ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleSettingChange('musicData', !dataSettings.musicData)}
                  >
                    {dataSettings.musicData ? 'Enabled' : 'Disabled'}
                  </Button>
                </div>
              </div>
            </div>

            {/* AI Features */}
            <div>
              <h4 className="font-medium mb-4">AI Features</h4>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="font-medium">Personality Analytics</h5>
                    <p className="text-sm text-muted-foreground">Generate Big Five personality insights from behavior patterns</p>
                  </div>
                  <Button
                    variant={dataSettings.personalityAnalytics ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleSettingChange('personalityAnalytics', !dataSettings.personalityAnalytics)}
                  >
                    {dataSettings.personalityAnalytics ? 'Enabled' : 'Disabled'}
                  </Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="font-medium">AI Recommendations</h5>
                    <p className="text-sm text-muted-foreground">Receive personalized content and activity suggestions</p>
                  </div>
                  <Button
                    variant={dataSettings.aiRecommendations ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleSettingChange('aiRecommendations', !dataSettings.aiRecommendations)}
                  >
                    {dataSettings.aiRecommendations ? 'Enabled' : 'Disabled'}
                  </Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="font-medium">Cross-Modal Insights</h5>
                    <p className="text-sm text-muted-foreground">Analyze patterns across different entertainment types</p>
                  </div>
                  <Button
                    variant={dataSettings.crossModalInsights ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleSettingChange('crossModalInsights', !dataSettings.crossModalInsights)}
                  >
                    {dataSettings.crossModalInsights ? 'Enabled' : 'Disabled'}
                  </Button>
                </div>
              </div>
            </div>

            {/* Data Retention */}
            <div>
              <h4 className="font-medium mb-4">Data Retention</h4>
              <div className="space-y-3">
                <div>
                  <label className="text-sm font-medium">Keep my data for:</label>
                  <select
                    value={dataSettings.dataRetention}
                    onChange={(e) => handleSettingChange('dataRetention', Number(e.target.value))}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                  >
                    <option value={30}>30 days</option>
                    <option value={90}>3 months</option>
                    <option value={180}>6 months</option>
                    <option value={365}>1 year</option>
                    <option value={730}>2 years</option>
                    <option value={-1}>Until I delete it</option>
                  </select>
                </div>
                <p className="text-xs text-muted-foreground">
                  Data older than this will be automatically deleted. Analysis and insights will be preserved.
                </p>
              </div>
            </div>

            {/* Anonymized Sharing */}
            <div className="flex items-center justify-between">
              <div>
                <h5 className="font-medium">Contribute to Research</h5>
                <p className="text-sm text-muted-foreground">Share anonymized data to improve mental health AI research</p>
              </div>
              <Button
                variant={dataSettings.shareAnonymized ? "default" : "outline"}
                size="sm"
                onClick={() => handleSettingChange('shareAnonymized', !dataSettings.shareAnonymized)}
              >
                {dataSettings.shareAnonymized ? 'Contributing' : 'Not Contributing'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Data Management */}
      <Card className="relative">
        <GlowingEffect disabled={false} proximity={150} spread={40} blur={2} />
        <CardHeader className="relative z-10">
          <CardTitle>Data Management & Export</CardTitle>
          <p className="text-muted-foreground">
            Download, view, or delete your personal data
          </p>
        </CardHeader>
        <CardContent className="relative z-10">
          <div className="space-y-4">
            {/* Export Data */}
            <div className="p-4 border rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h4 className="font-medium">Export Your Data</h4>
                  <p className="text-sm text-muted-foreground">
                    Download all your data in JSON format
                  </p>
                </div>
                <Button 
                  onClick={handleExportData}
                  disabled={exportStatus === 'loading'}
                  className="flex items-center space-x-2"
                >
                  {exportStatus === 'loading' && <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>}
                  <span>
                    {exportStatus === 'loading' ? 'Exporting...' : 
                     exportStatus === 'success' ? 'Exported!' : 
                     exportStatus === 'error' ? 'Error' : 'Export Data'}
                  </span>
                </Button>
              </div>
              <div className="text-xs text-muted-foreground space-y-1">
                <p>• Includes: Profile, entertainment data, analytics, preferences</p>
                <p>• Format: JSON file compatible with data portability standards</p>
                <p>• Privacy: Your personal data only, no other users' information</p>
              </div>
            </div>

            {/* View Data Usage */}
            <div className="p-4 border rounded-lg">
              <h4 className="font-medium mb-3">Data Usage Summary</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Entertainment Sessions:</span>
                  <span className="font-medium ml-2">47</span>
                </div>
                <div>
                  <span className="text-muted-foreground">AI Insights Generated:</span>
                  <span className="font-medium ml-2">23</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Games Played:</span>
                  <span className="font-medium ml-2">12</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Videos Watched:</span>
                  <span className="font-medium ml-2">8</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Music Sessions:</span>
                  <span className="font-medium ml-2">27</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Total Data Size:</span>
                  <span className="font-medium ml-2">2.3 MB</span>
                </div>
              </div>
            </div>

            {/* Delete Specific Data */}
            <div className="p-4 border border-red-200 rounded-lg">
              <h4 className="font-medium text-red-900 mb-3">Delete Specific Data</h4>
              <div className="grid gap-3">
                <Button 
                  variant="outline" 
                  className="w-full justify-start text-red-600 hover:text-red-700 border-red-200 hover:border-red-300"
                  onClick={() => handleDeleteData('gaming')}
                  disabled={deleteStatus === 'loading'}
                >
                  Delete Gaming Data
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start text-red-600 hover:text-red-700 border-red-200 hover:border-red-300"
                  onClick={() => handleDeleteData('video')}
                  disabled={deleteStatus === 'loading'}
                >
                  Delete Video Data
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start text-red-600 hover:text-red-700 border-red-200 hover:border-red-300"
                  onClick={() => handleDeleteData('music')}
                  disabled={deleteStatus === 'loading'}
                >
                  Delete Music Data
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start text-red-600 hover:text-red-700 border-red-200 hover:border-red-300"
                  onClick={() => handleDeleteData('all')}
                  disabled={deleteStatus === 'loading'}
                >
                  Delete All Entertainment Data
                </Button>
              </div>
              <p className="text-xs text-red-600 mt-3">
                Warning: Deleted data cannot be recovered. Your personality insights will be preserved.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Account Settings */}
      <Card className="relative">
        <GlowingEffect disabled={false} proximity={150} spread={40} blur={2} />
        <CardHeader className="relative z-10">
          <CardTitle>Account Settings</CardTitle>
        </CardHeader>
        <CardContent className="relative z-10">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Account Status</h4>
                <p className="text-sm text-muted-foreground">Active since {new Date(profile.created_at).toLocaleDateString()}</p>
              </div>
              <Badge variant="secondary">Active</Badge>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Email Notifications</h4>
                <p className="text-sm text-muted-foreground">Weekly insights and recommendations</p>
              </div>
              <Button variant="outline" size="sm">Configure</Button>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Two-Factor Authentication</h4>
                <p className="text-sm text-muted-foreground">Additional security for your account</p>
              </div>
              <Button variant="outline" size="sm">Enable</Button>
            </div>

            <div className="pt-4 border-t space-y-4">
              <div>
                <Button 
                  variant="outline" 
                  className="w-full text-red-600 hover:text-red-700"
                  onClick={handleDeactivateAccount}
                  disabled={deactivateStatus === 'loading'}
                >
                  {deactivateStatus === 'loading' ? 'Deactivating...' : 
                   deactivateStatus === 'success' ? 'Deactivated!' : 
                   'Deactivate Account'}
                </Button>
                <p className="text-xs text-muted-foreground mt-2 text-center">
                  This will disable your account but preserve your data for 30 days
                </p>
              </div>

              {/* Escape the Matrix Button */}
              <div className="pt-4 border-t border-red-200">
                <div className="text-center mb-4">
                  <h4 className="font-medium text-red-700 mb-2">⚠️ Nuclear Option ⚠️</h4>
                  <p className="text-xs text-red-600">
                    Complete digital erasure - no coming back from this
                  </p>
                </div>
                <Button 
                  variant="destructive" 
                  className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 relative overflow-hidden group"
                  onClick={handleEscapeMatrix}
                  disabled={escapeStatus === 'loading' || isDisappearing}
                >
                  <span className="relative z-10 flex items-center justify-center">
                    {escapeStatus === 'loading' ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Initiating Matrix Escape...
                      </>
                    ) : escapeStatus === 'success' ? (
                      '✨ Escaped Successfully ✨'
                    ) : (
                      '🔴 ESCAPE THE MATRIX 🔴'
                    )}
                  </span>
                  <div className="absolute inset-0 bg-gradient-to-r from-red-600 via-orange-500 to-red-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                </Button>
                <p className="text-xs text-red-700 mt-2 text-center font-medium">
                  Permanently deletes EVERYTHING - Account, data, existence
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Privacy Information */}
      <Card className="relative">
        <GlowingEffect disabled={false} proximity={150} spread={40} blur={2} />
        <CardHeader className="relative z-10">
          <CardTitle>Privacy Information</CardTitle>
        </CardHeader>
        <CardContent className="relative z-10">
          <div className="space-y-3 text-sm">
            <div>
              <h5 className="font-medium">Data Processing</h5>
              <p className="text-muted-foreground">
                Your entertainment data is processed locally and encrypted before storage. 
                AI analysis happens on secure servers with strict access controls.
              </p>
            </div>
            <div>
              <h5 className="font-medium">Data Sharing</h5>
              <p className="text-muted-foreground">
                We never sell personal data. Anonymized research contributions are optional 
                and help improve mental health AI for everyone.
              </p>
            </div>
            <div>
              <h5 className="font-medium">Your Rights</h5>
              <p className="text-muted-foreground">
                You have the right to access, correct, delete, or port your data at any time. 
                Contact support for assistance with data requests.
              </p>
            </div>
            <div className="pt-3 border-t">
              <div className="flex gap-4">
                <Button variant="ghost" size="sm">Privacy Policy</Button>
                <Button variant="ghost" size="sm">Terms of Service</Button>
                <Button variant="ghost" size="sm">Contact Support</Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Status Messages */}
      {(exportStatus === 'success' || deleteStatus === 'success' || deactivateStatus === 'success' || escapeStatus === 'success' || nameChangeStatus === 'success' || avatarUploadStatus === 'success') && (
        <div className="fixed bottom-4 right-4 p-4 bg-green-50 border border-green-200 rounded-lg shadow-lg z-40">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-green-500 rounded-full"></div>
            <span className="text-green-800 font-medium">
              {exportStatus === 'success' ? 'Data exported successfully!' : 
               deleteStatus === 'success' ? 'Data deleted successfully!' :
               deactivateStatus === 'success' ? 'Account deactivated successfully!' :
               escapeStatus === 'success' ? '✨ Successfully escaped the matrix! ✨' :
               nameChangeStatus === 'success' ? 'Name changed successfully!' :
               avatarUploadStatus === 'success' ? 'Avatar updated successfully!' : ''}
            </span>
          </div>
        </div>
      )}

      {(exportStatus === 'error' || deleteStatus === 'error' || deactivateStatus === 'error' || escapeStatus === 'error' || nameChangeStatus === 'error' || avatarUploadStatus === 'error') && (
        <div className="fixed bottom-4 right-4 p-4 bg-red-50 border border-red-200 rounded-lg shadow-lg z-40">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-red-500 rounded-full"></div>
            <span className="text-red-800 font-medium">
              {escapeStatus === 'error' ? 'Matrix escape failed! The system resisted.' : 
               nameChangeStatus === 'error' ? 'Name change failed. Please try again.' :
               avatarUploadStatus === 'error' ? 'Avatar upload failed. Please try again.' :
               'Operation failed. Please try again.'}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}