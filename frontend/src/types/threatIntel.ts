/**
 * PhishGuard AI — Threat Intelligence TypeScript Types
 *
 * Defines models and response structures for VirusTotal, URLScan,
 * Google Safe Browsing, AbuseIPDB, and unified aggregated threat intelligence reports.
 */

export interface VirusTotalReport {
  resource: string;
  scan_id?: string;
  permalink?: string;
  harmless_count: number;
  malicious_count: number;
  suspicious_count: number;
  undetected_count: number;
  total_engines: number;
  reputation_score: number; // 0 to 100
  categories: string[];
  verdict: 'clean' | 'suspicious' | 'malicious' | 'unknown';
}

export interface UrlScanReport {
  url: string;
  uuid: string;
  scan_page_url: string;
  screenshot_url?: string;
  malicious: boolean;
  score: number; // 0 to 100
  domain: string;
  ip_address?: string;
  server?: string;
  country?: string;
  verdict: 'clean' | 'suspicious' | 'malicious' | 'unknown';
}

export interface SafeBrowsingReport {
  url: string;
  is_flagged: boolean;
  threat_types: string[];
  platform_types: string[];
  verdict: 'clean' | 'suspicious' | 'malicious' | 'unknown';
}

export interface AbuseIpDbReport {
  ip_address: string;
  is_public: boolean;
  ip_version: number;
  abuse_confidence_score: number; // 0 to 100;
  total_reports: number;
  last_reported_at?: string;
  country_code?: string;
  country_name?: string;
  isp?: string;
  domain?: string;
  usage_type?: string;
  verdict: 'clean' | 'suspicious' | 'malicious' | 'unknown';
}

export interface ThreatIntelReport {
  target: string;
  target_type: 'url' | 'ip';
  scanned_at: string; // ISO DateTime
  virustotal?: VirusTotalReport;
  urlscan?: UrlScanReport;
  safebrowsing?: SafeBrowsingReport;
  abuseipdb?: AbuseIpDbReport;
  summary_verdict: 'clean' | 'suspicious' | 'malicious' | 'unknown';
  max_reputation_score: number; // 0 to 100
}

export interface ThreatIntelScanRequest {
  target: string;
  engines?: string[];
}
