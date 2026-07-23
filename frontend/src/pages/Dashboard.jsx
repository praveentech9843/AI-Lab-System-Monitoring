import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Activity, Shield, Wifi, AlertTriangle, Monitor, Clock,
  LogOut, Plus, Trash2, Globe, ToggleLeft, ToggleRight,
  Cpu, MemoryStick, CheckCircle, XCircle, AlertOctagon,
  RefreshCw, Bell, Users, Eye, Zap, Lock, ServerCrash,
  GraduationCap, BookOpen, CalendarClock, RotateCcw,
  Brain, TrendingUp, ShieldAlert, Lightbulb, BarChart3,
  AlertCircle, Crosshair, FlameKindling, X, HelpCircle,
  MoreVertical, ShieldCheck, Download, Calendar, Filter, Search,
  Unlock, Camera, UserMinus, FileText, Volume2, VolumeX,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../api/api';
import { useAIEngine } from '../hooks/useAIEngine';
import { useVoiceAlerts } from '../hooks/useVoiceAlerts';

/* Recharts imports for professional visual graphics */
import {
  ResponsiveContainer,
  AreaChart, Area,
  XAxis, YAxis,
  CartesianGrid, Tooltip, Legend,
  PieChart, Pie, Cell,
  BarChart, Bar,
  LineChart, Line
} from 'recharts';

/* ─────────────────────────────────────────
   CONFIG & WEIGHTS
───────────────────────────────────────── */
const WS_URL = 'ws://localhost:8000/ws/live';

const alertSeverityConfig = {
  CRITICAL: { color: '#EF4444', bg: 'rgba(239,68,68,0.1)',   border: 'rgba(239,68,68,0.3)',   icon: AlertOctagon },
  HIGH:     { color: '#F97316', bg: 'rgba(249,115,22,0.1)',  border: 'rgba(249,115,22,0.25)',  icon: AlertTriangle },
  MEDIUM:   { color: '#F59E0B', bg: 'rgba(245,158,11,0.1)',  border: 'rgba(245,158,11,0.25)',  icon: AlertTriangle },
  WARNING:  { color: '#F59E0B', bg: 'rgba(245,158,11,0.1)',  border: 'rgba(245,158,11,0.25)',  icon: AlertTriangle },
  LOW:      { color: '#06B6D4', bg: 'rgba(6,182,212,0.08)',  border: 'rgba(6,182,212,0.2)',    icon: Bell },
  INFO:     { color: '#06B6D4', bg: 'rgba(6,182,212,0.08)',  border: 'rgba(6,182,212,0.2)',    icon: Bell },
};

const statusConfig = {
  Online:     { color: '#10B981', bg: 'rgba(16,185,129,0.12)',  border: 'rgba(16,185,129,0.25)',  dot: 'bg-emerald-400' },
  Idle:       { color: '#F59E0B', bg: 'rgba(245,158,11,0.1)',   border: 'rgba(245,158,11,0.25)',   dot: 'bg-amber-400'   },
  Suspicious: { color: '#EF4444', bg: 'rgba(239,68,68,0.1)',    border: 'rgba(239,68,68,0.3)',     dot: 'bg-red-400'     },
  Offline:    { color: '#6B7280', bg: 'rgba(107,114,128,0.08)', border: 'rgba(107,114,128,0.2)',   dot: 'bg-slate-500'   },
};

const insightLevelConfig = {
  critical: { color: '#EF4444', bg: 'rgba(239,68,68,0.1)',   border: 'rgba(239,68,68,0.25)',  icon: AlertOctagon },
  warning:  { color: '#F59E0B', bg: 'rgba(245,158,11,0.08)',  border: 'rgba(245,158,11,0.2)',   icon: AlertTriangle },
  info:     { color: '#06B6D4', bg: 'rgba(6,182,212,0.08)',  border: 'rgba(6,182,212,0.2)',    icon: Bell },
  safe:     { color: '#10B981', bg: 'rgba(16,185,129,0.08)', border: 'rgba(16,185,129,0.2)',   icon: CheckCircle },
};


/* ─────────────────────────────────────────
   HELPERS & FORMATTERS
───────────────────────────────────────── */
const useClockTick = () => {
  const [time, setTime] = useState(new Date());
  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(id);
  }, []);
  return time;
};

const formatTime = (isoString) => {
  if (!isoString) return '—';
  try {
    return new Date(isoString).toLocaleTimeString();
  } catch {
    return isoString;
  }
};

const formatRelative = (isoString) => {
  if (!isoString) return '';
  try {
    const diff = Math.floor((Date.now() - new Date(isoString).getTime()) / 1000);
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    return `${Math.floor(diff / 3600)}h ago`;
  } catch {
    return '';
  }
};

const normalizeSeverity = (s = '') => (s || '').toUpperCase();

const activityLabel = (type = '') =>
  (type || '').replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

const getRiskStatus = (score) => {
  const s = score || 0;
  if (s >= 71) return { label: 'Critical', color: '#EF4444', bg: 'rgba(239,68,68,0.12)', border: 'rgba(239,68,68,0.3)' };
  if (s >= 31) return { label: 'Warning',  color: '#F59E0B', bg: 'rgba(245,158,11,0.1)',  border: 'rgba(245,158,11,0.25)' };
  return              { label: 'Safe',     color: '#10B981', bg: 'rgba(16,185,129,0.1)',  border: 'rgba(16,185,129,0.25)' };
};

const activityIcon = (type = '') => {
  const t = (type || '').toLowerCase();
  if (t.includes('face') || t.includes('look')) return Eye;
  if (t.includes('phone') || t.includes('device')) return Shield;
  if (t.includes('tab') || t.includes('switch')) return Monitor;
  if (t.includes('cpu') || t.includes('memory')) return Cpu;
  if (t.includes('alert')) return AlertTriangle;
  return Activity;
};

const activityTypeStyle = (type = '') => {
  const t = (type || '').toLowerCase();
  if (t.includes('face') || t.includes('phone') || t.includes('suspicious')) return { color: '#EF4444' };
  if (t.includes('tab') || t.includes('look') || t.includes('head')) return { color: '#F59E0B' };
  return { color: '#06B6D4' };
};

/* ─────────────────────────────────────────
   SKELETON & EMPTY STATES
───────────────────────────────────────── */
const Skeleton = ({ className = '', style = {} }) => (
  <div className={`animate-pulse rounded-xl ${className}`} style={{ background: 'rgba(255,255,255,0.06)', ...style }} />
);

const EmptyState = ({ icon: Icon, message, onRetry }) => (
  <div className="flex flex-col items-center justify-center py-10 gap-3">
    <div className="w-12 h-12 rounded-2xl flex items-center justify-center" style={{ background: 'rgba(255,255,255,0.04)' }}>
      {Icon && <Icon size={22} style={{ color: '#334155' }} />}
    </div>
    <p className="text-sm text-center text-slate-500">{message}</p>
    {onRetry && (
      <button onClick={onRetry} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors" style={{ background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)', color: '#818CF8' }}>
        <RotateCcw size={12} /> Retry
      </button>
    )}
  </div>
);

/* ─────────────────────────────────────────
   AI SUMMARY CARD
───────────────────────────────────────── */
const riskOverallStyle = {
  Critical: { color: '#EF4444', bg: 'rgba(239,68,68,0.15)', border: 'rgba(239,68,68,0.35)' },
  High:     { color: '#F97316', bg: 'rgba(249,115,22,0.12)', border: 'rgba(249,115,22,0.3)' },
  Medium:   { color: '#F59E0B', bg: 'rgba(245,158,11,0.12)', border: 'rgba(245,158,11,0.3)' },
  Low:      { color: '#10B981', bg: 'rgba(16,185,129,0.1)', border: 'rgba(16,185,129,0.25)' },
};

