/**
 * PhishGuard AI — Email Scanner Service
 *
 * Wraps Axios API client contracts for retrieving heuristic threat analysis
 * on pasted email contents.
 */

import { apiClient } from './api';
import type {
  EmailScanRequest,
  EmailScanResponse,
} from '../types/emailScanner';

/**
 * Submit pasted raw email content to be scanned for threat profile indicators.
 */
export const scanEmail = async (payload: EmailScanRequest): Promise<EmailScanResponse> => {
  const { data } = await apiClient.post<EmailScanResponse>('/email-scanner/scan', payload);
  return data;
};
