# infra/logging_setup.py
"""
Structured logging infrastructure.

Responsibilities:
- Configure stdlib logging as a transport
- Configure structlog event processing
- Provide context-aware loggers to services

Non-responsibilities:
- No business logic
- No log emission
- No domain knowledge
"""

import logging
import sys
from typing import Optional

import structlog


def configure_logging(level: str = "INFO"):
    """
    Initialize process-wide logging configuration.

    This must be called exactly once at application startup
    (e.g. in app/ask.py).

    It configures:
    - stdlib logging as a thin transport layer
    - structlog as the structured logging frontend
    """

    # Configure stdlib logging to pass through raw messages
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )

    # Configure structlog's event processing pipeline
    structlog.configure(
        processors=[
            # Add ISO-8601 timestamp to every log event
            structlog.processors.TimeStamper(fmt="iso"),

            # Add log level (info, warning, error, etc.)
            structlog.processors.add_log_level,

            # Optionally include stack info when requested
            structlog.processors.StackInfoRenderer(),

            # Render exceptions in structured form
            structlog.processors.format_exc_info,

            # Final renderer: convert event dict to JSON
            structlog.processors.JSONRenderer(),
        ],
        # Use stdlib logging under the hood
        logger_factory=structlog.stdlib.LoggerFactory(),

        # Enable .bind() for contextual loggers
        wrapper_class=structlog.stdlib.BoundLogger,

        # Cache loggers for performance
        cache_logger_on_first_use=True,
    )


def get_logger(
    component: str,
    *,
    conversation_id: Optional[str] = None,
    request_id: Optional[str] = None,
):
    """
    Return a structured logger bound to a logical component
    and optional correlation identifiers.

    This function does NOT emit logs.

    Args:
        component: Logical namespace (e.g. "services.search")
        conversation_id: Stable conversation identifier
        request_id: Per-request correlation identifier
    """

    # Base logger names the emitting component
    logger = structlog.get_logger(component)

    # Bind contextual identifiers if provided
    if conversation_id:
        logger = logger.bind(conversation_id=conversation_id)

    if request_id:
        logger = logger.bind(request_id=request_id)

    return logger
