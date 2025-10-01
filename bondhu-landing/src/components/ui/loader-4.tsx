import React from 'react';

const Loader = () => {
  return (
    <div className="flex flex-wrap" style={{
      width: 'calc(3 * (52px + 2px))',
      height: 'calc(3 * (52px + 2px))'
    }}>
      <div className="cell cell-1 animate-ripple" style={{ animationDelay: '0ms' }} />
      <div className="cell cell-2 animate-ripple" style={{ animationDelay: '100ms' }} />
      <div className="cell cell-3 animate-ripple" style={{ animationDelay: '200ms' }} />
      <div className="cell cell-4 animate-ripple" style={{ animationDelay: '100ms' }} />
      <div className="cell cell-5 animate-ripple" style={{ animationDelay: '200ms' }} />
      <div className="cell cell-6 animate-ripple" style={{ animationDelay: '200ms' }} />
      <div className="cell cell-7 animate-ripple" style={{ animationDelay: '300ms' }} />
      <div className="cell cell-8 animate-ripple" style={{ animationDelay: '300ms' }} />
      <div className="cell cell-9 animate-ripple" style={{ animationDelay: '400ms' }} />
      
      <style jsx>{`
        .cell {
          flex: 0 0 52px;
          margin: 1px;
          background-color: transparent;
          box-sizing: border-box;
          border-radius: 4px;
          height: 52px;
        }

        .cell-1 { --cell-color: #00FF87; }
        .cell-2 { --cell-color: #0CFD95; }
        .cell-3 { --cell-color: #17FBA2; }
        .cell-4 { --cell-color: #23F9B2; }
        .cell-5 { --cell-color: #30F7C3; }
        .cell-6 { --cell-color: #3DF5D4; }
        .cell-7 { --cell-color: #45F4DE; }
        .cell-8 { --cell-color: #53F1F0; }
        .cell-9 { --cell-color: #60EFFF; }

        @keyframes ripple {
          0% {
            background-color: transparent;
          }
          30% {
            background-color: var(--cell-color);
          }
          60% {
            background-color: transparent;
          }
          100% {
            background-color: transparent;
          }
        }

        .animate-ripple {
          animation: ripple 1.5s ease infinite;
        }
      `}</style>
    </div>
  );
}

export default Loader;
