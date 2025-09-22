import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')
  const redirectTo = searchParams.get('redirectTo') ?? '/dashboard'

  if (code) {
    const supabase = await createClient()
    const { data, error } = await supabase.auth.exchangeCodeForSession(code)
    
    if (!error && data.user) {
      // Check if profile exists, if not create one
      const { data: existingProfile } = await supabase
        .from('profiles')
        .select('id')
        .eq('id', data.user.id)
        .single()

      if (!existingProfile) {
        // Create profile for OAuth users
        const { error: profileError } = await supabase
          .from('profiles')
          .insert({
            id: data.user.id,
            full_name: data.user.user_metadata?.full_name || data.user.user_metadata?.name || data.user.email?.split('@')[0] || '',
            avatar_url: data.user.user_metadata?.avatar_url || null,
            onboarding_completed: false
          })

        if (profileError) {
          console.error('Profile creation error:', profileError)
        }
      }

      // Check onboarding status and redirect appropriately
      const { data: profile } = await supabase
        .from('profiles')
        .select('onboarding_completed')
        .eq('id', data.user.id)
        .single()

      const finalRedirect = !profile?.onboarding_completed 
        ? '/onboarding/personality' 
        : redirectTo

      return NextResponse.redirect(`${origin}${finalRedirect}`)
    }
  }

  // Return the user to the sign-in page with an error message
  return NextResponse.redirect(`${origin}/sign-in?error=auth_callback_error`)
}
