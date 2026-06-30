"""
PhishGuard AI — Email Parser Component

Responsible for extracting headers, sender metadata, attachments,
and body links/keywords from raw email MIME texts or plain text pastes.
"""

import re
import email
from email.message import Message
from typing import Dict, Any, List, Set


class EmailParser:
    """
    Parses pasted email content (MIME, RFC 822, or plain text with From/Subject headers).
    """

    # URL matching regex
    URL_REGEX = re.compile(
        r'(https?://[a-zA-Z0-9.\-_]+(?::\d+)?(?:/[a-zA-Z0-9.\-_~:/?#\[\]@!$&\'()*+,;=%]*)?)',
        re.IGNORECASE
    )

    # Keywords typical of phishing
    HIGH_RISK_KEYWORDS = {
        "urgency": ["urgent", "action required", "immediate", "suspension", "terminated", "expire", "critical"],
        "financial": ["billing", "payment", "bank", "invoice", "refund", "wire transfer", "credit card", "payroll"],
        "credentials": ["verify", "login", "signin", "reset password", "security code", "update credentials", "auth"],
    }

    def parse(self, raw_email: str) -> Dict[str, Any]:
        """
        Parses raw text to extract email components.
        """
        if not raw_email.strip():
            return {
                "sender": "",
                "subject": "",
                "headers": {},
                "body": "",
                "links": [],
                "keywords": [],
                "attachments": []
            }

        # Try parsing as standard MIME first
        msg = email.message_from_string(raw_email)
        
        # Check if it was successfully parsed as standard email format
        is_mime = bool(msg.get("From") or msg.get("Subject"))
        
        if is_mime:
            return self._parse_mime(msg)
        else:
            return self._parse_plain_text(raw_email)

    def _parse_mime(self, msg: Message) -> Dict[str, Any]:
        sender = msg.get("From", "").strip()
        subject = msg.get("Subject", "").strip()
        
        headers = {}
        for key, val in msg.items():
            headers[key.lower()] = val

        body_parts = []
        attachments = []

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disp = str(part.get("Content-Disposition"))

                # Check if it is an attachment
                if "attachment" in content_disp or part.get_filename():
                    filename = part.get_filename() or "unnamed_attachment"
                    attachments.append({
                        "filename": filename,
                        "content_type": content_type,
                        "size": len(part.get_payload(decode=True) or "")
                    })
                elif content_type in ("text/plain", "text/html"):
                    payload = part.get_payload(decode=True)
                    if payload:
                        body_parts.append(payload.decode(errors="ignore"))
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body_parts.append(payload.decode(errors="ignore"))

        body = "\n".join(body_parts)
        links = self._extract_links(body)
        keywords = self._extract_keywords(body + " " + subject)

        return {
            "sender": sender,
            "subject": subject,
            "headers": headers,
            "body": body,
            "links": list(links),
            "keywords": list(keywords),
            "attachments": attachments
        }

    def _parse_plain_text(self, text: str) -> Dict[str, Any]:
        """
        Fallback parser for non-MIME copy-paste formats.
        Locates headers like From: / Subject: via regex.
        """
        sender_match = re.search(r'(?:From|Sender|Sender Email):\s*([^\n\r]+)', text, re.IGNORECASE)
        subject_match = re.search(r'(?:Subject|Topic):\s*([^\n\r]+)', text, re.IGNORECASE)

        sender = sender_match.group(1).strip() if sender_match else ""
        subject = subject_match.group(1).strip() if subject_match else ""

        # Extract headers (naive match lines with Colons)
        headers = {}
        lines = text.splitlines()
        body_start_idx = 0
        
        for idx, line in enumerate(lines):
            if not line.strip():
                body_start_idx = idx
                break
            match = re.match(r'^([a-zA-Z\-]+):\s*(.*)$', line)
            if match:
                headers[match.group(1).lower()] = match.group(2).strip()
            else:
                # If first lines are not header format, treat whole text as body
                body_start_idx = 0
                break

        body = "\n".join(lines[body_start_idx:])
        if not body.strip():
            body = text

        links = self._extract_links(body)
        keywords = self._extract_keywords(body + " " + subject)

        return {
            "sender": sender,
            "subject": subject,
            "headers": headers,
            "body": body,
            "links": list(links),
            "keywords": list(keywords),
            "attachments": []  # Difficult to parse attachments from pure plain-text paste
        }

    def _extract_links(self, text: str) -> Set[str]:
        return set(self.URL_REGEX.findall(text))

    def _extract_keywords(self, text: str) -> Set[str]:
        text_lower = text.lower()
        matched = set()
        for cat, kw_list in self.HIGH_RISK_KEYWORDS.items():
            for kw in kw_list:
                if kw in text_lower:
                    matched.add(kw)
        return matched
