"""
PhishGuard AI — Email Threat Analyzer Component

Performs heuristic evaluation of parsed components to discover threat indicators.
"""

import re
from typing import Dict, Any, List
from urllib.parse import urlparse


class EmailAnalyzer:
    """
    Evaluates parsed email features for potential social engineering or phishing markers.
    """

    HIGH_RISK_ATTACHMENT_EXTENSIONS = (".exe", ".bat", ".scr", ".zip", ".html", ".htm", ".vbs", ".js")
    FREE_EMAIL_DOMAINS = ("gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "icloud.com")

    def analyze(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyzes parser results and yields list of detected threat indicators.
        """
        indicators = []

        sender = parsed_data.get("sender", "")
        subject = parsed_data.get("subject", "")
        headers = parsed_data.get("headers", {})
        links = parsed_data.get("links", [])
        keywords = parsed_data.get("keywords", [])
        attachments = parsed_data.get("attachments", [])

        # 1. Analyze Sender Domain & Brand impersonation
        sender_email = self._extract_email_address(sender)
        sender_domain = sender_email.split("@")[-1].lower() if "@" in sender_email else ""

        # Impersonation heuristic: check if subject or body mentions trusted brands, but sender uses free email domain
        has_free_sender = sender_domain in self.FREE_EMAIL_DOMAINS
        if has_free_sender:
            indicators.append({
                "category": "sender",
                "severity": "suspicious",
                "message": f"Sender uses a public free email domain ('{sender_domain}') instead of an official organization domain."
            })

        # 2. Analyze SPF / DKIM Authentication Headers
        auth_results = headers.get("authentication-results", "")
        dkim_header = headers.get("dkim-signature", "")
        
        if auth_results:
            auth_lower = auth_results.lower()
            if "spf=fail" in auth_lower:
                indicators.append({
                    "category": "headers",
                    "severity": "critical",
                    "message": "SPF validation failed — the sending server is not authorized by the sender's domain policy."
                })
            if "dkim=fail" in auth_lower:
                indicators.append({
                    "category": "headers",
                    "severity": "critical",
                    "message": "DKIM signature validation failed — the message contents may have been altered during transit."
                })
        elif sender_domain and not dkim_header and not has_free_sender:
            indicators.append({
                "category": "headers",
                "severity": "suspicious",
                "message": "Missing DKIM signature header — email origin authentication cannot be cryptographically verified."
            })

        # 3. Analyze Links / URLs
        if links:
            indicators.append({
                "category": "links",
                "severity": "suspicious",
                "message": f"Found {len(links)} external hyperlink(s) embedded in the message body."
            })

            for link in links:
                try:
                    parsed_url = urlparse(link if "://" in link else f"http://{link}")
                    link_domain = parsed_url.netloc.split(":")[0].lower()
                    
                    # Domain mismatch heuristic
                    if sender_domain and link_domain and sender_domain != link_domain and not has_free_sender:
                        # Exclude common CDNs/sub-domains
                        if not link_domain.endswith(sender_domain) and not sender_domain.endswith(link_domain):
                            indicators.append({
                                "category": "links",
                                "severity": "critical",
                                "message": f"Domain Mismatch: Link points to '{link_domain}' which does not align with sender domain '{sender_domain}'."
                            })
                except Exception:
                    pass

        # 4. Analyze Keywords
        if keywords:
            indicators.append({
                "category": "keywords",
                "severity": "suspicious",
                "message": f"Detected high-risk phishing keywords: {', '.join(keywords)}."
            })

        # 5. Analyze Attachments
        for attach in attachments:
            fname = attach.get("filename", "").lower()
            size = attach.get("size", 0)
            
            # High-risk extension
            if fname.endswith(self.HIGH_RISK_ATTACHMENT_EXTENSIONS):
                indicators.append({
                    "category": "attachments",
                    "severity": "critical",
                    "message": f"Suspicious Attachment: '{attach['filename']}' utilizes a high-risk file format type."
                })
            else:
                indicators.append({
                    "category": "attachments",
                    "severity": "suspicious",
                    "message": f"Email contains attachment '{attach['filename']}' ({round(size / 1024, 1)} KB)."
                })

        return indicators

    def _extract_email_address(self, sender: str) -> str:
        """Extract email address from From header string (e.g. 'Brand <info@brand.com>')."""
        match = re.search(r'<([^>]+)>', sender)
        if match:
            return match.group(1).strip()
        # Fallback if raw email format
        if "@" in sender:
            # naive match email
            match_email = re.search(r'([a-zA-Z0-9.\-_]+@[a-zA-Z0-9.\-_]+)', sender)
            if match_email:
                return match_email.group(1).strip()
        return sender.strip()
