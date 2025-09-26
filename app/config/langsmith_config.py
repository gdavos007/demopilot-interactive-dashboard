"""
Langsmith Configuration and Setup

This module handles Langsmith tracing configuration and initialization
for the Product Knowledge Agent.
"""

import os
from typing import Optional
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

def setup_langsmith_tracing() -> bool:
    """
    Set up Langsmith tracing if configured.
    
    Returns:
        bool: True if tracing is enabled and configured, False otherwise
    """
    if not settings.LANGSMITH_TRACING:
        logger.info("Langsmith tracing is disabled")
        return False
    
    if not settings.LANGSMITH_API_KEY:
        logger.warning("Langsmith tracing enabled but no API key provided")
        return False
    
    try:
        # Set environment variables for Langsmith
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGSMITH_ENDPOINT
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
        
        if settings.LANGSMITH_PROJECT:
            os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT
        
        logger.info(f"Langsmith tracing enabled for project: {settings.LANGSMITH_PROJECT}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to setup Langsmith tracing: {e}")
        return False

def get_langsmith_project() -> Optional[str]:
    """Get the current Langsmith project name."""
    return settings.LANGSMITH_PROJECT

def get_langsmith_dataset_id() -> Optional[str]:
    """Get the Langsmith dataset ID for evaluations."""
    return settings.LANGSMITH_DATASET_ID

def is_langsmith_enabled() -> bool:
    """Check if Langsmith tracing is enabled and properly configured."""
    return (
        settings.LANGSMITH_TRACING and 
        settings.LANGSMITH_API_KEY is not None and
        settings.LANGSMITH_PROJECT is not None
    )
