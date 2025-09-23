"use client";

import { useState, useEffect } from "react";
import { Heart, Sparkles, Brain, Smile } from "lucide-react";
import { cn } from "@/lib/utils";

interface BondhuAvatarProps {
  size?: "sm" | "md" | "lg";
  isTyping?: boolean;
  mood?: "happy" | "caring" | "thinking" | "excited";
  showAnimation?: boolean;
  className?: string;
}

export function BondhuAvatar({ 
  size = "md", 
  isTyping = false, 
  mood = "caring",
  showAnimation = true,
  className 
}: BondhuAvatarProps) {
  const [currentEmoji, setCurrentEmoji] = useState("😊");
  const [isAnimating, setIsAnimating] = useState(false);

  const sizeClasses = {
    sm: "w-8 h-8",
    md: "w-12 h-12", 
    lg: "w-16 h-16"
  };

  const iconSizes = {
    sm: "h-4 w-4",
    md: "h-6 w-6",
    lg: "h-8 w-8"
  };

  const moodEmojis = {
    happy: ["😊", "😄", "🌟"],
    caring: ["🤗", "💝", "🌸"],
    thinking: ["🤔", "💭", "🧠"],
    excited: ["✨", "🎉", "😃"]
  };

  const moodIcons = {
    happy: Smile,
    caring: Heart,
    thinking: Brain,
    excited: Sparkles
  };

  useEffect(() => {
    if (showAnimation && !isTyping) {
      const interval = setInterval(() => {
        const emojis = moodEmojis[mood];
        const randomEmoji = emojis[Math.floor(Math.random() * emojis.length)];
        setCurrentEmoji(randomEmoji);
        setIsAnimating(true);
        setTimeout(() => setIsAnimating(false), 300);
      }, 4000);

      return () => clearInterval(interval);
    }
  }, [mood, showAnimation, isTyping]);

  const MoodIcon = moodIcons[mood];

  return (
    <div className={cn("relative", className)}>
      <div 
        className={cn(
          sizeClasses[size],
          "rounded-full bg-gradient-to-br from-primary to-primary/80 flex items-center justify-center shadow-lg relative overflow-hidden transition-all duration-300",
          isTyping && "animate-pulse",
          isAnimating && "scale-110"
        )}
      >
        {/* Background animation */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-transparent rounded-full animate-pulse" />
        
        {/* Main icon */}
        <MoodIcon className={cn(iconSizes[size], "text-primary-foreground relative z-10")} />
        
        {/* Floating emoji */}
        {showAnimation && (
          <div 
            className={cn(
              "absolute inset-0 flex items-center justify-center text-lg transition-all duration-300",
              isAnimating ? "scale-125 opacity-100" : "scale-100 opacity-0"
            )}
          >
            {currentEmoji}
          </div>
        )}
      </div>
      
      {/* Status indicator */}
      <div className={cn(
        "absolute -bottom-1 -right-1 rounded-full border-2 border-card transition-all duration-300",
        size === "sm" ? "w-3 h-3" : size === "md" ? "w-4 h-4" : "w-5 h-5",
        isTyping 
          ? "bg-yellow-500 animate-bounce" 
          : "bg-primary animate-pulse"
      )} />
      
      {/* Sparkle effects */}
      {showAnimation && mood === "excited" && (
        <>
          <Sparkles className="absolute -top-1 -left-1 h-3 w-3 text-primary animate-ping" />
          <Sparkles className="absolute -bottom-1 -right-2 h-2 w-2 text-primary/60 animate-ping" style={{ animationDelay: "1s" }} />
        </>
      )}
    </div>
  );
}
