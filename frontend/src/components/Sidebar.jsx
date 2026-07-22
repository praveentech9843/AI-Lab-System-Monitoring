import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  FiGrid,
  FiUserCheck,
  FiUsers,
  FiClock,
  FiActivity,
  FiAlertTriangle,
} from 'react-icons/fi';

const navItems = [
  { name: 'Dashboard', path: '/', icon: FiGrid },
  { name: 'Students', path: '/students', icon: FiUserCheck },
  { name: 'Faculty', path: '/faculty', icon: FiUsers },
  { name: 'Exam Sessions', path: '/sessions', icon: FiClock },
  { name: 'Activities', path: '/activities', icon: FiActivity },
  { name: 'Alerts', path: '/alerts', icon: FiAlertTriangle },
];

const Sidebar = () => {
  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col min-h-screen">
      <div className="h-16 flex items-center px-6 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-sky-500 flex items-center justify-center font-bold text-white shadow-lg shadow-sky-500/30">
            AI
          </div>
          <span className="font-semibold text-slate-100 text-base tracking-wide">
            Lab Monitor
          </span>
        </div>
      </div>

      <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-sky-500/10 text-sky-400 border-l-2 border-sky-500'
                    : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                }`
              }
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-800 text-xs text-slate-500 text-center">
        v1.0.0 &bull; AI System Core
      </div>
    </aside>
  );
};

export default Sidebar;
