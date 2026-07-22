import React from 'react';

const Loader = ({ fullScreen = true }) => {
  const content = (
    <div className="flex flex-col items-center justify-center space-y-3">
      <div className="w-10 h-10 border-4 border-sky-500 border-t-transparent rounded-full animate-spin"></div>
      <span className="text-sm text-slate-400 font-medium">Loading system components...</span>
    </div>
  );

  if (fullScreen) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        {content}
      </div>
    );
  }

  return content;
};

export default Loader;
