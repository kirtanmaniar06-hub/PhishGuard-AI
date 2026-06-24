import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell
} from 'recharts';

// ─── MOCK DATA FOR CHARTS ───
const attackTimelineData = [
  { time: '00:00', attacks: 12, blocked: 12 },
  { time: '04:00', attacks: 8, blocked: 8 },
  { time: '08:00', attacks: 25, blocked: 24 },
  { time: '12:00', attacks: 42, blocked: 40 },
  { time: '16:00', attacks: 35, blocked: 35 },
  { time: '20:00', attacks: 19, blocked: 19 },
  { time: '24:00', attacks: 28, blocked: 27 },
];

const riskDistributionData = [
  { name: 'Credential Harvesting', value: 40, color: '#ef4444' }, // cyber-red
  { name: 'Malware Attachments', value: 25, color: '#f59e0b' },   // amber
  { name: 'Social Engineering', value: 20, color: '#3b82f6' },   // cyber-blue
  { name: 'Brand Impersonation', value: 10, color: '#06b6d4' },  // cyber-cyan
  { name: 'Clean / False Positives', value: 5, color: '#10b981' } // cyber-green
];

// ─── MOCK DATA FOR FEEDS & TABLES ───
const initialScansList = [
  { id: 'SCN-8492', target: 'http://secure-netbank-update.verify-auth.net/login', type: 'URL', score: 94, status: 'CRITICAL', time: '10 min ago' },
  { id: 'SCN-8491', target: 'Invoice_49202_Payment_Overdue.eml', type: 'EML File', score: 78, status: 'SUSPICIOUS', time: '25 min ago' },
  { id: 'SCN-8490', target: 'Urgent Action Required: CEO Wire Transfer.msg', type: 'MSG File', score: 88, status: 'CRITICAL', time: '1 hour ago' },
  { id: 'SCN-8489', target: 'https://paypal.com/signin', type: 'URL', score: 2, status: 'SAFE', time: '3 hours ago' },
  { id: 'SCN-8488', target: 'hr-portal-benefits-update.pdf', type: 'FILE', score: 45, status: 'SUSPICIOUS', time: '5 hours ago' },
  { id: 'SCN-8487', target: 'https://google.com', type: 'URL', score: 0, status: 'SAFE', time: '12 hours ago' },
  { id: 'SCN-8486', target: 'dhl-delivery-tracking-details.eml', type: 'EML File', score: 91, status: 'CRITICAL', time: '18 hours ago' },
  { id: 'SCN-8485', target: 'https://github.com/login', type: 'URL', score: 1, status: 'SAFE', time: '1 day ago' },
];

const intelligenceNews = [
  {
    tag: 'VULNERABILITY',
    title: 'CVE-2026-9041: Critical EML Parser Bug Exploited',
    desc: 'Attackers are bypassing gateway filters using malicious attachments structured with nested multipart headers.',
    time: '2 hours ago',
    color: 'text-cyber-red border-cyber-red/30 bg-cyber-red/5'
  },
  {
    tag: 'CAMPAIGN',
    title: 'OAuth Impersonation Targets CFOs',
    desc: 'Multi-stage OAuth request phishing lures finance users into delegating directory permissions to lookalike malicious domains.',
    time: '5 hours ago',
    color: 'text-amber-400 border-amber-500/30 bg-amber-500/5'
  },
  {
    tag: 'AI TRENDS',
    title: 'Adversarial LLM Generators on Dark Web',
    desc: 'Security researchers detect custom phishing generators configured to draft automated, highly localized phishing templates.',
    time: '1 day ago',
    color: 'text-cyber-cyan border-cyber-cyan/30 bg-cyber-cyan/5'
  }
];

