"""Content Discovery feature module.

This module provides content discovery, personalization, and recommendation
capabilities for the Learnora platform.
"""

from .models import LearningContent, UserProfile
from .service import LearnoraContentDiscovery

__all__ = [
    "LearningContent",
    "UserProfile",
    "LearnoraContentDiscovery",
]
