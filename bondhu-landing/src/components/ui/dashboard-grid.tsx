"use client";

import React from "react";
import { MessageCircle, Play, User, Settings, Sparkles, Brain, Shield, Activity, Gamepad2, Camera, Headphones } from "lucide-react";
import { GlowingEffect } from "@/components/ui/glowing-effect";
import { AnimatedExploreButton } from "@/components/ui/animated-explore-button";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";

interface DashboardGridProps {
  currentPage?: string;
  stats?: {
    gamesPlayedCount?: number;
    videosWatchedCount?: number;
    songsListenedCount?: number;
  } | null;
}

export function DashboardGrid({ currentPage = 'dashboard', stats }: DashboardGridProps) {
  const router = useRouter()

  const handlePersonalityInsightsClick = () => {
    router.push('/personality-insights')
  }

  const handleEntertainmentClick = () => {
    router.push('/entertainment')
  }

  const handleSettingsClick = () => {
    router.push('/settings')
  }

  return (
    <div className="grid grid-cols-2 gap-4">
      <GridItem
        area=""
        icon={<MessageCircle className="h-5 w-5" />}
        title="AI Chat Companion"
        description="Start a conversation with Bondhu, your personalized AI friend who understands your personality and adapts to your needs."
        onClick={() => { }} // No navigation since we're already on dashboard
        isActive={currentPage === 'dashboard'}
        gradient="from-blue-400/80 to-cyan-400/80"
        darkGradient="from-blue-500/60 to-cyan-500/60"
        buttonGradient="from-blue-500 to-cyan-500"
        buttonDarkGradient="dark:from-blue-600 dark:to-cyan-600"
        buttonBorder="border-cyan-400"
        showPreview={false}
      />
      <GridItem
        area=""
        icon={<Play className="h-5 w-5" />}
        title="Entertainment Hub"
        description="Explore games, videos, and music while Bondhu learns about your personality and preferences."
        onClick={handleEntertainmentClick}
        isActive={currentPage === 'entertainment'}
        gradient="from-violet-400/80 to-purple-400/80"
        darkGradient="from-violet-500/60 to-purple-500/60"
        buttonGradient="from-violet-500 to-purple-500"
        buttonDarkGradient="dark:from-violet-600 dark:to-purple-600"
        buttonBorder="border-purple-400"
        showPreview={true}
        previewType="entertainment"
        entertainmentStats={{
          gamesPlayed: stats?.gamesPlayedCount || 0,
          videosWatched: stats?.videosWatchedCount || 0,
          songsListened: stats?.songsListenedCount || 0
        }}
      />
      <GridItem
        area=""
        icon={<Brain className="h-5 w-5" />}
        title="Personality Insights"
        description="Discover deep insights about yourself through AI-powered personality analysis and growth tracking."
        onClick={handlePersonalityInsightsClick}
        isActive={currentPage === 'personality-insights'}
        gradient="from-emerald-400/80 to-teal-400/80"
        darkGradient="from-emerald-500/60 to-teal-500/60"
        buttonGradient="from-emerald-500 to-teal-500"
        buttonDarkGradient="dark:from-emerald-600 dark:to-teal-600"
        buttonBorder="border-teal-400"
        showPreview={true}
        previewType="personality"
      />
      <GridItem
        area=""
        icon={<Settings className="h-5 w-5" />}
        title="Privacy & Settings"
        description="Manage your data, privacy preferences, and customize your Bondhu experience."
        onClick={() => router.push('/settings')}
        isActive={currentPage === 'settings'}
        gradient="from-slate-400/80 to-gray-400/80"
        darkGradient="from-slate-500/60 to-gray-500/60"
        buttonGradient="from-slate-500 to-gray-500"
        buttonDarkGradient="dark:from-slate-600 dark:to-gray-600"
        buttonBorder="border-gray-400"
        showPreview={true}
        previewType="settings"
      />
    </div>
  );
}

interface GridItemProps {
  area: string;
  icon: React.ReactNode;
  title: string;
  description: React.ReactNode;
  onClick: () => void;
  isActive: boolean;
  gradient: string;
  darkGradient: string;
  buttonGradient: string;
  buttonDarkGradient: string;
  buttonBorder: string;
  showPreview?: boolean;
  previewType?: 'personality' | 'entertainment' | 'settings';
  entertainmentStats?: {
    gamesPlayed: number;
    videosWatched: number;
    songsListened: number;
  };
}

