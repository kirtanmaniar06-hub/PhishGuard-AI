/**
 * PhishGuard AI — Email Scanner TypeScript Definitions
 */

export interface EmailScanRequest {
  raw_email: string;
}

export interface EmailScanResponse {
  score: number; // 0 to 100
  status: 'SAFE' | 'SUSPICIOUS' | 'CRITICAL';
  explanation: string;
  sender?: string;
  subject?: string;
  links: string[];
  keywords: string[];
  attachments: string[];
  indicators: string[];
}
