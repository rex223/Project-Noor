// Activity Stats Tracker
// Helper utilities to track user activity and update stats

/**
 * Update the user's activity streak
 * Call this whenever the user performs any activity
 */
export async function updateActivityStreak(): Promise<void> {
  try {
    await fetch('/api/activity-stats', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'update_streak',
        data: {}
      })
    });
  } catch (error) {
    console.error('Failed to update activity streak:', error);
  }
}

/**
 * Track a chat message
 */
export async function trackChatMessage(messageCount: number = 1): Promise<void> {
  try {
    await fetch('/api/activity-stats', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'increment_chat',
        data: { messageCount }
      })
    });
    
    // Also update streak
    await updateActivityStreak();
  } catch (error) {
    console.error('Failed to track chat message:', error);
  }
}

/**
 * Track a completed game
 */
export async function trackGameComplete(gameName: string): Promise<void> {
  try {
    await fetch('/api/activity-stats', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'increment_game',
        data: { gameName }
      })
    });
    
    // Also update streak
    await updateActivityStreak();
  } catch (error) {
    console.error('Failed to track game completion:', error);
  }
}

/**
 * Track a video watched
 */
export async function trackVideoWatched(): Promise<void> {
  try {
    await fetch('/api/activity-stats', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'increment_video',
        data: {}
      })
    });
    
    // Also update streak
    await updateActivityStreak();
  } catch (error) {
    console.error('Failed to track video watched:', error);
  }
}

/**
 * Track a song listened
 */
export async function trackSongListened(): Promise<void> {
  try {
    await fetch('/api/activity-stats', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'increment_song',
        data: {}
      })
    });
    
    // Also update streak
    await updateActivityStreak();
  } catch (error) {
    console.error('Failed to track song listened:', error);
  }
}

/**
 * Update wellness score
 */
export async function updateWellnessScore(score: number, trend: number = 0): Promise<void> {
  try {
    await fetch('/api/activity-stats', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'update_wellness',
        data: { score, trend }
      })
    });
    
    // Also update streak
    await updateActivityStreak();
  } catch (error) {
    console.error('Failed to update wellness score:', error);
  }
}

/**
 * Add an achievement
 */
export async function addAchievement(name: string, description?: string): Promise<void> {
  try {
    await fetch('/api/activity-stats', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'add_achievement',
        data: { name, description }
      })
    });
  } catch (error) {
    console.error('Failed to add achievement:', error);
  }
}

/**
 * Update active sessions
 */
export async function updateActiveSessions(sessionTypes: string[]): Promise<void> {
  try {
    await fetch('/api/activity-stats', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'update_active_sessions',
        data: { sessionTypes }
      })
    });
  } catch (error) {
    console.error('Failed to update active sessions:', error);
  }
}

/**
 * Fetch current activity stats
 */
export async function fetchActivityStats(): Promise<any> {
  try {
    const response = await fetch('/api/activity-stats');
    if (!response.ok) {
      throw new Error('Failed to fetch activity stats');
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch activity stats:', error);
    return null;
  }
}

/**
 * Check and award milestone achievements
 */
export async function checkMilestoneAchievements(stats: any): Promise<void> {
  if (!stats) return;

  // First chat
  if (stats.totalMessages === 1) {
    await addAchievement('First Chat', 'Started your first conversation with Bondhu');
  }

  // 10 messages
  if (stats.totalMessages === 10) {
    await addAchievement('Chatterbox', 'Sent 10 messages to Bondhu');
  }

  // 100 messages
  if (stats.totalMessages === 100) {
    await addAchievement('Conversation Master', 'Sent 100 messages to Bondhu');
  }

  // First game
  if (stats.totalGamesPlayed === 1) {
    await addAchievement('Game On', 'Completed your first game');
  }

  // 10 games
  if (stats.totalGamesPlayed === 10) {
    await addAchievement('Game Enthusiast', 'Completed 10 games');
  }

  // 7 day streak
  if (stats.currentStreakDays === 7) {
    await addAchievement('Week Warrior', 'Maintained a 7-day activity streak');
  }

  // 30 day streak
  if (stats.currentStreakDays === 30) {
    await addAchievement('Month Master', 'Maintained a 30-day activity streak');
  }

  // High wellness score
  if (stats.wellnessScore >= 90) {
    await addAchievement('Wellness Champion', 'Achieved a wellness score of 90+');
  }
}
