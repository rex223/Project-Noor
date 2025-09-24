"use client";

import { Heart, MessageCircle, Gamepad2, TrendingUp, BarChart3, Activity, Trophy, Zap } from "lucide-react";
import { GlowingEffect } from "@/components/ui/glowing-effect";
import { cn } from "@/lib/utils";

interface DashboardStatsProps {
  stats?: {
    totalSessions?: number;
    totalGamesPlayed?: number;
    totalMessages?: number;
    achievements?: number;
    weeklyGrowth?: number;
    moodScore?: number;
    activeSessions?: number;
  };
}

export function DashboardStats({ stats }: DashboardStatsProps) {
  const defaultStats = {
    totalSessions: 47,
    totalGamesPlayed: 12,
    totalMessages: 150,
    achievements: 8,
    weeklyGrowth: 23,
    moodScore: 85,
    activeSessions: 3,
    ...stats
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
      {/* Row 1 */}
      <StatsCard
        icon={<Heart className="h-5 w-5" />}
        title="Wellness Score"
        value={`${defaultStats.moodScore}%`}
        description="Your overall mental wellness trend"
        trend="+12% this week"
        trendPositive={true}
      />
      <StatsCard
        icon={<MessageCircle className="h-5 w-5" />}
        title="Chat Sessions"
        value={defaultStats.totalMessages.toString()}
        description="Messages exchanged with Bondhu"
        trend="+8 today"
        trendPositive={true}
      />
      <StatsCard
        icon={<Gamepad2 className="h-5 w-5" />}
        title="Games Played"
        value={defaultStats.totalGamesPlayed.toString()}
        description="Interactive games completed"
        trend="+2 this week"
        trendPositive={true}
      />
      
      {/* Row 2 */}
      <StatsCard
        icon={<TrendingUp className="h-5 w-5" />}
        title="Growth Streak"
        value={`${defaultStats.weeklyGrowth} days`}
        description="Consecutive days of engagement"
        trend="Personal best!"
        trendPositive={true}
      />
      <StatsCard
        icon={<Trophy className="h-5 w-5" />}
        title="Achievements"
        value={defaultStats.achievements.toString()}
        description="Milestones and accomplishments"
        trend="+2 this month"
        trendPositive={true}
      />
      <StatsCard
        icon={<Activity className="h-5 w-5" />}
        title="Active Sessions"
        value={defaultStats.activeSessions.toString()}
        description="Current ongoing activities"
        trend="2 new today"
        trendPositive={true}
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
}

const StatsCard = ({ icon, title, value, description, trend, trendPositive }: StatsCardProps) => {
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
