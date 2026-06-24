"""
PhishGuard AI — SSL Certificate Analysis Service

Connects to target hosts over SSL, retrieves raw certificate data, parses
X509 details using cryptography, handles validation failures, and computes trust scores.
"""

import logging
import socket
import ssl
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from cryptography import x509
from cryptography.x509.oid import NameOID

logger = logging.getLogger("phishguard")


class SslService:
    """Service to query, parse and score SSL certificates of target domains."""

    @classmethod
    def _extract_host(cls, target: str) -> str:
        """Helper to extract domain/host from target URL."""
        target = target.strip()
        if not target:
            return ""
        try:
            if "://" not in target:
                parsed = urlparse(f"http://{target}")
            else:
                parsed = urlparse(target)
            host = parsed.netloc or parsed.path.split("/")[0]
            if ":" in host:
                host = host.split(":")[0]
            return host
        except Exception:
            return target

    @classmethod
    def _get_common_name(cls, name: x509.Name) -> str:
        """Extract Common Name (CN) attribute from cryptography X509 Name structure."""
        attrs = name.get_attributes_for_oid(NameOID.COMMON_NAME)
        if attrs:
            return str(attrs[0].value)
        # Fallback to rfc4514 format
        return name.rfc4514_string()

    @classmethod
    def analyze_ssl(cls, target: str) -> Dict[str, Any]:
        """
        Analyze the SSL certificate of the target domain.
        Returns a detailed dictionary of certificate parameters and trust scores.
        """
        host = cls._extract_host(target)
        if not host:
            return {
                "host": "",
                "valid": False,
                "issuer": None,
                "expiration_date": None,
                "encryption": None,
                "certificate_chain": [],
                "trust_score": 0,
                "status": "INVALID_HOST"
            }

        # 1. First test verified connection to see if cert is trusted
        is_verified = False
        verify_error_msg = None
        
        try:
            verify_context = ssl.create_default_context()
            with socket.create_connection((host, 443), timeout=4) as sock:
                with verify_context.wrap_socket(sock, server_hostname=host) as ssock:
                    is_verified = True
        except ssl.SSLCertVerificationError as e:
            verify_error_msg = f"Verification error: {e.reason or str(e)}"
        except ssl.SSLError as e:
            verify_error_msg = f"SSL error: {str(e)}"
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            return {
                "host": host,
                "valid": False,
                "issuer": None,
                "expiration_date": None,
                "encryption": None,
                "certificate_chain": [],
                "trust_score": 0,
                "status": f"CONNECTION_FAILURE: {str(e)}"
            }

        # 2. Query certificate details using an unverified context to get data even if invalid
        try:
            unverified_context = ssl.create_default_context()
            unverified_context.check_hostname = False
            unverified_context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((host, 443), timeout=4) as sock:
                with unverified_context.wrap_socket(sock, server_hostname=host) as ssock:
                    der_cert = ssock.getpeercert(binary_form=True)
                    leaf_cert = x509.load_der_x509_certificate(der_cert)
                    
                    # Extract attributes
                    issuer_cn = cls._get_common_name(leaf_cert.issuer)
                    
                    # Expiration date extraction
                    try:
                        expiration = leaf_cert.not_valid_after_utc
                    except AttributeError:
                        expiration = leaf_cert.not_valid_after
                        
                    is_expired = expiration.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc)
                    
                    # Public key / Encryption details
                    pub_key = leaf_cert.public_key()
                    key_size = getattr(pub_key, "key_size", None)
                    key_algo = pub_key.__class__.__name__.replace("PublicKey", "").replace("_", "")
                    encryption_str = f"{leaf_cert.signature_hash_algorithm.name.upper()} with {key_algo}"
                    if key_size:
                        encryption_str += f" ({key_size}-bit)"

                    # Parse certificate chain (if supported by Python version)
                    chain_list = []
                    # Try using get_verified_chain if verified, or get_unverified_chain as fallback
                    chain_func = getattr(ssock, "get_verified_chain" if is_verified else "get_unverified_chain", None)
                    if chain_func:
                        try:
                            raw_chain = chain_func() or []
                            for idx, cert_bytes in enumerate(raw_chain):
                                c = x509.load_der_x509_certificate(cert_bytes)
                                s_cn = cls._get_common_name(c.subject)
                                i_cn = cls._get_common_name(c.issuer)
                                chain_list.append(f"Depth {idx}: Subject: {s_cn}, Issuer: {i_cn}")
                        except Exception:
                            pass
                    
                    if not chain_list:
                        # Fallback to single leaf certificate in chain
                        chain_list.append(f"Depth 0: Subject: {cls._get_common_name(leaf_cert.subject)}, Issuer: {issuer_cn}")

                    # Calculate trust score
                    trust_score = 100
                    if not is_verified:
                        if is_expired:
                            trust_score = 15
                        elif "self-signed" in (verify_error_msg or "").lower():
                            trust_score = 30
                        else:
                            trust_score = 50  # Hostname mismatch or untrusted CA
                    
                    return {
                        "host": host,
                        "valid": is_verified and not is_expired,
                        "issuer": issuer_cn,
                        "expiration_date": expiration.isoformat(),
                        "encryption": encryption_str,
                        "certificate_chain": chain_list,
                        "trust_score": trust_score,
                        "status": "SUCCESS" if is_verified else f"UNTRUSTED ({verify_error_msg or 'validation failed'})"
                    }

        except Exception as err:
            logger.error(f"Failed parsing SSL certificate for {host}: {err}")
            return {
                "host": host,
                "valid": False,
                "issuer": None,
                "expiration_date": None,
                "encryption": None,
                "certificate_chain": [],
                "trust_score": 0,
                "status": f"PARSING_FAILURE: {str(err)}"
            }
