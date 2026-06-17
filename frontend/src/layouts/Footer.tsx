import React from 'react';

export const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="mt-auto border-t border-cyber-cyan/15 bg-cyber-black/90 py-8 text-gray-500 font-sans">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          
          {/* Platform Status */}
          <div className="col-span-1 md:col-span-2 space-y-3">
            <div className="flex items-center space-x-2">
              <div className="h-2 w-2 rounded-full bg-cyber-cyan shadow-[0_0_8px_rgba(6,182,212,0.8)]"></div>
              <span className="text-sm font-bold tracking-wider text-white">
                PHISHGUARD<span className="text-cyber-cyan font-extrabold">AI</span>
              </span>
            </div>
            <p className="text-xs text-gray-400 max-w-sm leading-relaxed">
              Enterprise-grade real-time phishing detection and simulator platform. Harnessing deep cognitive ML agents to protect corporate infrastructure from social engineering threats.
            </p>
          </div>

          {/* Site links */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-widest text-white">Navigation</h4>
            <ul className="space-y-2 text-xs">
              <li>
                <a href="/" className="hover:text-cyber-cyan transition-colors">Dashboard</a>
              </li>
              <li>
                <a href="/simulations" className="hover:text-cyber-cyan transition-colors">Simulations</a>
              </li>
              <li>
                <a href="/docs" className="hover:text-cyber-cyan transition-colors">API Documentation</a>
              </li>
            </ul>
          </div>

          {/* Telemetry Widgets */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-widest text-white">Security Status</h4>
            <div className="space-y-1.5 font-mono text-[10px] text-gray-400 bg-cyber-dark/60 p-3 rounded border border-cyber-cyan/10">
              <div className="flex justify-between">
                <span>ENCRYPTION:</span>
                <span className="text-cyber-cyan">AES_256_GCM</span>
              </div>
              <div className="flex justify-between">
                <span>THREAT DATABASE:</span>
                <span className="text-cyber-neon-blue">v4.8.12-LIVE</span>
              </div>
              <div className="flex justify-between">
                <span>NODE LOCATION:</span>
                <span className="text-white">US-EAST-1 (SECURED)</span>
              </div>
              <div className="flex justify-between">
                <span>AGENT STATUS:</span>
                <span className="text-cyber-green animate-pulse">ACTIVE_LISTENER</span>
              </div>
            </div>
          </div>

        </div>

        {/* Lower Row */}
        <div className="flex flex-col sm:flex-row items-center justify-between border-t border-gray-900 pt-6 text-[11px] font-mono">
          <div className="mb-4 sm:mb-0">
            &copy; {currentYear} PHISHGUARD AI. All rights secured.
          </div>
          <div className="flex space-x-6">
            <a href="/privacy" className="hover:text-cyber-cyan transition-colors">Privacy Charter</a>
            <a href="/terms" className="hover:text-cyber-cyan transition-colors">Terms of Service</a>
            <span className="text-cyber-cyan/40">|</span>
            <span className="text-cyber-cyan select-none animate-pulse">SECURE_SESSION_ACTIVE</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
