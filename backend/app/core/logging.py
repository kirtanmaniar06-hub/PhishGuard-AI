"""
PhishGuard AI — Loguru Logging Configuration

Structured logging with file rotation and console output.
"""

import sys
from pathlib import Path

from loguru import logger

from app.core.config import settings


def setup_logging() -> None:
    """Configure Loguru with console and file sinks."""

    # Remove default Loguru handler
    logger.remove()

    # ── Console sink ─────────────────────────────────────
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    # ── File sink (with rotation) ────────────────────────
    log_path = Path(settings.LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        str(log_path),
        level=settings.LOG_LEVEL,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
            "{name}:{function}:{line} — {message}"
        ),
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,  # thread-safe
    )

    logger.info(
        f"Logging initialized — level={settings.LOG_LEVEL}, "
        f"file={settings.LOG_FILE}"
    )
