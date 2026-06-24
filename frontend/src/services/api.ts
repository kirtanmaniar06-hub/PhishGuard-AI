/**
 * PhishGuard AI — API Client
 *
 * Centralised axios instance pre-configured with the backend base URL.
 * All service modules import from here.
 */
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 15_000,
});
