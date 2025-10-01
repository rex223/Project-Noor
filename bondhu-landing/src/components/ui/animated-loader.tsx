import React from 'react';

interface LoaderProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const Loader = ({ size = 'md', className = '' }: LoaderProps) => {
  const sizeMap = {
    sm: { cell: 'w-8 h-8', spacing: 'gap-0.5' },
    md: { cell: 'w-[52px] h-[52px]', spacing: 'gap-[1px]' },
    lg: { cell: 'w-16 h-16', spacing: 'gap-1' }
  };

  const { cell: cellSize, spacing } = sizeMap[size];

  return (
    <div className={`grid grid-cols-3 ${spacing} ${className}`}>
      {[
        { delay: 0, color: 'from-[#00FF87] to-[#00FF87]' },
        { delay: 100, color: 'from-[#0CFD95] to-[#0CFD95]' },
        { delay: 200, color: 'from-[#17FBA2] to-[#17FBA2]' },
        { delay: 100, color: 'from-[#23F9B2] to-[#23F9B2]' },
        { delay: 200, color: 'from-[#30F7C3] to-[#30F7C3]' },
        { delay: 200, color: 'from-[#3DF5D4] to-[#3DF5D4]' },
        { delay: 300, color: 'from-[#45F4DE] to-[#45F4DE]' },
        { delay: 300, color: 'from-[#53F1F0] to-[#53F1F0]' },
        { delay: 400, color: 'from-[#60EFFF] to-[#60EFFF]' },
      ].map((cell, index) => (
        <div
          key={index}
          className={`${cellSize} rounded bg-transparent animate-ripple`}
          style={{
            animationDelay: `${cell.delay}ms`,
            '--ripple-color': cell.color.match(/#[0-9A-F]{6}/i)?.[0] || '#00FF87',
          } as React.CSSProperties}
        />
      ))}
    </div>
  );
};

export default Loader;
