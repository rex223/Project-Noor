"use client";

import { MessageCircle, Play, User, Settings, Sparkles, Brain } from "lucide-react";
import { GlowingEffect } from "@/components/ui/glowing-effect";
import { cn } from "@/lib/utils";

interface DashboardGridProps {
  onSectionChange: (section: string) => void;
  activeSection?: string;
}

export function DashboardGrid({ onSectionChange, activeSection }: DashboardGridProps) {
  return (
    <div className="grid grid-cols-2 gap-4">
      <GridItem
        area=""
        icon={<MessageCircle className="h-5 w-5" />}
        title="AI Chat Companion"
        description="Start a conversation with Bondhu, your personalized AI friend who understands your personality and adapts to your needs."
        onClick={() => onSectionChange('chat')}
        isActive={activeSection === 'chat'}
        gradient="from-blue-400/80 to-cyan-400/80"
        darkGradient="from-blue-500/60 to-cyan-500/60"
      />
      <GridItem
        area=""
        icon={<Play className="h-5 w-5" />}
        title="Entertainment Hub"
        description="Explore games, videos, and music while Bondhu learns about your personality and preferences."
        onClick={() => onSectionChange('entertainment')}
        isActive={activeSection === 'entertainment'}
        gradient="from-violet-400/80 to-purple-400/80"
        darkGradient="from-violet-500/60 to-purple-500/60"
      />
      <GridItem
        area=""
        icon={<Brain className="h-5 w-5" />}
        title="Personality Insights"
        description="Discover deep insights about yourself through AI-powered personality analysis and growth tracking."
        onClick={() => onSectionChange('profile')}
        isActive={activeSection === 'profile'}
        gradient="from-emerald-400/80 to-teal-400/80"
        darkGradient="from-emerald-500/60 to-teal-500/60"
      />
      <GridItem
        area=""
        icon={<Settings className="h-5 w-5" />}
        title="Privacy & Settings"
        description="Manage your data, privacy preferences, and customize your Bondhu experience."
        onClick={() => onSectionChange('settings')}
        isActive={activeSection === 'settings'}
        gradient="from-slate-400/80 to-gray-400/80"
        darkGradient="from-slate-500/60 to-gray-500/60"
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
}

const GridItem = ({ icon, title, description, onClick, isActive, gradient, darkGradient }: GridItemProps) => {
  return (
    <div className="min-h-[8rem] list-none cursor-pointer" onClick={onClick}>
      <div className="relative h-full rounded-[1.25rem] border-[0.75px] border-border p-2 transition-all duration-300 hover:scale-[1.02]">
        <GlowingEffect
          spread={30}
          glow={true}
          disabled={false}
          proximity={80}
          inactiveZone={0.1}
          borderWidth={2}
        />
        <div className={cn(
          "relative flex h-full flex-col justify-between gap-4 overflow-hidden rounded-xl border-[0.75px] p-4 shadow-sm transition-all duration-300",
          isActive 
            ? `bg-gradient-to-br ${gradient} dark:bg-gradient-to-br dark:${darkGradient} text-white backdrop-blur-sm shadow-lg` 
            : "bg-card hover:bg-muted/30 dark:hover:bg-muted/20 backdrop-blur-sm"
        )}>
          <div className="relative flex flex-1 flex-col justify-between gap-3">
            <div className="flex items-start justify-between">
              <div className={cn(
                "w-fit rounded-lg border-[0.75px] p-2 transition-all duration-300",
                isActive 
                  ? "border-white/30 bg-white/15 backdrop-blur-sm shadow-lg" 
                  : "border-border bg-muted/70 dark:bg-muted/40 dark:border-border/50"
              )}>
                {icon}
              </div>
              {isActive && (
                <div className="flex items-center space-x-1 text-white/80">
                  <Sparkles className="h-4 w-4" />
                  <span className="text-xs font-medium">Active</span>
                </div>
              )}
            </div>
            
            <div className="space-y-2">
              <h3 className={cn(
                "text-lg leading-[1.25rem] font-semibold tracking-[-0.04em] text-balance",
                isActive ? "text-white" : "text-foreground"
              )}>
                {title}
              </h3>
              <p className={cn(
                "text-xs leading-[1.25rem] line-clamp-2",
                isActive ? "text-white/80" : "text-muted-foreground"
              )}>
                {description}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
