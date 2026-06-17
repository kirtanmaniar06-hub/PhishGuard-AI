import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

export const NotFound: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
      className="p-8 flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6"
    >
      <div className="font-mono text-7xl font-extrabold text-cyber-red tracking-widest cyber-glow-text-blue animate-pulse">
        404
      </div>
      <div className="space-y-2">
        <h2 className="text-xl font-bold text-white uppercase tracking-wider">ERROR: ACCESS_DENIED_OR_PAGE_ABSENT</h2>
        <p className="text-sm text-gray-400 max-w-sm font-mono mx-auto">
          The requested network node could not be resolved. Connection terminated.
        </p>
      </div>
      <div>
        <Link
          to="/"
          className="inline-block px-5 py-2 text-xs font-bold font-mono uppercase tracking-wider text-cyber-cyan border border-cyber-cyan rounded bg-cyber-cyan/10 hover:bg-cyber-cyan/25 transition-all shadow-[0_0_10px_rgba(6,182,212,0.15)] hover:shadow-[0_0_15px_rgba(6,182,212,0.3)]"
        >
          Return to Safe Node (Dashboard)
        </Link>
      </div>
    </motion.div>
  );
};
