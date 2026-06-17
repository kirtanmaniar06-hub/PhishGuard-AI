import React from 'react';
import { motion } from 'framer-motion';

export const Simulations: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="p-6 lg:p-8 space-y-6"
    >
      <div className="border-b border-cyber-cyan/10 pb-5">
        <h1 className="text-3xl font-bold text-white m-0">Phishing Simulations</h1>
        <p className="text-sm text-gray-400 font-mono mt-1">MODULE: SIM_CORE_V1</p>
      </div>

      <div className="bg-cyber-dark-card/30 p-8 rounded-lg border border-cyber-blue/15 text-center space-y-4">
        <div className="h-16 w-16 mx-auto rounded-full bg-cyber-blue/5 border border-cyber-blue/30 flex items-center justify-center text-cyber-blue-dark animate-pulse">
          <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 9.172V5L8 4z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-white">Simulation Orchestrator Shell</h3>
        <p className="text-xs text-gray-400 max-w-md mx-auto">
          Manage, generate, and track corporate phishing simulation campaigns. Automated training triggers will populate here.
        </p>
        <div className="pt-2">
          <span className="inline-block px-3 py-1 bg-cyber-blue/10 border border-cyber-blue/25 rounded text-xs font-mono text-cyber-blue-dark">
            SIMULATION_ENGINE_READY
          </span>
        </div>
      </div>
    </motion.div>
  );
};