export const Dashboard: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'CRITICAL' | 'SUSPICIOUS' | 'SAFE'>('ALL');
  const [selectedScanDetails, setSelectedScanDetails] = useState<any>(null);

  // Filter scan list
  const filteredScans = initialScansList.filter((scan) => {
    const matchesSearch = scan.target.toLowerCase().includes(searchTerm.toLowerCase()) || scan.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = statusFilter === 'ALL' || scan.status === statusFilter;
    return matchesSearch && matchesFilter;
  });

  // Risk Score Configuration
  const threatScore = 76;
  const strokeDashoffset = 440 - (440 * threatScore) / 100;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4 }}
      className="p-6 space-y-6 max-w-7xl mx-auto"
    >
      
      {/* ────────────────── SECTION 1: HEADER SUMMARY ────────────────── */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between border-b border-cyber-cyan/10 pb-5">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white font-mono uppercase">SECURITY CONTROL ROOM</h2>
          <p className="text-xs text-gray-400 font-mono mt-1">
            CORE_MODEL_VERSION: v3.2.1-NEURAL // STATUS: AUDITING_LIVE_FEED
          </p>
        </div>
        
        {/* Quick telemetry indicators */}
        <div className="flex flex-wrap gap-3 mt-4 md:mt-0 font-mono text-xs">
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded bg-cyber-red/5 border border-cyber-red/30 text-cyber-red">
            <span className="h-2 w-2 rounded-full bg-cyber-red animate-pulse" />
            <span>CRITICALS: 3</span>
          </div>
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded bg-cyber-cyan/5 border border-cyber-cyan/30 text-cyber-cyan">
            <span className="h-2 w-2 rounded-full bg-cyber-cyan animate-pulse" />
            <span>AI_CONFIDENCE: 98.4%</span>
          </div>
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded bg-cyber-green/5 border border-cyber-green/30 text-cyber-green">
            <span className="h-2 w-2 rounded-full bg-cyber-green" />
            <span>SANDBOX: ACTIVE</span>
          </div>
        </div>
      </div>

      {/* ────────────────── SECTION 2: SCORE / PIE / NEWS GRID ────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Widget 1: Threat Score Card */}
        <div className="bg-cyber-dark-card/40 border border-cyber-cyan/10 rounded-lg p-6 flex flex-col items-center justify-between min-h-[340px] relative overflow-hidden">
          <div className="absolute top-0 right-0 p-3 font-mono text-[9px] text-gray-500">SYS_SCORE_MODULE</div>
          
          <div className="w-full text-left">
            <h3 className="text-sm font-mono font-bold tracking-wider text-white uppercase">Overall Threat Index</h3>
            <p className="text-xs text-gray-400 font-mono mt-0.5">Weighted metric across all telemetry nodes</p>
          </div>

          {/* SVG Radial Gauge */}
          <div className="relative flex items-center justify-center my-4">
            <svg className="w-40 h-40 transform -rotate-90">
              {/* Background circle */}
              <circle
                cx="80"
                cy="80"
                r="70"
                stroke="rgba(12, 18, 32, 0.8)"
                strokeWidth="12"
                fill="transparent"
              />
              {/* Outer neon border track */}
              <circle
                cx="80"
                cy="80"
                r="70"
                stroke="rgba(6, 182, 212, 0.05)"
                strokeWidth="12"
                fill="transparent"
              />
              {/* Gauge line */}
              <motion.circle
                cx="80"
                cy="80"
                r="70"
                stroke={threatScore > 75 ? '#ef4444' : threatScore > 40 ? '#f59e0b' : '#10b981'}
                strokeWidth="12"
                fill="transparent"
                strokeDasharray="440"
                initial={{ strokeDashoffset: 440 }}
                animate={{ strokeDashoffset }}
                transition={{ duration: 1, ease: 'easeOut' }}
                strokeLinecap="round"
                className="drop-shadow-[0_0_8px_rgba(239,68,68,0.5)]"
              />
            </svg>
            
            {/* Center Label */}
            <div className="absolute flex flex-col items-center">
              <span className="text-4xl font-extrabold tracking-tight text-white font-mono">{threatScore}</span>
              <span className="text-[10px] font-mono tracking-widest text-cyber-red font-bold animate-pulse">CRITICAL RISK</span>
            </div>
          </div>

          <div className="w-full text-center border-t border-gray-800/60 pt-4 font-mono text-[11px] text-gray-400">
            <span>Threat status: <strong className="text-cyber-red">UNSTABLE</strong></span>
            <p className="text-[10px] text-gray-500 mt-1">Ingress signals are elevated. Immediate audit recommended.</p>
          </div>
        </div>

        {/* Widget 2: Risk Distribution Pie Chart */}
        <div className="bg-cyber-dark-card/40 border border-cyber-cyan/10 rounded-lg p-6 flex flex-col min-h-[340px] relative">
          <div className="absolute top-0 right-0 p-3 font-mono text-[9px] text-gray-500">DISTRIBUTION_DATA</div>
          
          <div className="mb-4">
            <h3 className="text-sm font-mono font-bold tracking-wider text-white uppercase">Threat Categories</h3>
            <p className="text-xs text-gray-400 font-mono mt-0.5">Classification of intercepted phishing vectors</p>
          </div>

          <div className="flex-1 flex items-center justify-center">
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={riskDistributionData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {riskDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0c1220',
                    borderColor: 'rgba(6, 182, 212, 0.3)',
                    color: '#f8fafc',
                    fontFamily: 'monospace',
                    fontSize: '11px',
                    borderRadius: '4px'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Legends */}
          <div className="grid grid-cols-2 gap-2 text-[10px] font-mono pt-4 border-t border-gray-800/60">
            {riskDistributionData.map((item, idx) => (
              <div key={idx} className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: item.color }} />
                <span className="text-gray-400 truncate">{item.name} ({item.value}%)</span>
              </div>
            ))}
          </div>
        </div>

        {/* Widget 3: Cyber Intelligence News Placeholder */}
        <div className="bg-cyber-dark-card/40 border border-cyber-cyan/10 rounded-lg p-6 flex flex-col min-h-[340px] relative">
          <div className="absolute top-0 right-0 p-3 font-mono text-[9px] text-gray-500">INTEL_FEED_LIVE</div>
          
          <div className="mb-4">
            <h3 className="text-sm font-mono font-bold tracking-wider text-white uppercase">Threat Intelligence</h3>
            <p className="text-xs text-gray-400 font-mono mt-0.5">Latest external threat indicators</p>
          </div>

          <div className="flex-1 space-y-3 overflow-y-auto max-h-[220px] pr-1">
            {intelligenceNews.map((news, idx) => (
              <div key={idx} className="p-3 rounded border border-gray-800 bg-cyber-black/40 hover:border-cyber-cyan/20 transition-all">
                <div className="flex justify-between items-center mb-1">
                  <span className={`text-[9px] font-mono font-bold border px-1.5 py-0.5 rounded ${news.color}`}>
                    {news.tag}
                  </span>
                  <span className="text-[9px] font-mono text-gray-500">{news.time}</span>
                </div>
                <h4 className="text-xs font-bold text-white leading-snug">{news.title}</h4>
                <p className="text-[10px] text-gray-400 mt-1 leading-relaxed">{news.desc}</p>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* ────────────────── SECTION 3: TIMELINE & RECENT SCANS ────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Widget 4: Attack Timeline Chart */}
        <div className="lg:col-span-2 bg-cyber-dark-card/40 border border-cyber-cyan/10 rounded-lg p-6 flex flex-col relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-cyber-cyan/1 to-transparent w-full h-[200%] pointer-events-none animate-scanline z-0" />
          <div className="absolute top-0 right-0 p-3 font-mono text-[9px] text-gray-500">TIME_SERIES_TELEMETRY</div>
          
          <div className="mb-6 relative z-10">
            <h3 className="text-sm font-mono font-bold tracking-wider text-white uppercase">Neural Threat Telemetry</h3>
            <p className="text-xs text-gray-400 font-mono mt-0.5">Comparison between total attacks vs blocked attempts</p>
          </div>

          <div className="h-64 w-full relative z-10">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={attackTimelineData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorAttacks" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.25}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorBlocked" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.25}/>
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.2} />
                <XAxis dataKey="time" stroke="#475569" fontSize={10} tickLine={false} />
                <YAxis stroke="#475569" fontSize={10} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0c1220',
                    borderColor: 'rgba(6, 182, 212, 0.3)',
                    color: '#f8fafc',
                    fontFamily: 'monospace',
                    fontSize: '11px',
                    borderRadius: '4px'
                  }}
                />
                <Area type="monotone" dataKey="attacks" stroke="#ef4444" strokeWidth={1.5} fillOpacity={1} fill="url(#colorAttacks)" name="Total Signals" />
                <Area type="monotone" dataKey="blocked" stroke="#06b6d4" strokeWidth={1.5} fillOpacity={1} fill="url(#colorBlocked)" name="Blocked Threats" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Widget 5: Recent Scans Stream */}
        <div className="bg-cyber-dark-card/40 border border-cyber-cyan/10 rounded-lg p-6 flex flex-col relative">
          <div className="absolute top-0 right-0 p-3 font-mono text-[9px] text-gray-500">REALTIME_STREAM</div>
          
          <div className="mb-4">
            <h3 className="text-sm font-mono font-bold tracking-wider text-white uppercase">Neural Ingress Stream</h3>
            <p className="text-xs text-gray-400 font-mono mt-0.5">Real-time alerts processed from integrations</p>
          </div>

          <div className="flex-1 space-y-3 overflow-y-auto max-h-[260px] pr-1">
            {initialScansList.slice(0, 4).map((scan, idx) => (
              <div
                key={idx}
                onClick={() => setSelectedScanDetails(scan)}
                className="p-3 rounded border border-gray-800 bg-cyber-black/40 hover:border-cyber-cyan/40 hover:bg-cyber-dark-card/25 cursor-pointer transition-all flex items-start justify-between space-x-3"
              >
                <div className="min-w-0 flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] font-mono text-cyber-cyan font-bold">{scan.id}</span>
                    <span className="text-[9px] font-mono text-gray-500">• {scan.type}</span>
                  </div>
                  <p className="text-xs text-white truncate font-mono mt-1">{scan.target}</p>
                  <span className="text-[9px] font-mono text-gray-500 block mt-1">{scan.time}</span>
                </div>
                
                <div className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${
                  scan.status === 'CRITICAL' 
                    ? 'bg-cyber-red/10 border-cyber-red/35 text-cyber-red shadow-[0_0_8px_rgba(239,68,68,0.15)]'
                    : scan.status === 'SUSPICIOUS'
                      ? 'bg-amber-500/10 border-amber-500/35 text-amber-400'
                      : 'bg-cyber-green/10 border-cyber-green/35 text-cyber-green'
                }`}>
                  {scan.score}%
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* ────────────────── SECTION 4: SCAN HISTORY TABLE ────────────────── */}
      <div className="bg-cyber-dark-card/30 border border-cyber-cyan/10 rounded-lg p-6 relative">
        <div className="absolute top-0 right-0 p-3 font-mono text-[9px] text-gray-500">DATABASE_RECORDS</div>
        
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
          <div>
            <h3 className="text-sm font-mono font-bold tracking-wider text-white uppercase">Complete Ingress Log</h3>
            <p className="text-xs text-gray-400 font-mono mt-0.5">Historical registry of analyzed vectors</p>
          </div>

          {/* Search and Filters */}
          <div className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              placeholder="Search target/ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-cyber-black border border-gray-800 rounded px-3 py-1.5 text-xs text-white font-mono focus:outline-none focus:border-cyber-cyan/40"
            />
            
            {/* Filter Pill switches */}
            <div className="flex bg-cyber-black border border-gray-800 rounded p-0.5 font-mono text-[10px]">
              {(['ALL', 'CRITICAL', 'SUSPICIOUS', 'SAFE'] as const).map((filter) => (
                <button
                  key={filter}
                  onClick={() => setStatusFilter(filter)}
                  className={`px-3 py-1 rounded cursor-pointer transition-all ${
                    statusFilter === filter
                      ? 'bg-cyber-cyan/10 border border-cyber-cyan/25 text-cyber-cyan font-bold'
                      : 'text-gray-400 hover:text-gray-200'
                  }`}
                >
                  {filter}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Table Body */}
        <div className="overflow-x-auto border border-gray-850 rounded-lg">
          <table className="w-full border-collapse font-mono text-xs text-left">
            <thead>
              <tr className="bg-cyber-dark-card/65 border-b border-gray-800 text-gray-400 uppercase tracking-widest text-[9.5px]">
                <th className="p-4">ID</th>
                <th className="p-4">Scan Target</th>
                <th className="p-4">Type</th>
                <th className="p-4">Threat Score</th>
                <th className="p-4">Classification</th>
                <th className="p-4">Timestamp</th>
                <th className="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-900 bg-cyber-black/20">
              {filteredScans.length > 0 ? (
                filteredScans.map((scan) => (
                  <tr key={scan.id} className="hover:bg-cyber-dark-card/10 transition-colors">
                    <td className="p-4 font-bold text-cyber-cyan">{scan.id}</td>
                    <td className="p-4 max-w-xs truncate text-white">{scan.target}</td>
                    <td className="p-4 text-gray-400">{scan.type}</td>
                    <td className="p-4 font-bold">{scan.score}%</td>
                    <td className="p-4">
                      <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold border ${
                        scan.status === 'CRITICAL'
                          ? 'bg-cyber-red/5 border-cyber-red/20 text-cyber-red'
                          : scan.status === 'SUSPICIOUS'
                            ? 'bg-amber-500/5 border-amber-500/20 text-amber-400'
                            : 'bg-cyber-green/5 border-cyber-green/20 text-cyber-green'
                      }`}>
                        {scan.status}
                      </span>
                    </td>
                    <td className="p-4 text-gray-500">{scan.time}</td>
                    <td className="p-4 text-right">
                      <button
                        onClick={() => setSelectedScanDetails(scan)}
                        className="px-2 py-1 text-[9px] font-bold text-cyber-cyan border border-cyber-cyan/30 rounded bg-cyber-cyan/5 hover:bg-cyber-cyan/15 transition-all cursor-pointer"
                      >
                        ANALYZE
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-gray-500">
                    NO RECORD MATCHES FILTER CRITERIA
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* ────────────────── DRAWER DETAILED MODAL OVERLAY ────────────────── */}
      {selectedScanDetails && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/85 backdrop-blur-sm" onClick={() => setSelectedScanDetails(null)} />
          
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="relative w-full max-w-lg bg-cyber-dark-card border border-cyber-cyan/30 rounded-lg p-6 shadow-2xl z-10 font-mono text-xs"
          >
            <div className="flex justify-between items-center border-b border-gray-800 pb-3 mb-4">
              <span className="text-cyber-cyan font-bold">ANALYSIS RECORD: {selectedScanDetails.id}</span>
              <button onClick={() => setSelectedScanDetails(null)} className="text-gray-400 hover:text-white cursor-pointer">
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <span className="text-gray-500 block">TARGET VECTOR:</span>
                <span className="text-white text-sm break-all font-bold">{selectedScanDetails.target}</span>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-gray-500 block">VECTOR TYPE:</span>
                  <span className="text-white">{selectedScanDetails.type}</span>
                </div>
                <div>
                  <span className="text-gray-500 block">TELEMETRY SCORE:</span>
                  <span className={`font-bold ${
                    selectedScanDetails.status === 'CRITICAL' ? 'text-cyber-red' : selectedScanDetails.status === 'SUSPICIOUS' ? 'text-amber-400' : 'text-cyber-green'
                  }`}>{selectedScanDetails.score}% ({selectedScanDetails.status})</span>
                </div>
              </div>
              <div>
                <span className="text-gray-500 block">TIMESTAMP:</span>
                <span className="text-white">{selectedScanDetails.time}</span>
              </div>
              
              <div className="p-3 bg-cyber-black rounded border border-gray-850">
                <span className="text-gray-500 block mb-1">AI INFRASTRUCTURE REPORT SUMMARY:</span>
                <p className="text-gray-300 leading-relaxed text-[11px]">
                  {selectedScanDetails.status === 'CRITICAL'
                    ? 'Neural NLP vectors confirm phishing pattern match. Malicious URI redirection discovered with 98.2% similarity coefficient. Recommendation: blacklist immediately.'
                    : selectedScanDetails.status === 'SUSPICIOUS'
                      ? 'Mild anomaly detected in headers. Urgent verbiage usage matches typical phishing patterns. SPF check verified, but domain age is under 30 days.'
                      : 'No anomaly signatures identified. Content, domains, and cryptographic signatures are aligned with standard whitelist entities.'
                  }
                </p>
              </div>
            </div>
            
            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setSelectedScanDetails(null)}
                className="px-4 py-2 text-black bg-cyber-cyan hover:bg-cyber-neon-cyan font-bold rounded transition-all cursor-pointer"
              >
                DISMISS REPORT
              </button>
            </div>
          </motion.div>
        </div>
      )}

    </motion.div>
  );
};
