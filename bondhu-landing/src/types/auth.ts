import { User } from '@supabase/supabase-js'

export interface Profile {
  id: string
  full_name: string | null
  avatar_url: string | null
  onboarding_completed: boolean
  personality_data: Record<string, unknown> | null
  created_at: string
  updated_at: string
  last_name_change?: string | null
}

export interface AuthState {
  user: User | null
  profile: Profile | null
  loading: boolean
}

export interface SignUpFormData {
  full_name: string
  email: string
  password: string
  privacy_policy: boolean
  terms_of_service: boolean
  age_confirmation: boolean
}

export interface SignInFormData {
  email: string
  password: string
  remember_me?: boolean
}

export interface PersonalityData {
  openness: number
  conscientiousness: number
  extraversion: number
  agreeableness: number
  neuroticism: number
  mental_health_goals: string[]
  preferred_communication_style: string
  stress_triggers: string[]
  coping_mechanisms: string[]
}
