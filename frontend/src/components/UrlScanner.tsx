/**
 * PhishGuard AI — URL Scanner Component
 *
 * Self-contained module that handles:
 *  - URL format validation (client-side regex)
 *  - Dispatch to backend /scans API via axios
 *  - Loading animation while waiting for response
 *  - Threat score + risk level result card
 *  - Error boundary display
 *  - History sidebar listing previous scans
 *  - Live Threat Intelligence API integration (VirusTotal, URLScan, GSB, AbuseIPDB)
 */

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { createScan, fetchScans, type ScanResult } from '../services/scanService';
import { scanTarget } from '../services/threatIntelService';
import { type ThreatIntelReport } from '../types/threatIntel';
import { predictUrl } from '../services/mlService';
import type { MLPredictionResponse } from '../types/ml';

/* ── Helpers ──────────────────────────────────────────── */
const URL_REGEX =
  /^(https?:\/\/)([\w-]+(\.[\w-]+)+)(:\d+)?(\/[\w\-.~:/?#[\]@!$&'()*+,;=%]*)?$/i;

const validateUrl = (value: string): string | null => {
  if (!value.trim()) return 'Please enter a URL to scan.';
  if (!URL_REGEX.test(value.trim()))
    return 'Invalid URL — must start with http:// or https:// and contain a valid domain.';
  return null;
};

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

function timeAgo(iso: string): string {
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

/* ── Sub-components ───────────────────────────────────── */

/** Animated radar / scanning indicator */
const ScanningRadar: React.FC = () => (
  <div className="flex flex-col items-center justify-center py-12 space-y-6">
    <div className="relative w-28 h-28">
      <span className="absolute inset-0 rounded-full border border-cyber-cyan/10 animate-ping" />
      <span className="absolute inset-3 rounded-full border border-cyber-cyan/20 animate-ping [animation-delay:0.3s]" />
      <span className="absolute inset-6 rounded-full border border-cyber-cyan/30 animate-pulse" />
      <div className="absolute inset-8 rounded-full border-[3px] border-cyber-cyan/20 border-t-cyber-cyan animate-spin" />
      <div className="absolute inset-0 flex items-center justify-center">
        <svg className="w-7 h-7 text-cyber-cyan animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      </div>
    </div>
    <div className="text-center space-y-1">
      <p className="font-mono text-xs text-cyber-cyan uppercase tracking-widest animate-pulse">
        Analyzing threat vector...
      </p>
      <p className="font-mono text-[10px] text-gray-500">
        Running heuristic checks · Inspecting domain · Parsing signals
      </p>
    </div>
  </div>
);

/** Circular skeleton shimmer for loading threat intel */
const ThreatIntelSkeleton: React.FC = () => (
  <div className="rounded-lg border border-cyan-500/10 bg-cyber-dark-card/20 p-6 space-y-5 animate-pulse">
    <div className="flex justify-between items-center border-b border-gray-800 pb-3">
      <div className="space-y-1.5">
        <div className="h-2.5 w-32 bg-gray-800 rounded" />
        <div className="h-2 w-48 bg-gray-900 rounded" />
      </div>
      <div className="h-5 w-16 bg-gray-800 rounded-full" />
    </div>
    <div className="flex gap-6 items-center">
      <div className="w-20 h-20 rounded-full bg-gray-800/60" />
      <div className="flex-1 space-y-3">
        <div className="h-2 w-full bg-gray-800 rounded" />
        <div className="h-2 w-5/6 bg-gray-800 rounded" />
        <div className="h-2 w-4/6 bg-gray-800 rounded" />
      </div>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="h-16 bg-gray-800/40 rounded border border-gray-900" />
      ))}
    </div>
  </div>
);

