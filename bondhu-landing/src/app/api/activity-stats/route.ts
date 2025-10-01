import { createClient } from '@/lib/supabase/server';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const supabase = await createClient();
    
    // Get the current user
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    
    if (userError || !user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Fetch user activity stats
    const { data: stats, error: statsError } = await supabase
      .from('user_activity_stats')
      .select('*')
      .eq('user_id', user.id)
      .single();

    if (statsError) {
      console.error('Error fetching activity stats:', statsError);
      return NextResponse.json(
        { error: 'Failed to fetch activity stats' },
        { status: 500 }
      );
    }

    // Transform the data to match the component's expected format
    const transformedStats = {
      wellnessScore: stats?.wellness_score || 0,
      wellnessTrend: stats?.wellness_trend || 0,
      totalMessages: stats?.total_messages || 0,
      messagesToday: stats?.messages_today || 0,
      totalGamesPlayed: stats?.total_games_played || 0,
      gamesThisWeek: stats?.games_this_week || 0,
      currentStreakDays: stats?.current_streak_days || 0,
      longestStreakDays: stats?.longest_streak_days || 0,
      totalAchievements: stats?.total_achievements || 0,
      achievementsThisMonth: stats?.achievements_this_month || 0,
      activeSessions: stats?.active_sessions || 0,
      activeSessionsToday: stats?.active_sessions_today || 0,
      gamesPlayedCount: stats?.games_played_count || 0,
      videosWatchedCount: stats?.videos_watched_count || 0,
      songsListenedCount: stats?.songs_listened_count || 0,
      lastActivityDate: stats?.last_activity_date,
      updatedAt: stats?.updated_at,
    };

    return NextResponse.json(transformedStats);
  } catch (error) {
    console.error('Unexpected error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// POST endpoint to update specific stats (can be called from chat, games, etc.)
export async function POST(request: Request) {
  try {
    const supabase = await createClient();
    
    // Get the current user
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    
    if (userError || !user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const body = await request.json();
    const { action, data } = body;

    switch (action) {
      case 'increment_chat':
        await supabase.rpc('increment_chat_session', {
          user_id: user.id,
          message_count: data?.messageCount || 1
        });
        break;

      case 'increment_game':
        await supabase.rpc('increment_game_played', {
          user_id: user.id,
          game_name: data?.gameName || null
        });
        break;

      case 'increment_video':
        await supabase.rpc('increment_video_watched', {
          user_id: user.id
        });
        break;

      case 'increment_song':
        await supabase.rpc('increment_song_listened', {
          user_id: user.id
        });
        break;

      case 'update_wellness':
        await supabase.rpc('update_wellness_score', {
          user_id: user.id,
          new_score: data?.score,
          trend_change: data?.trend || 0
        });
        break;

      case 'update_streak':
        await supabase.rpc('update_streak', {
          user_id: user.id
        });
        break;

      case 'add_achievement':
        await supabase.rpc('add_achievement', {
          user_id: user.id,
          achievement_name: data?.name,
          achievement_description: data?.description || null
        });
        break;

      case 'update_active_sessions':
        await supabase.rpc('update_active_sessions', {
          user_id: user.id,
          session_types: data?.sessionTypes || []
        });
        break;

      default:
        return NextResponse.json(
          { error: 'Invalid action' },
          { status: 400 }
        );
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Unexpected error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
