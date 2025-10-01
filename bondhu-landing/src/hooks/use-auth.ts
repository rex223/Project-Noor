/**
 * Authentication hook for Bondhu AI
 * Provides user session and profile information
 */

'use client'

import { useEffect, useState, useCallback } from 'react'
import { createClient } from '@/lib/supabase/client'
import type { User, Session } from '@supabase/supabase-js'
import type { Profile } from '@/types/auth'

interface UseAuthReturn {
    user: User | null
    profile: Profile | null
    session: Session | null
    isLoading: boolean
    error: Error | null
    signOut: () => Promise<void>
    refreshProfile: () => Promise<void>
}

export function useAuth(): UseAuthReturn {
    const [user, setUser] = useState<User | null>(null)
    const [profile, setProfile] = useState<Profile | null>(null)
    const [session, setSession] = useState<Session | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState<Error | null>(null)

    const supabase = createClient()

    // Fetch user profile from database
    const fetchProfile = useCallback(async (userId: string): Promise<Profile | null> => {
        try {
            const { data, error } = await supabase
                .from('profiles')
                .select('*')
                .eq('id', userId)
                .single()

            if (error) {
                console.error('Error fetching profile:', error)
                return null
            }

            return data as Profile
        } catch (err) {
            console.error('Profile fetch error:', err)
            return null
        }
    }, [supabase])

    // Initialize auth state
    useEffect(() => {
        let mounted = true

        const initializeAuth = async () => {
            try {
                // Get current session
                const { data: { session: currentSession }, error: sessionError } = await supabase.auth.getSession()

                if (sessionError) {
                    throw sessionError
                }

                if (mounted) {
                    setSession(currentSession)
                    setUser(currentSession?.user ?? null)

                    // Fetch profile if user exists
                    if (currentSession?.user) {
                        const userProfile = await fetchProfile(currentSession.user.id)
                        if (mounted) {
                            setProfile(userProfile)
                        }
                    }

                    setIsLoading(false)
                }
            } catch (err) {
                if (mounted) {
                    setError(err instanceof Error ? err : new Error('Failed to initialize auth'))
                    setIsLoading(false)
                }
            }
        }

        initializeAuth()

        // Listen for auth changes
        const { data: { subscription } } = supabase.auth.onAuthStateChange(
            async (event, currentSession) => {
                console.log('Auth state changed:', event)

                if (mounted) {
                    setSession(currentSession)
                    setUser(currentSession?.user ?? null)

                    if (currentSession?.user) {
                        const userProfile = await fetchProfile(currentSession.user.id)
                        if (mounted) {
                            setProfile(userProfile)
                        }
                    } else {
                        setProfile(null)
                    }
                }
            }
        )

        return () => {
            mounted = false
            subscription.unsubscribe()
        }
    }, [supabase.auth, fetchProfile])

    // Sign out function
    const signOut = useCallback(async () => {
        try {
            const { error } = await supabase.auth.signOut()
            if (error) throw error

            setUser(null)
            setProfile(null)
            setSession(null)
        } catch (err) {
            console.error('Sign out error:', err)
            setError(err instanceof Error ? err : new Error('Failed to sign out'))
        }
    }, [supabase.auth])

    // Manually refresh profile
    const refreshProfile = useCallback(async () => {
        if (!user?.id) return

        try {
            const userProfile = await fetchProfile(user.id)
            setProfile(userProfile)
        } catch (err) {
            console.error('Profile refresh error:', err)
            setError(err instanceof Error ? err : new Error('Failed to refresh profile'))
        }
    }, [user?.id, fetchProfile])

    return {
        user,
        profile,
        session,
        isLoading,
        error,
        signOut,
        refreshProfile
    }
}

export default useAuth