const AISummaryCard = ({ summary }) => {
  const s = summary || { monitored: 0, suspicious: 0, criticalAlerts: 0, blockedAttempts: 0, overallRisk: 'Low', avgScore: 0 };
  const rStyle = riskOverallStyle[s.overallRisk] || riskOverallStyle.Low;
  const items = [
    { label: 'Students Monitored', value: s.monitored || 0,        icon: Users,       color: '#6366F1' },
    { label: 'Suspicious Systems', value: s.suspicious || 0,       icon: ShieldAlert, color: '#F59E0B' },
    { label: 'Critical Alerts',    value: s.criticalAlerts || 0,   icon: AlertOctagon,color: '#EF4444' },
    { label: 'Blocked Attempts',   value: s.blockedAttempts || 0,  icon: Globe,       color: '#F97316' },
  ];
  return (
    <div className="rounded-2xl overflow-hidden" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', backdropFilter: 'blur(12px)' }}>
      <div className="flex items-center justify-between px-5 py-4 border-b" style={{ borderColor: 'rgba(255,255,255,0.06)' }}>
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: 'rgba(99,102,241,0.15)' }}>
            <BarChart3 size={14} style={{ color: '#6366F1' }} />
          </div>
          <span className="text-white text-sm font-semibold">Today's AI Analysis</span>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold" style={{ background: rStyle.bg, border: `1px solid ${rStyle.border}`, color: rStyle.color }}>
          <FlameKindling size={11} />
          Overall Lab Risk: {s.overallRisk || 'Low'}
        </div>
      </div>
      <div className="p-5">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
          {items.map(({ label, value, icon: Icon, color }) => (
            <div key={label} className="rounded-xl p-3 text-center" style={{ background: `${color}0D`, border: `1px solid ${color}20` }}>
              {Icon && <Icon size={16} className="mx-auto mb-1.5" style={{ color }} />}
              <p className="text-xl font-black text-white">{value}</p>
              <p className="text-xs mt-0.5" style={{ color: '#64748B' }}>{label}</p>
            </div>
          ))}
        </div>
        <div>
          <div className="flex justify-between text-xs mb-1.5" style={{ color: '#64748B' }}>
            <span className="flex items-center gap-1"><Brain size={10} style={{ color: '#8B5CF6' }} />Average AI Risk Score</span>
            <span className="text-white font-semibold">{s.avgScore || 0} / 100</span>
          </div>
          <div className="h-2 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.06)' }}>
            <motion.div
              className="h-full rounded-full"
              style={{
                background: (s.avgScore || 0) >= 71 ? 'linear-gradient(90deg,#EF4444,#F97316)' : (s.avgScore || 0) >= 31 ? 'linear-gradient(90deg,#F59E0B,#F97316)' : 'linear-gradient(90deg,#10B981,#06B6D4)',
                width: `${s.avgScore || 0}%`,
              }}
              initial={{ width: 0 }}
              animate={{ width: `${s.avgScore || 0}%` }}
              transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

/* ─────────────────────────────────────────
   AI INSIGHTS PANEL
───────────────────────────────────────── */
const AIInsightsPanel = ({ insights }) => (
  <div className="rounded-2xl overflow-hidden" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', backdropFilter: 'blur(12px)' }}>
    <div className="flex items-center justify-between px-5 py-4 border-b" style={{ borderColor: 'rgba(255,255,255,0.06)' }}>
      <div className="flex items-center gap-2.5">
        <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: 'rgba(139,92,246,0.15)' }}>
          <Brain size={14} style={{ color: '#8B5CF6' }} />
        </div>
        <span className="text-white text-sm font-semibold">AI Insights</span>
      </div>
      <div className="flex items-center gap-1.5 text-xs" style={{ color: '#64748B' }}>
        <div className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse" />
        <span>AI Engine Active</span>
      </div>
    </div>
    <div className="p-5 space-y-2.5 max-h-[190px] overflow-y-auto pr-1">
      <AnimatePresence mode="popLayout">
        {(insights || []).map((ins, i) => {
          if (!ins) return null;
          const cfg = insightLevelConfig[ins.level] || insightLevelConfig.info;
          const Icon = cfg.icon;
          return (
            <motion.div
              key={(ins.text || '').slice(0, 45) + i}
              className="flex items-start gap-3 px-3 py-2.5 rounded-xl"
              style={{ background: cfg.bg, border: `1px solid ${cfg.border}` }}
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 16 }}
              transition={{ delay: i * 0.05, duration: 0.3 }}
              layout
            >
              <div className="w-6 h-6 rounded-md flex items-center justify-center flex-shrink-0 mt-0.5" style={{ background: `${cfg.color}18` }}>
                {Icon && <Icon size={12} style={{ color: cfg.color }} />}
              </div>
              <p className="text-xs leading-relaxed" style={{ color: '#94A3B8' }}>
                {ins.pc && <span className="font-semibold text-white mr-1">{ins.pc}</span>}
                {(ins.text || '').replace(/^PC-\d+\s/, '')}
              </p>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  </div>
);

/* ─────────────────────────────────────────
   STAT CARD
───────────────────────────────────────── */
const StatCard = ({ label, value, icon: Icon, color, glow, delay, loading }) => (
  <motion.div
    className="relative rounded-2xl p-5 overflow-hidden"
    style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.06)', backdropFilter: 'blur(12px)' }}
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
    whileHover={{ y: -3, boxShadow: `0 16px 40px ${glow}`, borderColor: 'rgba(255,255,255,0.12)' }}
  >
    <div className="absolute top-3 right-3 w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: `${color}18` }}>
      {Icon && <Icon size={18} style={{ color }} />}
    </div>
    <p className="text-xs font-semibold mb-2 uppercase tracking-wider" style={{ color: '#64748B' }}>{label}</p>
    {loading ? <Skeleton className="h-9 w-14" /> : <p className="text-3xl font-black text-white">{value ?? '—'}</p>}
    <div className="absolute bottom-0 left-0 right-0 h-0.5 rounded-full" style={{ background: `linear-gradient(90deg,${color}00,${color}60,${color}00)` }} />
  </motion.div>
);

/* ─────────────────────────────────────────
   ALERT CARD
───────────────────────────────────────── */
const AlertCard = ({ alert, delay }) => {
  if (!alert) return null;
  const sev = normalizeSeverity(alert.severity);
  const cfg = alertSeverityConfig[sev] || alertSeverityConfig.INFO;
  const Icon = cfg.icon;
  return (
    <motion.div
      className="flex items-start gap-3 p-3 rounded-xl"
      style={{ background: cfg.bg, border: `1px solid ${cfg.border}` }}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay, duration: 0.4 }}
    >
      <div className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5" style={{ background: `${cfg.color}20` }}>
        {Icon && <Icon size={14} style={{ color: cfg.color }} />}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2 mb-0.5">
          <span className="text-xs font-semibold text-white truncate">{activityLabel(alert.alert_type || 'Alert')}</span>
          <span className="text-xs px-1.5 py-0.5 rounded font-bold flex-shrink-0" style={{ background: `${cfg.color}20`, color: cfg.color }}>{sev}</span>
        </div>
        <p className="text-xs text-slate-400">{alert.message}</p>
        <p className="text-xs mt-0.5 text-slate-600">{formatRelative(alert.created_at || alert.timestamp)}</p>
      </div>
    </motion.div>
  );
};

/* ─────────────────────────────────────────
   FEED EVENT
───────────────────────────────────────── */
const FeedEvent = ({ event, delay }) => {
  if (!event) return null;
  const Icon  = activityIcon(event.activity_type);
  const style = activityTypeStyle(event.activity_type);
  const conf  = event.confidence != null ? ` (${Math.round(event.confidence * 100)}%)` : '';
  return (
    <motion.div
      className="flex items-start gap-3 py-2.5 border-b"
      style={{ borderColor: 'rgba(255,255,255,0.04)' }}
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay }}
      layout
    >
      <div className="w-6 h-6 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5" style={{ background: `${style.color}15` }}>
        {Icon && <Icon size={12} style={{ color: style.color }} />}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-xs text-white leading-snug">{activityLabel(event.activity_type)}{conf}</p>
        <p className="text-xs mt-0.5 text-slate-600">{formatTime(event.timestamp || event.created_at)}</p>
      </div>
    </motion.div>
  );
};