/** Result card shown after a successful scan */
const ScanResultCard: React.FC<{ result: ScanResult }> = ({ result }) => {
  const cfg = statusConfig[result.status] ?? statusConfig.SAFE;
  const strokeDash = 283; // 2π × 45
  const offset = strokeDash - (strokeDash * result.score) / 100;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className={`rounded-lg border ${cfg.border} ${cfg.bg} ${cfg.glow} p-6 space-y-5`}
    >
      {/* Header row */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="min-w-0">
          <p className="font-mono text-[9px] text-gray-500 uppercase tracking-widest">Scan Result · #{result.id}</p>
          <p className="text-xs text-white font-mono mt-0.5 truncate" title={result.target}>
            {result.target}
          </p>
        </div>
        <span className={`self-start sm:self-auto shrink-0 px-3 py-1 rounded-full text-[10px] font-mono font-bold border ${cfg.badge}`}>
          {cfg.label}
        </span>
      </div>

      {/* Score gauge + verdict */}
      <div className="flex flex-col sm:flex-row gap-6 items-start">
        {/* SVG circular gauge */}
        <div className="flex flex-col items-center shrink-0">
          <svg width="90" height="90" className="-rotate-90">
            <circle cx="45" cy="45" r="36" stroke="rgba(255,255,255,0.05)" strokeWidth="8" fill="none" />
            <motion.circle
              cx="45" cy="45" r="36"
              stroke={result.status === 'CRITICAL' ? '#ef4444' : result.status === 'SUSPICIOUS' ? '#f59e0b' : '#10b981'}
              strokeWidth="8"
              fill="none"
              strokeDasharray={strokeDash}
              initial={{ strokeDashoffset: strokeDash }}
              animate={{ strokeDashoffset: offset }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
              strokeLinecap="round"
              className="drop-shadow-[0_0_6px_currentColor]"
            />
          </svg>
          <div className="-mt-16 flex flex-col items-center pointer-events-none select-none">
            <span className={`text-2xl font-extrabold font-mono ${cfg.color}`}>{result.score}</span>
            <span className="text-[9px] font-mono text-gray-500">/ 100</span>
          </div>
          <span className="mt-2 text-[9px] font-mono text-gray-400 uppercase tracking-widest">Heuristic Score</span>
        </div>

        {/* Verdict + indicators */}
        <div className="flex-1 space-y-4 min-w-0">
          <div>
            <p className="font-mono text-[9px] text-gray-500 uppercase tracking-wider mb-1">Verdict</p>
            <p className="text-xs text-gray-200 leading-relaxed font-mono">{result.verdict}</p>
          </div>

          {result.indicators.length > 0 && (
            <div>
              <p className="font-mono text-[9px] text-gray-500 uppercase tracking-wider mb-2">Risk Indicators</p>
              <div className="flex flex-wrap gap-2">
                {result.indicators.map((ind, i) => (
                  <span key={i} className={`text-[9px] font-mono px-2 py-0.5 rounded border ${cfg.badge}`}>
                    ⚑ {ind}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Score bar */}
          <div>
            <div className="flex justify-between font-mono text-[9px] text-gray-500 mb-1">
              <span>Heuristic intensity</span>
              <span>{result.score}%</span>
            </div>
            <div className="h-1.5 w-full bg-gray-900 rounded-full overflow-hidden">
              <motion.div
                className={`h-full rounded-full ${cfg.bar}`}
                initial={{ width: 0 }}
                animate={{ width: `${result.score}%` }}
                transition={{ duration: 0.7, ease: 'easeOut' }}
              />
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

/** ML prediction skeleton loading states */
const MlSkeleton: React.FC = () => (
  <div className="rounded-lg border border-cyan-500/10 bg-cyber-dark-card/20 p-6 space-y-4 animate-pulse">
    <div className="flex justify-between items-center border-b border-gray-800 pb-3">
      <div className="space-y-1">
        <div className="h-3 w-40 bg-gray-800 rounded" />
        <div className="h-2 w-28 bg-gray-900 rounded" />
      </div>
      <div className="h-5 w-20 bg-gray-800 rounded" />
    </div>
    <div className="flex gap-6 items-center">
      <div className="w-16 h-16 rounded-full bg-gray-800" />
      <div className="flex-1 space-y-2">
        <div className="h-2 w-full bg-gray-800 rounded" />
        <div className="h-2 w-3/4 bg-gray-800 rounded" />
      </div>
    </div>
  </div>
);

/** Random Forest ML predictions details card */
const MlPredictionCard: React.FC<{ ml: MLPredictionResponse }> = ({ ml }) => {
  const isPhishing = ml.prediction === 'phishing';
  const confidencePercent = Math.round(ml.confidence * 100);

  let riskBadgeColor = 'bg-cyber-green/10 border-cyber-green/40 text-cyber-green';
  let statusText = 'SAFE';
  if (isPhishing) {
    riskBadgeColor = 'bg-cyber-red/10 border-cyber-red/40 text-cyber-red animate-pulse';
    statusText = 'CRITICAL PHISHING';
  } else if (confidencePercent < 70) {
    riskBadgeColor = 'bg-amber-500/10 border-amber-500/40 text-amber-400';
    statusText = 'SUSPICIOUS';
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="rounded-lg border border-cyber-cyan/15 bg-cyber-dark-card/30 p-6 space-y-6"
    >
      <div className="flex justify-between items-center border-b border-gray-800/80 pb-3">
        <div>
          <h4 className="font-mono text-xs font-bold uppercase tracking-wider text-white">
            Random Forest Phishing Predictor
          </h4>
          <p className="font-mono text-[9px] text-gray-500 mt-0.5">
            Machine Learning analysis · Real-time inference
          </p>
        </div>
        <span className={`px-2.5 py-1 rounded text-[9px] font-mono font-bold border tracking-widest ${riskBadgeColor}`}>
          {statusText}
        </span>
      </div>

      <div className="flex flex-col md:flex-row gap-6 items-center">
        {/* Confidence Gauge */}
        <div className="flex flex-col items-center shrink-0">
          <div className="relative w-20 h-20 flex items-center justify-center rounded-full bg-cyber-black border border-gray-800">
            <span className={`text-xl font-extrabold font-mono ${isPhishing ? 'text-cyber-red' : 'text-cyber-green'}`}>
              {confidencePercent}%
            </span>
          </div>
          <span className="mt-2 text-[9px] font-mono text-gray-400 uppercase tracking-widest">Confidence</span>
        </div>

        {/* Feature Importance List */}
        <div className="flex-1 w-full space-y-3">
          <p className="font-mono text-[9px] text-gray-500 uppercase tracking-wider">
            Important Prediction Features
          </p>
          <div className="space-y-2">
            {ml.important_features.map((feat) => {
              const formattedName = feat.name.replace(/_/g, ' ');
              const barWidth = Math.round(feat.importance * 100);
              return (
                <div key={feat.name} className="space-y-1">
                  <div className="flex justify-between font-mono text-[9px] text-gray-300">
                    <span className="capitalize">{formattedName}</span>
                    <span className="text-gray-550">
                      val: {feat.value} (imp: {barWidth}%)
                    </span>
                  </div>
                  <div className="h-1 w-full bg-gray-900 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${isPhishing ? 'bg-cyber-red' : 'bg-cyber-cyan'}`}
                      style={{ width: `${barWidth}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

/** Deep Threat Intelligence details panel */
const ThreatIntelDetailsCard: React.FC<{ intel: ThreatIntelReport }> = ({ intel }) => {
  const score = Math.round(intel.max_reputation_score);
  
  // Calculate status configurations dynamically based on score
  let statusKey: 'SAFE' | 'SUSPICIOUS' | 'CRITICAL' = 'SAFE';
  if (score >= 65 || intel.summary_verdict === 'malicious') {
    statusKey = 'CRITICAL';
  } else if (score >= 20 || intel.summary_verdict === 'suspicious') {
    statusKey = 'SUSPICIOUS';
  }
  
  const cfg = statusConfig[statusKey];
  const strokeDash = 283;
  const offset = strokeDash - (strokeDash * score) / 100;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="rounded-lg border border-cyber-cyan/15 bg-cyber-dark-card/30 p-6 space-y-6"
    >
      {/* Header */}
      <div className="flex justify-between items-center border-b border-gray-800/80 pb-3">
        <div>
          <h4 className="font-mono text-xs font-bold uppercase tracking-wider text-white">
            Threat Intelligence Telemetry
          </h4>
          <p className="font-mono text-[9px] text-gray-500 mt-0.5">
            Real-time querying · VT, URLScan, Safe Browsing, AbuseIPDB
          </p>
        </div>
        <span className={`px-2 py-0.5 rounded text-[9px] font-mono font-bold uppercase border tracking-widest ${cfg.badge}`}>
          {intel.summary_verdict}
        </span>
      </div>

      {/* Main Gauges */}
      <div className="flex flex-col sm:flex-row gap-6 items-center">
        <div className="flex flex-col items-center shrink-0">
          <svg width="84" height="84" className="-rotate-90">
            <circle cx="42" cy="42" r="33" stroke="rgba(255,255,255,0.03)" strokeWidth="6" fill="none" />
            <motion.circle
              cx="42"
              cy="42"
              r="33"
              stroke={statusKey === 'CRITICAL' ? '#ef4444' : statusKey === 'SUSPICIOUS' ? '#f59e0b' : '#10b981'}
              strokeWidth="6"
              fill="none"
              strokeDasharray={strokeDash}
              initial={{ strokeDashoffset: strokeDash }}
              animate={{ strokeDashoffset: offset }}
              transition={{ duration: 0.8 }}
              strokeLinecap="round"
            />
          </svg>
          <div className="-mt-15 flex flex-col items-center">
            <span className={`text-xl font-bold font-mono ${cfg.color}`}>{score}</span>
            <span className="text-[8px] font-mono text-gray-600">/ 100</span>
          </div>
          <span className="mt-2 text-[8px] font-mono text-gray-500 uppercase tracking-widest">Max Threat score</span>
        </div>

        <div className="flex-1 space-y-3 font-mono text-[10px] w-full">
          <div className="flex justify-between border-b border-gray-800/40 pb-1.5">
            <span className="text-gray-500">Scan Target:</span>
            <span className="text-white truncate max-w-[200px]" title={intel.target}>{intel.target}</span>
          </div>
          <div className="flex justify-between border-b border-gray-800/40 pb-1.5">
            <span className="text-gray-500">Target Vector:</span>
            <span className="text-cyber-cyan uppercase">{intel.target_type}</span>
          </div>
          <div className="flex justify-between border-b border-gray-800/40 pb-1.5">
            <span className="text-gray-500">Risk Profile:</span>
            <span className={`font-bold ${cfg.color}`}>{statusKey} RISK</span>
          </div>
          <div className="flex justify-between border-b border-gray-800/40 pb-1.5">
            <span className="text-gray-500">Aggregated Verdict:</span>
            <span className="text-white capitalize">{intel.summary_verdict}</span>
          </div>
        </div>
      </div>

      {/* Services Breakdowns */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
        
        {/* VirusTotal Widget */}
        <div className="p-3.5 rounded bg-cyber-black/35 border border-gray-800/60 flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-[10px] font-bold text-white font-mono">VirusTotal v3</span>
              {intel.virustotal ? (
                <span className={`text-[8px] px-1 py-0.2 rounded border font-mono uppercase ${
                  intel.virustotal.verdict === 'malicious' ? 'bg-red-500/10 text-red-400 border-red-500/30' :
                  intel.virustotal.verdict === 'suspicious' ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' :
                  'bg-green-500/10 text-green-400 border-green-500/30'
                }`}>
                  {intel.virustotal.verdict}
                </span>
              ) : (
                <span className="text-[8px] text-gray-600 font-mono">UNAVAILABLE</span>
              )}
            </div>
            {intel.virustotal ? (
              <div className="space-y-1 text-[9px] font-mono text-gray-400">
                <p>Reputation Score: <strong className="text-white">{intel.virustotal.reputation_score}%</strong></p>
                <p>Detections: <span className="text-red-400">{intel.virustotal.malicious_count}</span> / {intel.virustotal.total_engines} engines</p>
                <p>Clean / Undetected: {intel.virustotal.harmless_count + intel.virustotal.undetected_count}</p>
              </div>
            ) : (
              <p className="text-[9px] font-mono text-gray-500">No report available or engine key disabled.</p>
            )}
          </div>
          {intel.virustotal?.permalink && (
            <a
              href={intel.virustotal.permalink}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[9px] font-mono text-cyber-cyan hover:underline mt-3 inline-block self-start cursor-pointer"
            >
              View VT Analysis ↗
            </a>
          )}
        </div>

        {/* URLScan Widget */}
        <div className="p-3.5 rounded bg-cyber-black/35 border border-gray-800/60 flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-[10px] font-bold text-white font-mono">urlscan.io API</span>
              {intel.urlscan ? (
                <span className={`text-[8px] px-1 py-0.2 rounded border font-mono uppercase ${
                  intel.urlscan.verdict === 'malicious' ? 'bg-red-500/10 text-red-400 border-red-500/30' :
                  intel.urlscan.verdict === 'suspicious' ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' :
                  'bg-green-500/10 text-green-400 border-green-500/30'
                }`}>
                  {intel.urlscan.verdict}
                </span>
              ) : (
                <span className="text-[8px] text-gray-600 font-mono">UNAVAILABLE</span>
              )}
            </div>
            {intel.urlscan ? (
              <div className="space-y-1 text-[9px] font-mono text-gray-400">
                <p>Risk Score Index: <strong className="text-white">{intel.urlscan.score}/100</strong></p>
                <p>Server Hosting: {intel.urlscan.server || 'Unknown'}</p>
                <p>Host Region: {intel.urlscan.country || 'Unknown'} ({intel.urlscan.ip_address || 'No IP'})</p>
              </div>
            ) : (
              <p className="text-[9px] font-mono text-gray-500">No report available or engine key disabled.</p>
            )}
          </div>
          {intel.urlscan?.scan_page_url && (
            <a
              href={intel.urlscan.scan_page_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[9px] font-mono text-cyber-cyan hover:underline mt-3 inline-block self-start cursor-pointer"
            >
              View URLScan Page ↗
            </a>
          )}
        </div>

        {/* Google Safe Browsing Widget */}
        <div className="p-3.5 rounded bg-cyber-black/35 border border-gray-800/60 flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-[10px] font-bold text-white font-mono">Google Safe Browsing</span>
              {intel.safebrowsing ? (
                <span className={`text-[8px] px-1 py-0.2 rounded border font-mono uppercase ${
                  intel.safebrowsing.is_flagged ? 'bg-red-500/10 text-red-400 border-red-500/30' : 'bg-green-500/10 text-green-400 border-green-500/30'
                }`}>
                  {intel.safebrowsing.is_flagged ? 'FLAGGED' : 'CLEAN'}
                </span>
              ) : (
                <span className="text-[8px] text-gray-600 font-mono">UNAVAILABLE</span>
              )}
            </div>
            {intel.safebrowsing ? (
              <div className="space-y-1 text-[9px] font-mono text-gray-400">
                <p>Listed Flagged: <strong className={intel.safebrowsing.is_flagged ? 'text-cyber-red' : 'text-cyber-green'}>
                  {intel.safebrowsing.is_flagged ? 'YES' : 'NO'}
                </strong></p>
                {intel.safebrowsing.threat_types.length > 0 && (
                  <p className="text-red-300">Matches: {intel.safebrowsing.threat_types.join(', ')}</p>
                )}
              </div>
            ) : (
              <p className="text-[9px] font-mono text-gray-500">No report available or engine key disabled.</p>
            )}
          </div>
        </div>

        {/* AbuseIPDB Widget */}
        <div className="p-3.5 rounded bg-cyber-black/35 border border-gray-800/60 flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-[10px] font-bold text-white font-mono">AbuseIPDB IP Intel</span>
              {intel.abuseipdb ? (
                <span className={`text-[8px] px-1 py-0.2 rounded border font-mono uppercase ${
                  intel.abuseipdb.verdict === 'malicious' ? 'bg-red-500/10 text-red-400 border-red-500/30' :
                  intel.abuseipdb.verdict === 'suspicious' ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' :
                  'bg-green-500/10 text-green-400 border-green-500/30'
                }`}>
                  {intel.abuseipdb.verdict}
                </span>
              ) : (
                <span className="text-[8px] text-gray-600 font-mono">UNAVAILABLE</span>
              )}
            </div>
            {intel.abuseipdb ? (
              <div className="space-y-1 text-[9px] font-mono text-gray-400">
                <p>Abuse Confidence: <strong className="text-white">{intel.abuseipdb.abuse_confidence_score}%</strong></p>
                <p>Total Abuse Reports: <span className="text-cyber-red font-bold">{intel.abuseipdb.total_reports}</span> reports</p>
                <p className="truncate">ISP: {intel.abuseipdb.isp || 'Unknown'}</p>
                <p className="truncate">Resolved IP: {intel.abuseipdb.ip_address || 'Failed'}</p>
              </div>
            ) : (
              <p className="text-[9px] font-mono text-gray-500">No report available or engine key disabled.</p>
            )}
          </div>
        </div>

      </div>
    </motion.div>
  );
};

/** Single history item row */
const HistoryItem: React.FC<{ scan: ScanResult; onClick: () => void; active: boolean }> = ({
  scan, onClick, active,
}) => {
  const cfg = statusConfig[scan.status] ?? statusConfig.SAFE;
  return (
    <button
      onClick={onClick}
      className={`w-full text-left px-3 py-2.5 rounded-lg border transition-all group ${
        active
          ? `${cfg.border} ${cfg.bg}`
          : 'border-transparent hover:border-gray-800 hover:bg-cyber-dark-card/20'
      }`}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="font-mono text-[10px] text-cyber-cyan font-bold shrink-0">#{scan.id}</span>
        <span className={`font-mono text-[9px] font-bold border px-1.5 py-0.5 rounded shrink-0 ${cfg.badge}`}>
          {scan.status}
        </span>
      </div>
      <p className="font-mono text-[10px] text-gray-300 truncate mt-0.5" title={scan.target}>
        {scan.target}
      </p>
      <p className="font-mono text-[9px] text-gray-600 mt-0.5">{timeAgo(scan.created_at)}</p>
    </button>
  );
};

/* ── Main Component ───────────────────────────────────── */
export const UrlScanner: React.FC = () => {
  const [url, setUrl] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [history, setHistory] = useState<ScanResult[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [selectedHistory, setSelectedHistory] = useState<ScanResult | null>(null);

  // Threat Intelligence state
  const [intelResult, setIntelResult] = useState<ThreatIntelReport | null>(null);
  const [intelLoading, setIntelLoading] = useState(false);
  const [intelError, setIntelError] = useState<string | null>(null);

  // Machine Learning state
  const [mlResult, setMlResult] = useState<MLPredictionResponse | null>(null);
  const [mlLoading, setMlLoading] = useState(false);
  const [mlError, setMlError] = useState<string | null>(null);

  /* Load history on mount */
  const loadHistory = useCallback(async () => {
    setHistoryLoading(true);
    try {
      const data = await fetchScans(30);
      setHistory(data);
    } catch {
      // History load failure is non-critical; silently ignore
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  useEffect(() => { loadHistory(); }, [loadHistory]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError(null);
    setResult(null);
    setSelectedHistory(null);
    setIntelResult(null);
    setIntelError(null);
    setMlResult(null);
    setMlError(null);

    // Client-side validation
    const err = validateUrl(url);
    if (err) {
      setValidationError(err);
      return;
    }
    setValidationError(null);

    setIsLoading(true);
    setIntelLoading(true);
    setMlLoading(true);

    try {
      const data = await createScan({ target: url.trim(), type: 'URL' });
      setResult(data);
      setUrl('');
      // Refresh history list
      loadHistory();
    } catch (error: any) {
      const msg =
        error?.response?.data?.detail ||
        error?.message ||
        'Unable to reach the backend. Ensure the API server is running on port 8000.';
      setApiError(msg);
    } finally {
      setIsLoading(false);
    }

    try {
      const intelData = await scanTarget({ target: url.trim() });
      setIntelResult(intelData);
    } catch (error: any) {
      const msg =
        error?.response?.data?.detail ||
        error?.message ||
        'Failed to query external threat intelligence.';
      setIntelError(msg);
    } finally {
      setIntelLoading(false);
    }

    try {
      const mlData = await predictUrl({ url: url.trim() });
      setMlResult(mlData);
    } catch (error: any) {
      const msg =
        error?.response?.data?.detail ||
        error?.message ||
        'Failed to query machine learning classifier.';
      setMlError(msg);
    } finally {
      setMlLoading(false);
    }
  };

  const displayedResult = selectedHistory ?? result;

  return (
    <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">

      {/* ── LEFT PANEL: Input + Result ── */}
      <div className="xl:col-span-2 space-y-5">

        {/* Section header */}
        <div className="border-b border-cyber-cyan/10 pb-4">
          <h3 className="text-sm font-mono font-bold uppercase tracking-wider text-white">
            URL Threat Intelligence Scanner
          </h3>
          <p className="text-xs text-gray-400 font-mono mt-0.5">
            Submit a URL to run heuristic analysis — no ML required
          </p>
        </div>

        {/* Input form */}
        <form onSubmit={handleSubmit} noValidate className="space-y-3">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1 relative group">
              {/* prefix indicator */}
              <span className="absolute left-3 top-1/2 -translate-y-1/2 font-mono text-[10px] text-cyber-cyan/60 select-none pointer-events-none">
                URL›
              </span>
              <input
                id="url-scanner-input"
                type="url"
                value={url}
                onChange={(e) => {
                  setUrl(e.target.value);
                  if (validationError) setValidationError(null);
                  if (apiError) setApiError(null);
                }}
                placeholder="https://example-suspicious-login.xyz"
                disabled={isLoading}
                className={`w-full bg-cyber-black border rounded-lg pl-12 pr-4 py-3 text-sm text-white font-mono
                  focus:outline-none transition-all duration-200 disabled:opacity-50
                  ${validationError
                    ? 'border-cyber-red/60 focus:border-cyber-red focus:shadow-[0_0_8px_rgba(239,68,68,0.2)]'
                    : 'border-gray-800 focus:border-cyber-cyan/50 focus:shadow-[0_0_10px_rgba(6,182,212,0.12)]'
                  }
                `}
              />
            </div>

            <button
              id="url-scan-submit"
              type="submit"
              disabled={isLoading}
              className="shrink-0 flex items-center justify-center gap-2 px-6 py-3 font-mono text-xs font-bold
                tracking-wider text-black bg-cyber-cyan hover:bg-cyber-neon-cyan
                rounded-lg shadow-[0_0_12px_rgba(6,182,212,0.3)] hover:shadow-[0_0_20px_rgba(0,240,255,0.5)]
                transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
            >
              {isLoading ? (
                <>
                  <span className="w-3.5 h-3.5 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                  SCANNING
                </>
              ) : (
                <>
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M11 19a8 8 0 100-16 8 8 0 000 16z" />
                  </svg>
                  SCAN URL
                </>
              )}
            </button>
          </div>

          {/* Validation error */}
          <AnimatePresence>
            {validationError && (
              <motion.p
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="font-mono text-[10px] text-cyber-red flex items-center gap-1.5"
              >
                <svg className="w-3 h-3 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                {validationError}
              </motion.p>
            )}
          </AnimatePresence>

          {/* Example inputs */}
          <div className="flex flex-wrap gap-2 pt-1">
            <span className="font-mono text-[9px] text-gray-600 self-center">Try:</span>
            {[
              'https://secure-login-paypal.xyz/update',
              'https://github.com',
              'http://bank-verify.temp-site.click/auth',
            ].map((ex) => (
              <button
                key={ex}
                type="button"
                onClick={() => { setUrl(ex); setValidationError(null); setApiError(null); }}
                className="font-mono text-[9px] text-gray-500 hover:text-cyber-cyan hover:underline transition-colors cursor-pointer"
              >
                {ex}
              </button>
            ))}
          </div>
        </form>

        {/* Loading animation */}
        <AnimatePresence>
          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="bg-cyber-dark-card/40 border border-cyber-cyan/10 rounded-lg"
            >
              <ScanningRadar />
            </motion.div>
          )}
        </AnimatePresence>

        {/* API error */}
        <AnimatePresence>
          {apiError && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="bg-cyber-red/5 border border-cyber-red/30 rounded-lg p-4 flex gap-3"
            >
              <svg className="w-5 h-5 text-cyber-red shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div>
                <p className="font-mono text-xs text-cyber-red font-bold">HEURISTIC_SCAN_FAILURE</p>
                <p className="font-mono text-[10px] text-red-400/80 mt-0.5">{apiError}</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Scan result / selected history */}
        <AnimatePresence>
          {displayedResult && !isLoading && (
            <div className="space-y-4">
              <ScanResultCard result={displayedResult} />
              
              {/* Dynamic Machine Learning Prediction Panel */}
              {mlLoading && <MlSkeleton />}
              
              {mlError && (
                <div className="bg-cyber-red/5 border border-cyber-red/20 rounded-lg p-4 flex gap-3">
                  <svg className="w-5 h-5 text-cyber-red shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <div>
                    <p className="font-mono text-xs text-cyber-red font-bold">ML_INFERENCE_FAILURE</p>
                    <p className="font-mono text-[9px] text-red-400/80 mt-0.5">{mlError}</p>
                  </div>
                </div>
              )}

              {mlResult && !mlLoading && (
                <MlPredictionCard ml={mlResult} />
              )}
              
              {/* Dynamic Threat Intelligence Sub-state Panel */}
              {intelLoading && <ThreatIntelSkeleton />}
              
              {intelError && (
                <div className="bg-cyber-red/5 border border-cyber-red/20 rounded-lg p-4 flex gap-3">
                  <svg className="w-5 h-5 text-cyber-red shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <div>
                    <p className="font-mono text-xs text-cyber-red font-bold">THREAT_INTEL_LOOKUP_FAILURE</p>
                    <p className="font-mono text-[9px] text-red-400/80 mt-0.5">{intelError}</p>
                  </div>
                </div>
              )}

              {intelResult && !intelLoading && (
                <ThreatIntelDetailsCard intel={intelResult} />
              )}
            </div>
          )}
        </AnimatePresence>

        {/* Placeholder when nothing shown yet */}
        {!isLoading && !displayedResult && !apiError && (
          <div className="bg-cyber-dark-card/20 border border-gray-900 rounded-lg p-8 text-center space-y-3">
            <div className="w-12 h-12 mx-auto rounded-full bg-cyber-cyan/5 border border-cyber-cyan/20 flex items-center justify-center">
              <svg className="w-6 h-6 text-cyber-cyan/50" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M11 19a8 8 0 100-16 8 8 0 000 16z" />
              </svg>
            </div>
            <p className="font-mono text-xs text-gray-500">No scan results yet — enter a URL above to begin analysis.</p>
          </div>
        )}
      </div>

      {/* ── RIGHT PANEL: History ── */}
      <div className="space-y-4">
        <div className="flex items-center justify-between border-b border-cyber-cyan/10 pb-3">
          <div>
            <h4 className="font-mono text-xs font-bold uppercase tracking-wider text-white">Scan History</h4>
            <p className="font-mono text-[9px] text-gray-500 mt-0.5">Latest {history.length} records</p>
          </div>
          <button
            onClick={loadHistory}
            disabled={historyLoading}
            title="Refresh history"
            className="p-1.5 text-gray-500 hover:text-cyber-cyan rounded-lg hover:bg-cyber-dark-card/30 transition-all disabled:opacity-40 cursor-pointer"
          >
            <svg className={`w-4 h-4 ${historyLoading ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>

        <div className="space-y-1.5 max-h-[520px] overflow-y-auto pr-1">
          {historyLoading && !history.length ? (
            <div className="py-6 text-center font-mono text-[10px] text-gray-600 animate-pulse">Loading history...</div>
          ) : history.length === 0 ? (
            <div className="py-6 text-center font-mono text-[10px] text-gray-600">No scan history found.</div>
          ) : (
            history.map((scan) => (
              <HistoryItem
                key={scan.id}
                scan={scan}
                active={selectedHistory?.id === scan.id}
                onClick={async () => {
                  if (scan.id === selectedHistory?.id) {
                    setSelectedHistory(null);
                    setIntelResult(null);
                    setIntelError(null);
                    setMlResult(null);
                    setMlError(null);
                  } else {
                    setSelectedHistory(scan);
                    setResult(null);
                    setIntelResult(null);
                    setIntelError(null);
                    setMlResult(null);
                    setMlError(null);
                    
                    // Fetch threat intel on-demand for selected history item
                    setIntelLoading(true);
                    try {
                      const intelData = await scanTarget({ target: scan.target });
                      setIntelResult(intelData);
                    } catch (error: any) {
                      const msg =
                        error?.response?.data?.detail ||
                        error?.message ||
                        'Failed to query external threat intelligence.';
                      setIntelError(msg);
                    } finally {
                      setIntelLoading(false);
                    }

                    // Fetch ML prediction on-demand for selected history item
                    setMlLoading(true);
                    try {
                      const mlData = await predictUrl({ url: scan.target });
                      setMlResult(mlData);
                    } catch (error: any) {
                      const msg =
                        error?.response?.data?.detail ||
                        error?.message ||
                        'Failed to query machine learning classifier.';
                      setMlError(msg);
                    } finally {
                      setMlLoading(false);
                    }
                  }
                }}
              />
            ))
          )}
        </div>
      </div>

    </div>
  );
};
