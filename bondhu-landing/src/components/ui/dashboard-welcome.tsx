"use client";

import { GlowingEffect } from "@/components/ui/glowing-effect";
import { Sparkles, Calendar, Clock } from "lucide-react";
import { cn } from "@/lib/utils";

interface DashboardWelcomeProps {
  userName?: string;
  lastActive?: string;
  streak?: number;
  compact?: boolean;
}

export function DashboardWelcome({ userName = "Friend", lastActive, streak = 7, compact = false }: DashboardWelcomeProps) {
  const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const currentDate = new Date().toLocaleDateString([], { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });

  if (compact) {
    return (
      <div className="mb-6">
        <div className="relative rounded-xl border-[0.75px] border-border p-2">
          <GlowingEffect
            spread={25}
            glow={true}
            disabled={false}
            proximity={60}
            inactiveZone={0.3}
            borderWidth={1}
          />
          <div className="relative overflow-hidden rounded-lg bg-gradient-to-r from-primary/2 to-secondary/2 dark:from-primary/4 dark:to-secondary/4 p-4 backdrop-blur-sm">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <h2 className="text-xl font-bold">Welcome back, {userName}!</h2>
                <span className="text-xl">👋</span>
              </div>
              <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                  <span>{streak} day streak</span>
                </div>
                <span>{currentTime}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mb-8">
      <div className="relative rounded-[1.5rem] border-[0.75px] border-border p-3">
        <GlowingEffect
          spread={40}
          glow={true}
          disabled={false}
          proximity={100}
          inactiveZone={0.2}
          borderWidth={1}
        />
        <div className="relative overflow-hidden rounded-xl border-[0.75px] bg-gradient-to-br from-primary/3 via-background/90 to-secondary/3 dark:from-primary/5 dark:via-background/80 dark:to-secondary/5 p-8 shadow-sm dark:shadow-[0px_0px_27px_0px_rgba(45,45,45,0.3)] backdrop-blur-sm">
          {/* Background decoration */}
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-emerald-400/8 to-blue-400/8 dark:from-emerald-500/12 dark:to-blue-500/12 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-tr from-violet-400/8 to-teal-400/8 dark:from-violet-500/12 dark:to-teal-500/12 rounded-full blur-2xl" />
          
          <div className="relative flex flex-col md:flex-row md:items-center md:justify-between gap-6">
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <h2 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
                  Welcome back, {userName}!
                </h2>
                <div className="flex items-center space-x-1">
                  <Sparkles className="h-6 w-6 text-primary animate-pulse" />
                  <span className="text-2xl">👋</span>
                </div>
              </div>
              
              <p className="text-lg text-muted-foreground max-w-2xl">
                Your AI companion awaits - ready to explore, discover, and grow together on your wellness journey.
              </p>
              
              <div className="flex flex-wrap items-center gap-4 text-sm">
                <div className="flex items-center space-x-2 text-muted-foreground">
                  <Calendar className="h-4 w-4" />
                  <span>{currentDate}</span>
                </div>
                <div className="flex items-center space-x-2 text-muted-foreground">
                  <Clock className="h-4 w-4" />
                  <span>{currentTime}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                  <span className="text-green-600 dark:text-green-400 font-medium">
                    {streak} day streak
                  </span>
                </div>
              </div>
            </div>
            
            <div className="flex flex-col space-y-3">
              <div className="bg-emerald-50/80 dark:bg-emerald-900/20 border border-emerald-200/50 dark:border-emerald-700/30 rounded-xl p-4 text-center backdrop-blur-sm">
                <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{streak}</div>
                <div className="text-xs text-muted-foreground">Day Streak</div>
              </div>
              <div className="bg-blue-50/80 dark:bg-blue-900/20 border border-blue-200/50 dark:border-blue-700/30 rounded-xl p-4 text-center backdrop-blur-sm">
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">85%</div>
                <div className="text-xs text-muted-foreground">Wellness Score</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
