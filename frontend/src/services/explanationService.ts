/**
 * PhishGuard AI — Explanation Service
 *
 * Wraps Axios API client contracts for retrieving natural language explanation
 * reasons explaining security predictions.
 */

import { apiClient } from './api';
import type {
  ExplanationRequest,
  ExplanationResponse,
} from '../types/explanation';

/**
 * Fetch explanation reasons for a URL threat verdict.
 */
export const fetchExplanation = async (
  payload: ExplanationRequest
): Promise<ExplanationResponse> => {
  const { data } = await apiClient.post<ExplanationResponse>('/explanation/explain', payload);
  return data;
};
