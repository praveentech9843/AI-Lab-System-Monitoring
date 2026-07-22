import React from 'react';
import { FiLogOut, FiShield, FiBell } from 'react-icons/fi';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { logout } = useAuth();

  return (
    <header className="h-16 bg-slate-900/80 backdrop-blur-md border-b border-slate-800 px-6 flex items-center justify-between sticky top-0 z-10">
      <div className="flex items-center space-x-2 text-slate-400 text-sm font-medium">
        <FiShield className="text-sky-400 w-4 h-4" />
        <span>System Monitoring Hub</span>
      </div>

      <div className="flex items-center space-x-4">
        <button
          className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors relative"
          title="Notifications"
        >
          <FiBell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-sky-500"></span>
        </button>

        <div className="h-4 w-px bg-slate-800"></div>

        <button
          onClick={logout}
          className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 text-sm font-medium transition-colors"
        >
          <FiLogOut className="w-4 h-4" />
          <span>Logout</span>
        </button>
      </div>
    </header>
  );
};

export default Navbar;
