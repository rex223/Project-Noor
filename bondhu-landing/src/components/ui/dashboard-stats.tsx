"use client";

import { Heart, MessageCircle, Gamepad2, TrendingUp, BarChart3, Activity } from "lucide-react";
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
    ...stats
  };

  return (
    <div className="grid grid-cols-1 gap-3">
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
        icon={<TrendingUp className="h-5 w-5" />}
        title="Growth Streak"
        value={`${defaultStats.weeklyGrowth} days`}
        description="Consecutive days of engagement"
        trend="Personal best!"
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
    <div className="min-h-[7rem] list-none">
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
        <div className="relative flex h-full flex-col justify-between gap-4 overflow-hidden rounded-xl border-[0.75px] bg-card p-4 shadow-sm">
          <div className="flex items-start justify-between">
            <div className="w-fit rounded-lg border-[0.75px] border-border bg-muted p-2">
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
          
          <div className="space-y-2">
            <div className="text-xl font-bold text-foreground">
              {value}
            </div>
            <div>
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