const GridItem = ({ icon, title, description, onClick, isActive, gradient, darkGradient, buttonGradient, buttonDarkGradient, buttonBorder, showPreview, previewType, entertainmentStats }: GridItemProps) => {
  const [isHovered, setIsHovered] = React.useState(false);
  
  return (
    <div 
      className="min-h-[10rem] list-none cursor-pointer group" 
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="relative h-full rounded-[1rem] border-[0.75px] border-border p-1.5 transition-all duration-300 hover:scale-[1.02] hover:shadow-xl hover:shadow-primary/10 dark:hover:shadow-primary/5">
        <GlowingEffect
          spread={30}
          glow={true}
          disabled={false}
          proximity={80}
          inactiveZone={0.1}
          borderWidth={2}
        />
        <div className={cn(
          "relative flex h-full flex-col justify-between gap-3 overflow-hidden rounded-lg border-[0.75px] p-4 shadow-md transition-all duration-300",
          isActive
            ? `bg-gradient-to-br ${gradient} dark:bg-gradient-to-br dark:${darkGradient} text-white backdrop-blur-sm shadow-lg hover:shadow-2xl`
            : "bg-card hover:bg-muted/40 dark:hover:bg-muted/30 backdrop-blur-sm hover:shadow-lg hover:border-primary/30"
        )}>
          <div className="relative flex flex-1 flex-col justify-between gap-2">
            <div className="flex items-start justify-between">
              <div className={cn(
                "w-fit rounded-lg border-[0.75px] p-2 transition-all duration-300 group-hover:scale-110 group-hover:shadow-md",
                isActive
                  ? "border-white/30 bg-white/15 backdrop-blur-sm shadow-lg group-hover:bg-white/25"
                  : "border-border bg-muted/70 dark:bg-muted/40 dark:border-border/50 group-hover:bg-primary/10 dark:group-hover:bg-primary/20 group-hover:border-primary/50 dark:group-hover:border-primary/60"
              )}>
                {icon}
              </div>
              
              {/* Animated Explore Button - Top Right */}
              <div className="flex items-center gap-2">
                <AnimatedExploreButton
                  label={isActive ? "Active" : "Explore"}
                  gradient={isActive ? gradient.replace('/80', '') : buttonGradient}
                  darkGradient={isActive ? `dark:${darkGradient.replace('/60', '')}` : buttonDarkGradient}
                  borderColor={isActive ? "border-white/40" : buttonBorder}
                  isActive={isActive}
                  isCardHovered={isHovered}
                />
              </div>
            </div>

            <div className="space-y-2">
              <h3 className={cn(
                "text-base leading-tight font-semibold tracking-[-0.02em] text-balance transition-all duration-300",
                isActive ? "text-white" : "text-foreground group-hover:text-primary"
              )}>
                {title}
              </h3>
              <p className={cn(
                "text-xs leading-snug line-clamp-2 transition-all duration-300",
                isActive ? "text-white/80" : "text-muted-foreground group-hover:text-foreground"
              )}>
                {description}
              </p>

              {/* Preview Components */}
              {showPreview && previewType === 'personality' && (
                <div className={cn(
                  "mt-2 pt-2 border-t transition-colors duration-300",
                  isActive
                    ? "border-white/30"
                    : "border-border/60 dark:border-border/40"
                )}>
                  <div className="flex items-center justify-between text-[10px]">
                    <span className={cn(
                      "font-medium",
                      isActive ? "text-white/80" : "text-foreground/70 dark:text-foreground/60"
                    )}>
                      Latest Insights
                    </span>
                    <Activity className={cn(
                      "h-2.5 w-2.5",
                      isActive ? "text-white/70" : "text-muted-foreground"
                    )} />
                  </div>
                  <div className="mt-1.5 grid grid-cols-3 gap-1">
                    <div className={cn(
                      "rounded-full h-0.5 w-full",
                      isActive ? "bg-emerald-400/40" : "bg-emerald-500/30 dark:bg-emerald-400/25"
                    )} />
                    <div className={cn(
                      "rounded-full h-0.5 w-full",
                      isActive ? "bg-blue-400/40" : "bg-blue-500/30 dark:bg-blue-400/25"
                    )} />
                    <div className={cn(
                      "rounded-full h-0.5 w-full",
                      isActive ? "bg-purple-400/40" : "bg-purple-500/30 dark:bg-purple-400/25"
                    )} />
                  </div>
                  <div className="mt-1 text-[10px]">
                    <span className={cn(
                      "font-medium",
                      isActive ? "text-white/90" : "text-foreground/80 dark:text-foreground/70"
                    )}>
                      Openness: 75% • Creativity: 82%
                    </span>
                  </div>
                </div>
              )}

              {showPreview && previewType === 'settings' && (
                <div className={cn(
                  "mt-2 pt-2 border-t transition-colors duration-300",
                  isActive
                    ? "border-white/30"
                    : "border-border/60 dark:border-border/40"
                )}>
                  <div className="flex items-center justify-between text-[10px]">
                    <span className={cn(
                      "font-medium",
                      isActive ? "text-white/80" : "text-foreground/70 dark:text-foreground/60"
                    )}>
                      Privacy Status
                    </span>
                    <Shield className={cn(
                      "h-2.5 w-2.5",
                      isActive ? "text-white/70" : "text-muted-foreground"
                    )} />
                  </div>
                  <div className="mt-1.5 flex items-center space-x-2">
                    <div className="flex-1 bg-green-500/20 rounded-full h-0.5" />
                    <span className={cn(
                      "text-[10px] font-medium",
                      isActive ? "text-green-300" : "text-green-600 dark:text-green-400"
                    )}>Secure</span>
                  </div>
                  <div className="mt-1 text-[10px]">
                    <span className={cn(
                      "font-medium",
                      isActive ? "text-white/90" : "text-foreground/80 dark:text-foreground/70"
                    )}>
                      All features enabled • Data encrypted
                    </span>
                  </div>
                </div>
              )}

              {showPreview && previewType === 'entertainment' && (
                <div className={cn(
                  "mt-2 pt-2 border-t transition-colors duration-300",
                  isActive
                    ? "border-white/30"
                    : "border-border/60 dark:border-border/40"
                )}>
                  <div className="flex items-center justify-between text-[10px] mb-1.5">
                    <span className={cn(
                      "font-medium",
                      isActive ? "text-white/80" : "text-foreground/70 dark:text-foreground/60"
                    )}>
                      Recent Activity
                    </span>
                    <Play className={cn(
                      "h-2.5 w-2.5",
                      isActive ? "text-white/70" : "text-muted-foreground"
                    )} />
                  </div>
                  <div className="flex items-center justify-between text-[10px]">
                    <div className="flex items-center space-x-0.5">
                      <Gamepad2 className={cn(
                        "h-2.5 w-2.5",
                        isActive ? "text-violet-300" : "text-violet-500 dark:text-violet-400"
                      )} />
                      <span className={cn(
                        "font-medium",
                        isActive ? "text-white/90" : "text-foreground/80 dark:text-foreground/70"
                      )}>{entertainmentStats?.gamesPlayed || 0} games</span>
                    </div>
                    <div className="flex items-center space-x-0.5">
                      <Camera className={cn(
                        "h-2.5 w-2.5",
                        isActive ? "text-pink-300" : "text-pink-500 dark:text-pink-400"
                      )} />
                      <span className={cn(
                        "font-medium",
                        isActive ? "text-white/90" : "text-foreground/80 dark:text-foreground/70"
                      )}>{entertainmentStats?.videosWatched || 0} videos</span>
                    </div>
                    <div className="flex items-center space-x-0.5">
                      <Headphones className={cn(
                        "h-2.5 w-2.5",
                        isActive ? "text-cyan-300" : "text-cyan-500 dark:text-cyan-400"
                      )} />
                      <span className={cn(
                        "font-medium",
                        isActive ? "text-white/90" : "text-foreground/80 dark:text-foreground/70"
                      )}>{entertainmentStats?.songsListened || 0} songs</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};


