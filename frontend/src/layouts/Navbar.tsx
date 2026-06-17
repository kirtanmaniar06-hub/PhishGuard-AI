import React, { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

export const Navbar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  const navItems = [
    { name: 'Dashboard', path: '/' },
    { name: 'Analytics', path: '/analytics' },
    { name: 'Simulations', path: '/simulations' },
    { name: 'Reports', path: '/reports' },
    { name: 'Settings', path: '/settings' },
  ];

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-cyber-cyan/20 bg-cyber-black/80 backdrop-blur-md">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo / Brand */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2 group">
              <div className="relative flex h-9 w-9 items-center justify-center rounded-lg border border-cyber-cyan bg-cyber-dark-card shadow-[0_0_10px_rgba(6,182,212,0.3)] transition-all duration-300 group-hover:scale-105 group-hover:shadow-[0_0_15px_rgba(6,182,212,0.6)]">
                {/* Shield / Security Logo SVG */}
                <svg
                  className="h-5 w-5 text-cyber-cyan animate-cyber-pulse"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                  />
                </svg>
              </div>
              <span className="text-xl font-bold tracking-wider text-white">
                PHISHGUARD<span className="text-cyber-cyan font-extrabold cyber-glow-text-cyan">AI</span>
              </span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <div className="flex space-x-6">
              {navItems.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.path}
                  className={({ isActive }) =>
                    `relative text-sm font-medium tracking-wide transition-all duration-200 hover:text-cyber-cyan ${
                      isActive ? 'text-cyber-cyan cyber-glow-text-cyan' : 'text-gray-400'
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      {item.name}
                      {isActive && (
                        <motion.div
                          layoutId="activeNavLine"
                          className="absolute -bottom-5 left-0 right-0 h-[2px] bg-cyber-cyan shadow-[0_0_8px_rgba(6,182,212,0.8)]"
                          transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                        />
                      )}
                    </>
                  )}
                </NavLink>
              ))}
            </div>

            {/* System Status Indicators */}
            <div className="flex items-center space-x-4 border-l border-gray-800 pl-6">
              <div className="flex items-center space-x-2">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyber-green opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-cyber-green"></span>
                </span>
                <span className="text-xs text-gray-500 font-mono">SYS_OK</span>
              </div>

              <button className="relative px-4 py-1.5 text-xs font-semibold tracking-wider text-cyber-cyan uppercase border border-cyber-cyan/30 rounded bg-cyber-cyan/5 hover:bg-cyber-cyan/15 hover:border-cyber-cyan transition-all duration-300 shadow-[0_0_5px_rgba(6,182,212,0.1)] hover:shadow-[0_0_12px_rgba(6,182,212,0.3)]">
                Secure Console
              </button>
            </div>
          </div>

          {/* Mobile Menu Button */}
          <div className="flex md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-cyber-dark-card hover:text-white focus:outline-none"
              aria-label="Toggle menu"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                {isOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer (Framer Motion) */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.25, ease: 'easeInOut' }}
            className="md:hidden border-t border-cyber-cyan/10 bg-cyber-dark/95"
          >
            <div className="space-y-1 px-2 pb-3 pt-2">
              {navItems.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.path}
                  onClick={() => setIsOpen(false)}
                  className={({ isActive }) =>
                    `block rounded-md px-3 py-2 text-base font-medium transition-all ${
                      isActive
                        ? 'bg-cyber-cyan/10 text-cyber-cyan border-l-2 border-cyber-cyan'
                        : 'text-gray-400 hover:bg-cyber-dark-card hover:text-white'
                    }`
                  }
                >
                  {item.name}
                </NavLink>
              ))}
              <div className="mt-4 border-t border-gray-800 pt-4 px-3 flex flex-col space-y-3">
                <div className="flex items-center space-x-2">
                  <span className="relative flex h-2.5 w-2.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyber-green opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyber-green"></span>
                  </span>
                  <span className="text-sm text-gray-400 font-mono">SYSTEM nominal</span>
                </div>
                <button className="w-full text-center px-4 py-2 text-sm font-semibold tracking-wider text-cyber-cyan uppercase border border-cyber-cyan/30 rounded bg-cyber-cyan/5 hover:bg-cyber-cyan/20 transition-all">
                  Secure Console
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};