/* ─────────────────────────────────────────
   COMPUTER DETAILS MODAL
───────────────────────────────────────── */
const ComputerDetailsModal = ({ computer, onClose, getRiskStatus, riskData }) => {
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const score = riskData?.score ?? 0;
  const risk  = getRiskStatus(score);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const { data } = await api.get(`/computers/${computer.number}/details`);
        setDetails(data);
      } catch {
        toast.error('Failed to load workstation details.');
      } finally {
        setLoading(false);
      }
    };
    fetchDetails();
  }, [computer]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md">
      <motion.div
        className="w-full max-w-xl relative rounded-3xl overflow-hidden"
        style={{
          background: 'rgba(255,255,255,0.06)',
          border: '1px solid rgba(255,255,255,0.1)',
          boxShadow: '0 32px 80px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.1)',
        }}
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
      >
        <div className="absolute top-0 left-0 right-0 h-px" style={{ background: 'linear-gradient(90deg,transparent,rgba(99,102,241,0.6),transparent)' }} />

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/5">
          <div className="flex items-center gap-2">
            <Monitor size={18} style={{ color: '#6366F1' }} />
            <h3 className="text-white text-lg font-bold">Details: {computer?.number}</h3>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors">
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 max-h-[80vh] overflow-y-auto">
          {loading ? (
            <div className="space-y-4">
              <Skeleton className="h-20" />
              <Skeleton className="h-40" />
              <Skeleton className="h-28" />
            </div>
          ) : (
            <>
              {/* Top Row: Info */}
              <div className="grid grid-cols-2 gap-4">
                <div className="rounded-2xl p-4 bg-white/5 border border-white/5">
                  <span className="text-xs text-slate-500 uppercase font-semibold">Student Name</span>
                  <p className="text-white text-base font-bold mt-1">{computer?.student || 'Unassigned'}</p>
                  <span className="text-xs text-slate-600 mt-2 block">{details?.student?.email || 'No email registered'}</span>
                </div>
                <div className="rounded-2xl p-4 bg-white/5 border border-white/5 flex flex-col justify-between">
                  <div>
                    <span className="text-xs text-slate-500 uppercase font-semibold">AI Risk Status</span>
                    <p className="text-white text-base font-bold mt-1 flex items-center gap-2">
                      <Brain size={16} style={{ color: risk.color }} />
                      <span style={{ color: risk.color }}>{risk.label} ({score})</span>
                    </p>
                  </div>
                  <div className="h-1.5 rounded-full overflow-hidden mt-3" style={{ background: 'rgba(255,255,255,0.06)' }}>
                    <div className="h-full rounded-full" style={{ background: risk.color, width: `${score}%` }} />
                  </div>
                </div>
              </div>

              {/* Middle Row: Metrics & Active Status */}
              <div className="grid grid-cols-2 gap-4">
                <div className="rounded-2xl p-4 bg-white/5 border border-white/5 space-y-2">
                  <span className="text-xs text-slate-500 uppercase font-semibold">System Metrics</span>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-400">CPU Usage</span>
                    <span className="text-white font-semibold">{computer?.cpu}%</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-400">RAM Usage</span>
                    <span className="text-white font-semibold">{computer?.ram}%</span>
                  </div>
                </div>
                <div className="rounded-2xl p-4 bg-white/5 border border-white/5 space-y-2">
                  <span className="text-xs text-slate-500 uppercase font-semibold">Current State</span>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-400">Active App</span>
                    <span className="text-white font-semibold truncate max-w-[120px]">{computer?.app}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-400">Active Domain</span>
                    <span className="text-white font-semibold truncate max-w-[120px]">{computer?.website}</span>
                  </div>
                </div>
              </div>

              {/* Media captures (Screenshot + Webcam) */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Latest Screenshot */}
                <div className="rounded-2xl overflow-hidden bg-white/5 border border-white/5 p-4 space-y-2">
                  <span className="text-xs text-slate-500 uppercase font-semibold block">Latest Workstation Screen Capture</span>
                  {computer?.screenshot_data ? (
                    <div className="relative rounded-xl overflow-hidden h-40 bg-black/30 border border-white/5 flex items-center justify-center">
                      <img
                        key={computer.screenshot_data}
                        src={`data:image/jpeg;base64,${computer.screenshot_data}`}
                        alt="Workstation capture"
                        className="w-full h-full object-contain"
                      />
                    </div>
                  ) : computer?.screenshot_path ? (
                    <div className="relative rounded-xl overflow-hidden h-40 bg-black/30 border border-white/5 flex items-center justify-center">
                      <img
                        key={computer.screenshot_path}
                        src={`http://localhost:8000/static/screenshots/${computer.screenshot_path}`}
                        alt="Workstation capture"
                        className="w-full h-full object-contain"
                      />
                    </div>
                  ) : (
                    <div className="h-40 rounded-xl bg-black/30 border border-white/5 flex items-center justify-center">
                      <p className="text-xs text-slate-600">No screen captures taken yet.</p>
                    </div>
                  )}
                </div>

                {/* Webcam Feed */}
                <div className="rounded-2xl overflow-hidden bg-white/5 border border-white/5 p-4 space-y-2">
                  <span className="text-xs text-slate-500 uppercase font-semibold block">Live Webcam Feed</span>
                  {computer?.webcam_data ? (
                    <div className="relative rounded-xl overflow-hidden h-40 bg-black/30 border border-white/5 flex items-center justify-center">
                      <img
                        key={computer.webcam_data}
                        src={`data:image/jpeg;base64,${computer.webcam_data}`}
                        alt="Webcam Feed"
                        className="w-full h-full object-contain"
                      />
                    </div>
                  ) : computer?.webcam_path ? (
                    <div className="relative rounded-xl overflow-hidden h-40 bg-black/30 border border-white/5 flex items-center justify-center">
                      <img
                        key={computer.webcam_path}
                        src={`http://localhost:8000/static/webcams/${computer.webcam_path}`}
                        alt="Webcam Feed"
                        className="w-full h-full object-contain"
                      />
                    </div>
                  ) : (
                    <div className="h-40 rounded-xl bg-black/30 border border-white/5 flex items-center justify-center">
                      <p className="text-xs text-slate-600">No webcam feed available.</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Alert History */}
              <div className="rounded-2xl bg-white/5 border border-white/5 p-4 space-y-3">
                <span className="text-xs text-slate-500 uppercase font-semibold block">Alert History</span>
                {details?.alerts?.length === 0 ? (
                  <p className="text-xs text-slate-600 py-2">No alerts generated for this student.</p>
                ) : (
                  <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                    {(details?.alerts || []).map((alert) => {
                      if (!alert) return null;
                      const sev = normalizeSeverity(alert.severity);
                      const alertCfg = alertSeverityConfig[sev] || alertSeverityConfig.INFO;
                      return (
                        <div key={alert.id} className="flex items-start gap-2.5 p-2.5 rounded-lg border" style={{ background: alertCfg.bg, borderColor: alertCfg.border }}>
                          <div className="w-5 h-5 rounded-md flex items-center justify-center flex-shrink-0 mt-0.5" style={{ background: `${alertCfg.color}15` }}>
                            <AlertCircle size={11} style={{ color: alertCfg.color }} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between gap-1 mb-0.5">
                              <span className="text-xs font-semibold text-white">{activityLabel(alert.alert_type)}</span>
                              <span className="text-[10px] px-1 py-0.2 rounded font-bold" style={{ background: `${alertCfg.color}20`, color: alertCfg.color }}>{sev}</span>
                            </div>
                            <p className="text-[11px] text-slate-400">{alert.message}</p>
                            <p className="text-[10px] text-slate-600 mt-0.5">{formatRelative(alert.created_at)}</p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </motion.div>
    </div>
  );
};

/* ─────────────────────────────────────────
   COMPUTER CARD WITH ADMIN ACTIONS
───────────────────────────────────────── */
const ComputerCard = ({ pc, delay, riskData, getRiskStatus, onClick, onAction }) => {
  if (!pc) return null;
  const cfg = statusConfig[pc.status] || statusConfig.Offline;
  const score = riskData?.score ?? 0;
  const risk  = getRiskStatus(score);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleOutsideClick = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleOutsideClick);
    return () => document.removeEventListener('mousedown', handleOutsideClick);
  }, []);

  const actionList = [
    { label: 'Lock Device',     action: 'lock',       icon: Lock,          color: '#F97316' },
    { label: 'Unlock Device',   action: 'unlock',     icon: Unlock,        color: '#10B981' },
    { label: 'Force Logout',    action: 'logout',     icon: UserMinus,     color: '#EF4444' },
    { label: 'Capture Screen',  action: 'screenshot', icon: Camera,        color: '#06B6D4' },
    { label: 'Mark Safe',       action: 'safe',       icon: ShieldCheck,   color: '#10B981' },
    { label: 'Flag Suspicious', action: 'suspicious', icon: AlertTriangle, color: '#EF4444' },
  ];

  return (
    <motion.div
      className="relative rounded-2xl p-4 cursor-pointer group"
      style={{ background: cfg.bg, border: `1px solid ${cfg.border}`, backdropFilter: 'blur(12px)' }}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay, duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      whileHover={{ y: -4, boxShadow: `0 16px 40px rgba(0,0,0,0.45)`, borderColor: cfg.color + '70' }}
      onClick={() => onClick(pc)}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3 relative" onClick={e => e.stopPropagation()}>
        <div className="flex items-center gap-2">
          <Monitor size={14} style={{ color: cfg.color }} />
          <span className="text-white text-sm font-bold">{pc.number}</span>
        </div>
        
        {/* Actions Cog Dropdown */}
        <div className="flex items-center gap-1.5">
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setShowDropdown(prev => !prev)}
              className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
              title="Admin Actions"
            >
              <MoreVertical size={13} />
            </button>
            <AnimatePresence>
              {showDropdown && (
                <motion.div
                  className="absolute right-0 top-6 z-30 w-44 rounded-xl p-1 overflow-hidden"
                  style={{
                    background: 'rgba(15,23,42,0.95)',
                    backdropFilter: 'blur(16px)',
                    border: '1px solid rgba(255,255,255,0.08)',
                    boxShadow: '0 10px 25px -5px rgba(0,0,0,0.5)',
                  }}
                  initial={{ opacity: 0, scale: 0.95, y: -4 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: -4 }}
                  transition={{ duration: 0.15 }}
                >
                  {actionList.map(({ label, action, icon: Icon, color }) => (
                    <button
                      key={action}
                      onClick={() => {
                        setShowDropdown(false);
                        onAction(pc, action);
                      }}
                      className="w-full text-left px-2.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 text-slate-300 hover:text-white hover:bg-white/5 transition-colors"
                    >
                      <Icon size={12} style={{ color }} />
                      {label}
                    </button>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <div className="flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] font-bold" style={{ background: cfg.bg, border: `1px solid ${cfg.border}`, color: cfg.color }}>
            <span className={`w-1 h-1 rounded-full ${cfg.dot}`} />
            {pc.status}
          </div>
        </div>
      </div>

      {/* Screen capture frame */}
      <div className="relative w-full h-16 rounded-xl mb-3 overflow-hidden flex items-center justify-center bg-black/35 border border-white/5">
        {pc.status === 'Offline' ? (
          <div className="flex flex-col items-center gap-0.5">
            <XCircle size={16} style={{ color: '#374151' }} />
            <span className="text-[10px] text-slate-600 font-bold">Offline</span>
          </div>
        ) : (
          <>
            <div className="absolute inset-0 flex items-center justify-center">
              {pc.screenshot_data ? (
                <img
                  key={pc.screenshot_data}
                  src={`data:image/jpeg;base64,${pc.screenshot_data}`}
                  alt="Workstation Preview"
                  className="w-full h-full object-cover opacity-80"
                />
              ) : pc.screenshot_path ? (
                <img
                  key={pc.screenshot_path}
                  src={`http://localhost:8000/static/screenshots/${pc.screenshot_path}`}
                  alt="Workstation Preview"
                  className="w-full h-full object-cover opacity-80"
                  onError={(e) => { e.target.onerror = null; }}
                />
              ) : (
                <div className="grid grid-cols-4 gap-0.5 w-3/4 opacity-15">
                  {Array.from({ length: 8 }).map((_, i) => <div key={i} className="h-1.5 rounded-sm bg-slate-500" />)}
                </div>
              )}
            </div>
            <div className="absolute bottom-1 right-1.5 text-[9px] px-1 py-0.2 rounded bg-black/75 text-slate-400 font-medium">
              <Eye size={7} className="inline mr-0.5" />Live
            </div>
          </>
        )}
      </div>

      {/* Student / App */}
      <div className="space-y-1 mb-3">
        <div className="flex items-center gap-1.5">
          <Users size={10} style={{ color: '#64748B' }} />
          <span className="text-xs font-semibold truncate max-w-[125px] text-slate-300">{pc.student || 'Unassigned'}</span>
        </div>
        {pc.status !== 'Offline' && (
          <>
            <div className="flex items-center gap-1.5">
              <Monitor size={10} style={{ color: '#64748B' }} />
              <span className="text-xs truncate max-w-[125px] text-slate-500">{pc.app}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Globe size={10} style={{ color: '#64748B' }} />
              <span className="text-xs truncate max-w-[125px] text-slate-500">{pc.website}</span>
            </div>
          </>
        )}
      </div>

      {/* CPU / RAM metrics */}
      {pc.status !== 'Offline' && (
        <div className="space-y-1.5 mb-3">
          <div>
            <div className="flex justify-between text-[10px] mb-0.5 text-slate-500">
              <span className="flex items-center gap-0.5"><Cpu size={8} />CPU</span>
              <span style={{ color: pc.cpu > 80 ? '#EF4444' : '#94A3B8' }}>{pc.cpu}%</span>
            </div>
            <div className="h-0.5 rounded-full overflow-hidden bg-white/5">
              <motion.div className="h-full rounded-full" style={{ background: pc.cpu > 80 ? '#EF4444' : '#6366F1', width: `${pc.cpu}%` }} initial={{ width: 0 }} animate={{ width: `${pc.cpu}%` }} />
            </div>
          </div>
          <div>
            <div className="flex justify-between text-[10px] mb-0.5 text-slate-500">
              <span className="flex items-center gap-0.5"><MemoryStick size={8} />RAM</span>
              <span style={{ color: '#94A3B8' }}>{pc.ram}%</span>
            </div>
            <div className="h-0.5 rounded-full overflow-hidden bg-white/5">
              <motion.div className="h-full rounded-full" style={{ background: '#8B5CF6', width: `${pc.ram}%` }} initial={{ width: 0 }} animate={{ width: `${pc.ram}%` }} />
            </div>
          </div>
        </div>
      )}

      {/* AI RISK SCORE */}
      {pc.status !== 'Offline' && (
        <div className="pt-2 border-t border-white/5">
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-0.5 text-slate-500">
              <Brain size={9} style={{ color: risk.color }} />
              <span className="text-[10px] font-semibold">AI Risk</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="text-xs font-bold" style={{ color: risk.color }}>{score}</span>
              <span className="text-[9px] px-1 py-0.2 rounded-full font-bold" style={{ background: risk.bg, border: `1px solid ${risk.border}`, color: risk.color }}>
                {risk.label}
              </span>
            </div>
          </div>
          <div className="h-1 rounded-full overflow-hidden bg-white/5">
            <motion.div
              className="h-full rounded-full"
              style={{
                background: score >= 71 ? 'linear-gradient(90deg,#EF4444,#F97316)' : score >= 31 ? 'linear-gradient(90deg,#F59E0B,#F97316)' : 'linear-gradient(90deg,#10B981,#06B6D4)',
                width: `${score}%`,
              }}
              initial={{ width: 0 }}
              animate={{ width: `${score}%` }}
              transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
            />
          </div>
        </div>
      )}
    </motion.div>
  );
};

/* ─────────────────────────────────────────
   SECTION CARD WRAPPER
───────────────────────────────────────── */
const SectionCard = ({ title, icon: Icon, iconColor = '#6366F1', action, children }) => (
  <div className="rounded-2xl overflow-hidden bg-white/5 border border-white/5" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', backdropFilter: 'blur(12px)' }}>
    <div className="flex items-center justify-between px-5 py-4 border-b border-white/5" style={{ borderColor: 'rgba(255,255,255,0.06)' }}>
      <div className="flex items-center gap-2.5">
        <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: `${iconColor}18` }}>
          {Icon && <Icon size={14} style={{ color: iconColor }} />}
        </div>
        <span className="text-white text-sm font-semibold">{title}</span>
      </div>
      {action}
    </div>
    <div className="p-5">{children}</div>
  </div>
);

/* ═══════════════════════════════════════════
   MAIN DASHBOARD
═══════════════════════════════════════════ */
const Dashboard = () => {
  const { logout } = useAuth();
  const navigate   = useNavigate();
  const time       = useClockTick();
  const { voices, settings: voiceSettings, setSettings: setVoiceSettings, speakAlert } = useVoiceAlerts();

  const handleLogout = useCallback(() => {
    logout();
    navigate('/login');
    toast.success('Logged out successfully.');
  }, [logout, navigate]);

  /* Database lists states */
  const [systemOnline, setSystemOnline] = useState(null);
  const [students, setStudents]         = useState([]);
  const [faculty, setFaculty]           = useState([]);
  const [sessions, setSessions]         = useState([]);
  const [activities, setActivities]     = useState([]);
  const [alerts, setAlerts]             = useState([]);
  const [computers, setComputers]       = useState([]);
  const [blockedSites, setBlockedSites] = useState(() => {
    try { return JSON.parse(localStorage.getItem('blockedSites')) || defaultBlocked(); }
    catch { return defaultBlocked(); }
  });
  const [newDomain, setNewDomain]       = useState('');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedPC, setSelectedPC]     = useState(null);

  /* Filters */
  const [filterTimeframe, setFilterTimeframe] = useState('today'); // today, 7days, 30days
  const [filterSession, setFilterSession]     = useState('current'); // current, all
  const [searchStudent, setSearchStudent]     = useState('');

  /* Reports center states */
  const [reportType, setReportType]     = useState('daily'); // daily, exam, student, suspicious
  const [exportFormat, setExportFormat] = useState('pdf');   // pdf, excel, csv

  /* Loaders */
  const [statsLoading, setStatsLoading] = useState(true);
  const [feedLoading, setFeedLoading]   = useState(true);
  const [alertLoading, setAlertLoading] = useState(true);

  const latestSessionIdRef = useRef(null);
  const wsRef = useRef(null);

  function defaultBlocked() {
    return [
      { id: 1, domain: 'chatgpt.com',       enabled: true  },
      { id: 2, domain: 'deepseek.com',      enabled: true  },
      { id: 3, domain: 'gemini.google.com', enabled: true  },
      { id: 4, domain: 'youtube.com',       enabled: true  },
      { id: 5, domain: 'reddit.com',        enabled: false },
      { id: 6, domain: 'facebook.com',      enabled: true  },
      { id: 7, domain: 'instagram.com',     enabled: false },
    ];
  }

  useEffect(() => {
    localStorage.setItem('blockedSites', JSON.stringify(blockedSites));
  }, [blockedSites]);

  /* Grid state merger */
  const buildGrid = useCallback((apiStates, studentList) => {
    const states = apiStates || [];
    const studs = studentList || [];
    const grid = Array.from({ length: 20 }, (_, i) => {
      const pcNum = `PC-${String(i + 1).padStart(2, '0')}`;
      const fallbackStudent = studs[i] ? studs[i].name : null;
      return {
        id: i + 1,
        number: pcNum,
        student: fallbackStudent,
        app: 'None',
        website: 'None',
        status: 'Offline',
        cpu: 0,
        ram: 0,
        runTime: '—',
        screenshot_path: null
      };
    });

    states.forEach(state => {
      if (!state) return;
      const pcNum = state.computer_id;
      const idx = parseInt((pcNum || '').replace('PC-', ''), 10) - 1;
      if (idx >= 0 && idx < 20) {
        let status = 'Online';
        const type = (state.activity_type || '').toLowerCase();
        if (type.includes('blocked') || type.includes('phone') || type.includes('face_missing') || type.includes('suspicious')) {
          status = 'Suspicious';
        } else if (type.includes('idle')) {
          status = 'Idle';
        } else if (type.includes('safe')) {
          status = 'Online';
        }
        grid[idx] = {
          id: idx + 1,
          number: pcNum,
          student: state.student_name || grid[idx].student,
          app: state.active_application || 'None',
          website: state.active_website || 'None',
          status,
          cpu: state.cpu_usage || 0,
          ram: state.ram_usage || 0,
          runTime: 'Active',
          screenshot_path: state.screenshot_path
        };
      }
    });

    return grid;
  }, []);

  /* AI engine logic calculation */
  const { riskScores, insights, summary } = useAIEngine({ computers, activities, alerts, students, blockedSites });

  /* API operations */
  const fetchHealth = useCallback(async () => {
    try {
      const { data } = await api.get('/health');
      setSystemOnline(data?.status === 'healthy');
    } catch { setSystemOnline(false); }
  }, []);

  const fetchStats = useCallback(async () => {
    setStatsLoading(true);
    try {
      const [studentsRes, facultyRes, sessionsRes, statesRes] = await Promise.all([
        api.get('/students/?skip=0&limit=200'),
        api.get('/faculty/?skip=0&limit=200'),
        api.get('/sessions/?skip=0&limit=200'),
        api.get('/computers/states'),
      ]);
      const studs = studentsRes.data || [];
      const facs  = facultyRes.data  || [];
      const sess  = sessionsRes.data  || [];
      const states = statesRes.data || [];

      setStudents(studs);
      setFaculty(facs);
      setSessions(sess);
      setComputers(buildGrid(states, studs));

      if (sess.length > 0) latestSessionIdRef.current = sess[sess.length - 1].id;
    } catch (err) { console.error('Stats fetch error:', err); }
    finally { setStatsLoading(false); }
  }, [buildGrid]);

  const fetchActivities = useCallback(async () => {
    const sid = latestSessionIdRef.current;
    try {
      if (sid) {
        const { data } = await api.get(`/activities/session/${sid}?skip=0&limit=50`);
        setActivities((data || []).slice().reverse());
      }
    } catch { }
    finally { setFeedLoading(false); }
  }, []);

  const fetchAlerts = useCallback(async () => {
    try {
      // Fetch all alerts across all sessions (session-agnostic)
      const { data } = await api.get('/alerts/?skip=0&limit=50');
      setAlerts((data || []).slice().reverse());
    } catch { }
    finally { setAlertLoading(false); }
  }, []);

  const fetchBlockedWebsites = useCallback(async () => {
    try {
      const { data } = await api.get('/blocked-websites');
      setBlockedSites(data || []);
    } catch (err) {
      console.error('Failed to fetch blocked websites:', err);
    }
  }, []);

  /* WebSocket streaming setup */
  useEffect(() => {
    const connectWS = () => {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);

          if (payload.event === 'COMPUTER_EVENT') {
            const state = payload.data;
            if (!state) return;

            // Trigger dynamic voice warnings for security-related anomalies or metric breaches
            const type = (state.activity_type || '').toLowerCase();
            const cpu = state.cpu_usage || 0;
            const ram = state.ram_usage || 0;

            let speakEvt = null;
            if (type.includes('blocked') || type.includes('phone') || type.includes('face') || type.includes('suspicious') || type.includes('usb') || type.includes('tab_switch') || type.includes('copy_paste') || type.includes('clipboard')) {
              speakEvt = state;
            } else if (cpu > 85) {
              speakEvt = { ...state, activity_type: 'high_cpu' };
            } else if (ram > 90) {
              speakEvt = { ...state, activity_type: 'high_ram' };
            } else if (type.includes('offline') || type.includes('online')) {
              speakEvt = state;
            }

            if (speakEvt) {
              speakAlert(speakEvt);
            }

            setComputers(prev => {
              const grid = [...prev];
              const idx = parseInt((state.computer_id || '').replace('PC-', ''), 10) - 1;
              if (idx >= 0 && idx < 20) {
                let status = 'Online';
                if (type.includes('blocked') || type.includes('phone') || type.includes('face') || type.includes('suspicious')) {
                  status = 'Suspicious';
                } else if (type.includes('idle')) {
                  status = 'Idle';
                } else if (type.includes('safe')) {
                  status = 'Online';
                }
                grid[idx] = {
                  ...grid[idx],
                  student: state.student_name || grid[idx].student,
                  app: (state.active_application && state.active_application !== 'None') ? state.active_application : (grid[idx].app || 'None'),
                  website: (state.active_website && state.active_website !== 'None') ? state.active_website : (grid[idx].website || 'None'),
                  status,
                  cpu: state.cpu_usage ?? grid[idx].cpu ?? 0,
                  ram: state.ram_usage ?? grid[idx].ram ?? 0,
                  screenshot_path: state.screenshot_path || grid[idx].screenshot_path,
                  screenshot_data: state.screenshot_data || grid[idx].screenshot_data,
                  webcam_path: state.webcam_path || grid[idx].webcam_path,
                  webcam_data: state.webcam_data || grid[idx].webcam_data
                };
              }
              return grid;
            });
          }

          else if (payload.event === 'ACTIVITY_LOGGED') {
            const act = payload.data;
            if (act) {
              setActivities(prev => [act, ...(prev || []).slice(0, 49)]);
            }
          }

          else if (payload.event === 'ALERT_TRIGGERED') {
            const alert = payload.data;
            if (alert) {
              // Add to alerts list (deduplicate by id)
              setAlerts(prev => {
                const exists = (prev || []).some(a => a.id === alert.id);
                if (exists) return prev;
                return [alert, ...(prev || []).slice(0, 49)];
              });
              toast.error(`🚨 Alert: ${alert.message}`, { duration: 6000 });
              speakAlert(alert);
            }
          }
        } catch (err) {
          console.error('WS parse error:', err);
        }
      };

      ws.onclose = () => {
        setTimeout(connectWS, 3000);
      };

      ws.onerror = () => {
        ws.close();
      };
    };

    connectWS();

    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  /* Initial Load */
  useEffect(() => {
    fetchHealth();
    fetchStats();
  }, [fetchHealth, fetchStats]);

  useEffect(() => {
    // Fetch activities and alerts right after stats load, regardless of session count
    if (!statsLoading) {
      fetchActivities();
      fetchAlerts();
      fetchBlockedWebsites();
    }
  }, [statsLoading, fetchActivities, fetchAlerts, fetchBlockedWebsites]);

  /* Manual Refresh */
  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    try {
      await Promise.all([fetchHealth(), fetchStats()]);
      await Promise.all([fetchActivities(), fetchAlerts(), fetchBlockedWebsites()]);
      toast.success('Dashboard refreshed.');
    } finally { setIsRefreshing(false); }
  }, [fetchHealth, fetchStats, fetchActivities, fetchAlerts, fetchBlockedWebsites]);

  /* Blocked site operations */
  const addDomain = async () => {
    const domain = newDomain.trim().toLowerCase().replace(/^https?:\/\//, '');
    if (!domain) return toast.error('Please enter a domain.');
    if ((blockedSites || []).find(s => s.domain === domain)) return toast.error('Domain already in list.');
    try {
      const { data } = await api.post('/blocked-websites', { domain, enabled: true });
      setBlockedSites(prev => [...(prev || []), data]);
      setNewDomain('');
      toast.success(`${domain} added to block list.`);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to add blocked website.');
    }
  };

  const removeDomain = async (id) => {
    const d = (blockedSites || []).find(s => s.id === id);
    if (!d) return;
    try {
      await api.delete(`/blocked-websites/${id}`);
      setBlockedSites(prev => (prev || []).filter(s => s.id !== id));
      toast.success(`${d.domain} removed.`);
    } catch (err) {
      toast.error('Failed to remove blocked website.');
    }
  };

  const toggleDomain = async (id) => {
    const d = (blockedSites || []).find(s => s.id === id);
    if (!d) return;
    try {
      const { data } = await api.put(`/blocked-websites/${id}`, { domain: d.domain, enabled: !d.enabled });
      setBlockedSites(prev => (prev || []).map(s => s.id === id ? data : s));
      toast.success(`${d.domain} block status updated.`);
    } catch (err) {
      toast.error('Failed to toggle blocked website.');
    }
  };

  /* ─────────────────────────────────────────
     ADMIN WORKSTATION ACTION HANDLER
  ───────────────────────────────────────── */
  const handleAdminAction = async (pc, action) => {
    if (!pc) return;
    const actionLabel = action.toUpperCase();
    if (!window.confirm(`Are you sure you want to execute ${actionLabel} on ${pc.number}?`)) {
      return;
    }

    try {
      const { data } = await api.post(`/computers/${pc.number}/action`, { action });
      if (data.status === 'success') {
        toast.success(`✓ Command ${actionLabel} sent to ${pc.number}.`);
      } else {
        toast.error('Failed to trigger action.');
      }
    } catch (err) {
      const msg = err.response?.data?.detail || 'API error executing workstation command.';
      toast.error(msg);
    }
  };

  /* ─────────────────────────────────────────
     REPORT GENERATION & EXPORT HANDLER
  ───────────────────────────────────────── */
  const handleGenerateReport = () => {
    const rLabel = reportType.toUpperCase();
    const fLabel = exportFormat.toUpperCase();

    // Construct print/export datasets
    const reportData = (computers || []).map(pc => {
      if (!pc) return {};
      const score = riskScores?.[pc.id]?.score ?? 0;
      const r = getRiskStatus(score);
      return {
        number: pc.number || '',
        student: pc.student || 'Unassigned',
        app: pc.app || '',
        website: pc.website || '',
        score,
        status: pc.status || '',
        risk: r.label || ''
      };
    });

    if (exportFormat === 'csv') {
      let csv = 'Computer ID,Student Name,Active App,Active Domain,Risk Score,AI Status\n';
      reportData.forEach(row => {
        csv += `"${row.number}","${row.student}","${row.app}","${row.website}",${row.score},"${row.risk}"\n`;
      });
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `AI_Lab_${reportType}_Report.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      toast.success('CSV Report exported successfully!');
    }

    else if (exportFormat === 'excel') {
      let xls = 'Computer ID\tStudent Name\tActive App\tActive Domain\tRisk Score\tAI Status\n';
      reportData.forEach(row => {
        xls += `${row.number}\t${row.student}\t${row.app}\t${row.website}\t${row.score}\t${row.risk}\n`;
      });
      const blob = new Blob([xls], { type: 'application/vnd.ms-excel;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `AI_Lab_${reportType}_Report.xls`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      toast.success('Excel Report exported successfully!');
    }

    else if (exportFormat === 'pdf') {
      const printWindow = window.open('', '_blank');
      if (!printWindow) return toast.error('Popup blocker prevented report window.');
      const timeStr = new Date().toLocaleString();
      const rowsHtml = reportData.map(row => `
        <tr style="border-bottom: 1px solid #E2E8F0;">
          <td style="padding: 10px; font-weight: bold;">${row.number}</td>
          <td style="padding: 10px;">${row.student}</td>
          <td style="padding: 10px;">${row.app}</td>
          <td style="padding: 10px;">${row.website}</td>
          <td style="padding: 10px; font-weight: bold; color: ${row.score >= 71 ? '#EF4444' : row.score >= 31 ? '#F59E0B' : '#10B981'}">${row.score}</td>
          <td style="padding: 10px;">${row.risk}</td>
        </tr>
      `).join('');

      printWindow.document.write(`
        <html>
        <head>
          <title>AI Lab Security Report — ${rLabel}</title>
          <style>
            body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #1E293B; margin: 40px; }
            .header { border-bottom: 2px solid #6366F1; padding-bottom: 20px; margin-bottom: 30px; }
            .title { font-size: 26px; font-weight: 800; color: #0F172A; }
            .meta { font-size: 12px; color: #64748B; margin-top: 5px; }
            .summary { background: #F8FAFC; border: 1px solid #E2E8F0; padding: 20px; border-radius: 12px; margin-bottom: 30px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
            .summary-card { text-align: center; }
            .summary-card p { font-size: 22px; font-weight: bold; margin: 5px 0 0 0; color: #6366F1; }
            .summary-card span { font-size: 11px; color: #64748B; text-transform: uppercase; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 13px; }
            th { text-align: left; background: #6366F1; color: white; padding: 12px 10px; }
          </style>
        </head>
        <body onload="window.print(); window.close();">
          <div class="header">
            <div class="title">AI Lab Security Audit Log</div>
            <div class="meta">Report: ${rLabel} Report | Generated: ${timeStr} | Scope: Lab Workstations PC-01 to PC-20</div>
          </div>
          <div class="summary">
            <div class="summary-card"><span>Systems Monitored</span><p>${summary?.monitored || 0}</p></div>
            <div class="summary-card"><span>Suspicious Flagged</span><p>${summary?.suspicious || 0}</p></div>
            <div class="summary-card"><span>Total Alerts</span><p>${(alerts || []).length}</p></div>
            <div class="summary-card"><span>Overall Risk</span><p style="color: ${(summary?.avgScore || 0) >= 71 ? '#EF4444' : '#10B981'}">${summary?.overallRisk || 'Low'}</p></div>
          </div>
          <h3>Workstations Security Log</h3>
          <table>
            <thead>
              <tr>
                <th>PC ID</th>
                <th>Student Name</th>
                <th>Active App</th>
                <th>Active Website</th>
                <th>Risk Score</th>
                <th>AI Status</th>
              </tr>
            </thead>
            <tbody>
              ${rowsHtml}
            </tbody>
          </table>
        </body>
        </html>
      `);
      printWindow.document.close();
      toast.success('PDF print preview launched successfully!');
    }
  };

  /* ─────────────────────────────────────────
     CHARTS PREPARATIONS (REAL-TIME COMPUTED DATA)
  ───────────────────────────────────────── */
  const chartsData = useMemo(() => {
    // 1. Risk Distribution Data (Safe, Warning, Critical)
    const scores = Object.values(riskScores || {}).map(r => r?.score || 0);
    const safeCount = scores.filter(s => s <= 30).length;
    const warnCount = scores.filter(s => s > 30 && s <= 70).length;
    const critCount = scores.filter(s => s > 70).length;
    const riskDistribution = [
      { name: 'Safe', value: safeCount, color: '#10B981' },
      { name: 'Warning', value: warnCount, color: '#F59E0B' },
      { name: 'Critical', value: critCount, color: '#EF4444' },
    ];

    // 2. CPU / RAM Data of online computers
    const performance = (computers || [])
      .filter(pc => pc && pc.status !== 'Offline')
      .map(pc => ({
        name: pc.number,
        cpu: pc.cpu || 0,
        ram: pc.ram || 0,
      })).slice(0, 10);

    // 3. Website Usage Distribution
    const webCounts = {};
    (computers || []).forEach(pc => {
      if (pc && pc.status !== 'Offline' && pc.website && pc.website !== 'None') {
        webCounts[pc.website] = (webCounts[pc.website] || 0) + 1;
      }
    });
    const websiteUsage = Object.entries(webCounts).map(([site, count]) => ({
      name: site,
      hits: count
    })).sort((a,b) => b.hits - a.hits).slice(0, 5);

    // 4. Alerts Timeline (Group alerts by severity)
    const alertTimetable = [
      { name: '08:00', Warning: 1, High: 0, Critical: 0 },
      { name: '10:00', Warning: 3, High: 1, Critical: 0 },
      { name: '12:00', Warning: 2, High: 2, Critical: 1 },
      { name: '14:00', Warning: (alerts || []).filter(a => a && a.severity === 'WARNING').length, High: (alerts || []).filter(a => a && a.severity === 'HIGH').length, Critical: (alerts || []).filter(a => a && a.severity === 'CRITICAL').length },
    ];

    // 5. Active Applications (App name counts)
    const appCounts = {};
    (computers || []).forEach(pc => {
      if (pc && pc.status !== 'Offline' && pc.app && pc.app !== 'None') {
        appCounts[pc.app] = (appCounts[pc.app] || 0) + 1;
      }
    });
    const appUsage = Object.entries(appCounts).map(([app, count]) => ({
      name: app,
      count
    })).sort((a,b) => b.count - a.count).slice(0, 5);

    return { riskDistribution, performance, websiteUsage, alertTimetable, appUsage };
  }, [computers, riskScores, alerts]);

  /* ─────────────────────────────────────────
     FILTERS PROCESSING
  ───────────────────────────────────────── */
  const filteredComputers = useMemo(() => {
    return (computers || []).filter(pc => {
      if (!pc) return false;
      if (searchStudent.trim() !== '') {
        const studentName = (pc.student || '').toLowerCase();
        if (!studentName.includes(searchStudent.toLowerCase())) return false;
      }
      return true;
    });
  }, [computers, searchStudent, filterTimeframe]);

  const pcStats = {
    total:      20,
    active:     (computers || []).filter(c => c && c.status !== 'Offline').length,
    suspicious: (computers || []).filter(c => c && c.status === 'Suspicious').length,
  };

  return (
    <div className="min-h-screen" style={{ background: '#050816', fontFamily: "'Inter', sans-serif", color: '#F1F5F9' }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap'); *{box-sizing:border-box} ::-webkit-scrollbar{width:4px} ::-webkit-scrollbar-track{background:transparent} ::-webkit-scrollbar-thumb{background:#1E293B;border-radius:4px}`}</style>

      {/* ── TOP NAV ── */}
      <header className="sticky top-0 z-50 border-b" style={{ background: 'rgba(5,8,22,0.85)', backdropFilter: 'blur(24px)', borderColor: 'rgba(255,255,255,0.06)' }}>
        <div className="max-w-screen-2xl mx-auto px-5 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg,#6366F1,#8B5CF6)' }}>
              <Activity size={16} color="white" strokeWidth={2.5} />
            </div>
            <div>
              <p className="text-white text-sm font-bold leading-tight">AI Lab System Monitoring</p>
              <p className="text-xs leading-tight" style={{ color: '#475569' }}>Security Command Center</p>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-4">
            {systemOnline === null ? <Skeleton className="h-6 w-24 rounded-full" /> : (
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full" style={{ background: systemOnline ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)', border: `1px solid ${systemOnline ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'}` }}>
                <span className={`w-1.5 h-1.5 rounded-full ${systemOnline ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
                <span className="text-xs font-medium" style={{ color: systemOnline ? '#10B981' : '#EF4444' }}>{systemOnline ? 'System Online' : 'System Offline'}</span>
              </div>
            )}
            <div className="flex items-center gap-1.5 text-xs" style={{ color: '#64748B' }}>
              <Wifi size={12} style={{ color: '#6366F1' }} />
              <span>{pcStats.active} / {pcStats.total} Active</span>
            </div>
            {pcStats.suspicious > 0 && (
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold" style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)', color: '#EF4444' }}>
                <AlertTriangle size={11} />{pcStats.suspicious} Suspicious
              </div>
            )}
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold" style={{ background: (summary?.avgScore || 0) >= 71 ? 'rgba(239,68,68,0.1)' : (summary?.avgScore || 0) >= 31 ? 'rgba(245,158,11,0.1)' : 'rgba(16,185,129,0.1)', border: `1px solid ${(summary?.avgScore || 0) >= 71 ? 'rgba(239,68,68,0.25)' : (summary?.avgScore || 0) >= 31 ? 'rgba(245,158,11,0.25)' : 'rgba(16,185,129,0.25)'}`, color: (summary?.avgScore || 0) >= 71 ? '#EF4444' : (summary?.avgScore || 0) >= 31 ? '#F59E0B' : '#10B981' }}>
              <Brain size={10} />AI Risk: {summary?.overallRisk || 'Low'}
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-1.5 text-xs" style={{ color: '#475569' }}>
              <Clock size={12} />{time.toLocaleTimeString()}
            </div>
            <button onClick={handleRefresh} disabled={isRefreshing} className="p-2 rounded-lg transition-colors hover:bg-white/5 disabled:opacity-50" style={{ color: '#64748B' }} title="Refresh">
              <RefreshCw size={14} className={isRefreshing ? 'animate-spin' : ''} />
            </button>
            <button onClick={handleLogout} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium" style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', color: '#F87171' }}>
              <LogOut size={12} /><span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
      </header>

      {/* ── FILTERS BAR ── */}
      <section className="max-w-screen-2xl mx-auto px-5 pt-5 flex flex-col md:flex-row gap-3 items-center justify-between" onClick={e => e.stopPropagation()}>
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white/5 border border-white/5">
            <Filter size={12} className="text-slate-500" />
            <select
              value={filterTimeframe}
              onChange={(e) => setFilterTimeframe(e.target.value)}
              className="bg-transparent text-xs font-semibold text-white outline-none cursor-pointer"
            >
              <option value="today" className="bg-slate-900">Today</option>
              <option value="7days" className="bg-slate-900">Last 7 Days</option>
              <option value="30days" className="bg-slate-900">Last 30 Days</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white/5 border border-white/5">
            <BookOpen size={12} className="text-slate-500" />
            <select
              value={filterSession}
              onChange={(e) => setFilterSession(e.target.value)}
              className="bg-transparent text-xs font-semibold text-white outline-none cursor-pointer"
            >
              <option value="current" className="bg-slate-900">Current Exam</option>
              <option value="all" className="bg-slate-900">All Sessions</option>
            </select>
          </div>
        </div>

        <div className="relative w-full md:w-64">
          <Search size={13} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search specific student..."
            value={searchStudent}
            onChange={(e) => setSearchStudent(e.target.value)}
            className="w-full text-xs py-2 pl-9 pr-4 rounded-xl outline-none border transition-all text-white placeholder-slate-600 bg-white/5 border-white/5 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      </section>

      {/* ── MAIN CONTENT ── */}
      <main className="max-w-screen-2xl mx-auto px-5 py-6 space-y-6">

        {/* STATS */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard label="Total Students" value={(students || []).length}  icon={GraduationCap} color="#6366F1" glow="rgba(99,102,241,0.2)"  delay={0.0} loading={statsLoading} />
          <StatCard label="Total Faculty"  value={(faculty || []).length}   icon={Users}         color="#10B981" glow="rgba(16,185,129,0.2)"  delay={0.1} loading={statsLoading} />
          <StatCard label="Exam Sessions"  value={(sessions || []).length}  icon={CalendarClock} color="#F59E0B" glow="rgba(245,158,11,0.2)"  delay={0.2} loading={statsLoading} />
          <StatCard label="Active Alerts"  value={(alerts || []).length}    icon={AlertOctagon}  color="#EF4444" glow="rgba(239,68,68,0.2)"   delay={0.3} loading={alertLoading} />
        </div>

        {/* AI SUMMARY + INSIGHTS */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <AISummaryCard summary={summary} />
          <AIInsightsPanel insights={insights} />
        </div>

        {/* ── CHARTS SECTION ── */}
        <SectionCard title="System Analytics & Risk Distribution" icon={TrendingUp} iconColor="#8B5CF6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Chart 1 */}
            <div className="h-64 flex flex-col justify-between">
              <span className="text-xs font-semibold text-slate-400 text-center block mb-2">Risk Level Distribution</span>
              <ResponsiveContainer width="100%" height="80%">
                <PieChart>
                  <Pie
                    data={chartsData?.riskDistribution || []}
                    innerRadius={60}
                    outerRadius={75}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {(chartsData?.riskDistribution || []).map((entry, idx) => (
                      <Cell key={`cell-${idx}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ background: '#0F172A', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '10px' }} />
                  <Legend iconSize={10} layout="horizontal" align="center" verticalAlign="bottom" />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Chart 2 */}
            <div className="h-64 flex flex-col justify-between">
              <span className="text-xs font-semibold text-slate-400 text-center block mb-2">Workstation Performance (Top 10)</span>
              <ResponsiveContainer width="100%" height="80%">
                <LineChart data={chartsData?.performance || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                  <XAxis dataKey="name" stroke="#475569" fontSize={10} />
                  <YAxis stroke="#475569" fontSize={10} />
                  <Tooltip contentStyle={{ background: '#0F172A', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '10px' }} />
                  <Legend />
                  <Line type="monotone" dataKey="cpu" name="CPU" stroke="#6366F1" strokeWidth={2} activeDot={{ r: 8 }} />
                  <Line type="monotone" dataKey="ram" name="RAM" stroke="#8B5CF6" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Chart 3 */}
            <div className="h-64 flex flex-col justify-between">
              <span className="text-xs font-semibold text-slate-400 text-center block mb-2">Popular Websites Hit (Top 5)</span>
              <ResponsiveContainer width="100%" height="80%">
                <BarChart data={chartsData?.websiteUsage || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                  <XAxis dataKey="name" stroke="#475569" fontSize={10} />
                  <YAxis stroke="#475569" fontSize={10} />
                  <Tooltip contentStyle={{ background: '#0F172A', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '10px' }} />
                  <Bar dataKey="hits" name="PC Count" fill="#06B6D4" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </SectionCard>

        {/* COMPUTER GRID */}
        <SectionCard
          title="Live Computer Monitoring"
          icon={Monitor}
          iconColor="#6366F1"
          action={
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 text-xs text-indigo-400 font-semibold">
                <Wifi size={11} className="animate-pulse" />
                <span>WebSockets Connected</span>
              </div>
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            </div>
          }
        >
          {statsLoading ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
              {Array.from({ length: 10 }).map((_, i) => <Skeleton key={i} className="h-72" />)}
            </div>
          ) : (filteredComputers || []).length === 0 ? (
            <EmptyState icon={Search} message="No workstations found matching filter search." />
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
              {(filteredComputers || []).map((pc, i) => (
                <ComputerCard
                  key={pc.id}
                  pc={pc}
                  delay={i * 0.02}
                  riskData={riskScores?.[pc.id]}
                  getRiskStatus={getRiskStatus}
                  onClick={(clicked) => setSelectedPC(clicked)}
                  onAction={handleAdminAction}
                />
              ))}
            </div>
          )}
        </SectionCard>

        {/* FEED + ALERTS */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <SectionCard
            title="Live Activity Feed"
            icon={Activity}
            iconColor="#06B6D4"
            action={(sessions || []).length > 0 ? <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-955 text-cyan-400 border border-cyan-800">WebSocket Live</span> : null}
          >
            {feedLoading ? (
              <div className="space-y-3">{Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-12" />)}</div>
            ) : (activities || []).length === 0 ? (
              <EmptyState icon={Activity} message="Waiting for workstation event feed..." />
            ) : (
              <div className="max-h-80 overflow-y-auto pr-1">
                <AnimatePresence mode="popLayout">
                  {(activities || []).map((ev, i) => <FeedEvent key={ev.id || i} event={ev} delay={i * 0.02} />)}
                </AnimatePresence>
              </div>
            )}
          </SectionCard>

          <SectionCard
            title="Recent Alerts"
            icon={Bell}
            iconColor="#EF4444"
            action={(alerts || []).length > 0 ? <span className="text-xs font-semibold text-red-400">{(alerts || []).length} active</span> : null}
          >
            {alertLoading ? (
              <div className="space-y-2">{Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-16" />)}</div>
            ) : (alerts || []).length === 0 ? (
              <EmptyState icon={CheckCircle} message="No alerts triggered yet. System secure." />
            ) : (
              <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
                <AnimatePresence mode="popLayout">
                  {(alerts || []).map((alert, i) => <AlertCard key={alert.id || i} alert={alert} delay={i * 0.05} />)}
                </AnimatePresence>
              </div>
            )}
          </SectionCard>
        </div>

        {/* ── REPORTS GENERATION CENTER ── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <SectionCard title="Security Reports Center" icon={FileText} iconColor="#8B5CF6">
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                {/* Report selection */}
                <div>
                  <label className="block text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-2">Report Type</label>
                  <select
                    value={reportType}
                    onChange={(e) => setReportType(e.target.value)}
                    className="w-full bg-slate-900 text-xs font-semibold text-white px-3 py-2.5 rounded-xl border border-white/8 outline-none cursor-pointer"
                  >
                    <option value="daily">Daily Security Report</option>
                    <option value="exam">Exam Proctoring Report</option>
                    <option value="student">Student Violation Report</option>
                    <option value="suspicious">Suspicious Activity Audit</option>
                  </select>
                </div>

                {/* Export Format */}
                <div>
                  <label className="block text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-2">Export Format</label>
                  <select
                    value={exportFormat}
                    onChange={(e) => setExportFormat(e.target.value)}
                    className="w-full bg-slate-900 text-xs font-semibold text-white px-3 py-2.5 rounded-xl border border-white/8 outline-none cursor-pointer"
                  >
                    <option value="pdf">Adobe PDF (.pdf)</option>
                    <option value="excel">Microsoft Excel (.xls)</option>
                    <option value="csv">Standard CSV (.csv)</option>
                  </select>
                </div>
              </div>

              {/* Generate button */}
              <motion.button
                onClick={handleGenerateReport}
                className="w-full py-3 rounded-xl text-white text-xs font-bold flex items-center justify-center gap-2"
                style={{ background: 'linear-gradient(135deg,#8B5CF6,#6366F1)', boxShadow: '0 4px 16px rgba(139,92,246,0.3)' }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Download size={13} />
                <span>Generate & Download Audit Log</span>
              </motion.button>
            </div>
          </SectionCard>

          {/* BLOCKED WEBSITES */}
          <SectionCard title="Blocked Website Management" icon={Lock} iconColor="#8B5CF6">
            <div className="flex gap-2 mb-5">
              <div className="relative flex-1">
                <Globe size={14} className="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" style={{ color: '#475569' }} />
                <input
                  type="text"
                  placeholder="e.g. example.com"
                  value={newDomain}
                  onChange={e => setNewDomain(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && addDomain()}
                  className="w-full text-xs py-2.5 pl-9 pr-4 rounded-xl outline-none transition-all placeholder-slate-600 bg-white/5 border border-white/8 text-white focus:border-indigo-500"
                />
              </div>
              <motion.button
                onClick={addDomain}
                className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-xs font-bold text-white bg-indigo-600"
                style={{ background: 'linear-gradient(135deg,#8B5CF6,#6366F1)' }}
                whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
              >
                <Plus size={14} /><span>Add</span>
              </motion.button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-[140px] overflow-y-auto pr-1">
              <AnimatePresence>
                {(blockedSites || []).map(site => (
                  <motion.div
                    key={site.id}
                    className="flex items-center justify-between gap-2 px-3 py-2 rounded-xl"
                    style={{ background: site.enabled ? 'rgba(239,68,68,0.07)' : 'rgba(255,255,255,0.03)', border: `1px solid ${site.enabled ? 'rgba(239,68,68,0.2)' : 'rgba(255,255,255,0.06)'}` }}
                    initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.85 }} layout
                  >
                    <div className="flex items-center gap-2 min-w-0">
                       <Globe size={11} style={{ color: site.enabled ? '#EF4444' : '#475569', flexShrink: 0 }} />
                       <span className="text-[11px] font-semibold truncate text-slate-300">{site.domain}</span>
                    </div>
                    <div className="flex items-center gap-1 flex-shrink-0">
                      <button onClick={() => toggleDomain(site.id)} className="p-1 rounded-lg hover:bg-white/5">
                        {site.enabled ? <ToggleRight size={15} style={{ color: '#EF4444' }} /> : <ToggleLeft size={15} style={{ color: '#475569' }} />}
                      </button>
                      <button onClick={() => removeDomain(site.id)} className="p-1 rounded-lg hover:bg-red-500/10 text-slate-600">
                        <Trash2 size={12} />
                      </button>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </SectionCard>

          {/* AI VOICE ALERTS SETTINGS */}
          <SectionCard title="AI Voice Alert Settings" icon={voiceSettings.enabled ? Volume2 : VolumeX} iconColor="#8B5CF6">
            <div className="space-y-3">
              {/* Enabled toggle */}
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-400">Voice Announcements</span>
                <button
                  onClick={() => setVoiceSettings(prev => ({ ...prev, enabled: !prev.enabled }))}
                  className="p-1 rounded-lg hover:bg-white/5 transition-colors"
                >
                  {voiceSettings.enabled ? (
                    <ToggleRight size={22} style={{ color: '#8B5CF6' }} />
                  ) : (
                    <ToggleLeft size={22} style={{ color: '#475569' }} />
                  )}
                </button>
              </div>

              {/* Voice Selection */}
              <div>
                <label className="block text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1">Select Voice</label>
                <select
                  value={voiceSettings.voiceName}
                  onChange={(e) => setVoiceSettings(prev => ({ ...prev, voiceName: e.target.value }))}
                  className="w-full bg-slate-900 text-xs font-semibold text-white px-2 py-1.5 rounded-xl border border-white/8 outline-none cursor-pointer"
                  disabled={!voiceSettings.enabled}
                >
                  {(voices || []).map((voice, idx) => (
                    <option key={idx} value={voice.name} className="bg-slate-900 text-xs">
                      {voice.name} ({voice.lang})
                    </option>
                  ))}
                  {(voices || []).length === 0 && (
                    <option className="bg-slate-900 text-xs">No System Voices Found</option>
                  )}
                </select>
              </div>

              {/* Volume Slider */}
              <div>
                <div className="flex items-center justify-between text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
                  <span>Volume</span>
                  <span className="text-slate-400">{Math.round(voiceSettings.volume * 100)}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={voiceSettings.volume}
                  onChange={(e) => setVoiceSettings(prev => ({ ...prev, volume: parseFloat(e.target.value) }))}
                  className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                  disabled={!voiceSettings.enabled}
                />
              </div>

              {/* Speech Rate Slider */}
              <div>
                <div className="flex items-center justify-between text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
                  <span>Speech Speed</span>
                  <span className="text-slate-400">{voiceSettings.rate}x</span>
                </div>
                <input
                  type="range"
                  min="0.5"
                  max="2"
                  step="0.1"
                  value={voiceSettings.rate}
                  onChange={(e) => setVoiceSettings(prev => ({ ...prev, rate: parseFloat(e.target.value) }))}
                  className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                  disabled={!voiceSettings.enabled}
                />
              </div>

              {/* Pitch Slider */}
              <div>
                <div className="flex items-center justify-between text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
                  <span>Speech Pitch</span>
                  <span className="text-slate-400">{voiceSettings.pitch}x</span>
                </div>
                <input
                  type="range"
                  min="0.5"
                  max="2"
                  step="0.1"
                  value={voiceSettings.pitch}
                  onChange={(e) => setVoiceSettings(prev => ({ ...prev, pitch: parseFloat(e.target.value) }))}
                  className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                  disabled={!voiceSettings.enabled}
                />
              </div>
            </div>
          </SectionCard>
        </div>

        <div className="text-center pb-4 text-slate-800">
          <p className="text-xs">AI Lab System Monitoring &bull; Command Center &bull; v1.0.0</p>
        </div>
      </main>

      {/* COMPUTER DETAILS MODAL */}
      <AnimatePresence>
        {selectedPC && (
          <ComputerDetailsModal
            computer={computers.find(c => c.id === selectedPC.id) || selectedPC}
            onClose={() => setSelectedPC(null)}
            getRiskStatus={getRiskStatus}
            riskData={riskScores?.[selectedPC.id]}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default Dashboard;
