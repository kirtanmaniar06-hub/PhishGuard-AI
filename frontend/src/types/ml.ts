/**
 * PhishGuard AI — Machine Learning Types
 */

export interface ClassProbabilities {
  safe: number;
  phishing: number;
}

export interface FeatureImportanceItem {
  name: string;
  importance: number;
  value: number;
}

export interface MLPredictionResponse {
  url: string;
  prediction: 'phishing' | 'safe';
  confidence: number;
  probability: ClassProbabilities;
  important_features: FeatureImportanceItem[];
}

export interface MLPredictionRequest {
  url: string;
}

export interface MLEvaluationResponse {
  total_samples: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  confusion_matrix: {
    tp: number;
    fp: number;
    tn: number;
    fn: number;
  };
}
