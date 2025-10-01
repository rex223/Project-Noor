import { ArrowRight } from "lucide-react";

interface AnimatedExploreButtonProps {
  label?: string;
  gradient?: string;
  darkGradient?: string;
  borderColor?: string;
  isActive?: boolean;
  isCardHovered?: boolean;
}

export const AnimatedExploreButton = ({ 
  label = "Explore",
  gradient = "from-[#c0c7ff] to-[#4c64ff]",
  darkGradient = "dark:from-[#070e41] dark:to-[#263381]",
  borderColor = "border-[#656fe2]",
  isActive = false,
  isCardHovered = false
}: AnimatedExploreButtonProps) => {
  const isExpanded = isActive || isCardHovered;
  
  return (
    <button 
      className={`
        relative inline-flex h-10 items-center justify-center overflow-hidden rounded-full 
        bg-gradient-to-r ${gradient} ${darkGradient}
        font-medium text-white border-2 ${borderColor}
        transition-all duration-300
        ${isExpanded ? 'w-28' : 'w-10'}
      `}
      aria-label={label}
      onClick={(e) => e.stopPropagation()} // Prevent double-click on card
    >
      <div className={`
        inline-flex whitespace-nowrap transition-all duration-200 text-sm
        ${isExpanded ? 'opacity-100 -translate-x-3' : 'opacity-0'}
      `}>
        {label}
      </div>
      <div className="absolute right-2.5">
        <ArrowRight className="h-4 w-4" />
      </div>
    </button>
  );
};
