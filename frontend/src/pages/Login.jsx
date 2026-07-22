import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';
import { Eye, EyeOff, User, Lock, Shield, Activity, ArrowRight, Loader2, Cpu, Wifi, Brain } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { authService } from '../services/authService';

const fadeUp = {
  hidden: { opacity: 0, y: 28 },
  visible: (i = 0) => ({
    opacity: 1, y: 0,
    transition: { delay: i * 0.1, duration: 0.6, ease: [0.16, 1, 0.3, 1] },
  }),
};

const Blob = ({ style, color }) => (
  <motion.div
    className="absolute rounded-full pointer-events-none"
    style={{ background: color, filter: 'blur(90px)', ...style }}
    animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.5, 0.3] }}
    transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
  />
);

const features = [
  { icon: Cpu, label: 'Real-time Monitoring', desc: 'Live computer stats across every lab workstation.' },
  { icon: Brain, label: 'AI Risk Detection', desc: 'Confidence-weighted behavioral anomaly scoring.' },
  { icon: Wifi, label: 'WebSocket Streams', desc: 'Sub-50ms live data push to the dashboard.' },
  { icon: Shield, label: 'Secure & Encrypted', desc: 'JWT + Argon2 authentication with role-based access.' },
];

const NetworkSVG = () => (
  <svg viewBox="0 0 500 400" className="absolute inset-0 w-full h-full opacity-[0.07]" xmlns="http://www.w3.org/2000/svg">
    {[[60,80],[190,55],[320,115],[440,72],[95,205],[245,215],[385,195],[155,325],[315,345],[455,295]].map(([cx,cy],i) => (
      <g key={i}>
        <circle cx={cx} cy={cy} r="5" fill="#6366F1" opacity="0.9"/>
        <circle cx={cx} cy={cy} r="14" fill="#6366F1" opacity="0.12"/>
      </g>
    ))}
    {[[60,80,190,55],[190,55,320,115],[320,115,440,72],[60,80,95,205],[190,55,245,215],
      [320,115,385,195],[95,205,245,215],[245,215,385,195],[95,205,155,325],
      [245,215,315,345],[385,195,455,295],[155,325,315,345]].map(([x1,y1,x2,y2],i) => (
      <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="#6366F1" strokeWidth="0.8" strokeOpacity="0.45"/>
    ))}
  </svg>
);

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm({ mode: 'onTouched' });

  const onSubmit = async (data) => {
    setIsLoading(true);
    try {
      const response = await authService.login({ username: data.username, password: data.password });
      login(response.access_token);
      toast.success('Access granted. Welcome back.');
      navigate('/');
    } catch (error) {
      const message = error?.response?.data?.detail || 'Invalid credentials. Access denied.';
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const inputStyle = (hasError) => ({
    background: 'rgba(255,255,255,0.05)',
    border: `1px solid ${hasError ? 'rgba(248,113,113,0.5)' : 'rgba(255,255,255,0.08)'}`,
    color: '#F1F5F9',
    boxShadow: hasError ? '0 0 0 3px rgba(248,113,113,0.1)' : 'none',
  });

  return (
    <div className="min-h-screen w-full flex overflow-hidden relative" style={{ background: '#050816', fontFamily: "'Inter', sans-serif" }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');* { box-sizing: border-box; }`}</style>

      {/* ── LEFT PANEL ── */}
      <div className="hidden lg:flex lg:w-[52%] relative flex-col justify-center px-16 xl:px-24 py-16 overflow-hidden">
        <Blob style={{ width: 550, height: 550, top: -180, left: -150 }} color="rgba(99,102,241,0.2)" />
        <Blob style={{ width: 350, height: 350, bottom: -100, right: -60 }} color="rgba(139,92,246,0.15)" />
        <Blob style={{ width: 250, height: 250, top: '45%', left: '35%' }} color="rgba(6,182,212,0.1)" />
        <NetworkSVG />

        <div className="relative z-10 max-w-xl">
          <motion.div className="flex items-center gap-3 mb-14" variants={fadeUp} initial="hidden" animate="visible" custom={0}>
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg,#6366F1,#8B5CF6)' }}>
              <Activity size={20} color="white" strokeWidth={2.5}/>
            </div>
            <span className="text-white font-semibold text-sm tracking-wide">AI Lab Monitor</span>
          </motion.div>

          <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={1}>
            <h1 className="font-black leading-[1.0] mb-2" style={{ fontSize: 'clamp(50px,5vw,74px)', letterSpacing: '-2px' }}>
              <span className="text-white block">Monitor.</span>
              <span className="block" style={{ background: 'linear-gradient(90deg,#6366F1,#8B5CF6,#06B6D4)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent' }}>Analyze.</span>
              <span className="text-white block">Protect.</span>
            </h1>
          </motion.div>

          <motion.p className="text-base leading-relaxed mb-12" style={{ color: '#94A3B8', maxWidth: 400 }} variants={fadeUp} initial="hidden" animate="visible" custom={2}>
            The AI-powered proctoring platform delivering real-time behavioral analysis, anomaly detection, and instant alerting across every lab workstation.
          </motion.p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {features.map(({ icon: Icon, label, desc }, i) => (
              <motion.div
                key={label}
                className="relative rounded-2xl p-4 border border-white/5"
                style={{ background: 'rgba(255,255,255,0.04)', backdropFilter: 'blur(12px)' }}
                variants={fadeUp} initial="hidden" animate="visible" custom={3 + i * 0.4}
                whileHover={{ y: -4, borderColor: 'rgba(99,102,241,0.3)', boxShadow: '0 16px 40px rgba(99,102,241,0.15)' }}
                transition={{ duration: 0.2 }}
              >
                <div className="w-8 h-8 rounded-lg flex items-center justify-center mb-3" style={{ background: 'linear-gradient(135deg,#6366F1,#8B5CF6)', boxShadow: '0 4px 16px rgba(99,102,241,0.3)' }}>
                  <Icon size={15} color="white" strokeWidth={2.5}/>
                </div>
                <p className="text-white text-xs font-semibold mb-0.5">{label}</p>
                <p className="text-xs leading-snug" style={{ color: '#64748B' }}>{desc}</p>
              </motion.div>
            ))}
          </div>

          <motion.div className="flex items-center gap-8 mt-10" variants={fadeUp} initial="hidden" animate="visible" custom={6}>
            {[['99.9%','Uptime'],['< 50ms','Latency'],['24/7','Monitoring']].map(([val,lbl]) => (
              <div key={lbl}>
                <p className="text-white font-bold text-sm">{val}</p>
                <p className="text-xs" style={{ color: '#475569' }}>{lbl}</p>
              </div>
            ))}
          </motion.div>
        </div>
      </div>

      {/* ── RIGHT PANEL ── */}
      <div className="flex-1 flex items-center justify-center px-4 sm:px-8 py-16 relative">
        <Blob style={{ width: 400, height: 400, top: '10%', right: '-5%' }} color="rgba(99,102,241,0.12)" />
        <Blob style={{ width: 300, height: 300, bottom: '5%', left: '5%' }} color="rgba(6,182,212,0.08)" />

        <motion.div className="w-full max-w-sm relative z-10" variants={fadeUp} initial="hidden" animate="visible" custom={1}>
          <motion.div
            className="relative rounded-3xl p-8 sm:p-10"
            style={{ background: 'rgba(255,255,255,0.06)', backdropFilter: 'blur(32px)', border: '1px solid rgba(255,255,255,0.1)', boxShadow: '0 32px 80px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.1)' }}
            animate={{ y: [0, -6, 0] }}
            transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
          >
            <div className="absolute top-0 left-8 right-8 h-px rounded-full" style={{ background: 'linear-gradient(90deg,transparent,rgba(99,102,241,0.8),rgba(6,182,212,0.6),transparent)' }}/>

            <motion.div className="flex flex-col items-center mb-8" variants={fadeUp} initial="hidden" animate="visible" custom={2}>
              <div className="w-14 h-14 rounded-2xl flex items-center justify-center mb-4" style={{ background: 'linear-gradient(135deg,#6366F1,#8B5CF6)', boxShadow: '0 8px 32px rgba(99,102,241,0.4)' }}>
                <Shield size={26} color="white" strokeWidth={2}/>
              </div>
              <h2 className="text-white font-bold text-xl tracking-tight">Welcome back</h2>
              <p className="text-sm mt-1" style={{ color: '#64748B' }}>AI Lab Monitoring Portal</p>
            </motion.div>

            {/* Hint badge */}
            <motion.div
              className="mb-5 px-3 py-2 rounded-xl text-center text-xs"
              style={{ background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)', color: '#94A3B8' }}
              variants={fadeUp} initial="hidden" animate="visible" custom={2.5}
            >
              Demo: <span className="text-indigo-400 font-semibold">labadmin</span> / <span className="text-indigo-400 font-semibold">admin123</span>
            </motion.div>

            <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
              {/* Username */}
              <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={3}>
                <label htmlFor="login-username" className="block text-xs font-semibold mb-1.5 uppercase tracking-wider" style={{ color: '#94A3B8' }}>Username</label>
                <div className="relative">
                  <User size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" style={{ color: errors.username ? '#F87171' : '#475569' }}/>
                  <input
                    id="login-username"
                    type="text"
                    autoComplete="username"
                    placeholder="labadmin"
                    disabled={isLoading}
                    {...register('username', { required: 'Username is required.' })}
                    className="w-full text-sm py-3 pl-10 pr-4 rounded-xl outline-none transition-all disabled:opacity-50 disabled:cursor-not-allowed placeholder-slate-600"
                    style={inputStyle(!!errors.username)}
                    onFocus={e => { e.target.style.border = '1px solid rgba(99,102,241,0.6)'; e.target.style.boxShadow = '0 0 0 3px rgba(99,102,241,0.12)'; }}
                    onBlur={e => { if (!errors.username) { e.target.style.border = '1px solid rgba(255,255,255,0.08)'; e.target.style.boxShadow = 'none'; } }}
                  />
                </div>
                <AnimatePresence>
                  {errors.username && (
                    <motion.p className="mt-1.5 text-xs" style={{ color: '#F87171' }} initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                      {errors.username.message}
                    </motion.p>
                  )}
                </AnimatePresence>
              </motion.div>

              {/* Password */}
              <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={4}>
                <label htmlFor="login-password" className="block text-xs font-semibold mb-1.5 uppercase tracking-wider" style={{ color: '#94A3B8' }}>Password</label>
                <div className="relative">
                  <Lock size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" style={{ color: errors.password ? '#F87171' : '#475569' }}/>
                  <input
                    id="login-password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    placeholder="••••••••"
                    disabled={isLoading}
                    {...register('password', { required: 'Password is required.', minLength: { value: 6, message: 'Minimum 6 characters.' } })}
                    className="w-full text-sm py-3 pl-10 pr-11 rounded-xl outline-none transition-all disabled:opacity-50 disabled:cursor-not-allowed placeholder-slate-600"
                    style={inputStyle(!!errors.password)}
                    onFocus={e => { e.target.style.border = '1px solid rgba(99,102,241,0.6)'; e.target.style.boxShadow = '0 0 0 3px rgba(99,102,241,0.12)'; }}
                    onBlur={e => { if (!errors.password) { e.target.style.border = '1px solid rgba(255,255,255,0.08)'; e.target.style.boxShadow = 'none'; } }}
                  />
                  <button type="button" id="toggle-password-visibility" onClick={() => setShowPassword(p => !p)} disabled={isLoading} aria-label={showPassword ? 'Hide' : 'Show'} className="absolute right-3.5 top-1/2 -translate-y-1/2 transition-colors hover:text-white" style={{ color: '#475569' }}>
                    {showPassword ? <EyeOff size={15}/> : <Eye size={15}/>}
                  </button>
                </div>
                <AnimatePresence>
                  {errors.password && (
                    <motion.p className="mt-1.5 text-xs" style={{ color: '#F87171' }} initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                      {errors.password.message}
                    </motion.p>
                  )}
                </AnimatePresence>
              </motion.div>

              {/* Submit */}
              <motion.button
                id="login-submit-btn"
                type="submit"
                disabled={isLoading}
                className="w-full py-3.5 rounded-xl text-white text-sm font-semibold flex items-center justify-center gap-2 mt-2 disabled:opacity-70 disabled:cursor-not-allowed"
                style={{ background: 'linear-gradient(135deg,#6366F1,#8B5CF6)', boxShadow: '0 4px 24px rgba(99,102,241,0.4)' }}
                whileHover={!isLoading ? { scale: 1.02, boxShadow: '0 8px 32px rgba(99,102,241,0.6)' } : {}}
                whileTap={!isLoading ? { scale: 0.98 } : {}}
                variants={fadeUp} initial="hidden" animate="visible" custom={5}
              >
                {isLoading ? (<><Loader2 size={16} className="animate-spin"/><span>Authenticating…</span></>) : (<><span>Access System</span><ArrowRight size={16}/></>)}
              </motion.button>
            </form>

            <div className="flex items-center gap-3 my-5">
              <div className="flex-1 h-px" style={{ background: 'rgba(255,255,255,0.06)' }}/>
              <span className="text-xs" style={{ color: '#334155' }}>SECURED BY</span>
              <div className="flex-1 h-px" style={{ background: 'rgba(255,255,255,0.06)' }}/>
            </div>

            <div className="flex items-center justify-center gap-5">
              {[['🔒','JWT Bearer'],['⚡','Argon2 Hash'],['🛡','FastAPI']].map(([ic,lbl]) => (
                <div key={lbl} className="flex items-center gap-1.5">
                  <span className="text-xs">{ic}</span>
                  <span className="text-xs" style={{ color: '#475569' }}>{lbl}</span>
                </div>
              ))}
            </div>

            <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-3/4 h-px" style={{ background: 'linear-gradient(90deg,transparent,rgba(139,92,246,0.6),transparent)' }}/>
          </motion.div>

          <motion.div className="mt-5 flex items-center justify-center gap-2" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.8 }}>
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"/>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"/>
            </span>
            <span className="text-xs" style={{ color: '#334155' }}>All systems operational</span>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
};

export default Login;
