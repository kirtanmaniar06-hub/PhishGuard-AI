import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

// CountUp helper for stats
const CountUp: React.FC<{ value: number; duration?: number; suffix?: string; decimals?: number }> = ({
  value,
  duration = 1.5,
  suffix = '',
  decimals = 0,
}) => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let start = 0;
    const end = value;
    if (start === end) return;

    const totalMiliseconds = duration * 1000;
    const incrementTime = 30;
    const totalSteps = totalMiliseconds / incrementTime;
    const stepIncrement = (end - start) / totalSteps;

    const timer = setInterval(() => {
      start += stepIncrement;
      if (start >= end) {
        clearInterval(timer);
        setCount(end);
      } else {
        setCount(start);
      }
    }, incrementTime);

    return () => clearInterval(timer);
  }, [value, duration]);

  return (
    <span>
      {decimals > 0 ? count.toFixed(decimals) : Math.floor(count)}
      {suffix}
    </span>
  );
};

const rawLogs = [
  'SYSTEM: Initializing cognitive security agent...',
  'AGENT: Active node listener established on port ::443',
  'AI_ENGINE: Injecting localized training vectors...',
  'SCANNER: Scanning mail transport node [IMAP_INBOUND]',
  'WARNING: Detected spear-phishing payload target in node #4',
  'THREAT: Attack signature match: [CVE-2026-MICRO_AUTH]',
  'ACTION: Simulated payload intercepted & quarantined.',
  'ANALYTICS: Recording behavioral response latency (1.4s)',
  'IMMUNIZER: Dispatched micro-learning module: Phish_Shield_v12',
  'POSTURE: Node posture updated to 99.8% NOMINAL',
];

