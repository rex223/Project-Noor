"use client";

import { Heart, MessageCircle, Gamepad2, TrendingUp, BarChart3, Activity, Trophy, Zap } from "lucide-react";
import { GlowingEffect } from "@/components/ui/glowing-effect";
import { cn } from "@/lib/utils";

interface DashboardStatsProps {
  stats?: {
    wellnessScore?: number;
    wellnessTrend?: number;
    totalMessages?: number;
    messagesToday?: number;
    totalGamesPlayed?: number;
    gamesThisWeek?: number;
    currentStreakDays?: number;
    longestStreakDays?: number;
    totalAchievements?: number;
    achievementsThisMonth?: number;
    activeSessions?: number;
    activeSessionsToday?: number;
  } | null;
}

export function DashboardStats({ stats }: DashboardStatsProps) {
  // Show loading state with default values if stats are null/undefined
  const isLoading = !stats;
  
  const wellnessScore = stats?.wellnessScore || 0;
  const wellnessTrend = stats?.wellnessTrend || 0;
  const totalMessages = stats?.totalMessages || 0;
  const messagesToday = stats?.messagesToday || 0;
  const totalGamesPlayed = stats?.totalGamesPlayed || 0;
  const gamesThisWeek = stats?.gamesThisWeek || 0;
  const currentStreakDays = stats?.currentStreakDays || 0;
  const totalAchievements = stats?.totalAchievements || 0;
  const achievementsThisMonth = stats?.achievementsThisMonth || 0;
  const activeSessions = stats?.activeSessions || 0;

  // Calculate trend text
  const wellnessTrendText = wellnessTrend > 0 
    ? `+${wellnessTrend}% this week` 
    : wellnessTrend < 0 
    ? `${wellnessTrend}% this week` 
    : 'No change';
  
  const messageTrendText = messagesToday > 0 
    ? `+${messagesToday} today` 
    : 'Start chatting!';
  
  const gameTrendText = gamesThisWeek > 0 
    ? `+${gamesThisWeek} this week` 
    : 'Play your first game!';
  
  const streakText = currentStreakDays > 0 
    ? currentStreakDays >= 7 
      ? 'Amazing streak!' 
      : 'Keep it up!' 
    : 'Start your streak!';
  
  const achievementTrendText = achievementsThisMonth > 0 
    ? `+${achievementsThisMonth} this month` 
    : 'Earn your first!';
  
  const activeSessionText = activeSessions > 0 
    ? `${activeSessions} active now` 
    : 'No active sessions';

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
      {/* Row 1 */}
      <StatsCard
        icon={<Heart className="h-5 w-5" />}
        title="Wellness Score"
        value={isLoading ? '--' : `${wellnessScore}%`}
        description="Your overall mental wellness trend"
        trend={wellnessTrendText}
        trendPositive={wellnessTrend >= 0}
        isLoading={isLoading}
      />
      <StatsCard
        icon={<MessageCircle className="h-5 w-5" />}
        title="Chat Sessions"
        value={isLoading ? '--' : totalMessages.toString()}
        description="Messages exchanged with Bondhu"
        trend={messageTrendText}
        trendPositive={messagesToday >= 0}
        isLoading={isLoading}
      />
      <StatsCard
        icon={<Gamepad2 className="h-5 w-5" />}
        title="Games Played"
        value={isLoading ? '--' : totalGamesPlayed.toString()}
        description="Interactive games completed"
        trend={gameTrendText}
        trendPositive={gamesThisWeek >= 0}
        isLoading={isLoading}
      />
      
      {/* Row 2 */}
      <StatsCard
        icon={<TrendingUp className="h-5 w-5" />}
        title="Growth Streak"
        value={isLoading ? '--' : `${currentStreakDays} days`}
        description="Consecutive days of engagement"
        trend={streakText}
        trendPositive={currentStreakDays >= 3}
        isLoading={isLoading}
      />
      <StatsCard
        icon={<Trophy className="h-5 w-5" />}
        title="Achievements"
        value={isLoading ? '--' : totalAchievements.toString()}
        description="Milestones and accomplishments"
        trend={achievementTrendText}
        trendPositive={achievementsThisMonth >= 0}
        isLoading={isLoading}
      />
      <StatsCard
        icon={<Activity className="h-5 w-5" />}
        title="Active Sessions"
        value={isLoading ? '--' : activeSessions.toString()}
        description="Current ongoing activities"
        trend={activeSessionText}
        trendPositive={activeSessions > 0}
        isLoading={isLoading}
      />
    </div>
  );
}

interface StatsCardProps {
  icon: React.ReactNode;
  title: string;
  value: string;
  description: string;
  trend: string;
  trendPositive: boolean;
  isLoading?: boolean;
}

const StatsCard = ({ icon, title, value, description, trend, trendPositive, isLoading }: StatsCardProps) => {
  return (
    <div className="min-h-[9rem] list-none">
      <div className="relative h-full rounded-[1.25rem] border-[0.75px] border-border p-2">
        <GlowingEffect
          spread={30}
          glow={true}
          disabled={false}
          proximity={80}
          inactiveZone={0.1}
          borderWidth={1}
          variant="default"
        />
        <div className="relative flex h-full flex-col justify-between gap-4 overflow-hidden rounded-xl border-[0.75px] bg-card p-5 shadow-sm">
          <div className="flex items-start justify-between">
            <div className="w-fit rounded-lg border-[0.75px] border-border bg-muted p-2.5">
              {icon}
            </div>
            <div className={cn(
              "text-xs font-medium px-2 py-1 rounded-full",
              trendPositive 
                ? "text-green-700 bg-green-100 dark:text-green-300 dark:bg-green-900/30"
                : "text-red-700 bg-red-100 dark:text-red-300 dark:bg-red-900/30"
            )}>
              {trend}
            </div>
          </div>
          
          <div className="space-y-3">
            <div className="text-2xl font-bold text-foreground">
              {value}
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-semibold text-foreground">
                {title}
              </h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                {description}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
