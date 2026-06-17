import React from 'react';
import { motion } from 'framer-motion';

export const Reports: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="p-6 lg:p-8 space-y-6"
    >
      <div className="border-b border-cyber-cyan/10 pb-5">
        <h1 className="text-3xl font-bold text-white m-0">Compliance & Reports</h1>
        <p className="text-sm text-gray-400 font-mono mt-1">MODULE: AUDIT_REPORTS</p>
      </div>

      <div className="bg-cyber-dark-card/30 p-8 rounded-lg border border-cyber-cyan/10 text-center space-y-4">
        <div className="h-16 w-16 mx-auto rounded-full bg-cyber-cyan/5 border border-cyber-cyan/30 flex items-center justify-center text-cyber-cyan animate-pulse">
          <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-white">Compliance Report Center</h3>
        <p className="text-xs text-gray-400 max-w-md mx-auto">
          Export executive CSV and PDF reports. View enterprise cyber security rating and employee risk matrices.
        </p>
        <div className="pt-2">
          <span className="inline-block px-3 py-1 bg-cyber-cyan/10 border border-cyber-cyan/25 rounded text-xs font-mono text-cyber-cyan">
            PDF_EXPORTS_STANDBY
          </span>
        </div>
      </div>
    </motion.div>
  );
};
