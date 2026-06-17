import React from 'react';
import { motion } from 'framer-motion';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';

const mockData = [
  { time: '00:00', threats: 12 },
  { time: '04:00', threats: 8 },
  { time: '08:00', threats: 25 },
  { time: '12:00', threats: 42 },
  { time: '16:00', threats: 35 },
  { time: '20:00', threats: 19 },
  { time: '24:00', threats: 28 },
];

export const Dashboard: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-8 p-6 lg:p-8"
    >
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between border-b border-cyber-cyan/10 pb-5">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white m-0">Security Command Center</h1>
          <p className="text-sm text-gray-400 font-mono mt-1">
            ENDPOINT_NODE: SEC-MAIN-01 // SECURITY_LEVEL: HIGH
          </p>
        </div>
        <div className="mt-4 md:mt-0 flex items-center space-x-3 font-mono text-xs">
          <span className="bg-cyber-red/10 border border-cyber-red/30 text-cyber-red px-3 py-1.5 rounded animate-pulse">
            CRITICAL_ALERTS: 2
          </span>
          <span className="bg-cyber-cyan/10 border border-cyber-cyan/30 text-cyber-cyan px-3 py-1.5 rounded">
            DATABASE: SECURE
          </span>
        </div>
      </div>

      {/* Grid Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[
          { title: 'Security Posture', value: '98.4%', change: '+0.2% vs yesterday', color: 'text-cyber-cyan', border: 'border-cyber-cyan/25' },
          { title: 'Simulations Executed', value: '1,248', change: '15 Active campaigns', color: 'text-cyber-blue-dark', border: 'border-cyber-blue/25' },
          { title: 'Phishing Intercepts', value: '432', change: '+12.4% network threat', color: 'text-cyber-red', border: 'border-cyber-red/25' },
          { title: 'Agent Training Rate', value: '92.1%', change: 'Target 95% compliance', color: 'text-cyber-green', border: 'border-cyber-green/25' }
        ].map((card, idx) => (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1, duration: 0.4 }}
            className={`bg-cyber-dark-card/50 p-6 rounded-lg border ${card.border} hover:shadow-[0_0_15px_rgba(6,182,212,0.1)] transition-all`}
          >
            <h3 className="text-xs font-mono tracking-widest text-gray-400 uppercase">{card.title}</h3>
            <p className={`text-3xl font-bold mt-2 ${card.color}`}>{card.value}</p>
            <span className="text-[11px] font-mono text-gray-500 block mt-1">{card.change}</span>
          </motion.div>
        ))}
      </div>

      {/* Charts & Diagnostics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Network Threat Activity Chart */}
        <div className="lg:col-span-2 bg-cyber-dark-card/40 p-6 rounded-lg border border-cyber-cyan/10 cyber-grid relative overflow-hidden">
          {/* Scanline Effect */}
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-cyber-cyan/2 to-transparent w-full h-[200%] pointer-events-none animate-scanline z-0" />
          
          <div className="relative z-10 flex items-center justify-between mb-6">
            <div>
              <h3 className="text-md font-semibold text-white">Network Threat activity</h3>
              <p className="text-xs text-gray-400 font-mono">Real-time packet intrusion telemetry</p>
            </div>
            <span className="text-xs font-mono text-cyber-cyan bg-cyber-cyan/5 border border-cyber-cyan/20 px-2 py-0.5 rounded">
              LIVE_STREAM
            </span>
          </div>

          <div className="h-72 relative z-10">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={mockData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorThreats" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.3} />
                <XAxis dataKey="time" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0a0f1d',
                    borderColor: 'rgba(6, 182, 212, 0.3)',
                    color: '#f8fafc',
                    fontFamily: 'monospace',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="threats"
                  stroke="#06b6d4"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorThreats)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Console Log Logins / Audits */}
        <div className="bg-cyber-dark-card/40 p-6 rounded-lg border border-cyber-blue/15 flex flex-col">
          <h3 className="text-md font-semibold text-white mb-2">Live Agent logs</h3>
          <p className="text-xs text-gray-400 font-mono mb-4">Real-time training & audit events</p>
          
          <div className="flex-1 space-y-3 font-mono text-xs overflow-y-auto max-h-72">
            {[
              { time: '13:02:11', event: 'SIM_AGENT_DEPLOYED', detail: 'ID: 4122x', status: 'OK', color: 'text-cyber-cyan' },
              { time: '13:01:45', event: 'PHISH_ATTEMPT_BLOCKED', detail: 'ip: 184.23.11.9', status: 'WARN', color: 'text-cyber-red' },
              { time: '12:59:02', event: 'DB_SYNC_COMPLETE', detail: 'checksum: 0x8F2', status: 'OK', color: 'text-cyber-green' },
              { time: '12:55:18', event: 'USER_COMPLIANCE_PASS', detail: 'Employee ID: 9402', status: 'OK', color: 'text-cyber-green' },
              { time: '12:51:30', event: 'CRITICAL_CVE_SCANNED', detail: 'CVE-2026-9041', status: 'INFO', color: 'text-cyber-blue-dark' }
            ].map((log, idx) => (
              <div key={idx} className="p-2.5 rounded bg-cyber-black/50 border border-gray-900 flex justify-between items-start space-x-2">
                <div>
                  <span className="text-gray-500 text-[10px] block">{log.time}</span>
                  <span className="text-white font-bold block">{log.event}</span>
                  <span className="text-gray-400 text-[10px] block">{log.detail}</span>
                </div>
                <span className={`text-[10px] px-1.5 py-0.5 rounded bg-gray-900 border border-gray-800 ${log.color}`}>
                  {log.status}
                </span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </motion.div>
  );
};
