/**
 * Environment Configuration Validation
 * Validates that all required environment variables are properly set
 */

export interface EnvironmentConfig {
    apiBaseUrl: string
    supabaseUrl: string
    supabaseAnonKey: string
}

export function validateEnvironment(): EnvironmentConfig {
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

    if (!apiBaseUrl) {
        console.warn('NEXT_PUBLIC_API_BASE_URL not set, using default: http://localhost:8000')
    }

    if (!supabaseUrl) {
        throw new Error('NEXT_PUBLIC_SUPABASE_URL is required')
    }

    if (!supabaseAnonKey) {
        throw new Error('NEXT_PUBLIC_SUPABASE_ANON_KEY is required')
    }

    return {
        apiBaseUrl: apiBaseUrl || 'http://localhost:8000',
        supabaseUrl,
        supabaseAnonKey
    }
}

export function getApiBaseUrl(): string {
    return process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
}

export function isDevEnvironment(): boolean {
    return process.env.NODE_ENV === 'development'
}

export function isProdEnvironment(): boolean {
    return process.env.NODE_ENV === 'production'
}

// Log environment status in development
if (typeof window !== 'undefined' && isDevEnvironment()) {
    console.log('🔧 Environment Configuration:', {
        apiBaseUrl: getApiBaseUrl(),
        supabaseConfigured: !!process.env.NEXT_PUBLIC_SUPABASE_URL,
        environment: process.env.NODE_ENV
    })
}