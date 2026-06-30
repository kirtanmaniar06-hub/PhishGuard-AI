/**
 * PhishGuard AI — Explanation Types
 */

export interface ExplanationRequest {
  url: string;
  verdict: string;
  heuristics: Record<string, any>;
  threat_intel: Record<string, any>;
}

export interface ExplanationResponse {
  explanation: string;
  provider: 'ai' | 'rules';
}
