import React, { useState, useEffect } from 'react';
import { NavLink, useLocation, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { createScan } from '../services/scanService';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isScanModalOpen, setIsScanModalOpen] = useState(false);
  const [scanInput, setScanInput] = useState('');
  const [scanType, setScanType] = useState<'url' | 'email'>('url');
  const [isScanning, setIsScanning] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);
  const [scanResult, setScanResult] = useState<any>(null);
  const [currentTime, setCurrentTime] = useState('');

  const location = useLocation();

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    {
      name: 'Console Dashboard',
      path: '/dashboard',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2H6a2 2 0 01-2-2v-4zM14 16a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2v-4z" />
        </svg>
      ),
    },
    {
      name: 'Threat Analytics',
      path: '/analytics',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
    },
    {
      name: 'Threat Simulations',
      path: '/simulations',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
    },
    {
      name: 'Email Scanner',
      path: '/email-scanner',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 19v-8.93a2 2 0 01.89-1.664l8-5.333a2 2 0 012.22 0l8 5.333A2 2 0 0121 10.07V19M3 19a2 2 0 002 2h14a2 2 0 002-2M3 19l6.75-4.5M21 19l-6.75-4.5M3 10l6.75 4.5M21 10l-6.75 4.5m0 0l-2.25-1.5a2 2 0 00-2.22 0l-2.25 1.5" />
        </svg>
      ),
    },
    {
      name: 'QR Scanner',
      path: '/qr-scanner',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v1m0 11v2m0-6h.01M12 2a10 10 0 100 20 10 10 0 000-20zM6 6h4v4H6V6zm0 8h4v4H6v-4zm8-8h4v4h-4V6z" />
        </svg>
      ),
    },
    {
      name: 'Incident Reports',
      path: '/reports',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
    },
    {
      name: 'System Settings',
      path: '/settings',
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      ),
    },
  ];

  const getPageTitle = () => {
    const activeItem = navItems.find((item) => location.pathname === item.path);
    return activeItem ? activeItem.name : 'Console';
  };

  const handleStartScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!scanInput.trim()) return;

    setIsScanning(true);
    setScanProgress(0);
    setScanResult(null);

    const interval = setInterval(() => {
      setScanProgress((prev) => (prev >= 90 ? 90 : prev + 15));
    }, 150);

    try {
      const data = await createScan({
        target: scanInput.trim(),
        type: scanType === 'url' ? 'URL' : 'EMAIL',
      });
      clearInterval(interval);
      setScanProgress(100);
      
      // Artificial short delay for visual completion
      setTimeout(() => {
        setIsScanning(false);
        setScanResult({
          score: data.score,
          status: data.status,
          analyzedTarget: data.target,
          verdict: data.verdict,
          indicators: data.indicators
        });
      }, 300);
    } catch (err: any) {
      clearInterval(interval);
      setIsScanning(false);
      const errMsg = err?.response?.data?.detail || err?.message || 'Backend connection error';
      setScanResult({
        score: 0,
        status: 'SAFE',
        analyzedTarget: scanInput,
        verdict: `Failed to run threat analysis: ${errMsg}`,
        indicators: ['Connection failed. Ensure backend server is running on port 8000.']
      });
    }
  };

  const resetScan = () => {
    setScanInput('');
    setScanResult(null);
    setScanProgress(0);
    setIsScanning(false);
  };

  return (
    <div className="flex h-screen w-full overflow-hidden bg-cyber-black font-sans text-gray-200">
      
      {/* ────────────────── LEFT SIDEBAR (DESKTOP) ────────────────── */}
      <aside className="hidden lg:flex flex-col w-64 bg-cyber-dark-card/50 border-r border-cyber-cyan/10 backdrop-blur-lg flex-shrink-0">
        
        {/* Brand/Logo Header */}
        <div className="flex items-center h-16 px-6 border-b border-cyber-cyan/10">
          <Link to="/" className="flex items-center space-x-2.5 group">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-cyber-cyan bg-cyber-dark shadow-[0_0_10px_rgba(6,182,212,0.2)] group-hover:shadow-[0_0_15px_rgba(6,182,212,0.5)] transition-all">
              <svg className="h-5 w-5 text-cyber-cyan animate-cyber-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <span className="text-md font-bold tracking-wider text-white font-mono uppercase">
              PhishGuard<span className="text-cyber-cyan font-extrabold cyber-glow-text-cyan">AI</span>
            </span>
          </Link>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `relative flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-all duration-200 group overflow-hidden ${
                  isActive 
                    ? 'text-cyber-cyan bg-cyber-cyan/5 border-l-2 border-cyber-cyan shadow-[inset_0_0_10px_rgba(6,182,212,0.05)] font-semibold' 
                    : 'text-gray-400 hover:text-gray-100 hover:bg-cyber-dark-card/30'
                }`
              }
            >
              {({ isActive }) => (
                <div className="flex items-center space-x-3 relative z-10 w-full">
                  <span className={`${isActive ? 'text-cyber-cyan' : 'text-gray-500 group-hover:text-gray-300'}`}>
                    {item.icon}
                  </span>
                  <span>{item.name}</span>
                </div>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Sidebar Footer Status */}
        <div className="p-4 border-t border-cyber-cyan/10 bg-cyber-black/30 font-mono text-[10px] space-y-2">
          <div className="flex items-center justify-between text-gray-500">
            <span>SECURE SHELL:</span>
            <span className="text-cyber-green">ACTIVE</span>
          </div>
          <div className="flex items-center justify-between text-gray-500">
            <span>NODE_ID:</span>
            <span className="text-cyber-cyan">PG-NODE-01</span>
          </div>
          <div className="flex items-center justify-between text-gray-500">
            <span>SYS_CLOCK:</span>
            <span className="text-gray-400 font-bold">{currentTime}</span>
          </div>
          <div className="mt-3 pt-3 border-t border-gray-800 flex items-center space-x-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyber-green opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-cyber-green"></span>
            </span>
            <span className="text-[9px] text-gray-400 uppercase tracking-widest">Nominal Status</span>
          </div>
        </div>
      </aside>

      {/* ────────────────── MOBILE SLIDE-OVER DRAWER ────────────────── */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.5 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsMobileMenuOpen(false)}
              className="lg:hidden fixed inset-0 z-40 bg-black/80 backdrop-blur-sm"
            />
            {/* Drawer Content */}
            <motion.aside
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="lg:hidden fixed inset-y-0 left-0 w-64 z-50 bg-cyber-dark-card border-r border-cyber-cyan/20 p-5 flex flex-col justify-between"
            >
              <div className="space-y-6">
                <div className="flex items-center justify-between border-b border-cyber-cyan/10 pb-4">
                  <div className="flex items-center space-x-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-cyber-cyan bg-cyber-dark shadow-[0_0_10px_rgba(6,182,212,0.3)]">
                      <svg className="h-4 w-4 text-cyber-cyan" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                      </svg>
                    </div>
                    <span className="text-sm font-bold tracking-wider text-white">
                      PHISHGUARD<span className="text-cyber-cyan">AI</span>
                    </span>
                  </div>
                  <button onClick={() => setIsMobileMenuOpen(false)} className="text-gray-400 hover:text-white">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <nav className="space-y-2">
                  {navItems.map((item) => (
                    <NavLink
                      key={item.path}
                      to={item.path}
                      onClick={() => setIsMobileMenuOpen(false)}
                      className={({ isActive }) =>
                        `flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-all duration-150 ${
                          isActive 
                            ? 'text-cyber-cyan bg-cyber-cyan/10 border-l-2 border-cyber-cyan' 
                            : 'text-gray-400 hover:text-gray-100 hover:bg-cyber-dark-card/30'
                        }`
                      }
                    >
                      <span className="mr-3 text-gray-400">{item.icon}</span>
                      {item.name}
                    </NavLink>
                  ))}
                </nav>
              </div>

              {/* Mobile Sidebar Footer */}
              <div className="pt-4 border-t border-cyber-cyan/10 font-mono text-[9px] text-gray-500 space-y-1">
                <div>SYSTEM STATUS: <span className="text-cyber-green font-bold">NOMINAL</span></div>
                <div>TIME: <span className="text-white">{currentTime}</span></div>
              </div>
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* ────────────────── MAIN WINDOW AREA ────────────────── */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        
        {/* TOP BAR / NAVIGATION */}
        <header className="flex items-center justify-between h-16 px-6 bg-cyber-dark-card/20 border-b border-cyber-cyan/10 backdrop-blur-md z-30">
          
          {/* Mobile hamburger button + Title */}
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setIsMobileMenuOpen(true)}
              className="lg:hidden p-2 -ml-2 text-gray-400 hover:text-white hover:bg-cyber-dark-card rounded-lg focus:outline-none"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <div className="flex flex-col">
              <span className="text-[10px] text-cyber-cyan font-mono tracking-widest uppercase">CONSOLE HUB</span>
              <h1 className="text-lg font-bold text-white tracking-tight">{getPageTitle()}</h1>
            </div>
          </div>

          {/* Action Tools */}
          <div className="flex items-center space-x-4">
            
            {/* Quick Scan Input Button */}
            <button
              onClick={() => setIsScanModalOpen(true)}
              className="hidden md:flex items-center space-x-2 px-3 py-1.5 text-xs font-mono font-bold tracking-wider text-cyber-cyan border border-cyber-cyan/40 bg-cyber-cyan/5 rounded-md hover:bg-cyber-cyan/15 hover:border-cyber-cyan hover:shadow-[0_0_10px_rgba(0,240,255,0.25)] transition-all cursor-pointer"
            >
              <svg className="w-4 h-4 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
              </svg>
              <span>QUICK SCAN</span>
            </button>

            {/* Quick Scan Icon Button for Mobile */}
            <button
              onClick={() => setIsScanModalOpen(true)}
              className="flex md:hidden p-2 text-cyber-cyan border border-cyber-cyan/20 bg-cyber-cyan/5 rounded-lg hover:bg-cyber-cyan/15"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
              </svg>
            </button>

            {/* Notification indicator */}
            <div className="relative">
              <button className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-cyber-dark-card/30 relative">
                <span className="absolute top-1.5 right-1.5 flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyber-red opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-cyber-red"></span>
                </span>
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
              </button>
            </div>

            {/* Profile Menu */}
            <div className="relative">
              <button
                onClick={() => setIsProfileOpen(!isProfileOpen)}
                className="flex items-center space-x-2.5 p-1 rounded-full border border-gray-800 hover:border-cyber-cyan/50 hover:bg-cyber-dark-card/30 transition-all focus:outline-none cursor-pointer"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-cyber-blue to-cyber-cyan flex items-center justify-center text-white font-mono font-bold text-xs shadow-md border border-cyber-cyan/30">
                  SA
                </div>
              </button>
              
              <AnimatePresence>
                {isProfileOpen && (
                  <>
                    <div className="fixed inset-0 z-10" onClick={() => setIsProfileOpen(false)} />
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: 10 }}
                      className="absolute right-0 mt-2 w-56 bg-cyber-dark-card border border-cyber-cyan/20 rounded-lg shadow-xl py-2 z-20 font-mono text-xs"
                    >
                      <div className="px-4 py-3 border-b border-gray-800">
                        <p className="text-gray-400">Security Analyst</p>
                        <p className="text-white font-bold truncate">superadmin@phishguard.ai</p>
                      </div>
                      <Link
                        to="/settings"
                        onClick={() => setIsProfileOpen(false)}
                        className="block px-4 py-2.5 text-gray-300 hover:text-white hover:bg-cyber-cyan/10 transition-all animate-none"
                      >
                        ⚙️ View Settings
                      </Link>
                      <a
                        href="#logout"
                        className="block px-4 py-2.5 text-cyber-red hover:bg-cyber-red/10 transition-all border-t border-gray-800"
                        onClick={(e) => {
                          e.preventDefault();
                          setIsProfileOpen(false);
                          alert('Logout simulation executed.');
                        }}
                      >
                        ⚡ Disconnect Session
                      </a>
                    </motion.div>
                  </>
                )}
              </AnimatePresence>
            </div>

          </div>
        </header>

        {/* CENTRAL VIEWPORT */}
        <main className="flex-1 overflow-y-auto w-full bg-cyber-black relative">
          {/* Subtle Grid overlay in viewport background */}
          <div className="absolute inset-0 cyber-grid opacity-30 pointer-events-none z-0" />
          
          <div className="relative z-10 w-full min-h-full">
            {children}
          </div>
        </main>
      </div>

      {/* ────────────────── QUICK SCAN OVERLAY MODAL ────────────────── */}
      <AnimatePresence>
        {isScanModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.7 }}
              exit={{ opacity: 0 }}
              onClick={() => { if (!isScanning) setIsScanModalOpen(false); }}
              className="absolute inset-0 bg-black/85 backdrop-blur-md"
            />

            {/* Modal Body */}
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              transition={{ type: 'spring', damping: 20 }}
              className="relative w-full max-w-2xl bg-cyber-dark-card border border-cyber-cyan/30 rounded-lg overflow-hidden shadow-[0_0_30px_rgba(6,182,212,0.15)] z-10"
            >
              
              {/* Scanline decoration */}
              <div className="absolute top-0 left-0 right-0 h-[2px] bg-cyber-cyan animate-pulse shadow-[0_0_10px_rgba(0,240,255,0.8)]" />

              {/* Header */}
              <div className="flex items-center justify-between px-6 py-4 border-b border-cyber-cyan/10">
                <div className="flex items-center space-x-2">
                  <span className="flex h-2 w-2 rounded-full bg-cyber-cyan animate-ping" />
                  <span className="font-mono text-xs text-cyber-cyan uppercase tracking-widest">AI_MODEL_INGESTION_SHELL</span>
                </div>
                <button
                  onClick={() => setIsScanModalOpen(false)}
                  disabled={isScanning}
                  className="text-gray-400 hover:text-white transition-all disabled:opacity-30 cursor-pointer"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Body Content */}
              <div className="p-6">
                {!isScanning && !scanResult && (
                  <form onSubmit={handleStartScan} className="space-y-4">
                    <h3 className="text-lg font-bold text-white">Ingest Threat Vector</h3>
                    <p className="text-xs text-gray-400 font-mono">
                      Submit suspicious URLs or email content to be analyzed in real-time by the PhishGuard AI neural networks.
                    </p>

                    {/* Scan type switch */}
                    <div className="flex space-x-4 border-b border-gray-800 pb-3">
                      <button
                        type="button"
                        onClick={() => setScanType('url')}
                        className={`text-xs font-mono font-bold px-3 py-1.5 rounded transition-all cursor-pointer ${
                          scanType === 'url' 
                            ? 'text-cyber-cyan bg-cyber-cyan/10 border border-cyber-cyan/35' 
                            : 'text-gray-400 hover:text-gray-200'
                        }`}
                      >
                        🌐 URL Analysis
                      </button>
                      <button
                        type="button"
                        onClick={() => setScanType('email')}
                        className={`text-xs font-mono font-bold px-3 py-1.5 rounded transition-all cursor-pointer ${
                          scanType === 'email' 
                            ? 'text-cyber-cyan bg-cyber-cyan/10 border border-cyber-cyan/35' 
                            : 'text-gray-400 hover:text-gray-200'
                        }`}
                      >
                        📧 Email Headers / Content
                      </button>
                    </div>

                    <div className="space-y-2">
                      <label className="block text-xs font-mono text-gray-400">
                        {scanType === 'url' ? 'Suspicious Web Link' : 'Email Content / Raw Text Body'}
                      </label>
                      {scanType === 'url' ? (
                        <input
                          type="url"
                          required
                          placeholder="e.g., http://secure-login-phishguard-verification.temp-site.xyz"
                          value={scanInput}
                          onChange={(e) => setScanInput(e.target.value)}
                          className="w-full bg-cyber-black border border-gray-800 rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-cyber-cyan/50 focus:shadow-[0_0_8px_rgba(0,240,255,0.15)] transition-all font-mono"
                        />
                      ) : (
                        <textarea
                          required
                          rows={5}
                          placeholder="Paste email subject, body, or raw headers here..."
                          value={scanInput}
                          onChange={(e) => setScanInput(e.target.value)}
                          className="w-full bg-cyber-black border border-gray-800 rounded px-3 py-2 text-xs text-white focus:outline-none focus:border-cyber-cyan/50 focus:shadow-[0_0_8px_rgba(0,240,255,0.15)] transition-all font-mono"
                        />
                      )}
                    </div>

                    <div className="flex justify-end pt-3">
                      <button
                        type="submit"
                        className="px-5 py-2 text-xs font-mono font-bold tracking-wider text-black bg-cyber-cyan hover:bg-cyber-neon-cyan rounded shadow-[0_0_15px_rgba(6,182,212,0.4)] hover:shadow-[0_0_20px_rgba(0,240,255,0.7)] transition-all duration-300 cursor-pointer"
                      >
                        RUN DETECTION SIGNAL
                      </button>
                    </div>
                  </form>
                )}

                {/* Scanning Progress */}
                {isScanning && (
                  <div className="py-8 text-center space-y-6">
                    <div className="relative w-24 h-24 mx-auto">
                      {/* Radar-like scanning circles */}
                      <span className="absolute inset-0 rounded-full border-2 border-cyber-cyan/10 animate-ping" />
                      <span className="absolute inset-2 rounded-full border-2 border-cyber-cyan/30 animate-pulse" />
                      <div className="absolute inset-4 rounded-full border-4 border-cyber-cyan/40 border-t-cyber-cyan animate-spin" />
                      <div className="absolute inset-0 flex items-center justify-center font-mono text-xs text-cyber-cyan font-bold">
                        {scanProgress}%
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <h4 className="text-md font-bold text-white font-mono uppercase tracking-widest animate-pulse">Running AI Model Inference...</h4>
                      <p className="text-xs text-gray-500 max-w-sm mx-auto font-mono">
                        Vectorizing inputs, checking heuristic SPF records, analyzing urgency scores, and executing threat pattern parsing.
                      </p>
                    </div>

                    <div className="max-w-md mx-auto h-2 bg-cyber-black rounded-full overflow-hidden border border-gray-800">
                      <div className="h-full bg-cyber-cyan transition-all duration-150" style={{ width: `${scanProgress}%` }} />
                    </div>
                  </div>
                )}

                {/* Scan Result */}
                {scanResult && (
                  <div className="space-y-6">
                    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-gray-800 pb-4">
                      <div>
                        <h4 className="text-md font-bold text-white">Detection Report</h4>
                        <span className="text-[10px] text-gray-500 font-mono block mt-1 truncate max-w-md">
                          TARGET: {scanResult.analyzedTarget}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-mono text-gray-400">Threat Index:</span>
                        <span className={`px-3 py-1 font-mono font-bold text-sm rounded ${
                          scanResult.status === 'CRITICAL' 
                            ? 'bg-cyber-red/20 border border-cyber-red/40 text-cyber-red'
                            : scanResult.status === 'SUSPICIOUS'
                              ? 'bg-amber-500/20 border border-amber-500/40 text-amber-400'
                              : 'bg-cyber-green/20 border border-cyber-green/40 text-cyber-green'
                        }`}>
                          {scanResult.score}/100 ({scanResult.status})
                        </span>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div>
                        <span className="text-xs font-mono text-gray-400 uppercase tracking-wider block mb-1">AI Classification Verdict</span>
                        <div className="p-4 rounded bg-cyber-black border border-gray-800 text-xs leading-relaxed text-gray-200 font-mono">
                          {scanResult.verdict}
                        </div>
                      </div>

                      <div>
                        <span className="text-xs font-mono text-gray-400 uppercase tracking-wider block mb-2">Key Risk Indicators</span>
                        <div className="flex flex-wrap gap-2">
                          {scanResult.indicators.map((ind: string, idx: number) => (
                            <span
                              key={idx}
                              className={`text-[10px] font-mono px-2 py-1 rounded border ${
                                scanResult.status === 'CRITICAL'
                                  ? 'bg-cyber-red/5 border-cyber-red/20 text-cyber-red shadow-[0_0_8px_rgba(239,68,68,0.15)]'
                                  : scanResult.status === 'SUSPICIOUS'
                                    ? 'bg-amber-500/5 border-amber-500/20 text-amber-400 shadow-[0_0_8px_rgba(245,158,11,0.15)]'
                                    : 'bg-cyber-green/5 border-cyber-green/20 text-cyber-green shadow-[0_0_8px_rgba(16,185,129,0.15)]'
                              }`}
                            >
                              ❗ {ind}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div className="flex justify-between border-t border-gray-800 pt-4 mt-6">
                      <button
                        onClick={resetScan}
                        className="px-4 py-2 text-xs font-mono font-bold text-gray-400 hover:text-white border border-gray-800 rounded hover:bg-cyber-dark-card transition-all cursor-pointer"
                      >
                        INGEST NEW VECTOR
                      </button>
                      <button
                        onClick={() => setIsScanModalOpen(false)}
                        className="px-4 py-2 text-xs font-mono font-bold text-black bg-cyber-cyan hover:bg-cyber-neon-cyan rounded transition-all cursor-pointer"
                      >
                        CLOSE CONSOLE SHELL
                      </button>
                    </div>
                  </div>
                )}
              </div>

            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </div>
  );
};
