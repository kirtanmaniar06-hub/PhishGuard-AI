/**
 * PhishGuard AI — Email Scanner Component
 *
 * Provides copy-paste interface to parse and heuristics-check MIME/plaintext email bodies.
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { scanEmail } from '../services/emailScannerService';
import type { EmailScanResponse } from '../types/emailScanner';

const statusConfig = {
  SAFE: {
    label: 'SAFE',
    color: 'text-cyber-green',
    border: 'border-cyber-green/30',
    bg: 'bg-cyber-green/5',
    glow: 'shadow-[0_0_20px_rgba(16,185,129,0.12)]',
    badge: 'bg-cyber-green/10 border-cyber-green/40 text-cyber-green',
    bar: 'bg-cyber-green',
  },
  SUSPICIOUS: {
    label: 'SUSPICIOUS',
    color: 'text-amber-400',
    border: 'border-amber-500/30',
    bg: 'bg-amber-500/5',
    glow: 'shadow-[0_0_20px_rgba(245,158,11,0.12)]',
    badge: 'bg-amber-500/10 border-amber-500/40 text-amber-400',
    bar: 'bg-amber-400',
  },
  CRITICAL: {
    label: 'CRITICAL',
    color: 'text-cyber-red',
    border: 'border-cyber-red/30',
    bg: 'bg-cyber-red/5',
    glow: 'shadow-[0_0_20px_rgba(239,68,68,0.12)]',
    badge: 'bg-cyber-red/10 border-cyber-red/40 text-cyber-red',
    bar: 'bg-cyber-red',
  },
};

export const EmailScanner: React.FC = () => {
  const [rawEmail, setRawEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<EmailScanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);

    if (!rawEmail.trim()) {
      setError('Please paste or type email contents to analyze.');
      return;
    }

    setIsLoading(true);
    try {
      const data = await scanEmail({ raw_email: rawEmail });
      setResult(data);
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || 'Failed to analyze email content.';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const getRiskClass = () => {
    if (!result) return statusConfig.SAFE;
    return statusConfig[result.status] || statusConfig.SAFE;
  };

  const cfg = getRiskClass();
  const strokeDash = 283;
  const offset = result ? strokeDash - (strokeDash * result.score) / 100 : strokeDash;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-cyber-cyan/10 pb-4">
        <h3 className="text-sm font-mono font-bold uppercase tracking-wider text-white">
          Email Phishing Analyzer
        </h3>
        <p className="text-xs text-gray-400 font-mono mt-0.5">
          Paste the raw email header and body to scan for domain spoofing, suspicious links, and urgent language.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Side Input Form */}
        <div className="lg:col-span-2 space-y-4">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="relative group">
              <textarea
                value={rawEmail}
                onChange={(e) => {
                  setRawEmail(e.target.value);
                  if (error) setError(null);
                }}
                disabled={isLoading}
                rows={12}
                placeholder={`Paste email MIME text or body headers here...\n\nExample:\nFrom: support@chase-login-update.com\nSubject: Action Required: Account locked!\n\nPlease log in immediately to confirm billing details.`}
                className="w-full bg-cyber-black border border-gray-800 rounded-lg p-4 text-xs font-mono text-white focus:outline-none focus:border-cyber-cyan/50 focus:shadow-[0_0_10px_rgba(6,182,212,0.12)] transition-all resize-y disabled:opacity-50"
              />
            </div>

            <div className="flex justify-between items-center">
              <button
                type="button"
                onClick={() => {
                  setRawEmail(
                    "From: account-security@paypal-update.net\n" +
                    "Subject: URGENT: Action required to verify billing account\n" +
                    "Authentication-Results: spf=fail dkim=fail\n" +
                    "\n" +
                    "Immediate login required. We detected a suspicious billing charge on your account. " +
                    "Please verify your identity at http://fake-login-paypal.net/auth."
                  );
                }}
                className="text-[10px] font-mono text-gray-500 hover:text-cyber-cyan hover:underline transition-colors cursor-pointer"
              >
                Load Phishing Example
              </button>

              <button
                type="submit"
                disabled={isLoading}
                className="flex items-center gap-2 px-6 py-2.5 font-mono text-xs font-bold tracking-wider text-black bg-cyber-cyan hover:bg-cyber-neon-cyan rounded-lg shadow-[0_0_12px_rgba(6,182,212,0.3)] transition-all cursor-pointer disabled:opacity-50"
              >
                {isLoading ? 'ANALYZING...' : 'ANALYZE EMAIL'}
              </button>
            </div>
          </form>

          {error && (
            <div className="bg-cyber-red/5 border border-cyber-red/30 rounded-lg p-4 flex gap-3">
              <div className="text-cyber-red shrink-0 text-xs font-mono font-bold">ERROR</div>
              <p className="font-mono text-[10px] text-red-400">{error}</p>
            </div>
          )}

          {/* Results panel */}
          <AnimatePresence>
            {result && !isLoading && (
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className={`rounded-lg border ${cfg.border} ${cfg.bg} ${cfg.glow} p-6 space-y-6`}
              >
                <div className="flex justify-between items-center border-b border-gray-800/80 pb-3">
                  <div>
                    <h4 className="font-mono text-xs font-bold uppercase tracking-wider text-white">
                      Threat Risk Assessment
                    </h4>
                    <p className="font-mono text-[9px] text-gray-500 mt-0.5">
                      Sender: {result.sender || 'Unknown'} · Subject: {result.subject || 'No Subject'}
                    </p>
                  </div>
                  <span className={`px-2.5 py-1 rounded text-[9px] font-mono font-bold border tracking-widest ${cfg.badge}`}>
                    {cfg.label}
                  </span>
                </div>

                <div className="flex flex-col md:flex-row gap-6 items-center">
                  <div className="flex flex-col items-center shrink-0">
                    <svg width="90" height="90" className="-rotate-90">
                      <circle cx="45" cy="45" r="36" stroke="rgba(255,255,255,0.05)" strokeWidth="8" fill="none" />
                      <motion.circle
                        cx="45"
                        cy="45"
                        r="36"
                        stroke={result.status === 'CRITICAL' ? '#ef4444' : result.status === 'SUSPICIOUS' ? '#f59e0b' : '#10b981'}
                        strokeWidth="8"
                        fill="none"
                        strokeDasharray={strokeDash}
                        initial={{ strokeDashoffset: strokeDash }}
                        animate={{ strokeDashoffset: offset }}
                        transition={{ duration: 0.8, ease: 'easeOut' }}
                        strokeLinecap="round"
                      />
                    </svg>
                    <div className="-mt-16 flex flex-col items-center select-none">
                      <span className={`text-2xl font-extrabold font-mono ${cfg.color}`}>{result.score}</span>
                      <span className="text-[9px] font-mono text-gray-500">/ 100</span>
                    </div>
                    <span className="mt-2 text-[9px] font-mono text-gray-400 uppercase tracking-widest">Risk Score</span>
                  </div>

                  <div className="flex-1 w-full space-y-3">
                    <div>
                      <p className="font-mono text-[9px] text-gray-500 uppercase tracking-wider mb-1">Risk Summary</p>
                      <p className="font-mono text-[11px] text-gray-300 leading-relaxed">{result.explanation}</p>
                    </div>

                    <div>
                      <div className="flex justify-between font-mono text-[9px] text-gray-500 mb-1">
                        <span>Threat intensity</span>
                        <span>{result.score}%</span>
                      </div>
                      <div className="h-1.5 w-full bg-gray-900 rounded-full overflow-hidden">
                        <div className={`h-full rounded-full ${cfg.bar}`} style={{ width: `${result.score}%` }} />
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Right Side Indicators / Findings List */}
        <div className="space-y-4">
          <div className="border-b border-cyber-cyan/10 pb-3">
            <h4 className="font-mono text-xs font-bold uppercase tracking-wider text-white">Security Findings</h4>
            <p className="font-mono text-[9px] text-gray-500 mt-0.5">Scanned heuristics indicators</p>
          </div>

          <div className="space-y-3">
            {result ? (
              result.indicators.length > 0 ? (
                result.indicators.map((ind, i) => (
                  <div key={i} className="rounded-lg border border-gray-800 bg-cyber-dark-card/20 p-3.5 space-y-1">
                    <div className="flex items-center gap-1.5 font-mono text-[9px] font-bold text-cyber-red uppercase">
                      <span>⚑ HIGH RISK</span>
                    </div>
                    <p className="font-mono text-[10px] text-gray-300 leading-relaxed">{ind}</p>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 font-mono text-[10px] text-cyber-green">
                  ✓ Clean Scan: No threat indicators detected.
                </div>
              )
            ) : (
              <div className="text-center py-8 font-mono text-[10px] text-gray-650">
                Pasted email findings will populate here.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
