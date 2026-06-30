/**
 * PhishGuard AI — Machine Learning Service
 *
 * Wraps Axios API client contracts for retrieving Random Forest classifier
 * prediction results and model metrics from the backend.
 */

import { apiClient } from './api';
import type {
  MLPredictionRequest,
  MLPredictionResponse,
  MLEvaluationResponse,
} from '../types/ml';

/**
 * Run Random Forest prediction on the target URL.
 */
export const predictUrl = async (payload: MLPredictionRequest): Promise<MLPredictionResponse> => {
  const { data } = await apiClient.post<MLPredictionResponse>('/ml/predict', payload);
  return data;
};

/**
 * Fetch validation metrics of the current model.
 */
export const fetchModelMetrics = async (): Promise<MLEvaluationResponse> => {
  const { data } = await apiClient.get<MLEvaluationResponse>('/ml/evaluate');
  return data;
};