export const Landing: React.FC = () => {
  // Terminal log simulator states
  const [terminalLogs, setTerminalLogs] = useState<string[]>([]);
  const [logIndex, setLogIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      if (logIndex < rawLogs.length) {
        setTerminalLogs((prev) => [...prev, rawLogs[logIndex]]);
        setLogIndex((prev) => prev + 1);
      } else {
        // Clear and restart simulation logs
        setTerminalLogs([rawLogs[0]]);
        setLogIndex(1);
      }
    }, 2000);

    return () => clearInterval(timer);
  }, [logIndex]);

  return (
    <div className="relative w-full min-h-screen overflow-hidden bg-cyber-black text-gray-100 font-sans">
      
      {/* ── BACKGROUND TELEMETRY LAYER ───────────────────────────────── */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        {/* Neon Grid Layer */}
        <div className="absolute inset-0 cyber-grid opacity-25" />
        
        {/* Moving Laser Scanner Line */}
        <motion.div
          animate={{ y: ['-100%', '100%'] }}
          transition={{ repeat: Infinity, duration: 10, ease: 'linear' }}
          className="absolute left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-cyber-cyan to-transparent shadow-[0_0_12px_rgba(6,182,212,0.8)] z-0"
        />

        {/* Ambient Neon Blur Glows */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-cyber-cyan/10 blur-[120px] animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full bg-cyber-blue/10 blur-[120px] animate-pulse" style={{ animationDelay: '1.5s' }} />
      </div>

      {/* ── HERO SECTION ────────────────────────────────────────────── */}
      <section className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-24 md:pt-32 md:pb-32 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
        
        {/* Hero Left Content */}
        <div className="lg:col-span-7 space-y-6 text-left">
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyber-cyan/10 border border-cyber-cyan/30"
          >
            <span className="h-1.5 w-1.5 rounded-full bg-cyber-cyan animate-ping" />
            <span className="text-[10px] font-mono tracking-widest text-cyber-cyan uppercase">
              Secure Human Perimeter // v2.0
            </span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.6 }}
            className="text-4xl sm:text-6xl font-bold tracking-tight text-white leading-tight"
          >
            Defend Your Team Against{' '}
            <span className="bg-gradient-to-r from-cyber-cyan to-cyber-neon-blue bg-clip-text text-transparent [text-shadow:0_0_30px_rgba(6,182,212,0.2)]">
              Cognitive Exploits
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="text-lg text-gray-400 max-w-xl leading-relaxed"
          >
            Train, simulate, and immunize your workforce against spear-phishing and social engineering vectors using autonomous AI agents and behavioral telemetry.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="flex flex-col sm:flex-row gap-4 pt-4"
          >
            <Link
              to="/dashboard"
              className="px-8 py-3.5 text-sm font-bold tracking-wider text-black bg-cyber-cyan rounded hover:bg-cyber-cyan/90 transition-all duration-300 shadow-[0_0_15px_rgba(6,182,212,0.4)] hover:shadow-[0_0_25px_rgba(6,182,212,0.6)] text-center select-none"
            >
              LAUNCH SECURE CONSOLE
            </Link>
            <Link
              to="/simulations"
              className="px-8 py-3.5 text-sm font-bold tracking-wider text-white border border-cyber-cyan/30 bg-cyber-cyan/5 rounded hover:bg-cyber-cyan/15 hover:border-cyber-cyan transition-all duration-300 text-center select-none"
            >
              RUN SIMULATOR
            </Link>
          </motion.div>
        </div>

        {/* Hero Right Interactive Terminal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="lg:col-span-5 bg-cyber-dark/80 backdrop-blur-xl rounded-xl border border-cyber-cyan/20 overflow-hidden shadow-[0_0_30px_rgba(6,182,212,0.1)]"
        >
          {/* Terminal Window Header */}
          <div className="flex items-center justify-between px-4 py-3 bg-cyber-dark-card/80 border-b border-cyber-cyan/15">
            <div className="flex space-x-2">
              <span className="w-3 h-3 rounded-full bg-cyber-red/70" />
              <span className="w-3 h-3 rounded-full bg-cyber-blue/70" />
              <span className="w-3 h-3 rounded-full bg-cyber-green/70" />
            </div>
            <span className="text-[10px] font-mono text-gray-500 tracking-wider">
              TELEMETRY_STREAM // LIVE
            </span>
          </div>

          {/* Terminal Screen */}
          <div className="p-4 h-64 font-mono text-[11px] text-cyber-cyan/90 space-y-2 overflow-y-auto select-none">
            <AnimatePresence>
              {terminalLogs.map((log, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -5 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.35 }}
                  className={
                    log.includes('WARNING')
                      ? 'text-yellow-400'
                      : log.includes('THREAT')
                      ? 'text-cyber-red'
                      : log.includes('ACTION') || log.includes('POSTURE')
                      ? 'text-cyber-green'
                      : 'text-cyber-cyan/80'
                  }
                >
                  <span className="text-cyber-cyan/40 mr-1.5">&gt;</span>
                  {log}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </motion.div>
      </section>

      {/* ── FEATURES SECTION ────────────────────────────────────────── */}
      <section className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 border-t border-gray-900">
        <div className="text-center max-w-3xl mx-auto space-y-3 mb-16">
          <span className="text-xs font-mono tracking-widest text-cyber-cyan uppercase font-semibold">
            DEFENSE SYSTEMS
          </span>
          <h2 className="text-3xl sm:text-4xl font-bold text-white tracking-tight">
            Cognitive Defensive Architecture
          </h2>
          <p className="text-sm text-gray-400">
            Harnessing adaptive intelligence to shield the corporate infrastructure from spear-phishing.
          </p>
        </div>

        {/* Features Card Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            {
              title: 'Autonomous Simulator',
              desc: 'Dispatches simulated phishing templates customized to employee profiles, adapting attack vectors dynamically.',
              icon: (
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
              ),
              glow: 'hover:shadow-[0_0_20px_rgba(6,182,212,0.15)] hover:border-cyber-cyan/50',
            },
            {
              title: 'Behavioral Scorecard',
              desc: 'Aggregates threat reporting speed, payload clicks, and historical compliance data into secure profile analytics.',
              icon: (
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 002 2h2a2 2 0 002-2z" />
                </svg>
              ),
              glow: 'hover:shadow-[0_0_20px_rgba(37,99,235,0.15)] hover:border-cyber-blue/50',
            },
            {
              title: 'Adaptive Mitigation',
              desc: 'Deploys localized warning flags directly within browsers, triggering real-time micro-training modules.',
              icon: (
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              ),
              glow: 'hover:shadow-[0_0_20px_rgba(16,187,129,0.15)] hover:border-cyber-green/50',
            },
          ].map((feat) => (
            <motion.div
              key={feat.title}
              whileHover={{ y: -6 }}
              className={`bg-cyber-dark-card/20 backdrop-blur-md p-8 rounded-lg border border-white/5 transition-all duration-300 ${feat.glow}`}
            >
              <div className="h-12 w-12 rounded-lg bg-cyber-dark/80 border border-cyber-cyan/20 flex items-center justify-center text-cyber-cyan mb-6">
                {feat.icon}
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">{feat.title}</h3>
              <p className="text-sm text-gray-400 leading-relaxed">{feat.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── HOW IT WORKS SECTION ────────────────────────────────────── */}
      <section className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 border-t border-gray-900">
        <div className="text-center max-w-3xl mx-auto space-y-3 mb-20">
          <span className="text-xs font-mono tracking-widest text-cyber-cyan uppercase font-semibold">
            THE SYSTEM IN ACTION
          </span>
          <h2 className="text-3xl sm:text-4xl font-bold text-white tracking-tight">
            The Immunization Lifecycle
          </h2>
          <p className="text-sm text-gray-400">
            Four structural phases to transition your workforce from targets to defensive sensors.
          </p>
        </div>

        {/* Steps Timeline Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 relative">
          
          {/* Vertical connecting neon bar in background for desktop */}
          <div className="absolute top-1/2 left-[12%] right-[12%] h-[1px] bg-gradient-to-r from-cyber-cyan/10 via-cyber-blue/30 to-cyber-cyan/10 hidden md:block z-0" />

          {[
            {
              step: '01',
              title: 'Deploy & Listen',
              detail: 'Cognitive agents establish background integrations with enterprise user directories securely.',
            },
            {
              step: '02',
              title: 'Target & Send',
              detail: 'Customized spear-phishing lures match specific roles (Finance, IT, HR) to test resilience.',
            },
            {
              step: '03',
              title: 'Track Telemetry',
              detail: 'Capture click events, credentials submissions, and time elapsed before threat report flags.',
            },
            {
              step: '04',
              title: 'Micro-Immunize',
              detail: 'Users who fail simulation are redirected immediately to 60-second micro-learning sessions.',
            },
          ].map((item) => (
            <div key={item.step} className="relative z-10 text-center md:text-left space-y-4">
              <div className="h-12 w-12 rounded-full bg-cyber-dark/95 border-2 border-cyber-cyan flex items-center justify-center font-mono font-bold text-cyber-cyan mx-auto md:mx-0 shadow-[0_0_12px_rgba(6,182,212,0.4)]">
                {item.step}
              </div>
              <h3 className="text-lg font-bold text-white pt-2">{item.title}</h3>
              <p className="text-xs text-gray-400 leading-relaxed max-w-xs mx-auto md:mx-0">
                {item.detail}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* ── THREAT STATISTICS SECTION ────────────────────────────────── */}
      <section className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 border-t border-gray-900 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
        
        {/* Stats Left */}
        <div className="lg:col-span-5 space-y-6">
          <span className="text-xs font-mono tracking-widest text-cyber-cyan uppercase font-semibold">
            TELEMETRY & IMPACT
          </span>
          <h2 className="text-3xl sm:text-4xl font-bold text-white tracking-tight">
            Security That Speaks in Numbers
          </h2>
          <p className="text-sm text-gray-400 leading-relaxed">
            PhishGuard AI reduces enterprise vulnerability windows systematically. Watch threat intercept ratios decay as cognitive training propagates.
          </p>

          <div className="grid grid-cols-2 gap-6 pt-4">
            <div className="p-4 bg-cyber-dark-card/15 border border-white/5 rounded-lg text-left">
              <p className="text-4xl font-bold text-cyber-cyan">
                <CountUp value={98} suffix="%" />
              </p>
              <span className="text-[10px] font-mono text-gray-500 uppercase tracking-wider block mt-1">
                EXPLOIT REDUCTION
              </span>
            </div>
            <div className="p-4 bg-cyber-dark-card/15 border border-white/5 rounded-lg text-left">
              <p className="text-4xl font-bold text-cyber-cyan">
                <CountUp value={2.1} decimals={1} suffix="s" />
              </p>
              <span className="text-[10px] font-mono text-gray-500 uppercase tracking-wider block mt-1">
                REPORT LATENCY
              </span>
            </div>
          </div>
        </div>

        {/* Stats Right Custom SVG Chart Visual */}
        <div className="lg:col-span-7 bg-cyber-dark-card/30 backdrop-blur-md border border-white/5 rounded-xl p-8 relative overflow-hidden">
          
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-cyber-cyan/2 to-transparent w-full h-[200%] pointer-events-none animate-scanline z-0" />
          
          <div className="flex justify-between items-center mb-6 relative z-10">
            <div>
              <h4 className="text-sm font-semibold text-white">Simulation Learning Curve</h4>
              <p className="text-[10px] font-mono text-gray-500">CAMP_EXPLOIT_RATE // 12_WEEK_INTERVAL</p>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 border border-cyber-cyan/30 bg-cyber-cyan/5 text-cyber-cyan rounded">
              DECELERATION: SECURE
            </span>
          </div>

          {/* Premium Vector Chart */}
          <div className="h-64 w-full relative z-10 flex items-end">
            <svg viewBox="0 0 500 200" className="w-full h-full text-cyber-cyan">
              <defs>
                <linearGradient id="chart-glow" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.4" />
                  <stop offset="100%" stopColor="#06b6d4" stopOpacity="0" />
                </linearGradient>
              </defs>
              {/* Grid Lines */}
              <line x1="0" y1="50" x2="500" y2="50" stroke="#1e293b" strokeOpacity="0.3" strokeDasharray="3 3" />
              <line x1="0" y1="100" x2="500" y2="100" stroke="#1e293b" strokeOpacity="0.3" strokeDasharray="3 3" />
              <line x1="0" y1="150" x2="500" y2="150" stroke="#1e293b" strokeOpacity="0.3" strokeDasharray="3 3" />
              
              {/* Chart Path Area */}
              <path
                d="M 0 40 Q 100 50 180 120 T 320 170 T 500 180 L 500 200 L 0 200 Z"
                fill="url(#chart-glow)"
              />
              
              {/* Chart Path Line */}
              <path
                d="M 0 40 Q 100 50 180 120 T 320 170 T 500 180"
                fill="none"
                stroke="#06b6d4"
                strokeWidth="3"
                className="shadow-[0_0_12px_rgba(6,182,212,0.8)]"
              />

              {/* Data points */}
              <circle cx="180" cy="120" r="5" fill="#00f0ff" />
              <circle cx="320" cy="170" r="5" fill="#00f0ff" />
              <circle cx="500" cy="180" r="5" fill="#00f0ff" />
            </svg>
          </div>
        </div>
      </section>

      {/* ── CALL TO ACTION SECTION ──────────────────────────────────── */}
      <section className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 border-t border-gray-900">
        <div className="bg-gradient-to-r from-cyber-cyan/5 via-cyber-blue/5 to-cyber-cyan/5 border border-cyber-cyan/15 rounded-2xl p-8 sm:p-12 text-center space-y-6 relative overflow-hidden shadow-[0_0_30px_rgba(6,182,212,0.05)]">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full bg-cyber-cyan/5 blur-3xl z-0 pointer-events-none" />
          
          <div className="relative z-10 max-w-2xl mx-auto space-y-4">
            <h2 className="text-3xl sm:text-5xl font-bold text-white tracking-tight">
              Ready to Lock Your Node?
            </h2>
            <p className="text-sm text-gray-400 leading-relaxed">
              Start dispatching automated campaigns and evaluate compliance matrices in minutes.
            </p>
            <div className="pt-6 flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/dashboard"
                className="px-8 py-3.5 text-sm font-bold tracking-wider text-black bg-cyber-cyan rounded hover:bg-cyber-cyan/95 transition-all duration-300 shadow-[0_0_15px_rgba(6,182,212,0.4)] text-center select-none"
              >
                PROVISION NODE NOW
              </Link>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
};
