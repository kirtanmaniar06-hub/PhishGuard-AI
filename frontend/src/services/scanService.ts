/**
 * PhishGuard AI — Scan Service
 *
 * Wraps all API calls relating to URL/email scanning.
 */
import { apiClient } from './api';

export interface ScanResult {
  id: number;
  target: string;
  type: string;
  score: number;
  status: 'SAFE' | 'SUSPICIOUS' | 'CRITICAL';
  verdict: string;
  indicators: string[];
  created_at: string;
}

export interface ScanCreate {
  target: string;
  type?: string;
}

/** Submit a URL or email string for analysis. */
export const createScan = async (payload: ScanCreate): Promise<ScanResult> => {
  const { data } = await apiClient.post<ScanResult>('/scans/', payload);
  return data;
};

/** Fetch paginated scan history list. */
export const fetchScans = async (limit = 50): Promise<ScanResult[]> => {
  const { data } = await apiClient.get<ScanResult[]>('/scans/', {
    params: { limit },
  });
  return data;
};
