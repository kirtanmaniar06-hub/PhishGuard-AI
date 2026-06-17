"""
PhishGuard AI — Password Cryptography Utilities

Uses the standard bcrypt library directly to handle secure password hashing
and verification. Bypasses deprecated passlib packaging issues.
"""

import bcrypt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare a plain-text password with its stored bcrypt hash."""
    try:
        password_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        # Returns False if decoding fails or formatting is invalid
        return False


def get_password_hash(password: str) -> str:
    """Generate a bcrypt hash of a plain-text password."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")
