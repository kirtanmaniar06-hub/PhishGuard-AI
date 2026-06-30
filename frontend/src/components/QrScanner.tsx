/**
 * PhishGuard AI — QR Scanner Component
 *
 * Decodes QR code images client-side using jsQR, then runs backend heuristic
 * analysis on the decoded target URL to report threat statuses.
 */

import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import jsQR from 'jsqr';
import { createScan } from '../services/scanService';

interface ScanResult {
  score: number;
  status: 'SAFE' | 'SUSPICIOUS' | 'CRITICAL';
  analyzedTarget: string;
  verdict: string;
  indicators: string[];
}

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

export const QrScanner: React.FC = () => {
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [decodedText, setDecodedText] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    setDecodedText(null);
    setScanResult(null);
    
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result as string;
      setImagePreview(dataUrl);
      decodeQRFromDataUrl(dataUrl);
    };
    reader.readAsDataURL(file);
  };

  const decodeQRFromDataUrl = (dataUrl: string) => {
    setIsLoading(true);
    const img = new Image();
    img.src = dataUrl;
    img.onload = () => {
      try {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        if (!context) {
          setError('Failed to initialize canvas context.');
          setIsLoading(false);
          return;
        }

        canvas.width = img.width;
        canvas.height = img.height;
        context.drawImage(img, 0, 0, img.width, img.height);
        
        const imageData = context.getImageData(0, 0, img.width, img.height);
        const code = jsQR(imageData.data, imageData.width, imageData.height);

        if (code && code.data) {
          setDecodedText(code.data);
          analyzeDecodedUrl(code.data);
        } else {
          setError('Could not locate or decode QR code in the uploaded image.');
          setIsLoading(false);
        }
      } catch (err: any) {
        setError(`QR processing error: ${err.message}`);
        setIsLoading(false);
      }
    };
    img.onerror = () => {
      setError('Failed to load image file.');
      setIsLoading(false);
    };
  };

  const analyzeDecodedUrl = async (url: string) => {
    try {
      const data = await createScan({
        target: url,
        type: 'QR',
      });
      setScanResult({
        score: data.score,
        status: data.status,
        analyzedTarget: data.target,
        verdict: data.verdict,
        indicators: data.indicators,
      });
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || 'Failed to analyze target URL.';
      setError(`QR decoded target analysis failed: ${msg}`);
    } finally {
      setIsLoading(false);
    }
  };

  const resetScanner = () => {
    setImagePreview(null);
    setDecodedText(null);
    setScanResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const cfg = scanResult ? statusConfig[scanResult.status] : statusConfig.SAFE;
  const strokeDash = 283;
  const offset = scanResult ? strokeDash - (strokeDash * scanResult.score) / 100 : strokeDash;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-cyber-cyan/10 pb-4">
        <h3 className="text-sm font-mono font-bold uppercase tracking-wider text-white">
          QR Code Scan Analyzer
        </h3>
        <p className="text-xs text-gray-400 font-mono mt-0.5">
          Upload an image file containing a QR code to extract and run heuristic phishing analysis on the redirect destination URL.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Drag/Drop & Upload panel */}
        <div className="lg:col-span-1 space-y-4">
          <div
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-gray-800 hover:border-cyber-cyan/50 bg-cyber-dark-card/20 rounded-lg p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center min-h-[220px]"
          >
            <input
              type="file"
              ref={fileInputRef}
              accept="image/*"
              onChange={handleImageUpload}
              className="hidden"
            />
            {imagePreview ? (
              <div className="space-y-3">
                <img src={imagePreview} alt="Upload preview" className="max-h-40 mx-auto rounded border border-gray-800" />
                <p className="font-mono text-[9px] text-gray-500">Click to upload a different image</p>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="w-12 h-12 mx-auto rounded-full bg-cyber-cyan/5 border border-cyber-cyan/20 flex items-center justify-center">
                  <svg className="w-6 h-6 text-cyber-cyan/50" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                  </svg>
                </div>
                <p className="font-mono text-xs text-white">Choose QR Code Image</p>
                <p className="font-mono text-[9px] text-gray-500">Supports PNG, JPG, JPEG formats</p>
              </div>
            )}
          </div>

          {imagePreview && (
            <button
              onClick={resetScanner}
              className="w-full py-2.5 font-mono text-xs font-bold text-gray-400 hover:text-white border border-gray-800 hover:bg-cyber-dark-card/30 rounded-lg transition-all cursor-pointer"
            >
              CLEAR IMAGE
            </button>
          )}

          {isLoading && (
            <div className="rounded-lg border border-cyan-500/10 bg-cyber-dark-card/20 p-5 animate-pulse text-center">
              <span className="w-4 h-4 border-2 border-cyber-cyan border-t-transparent rounded-full animate-spin inline-block mr-2 align-middle" />
              <span className="font-mono text-xs text-cyber-cyan">Decoding and Vectorizing QR...</span>
            </div>
          )}

          {error && (
            <div className="bg-cyber-red/5 border border-cyber-red/30 rounded-lg p-4 flex gap-3">
              <div className="text-cyber-red shrink-0 text-xs font-mono font-bold">ERROR</div>
              <p className="font-mono text-[10px] text-red-400 leading-normal">{error}</p>
            </div>
          )}
        </div>

        {/* Right Scan Report Details panel */}
        <div className="lg:col-span-2 space-y-4">
          <AnimatePresence>
            {scanResult && decodedText && (
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className={`rounded-lg border ${cfg.border} ${cfg.bg} ${cfg.glow} p-6 space-y-6`}
              >
                <div className="flex justify-between items-center border-b border-gray-800 pb-3">
                  <div>
                    <h4 className="font-mono text-xs font-bold uppercase tracking-wider text-white">
                      QR Target Scan Report
                    </h4>
                    <p className="font-mono text-[10px] text-gray-400 mt-1 select-all break-all bg-cyber-black/40 px-2 py-1 rounded border border-gray-800/80">
                      Redirect URL: <strong className="text-white font-mono">{decodedText}</strong>
                    </p>
                  </div>
                  <span className={`px-2.5 py-1 rounded text-[9px] font-mono font-bold border tracking-widest ${cfg.badge} shrink-0 self-start`}>
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
                        stroke={scanResult.status === 'CRITICAL' ? '#ef4444' : scanResult.status === 'SUSPICIOUS' ? '#f59e0b' : '#10b981'}
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
                      <span className={`text-2xl font-extrabold font-mono ${cfg.color}`}>{scanResult.score}</span>
                      <span className="text-[9px] font-mono text-gray-500">/ 100</span>
                    </div>
                    <span className="mt-2 text-[9px] font-mono text-gray-400 uppercase tracking-widest">Risk Score</span>
                  </div>

                  <div className="flex-1 w-full space-y-4">
                    <div>
                      <p className="font-mono text-[9px] text-gray-500 uppercase tracking-wider mb-1">AI Verdict Analysis</p>
                      <p className="font-mono text-[11px] text-gray-300 leading-relaxed">{scanResult.verdict}</p>
                    </div>

                    <div>
                      <span className="font-mono text-[9px] text-gray-500 uppercase tracking-wider block mb-2">Target Risk Factors</span>
                      <div className="flex flex-wrap gap-1.5">
                        {scanResult.indicators.map((ind, i) => (
                          <span
                            key={i}
                            className={`text-[9px] font-mono px-2 py-0.5 rounded border ${
                              scanResult.status === 'CRITICAL'
                                ? 'bg-cyber-red/5 border-cyber-red/20 text-cyber-red'
                                : scanResult.status === 'SUSPICIOUS'
                                  ? 'bg-amber-500/5 border-amber-500/20 text-amber-400'
                                  : 'bg-cyber-green/5 border-cyber-green/20 text-cyber-green'
                            }`}
                          >
                            ❗ {ind}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {!scanResult && !isLoading && (
            <div className="border border-gray-900 bg-cyber-dark-card/10 rounded-lg p-8 text-center flex flex-col items-center justify-center min-h-[220px]">
              <svg className="w-8 h-8 text-gray-650 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-.778.099-1.533.284-2.253" />
              </svg>
              <p className="font-mono text-xs text-gray-500">No active scan — upload a QR Code image to decode redirect targets.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
