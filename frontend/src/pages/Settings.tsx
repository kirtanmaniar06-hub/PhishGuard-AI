import React from 'react';
import { motion } from 'framer-motion';

export const Settings: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="p-6 lg:p-8 space-y-6"
    >
      <div className="border-b border-cyber-cyan/10 pb-5">
        <h1 className="text-3xl font-bold text-white m-0">Settings</h1>
        <p className="text-sm text-gray-400 font-mono mt-1">MODULE: CORE_SETTINGS</p>
      </div>

      <div className="bg-cyber-dark-card/30 p-8 rounded-lg border border-cyber-blue/15 text-center space-y-4">
        <div className="h-16 w-16 mx-auto rounded-full bg-cyber-blue/5 border border-cyber-blue/30 flex items-center justify-center text-cyber-blue-dark animate-pulse">
          <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-white">System Settings Shell</h3>
        <p className="text-xs text-gray-400 max-w-md mx-auto">
          Configure API key integration, ML model thresholds, email ingestion webhooks, and SMTP test channels.
        </p>
        <div className="pt-2">
          <span className="inline-block px-3 py-1 bg-cyber-blue/10 border border-cyber-blue/25 rounded text-xs font-mono text-cyber-blue-dark">
            CONFIG_STATUS_LOADED
          </span>
        </div>
      </div>
    </motion.div>
  );
};
