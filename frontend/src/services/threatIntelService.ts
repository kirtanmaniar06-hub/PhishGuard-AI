/**
 * PhishGuard AI — Threat Intelligence Service
 *
 * Wraps Axios API client contracts for retrieving threat intelligence reports
 * from VirusTotal, URLScan, Google Safe Browsing, and AbuseIPDB.
 */

import { apiClient } from './api';
import type {
  ThreatIntelScanRequest,
  ThreatIntelReport,
  VirusTotalReport,
  UrlScanReport,
  SafeBrowsingReport,
  AbuseIpDbReport,
} from '../types/threatIntel';

/**
 * Submit a URL or IP to be scanned across multiple threat intelligence sources.
 */
export const scanTarget = async (payload: ThreatIntelScanRequest): Promise<ThreatIntelReport> => {
  const { data } = await apiClient.post<ThreatIntelReport>('/threat-intel/scan', payload);
  return data;
};

/**
 * Fetch the configuration readiness status of all integrated intelligence engine providers.
 */
export const fetchEngines = async (): Promise<Record<string, boolean>> => {
  const { data } = await apiClient.get<Record<string, boolean>>('/threat-intel/engines');
  return data;
};

/**
 * Query VirusTotal API reputation reports for a specific URL, domain, or IP address.
 */
export const fetchVirusTotal = async (resource: string): Promise<VirusTotalReport> => {
  const encodedResource = encodeURIComponent(resource);
  const { data } = await apiClient.get<VirusTotalReport>(`/threat-intel/virustotal/${encodedResource}`);
  return data;
};

/**
 * Fetch detailed page analysis results from urlscan.io using a past scan UUID.
 */
export const fetchUrlScan = async (uuid: string): Promise<UrlScanReport> => {
  const { data } = await apiClient.get<UrlScanReport>(`/threat-intel/urlscan/${uuid}`);
  return data;
};

/**
 * Verify URL reputation against Google Safe Browsing threat lists.
 */
export const checkSafeBrowsing = async (url: string): Promise<SafeBrowsingReport> => {
  const { data } = await apiClient.post<SafeBrowsingReport>('/threat-intel/safebrowsing/check', null, {
    params: { url },
  });
  return data;
};

/**
 * Query AbuseIPDB IP reputation and abuse score for an IP address.
 */
export const fetchAbuseIpDb = async (ip: string): Promise<AbuseIpDbReport> => {
  const { data } = await apiClient.get<AbuseIpDbReport>(`/threat-intel/abuseipdb/${ip}`);
  return data;
};
