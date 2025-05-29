# Gary Bot - AI-Powered LinkedIn Post Generator
# For Gary Lin, Co-Founder of Explo

__version__ = "1.0.0"
__author__ = "AI Assistant"
__description__ = "AI-powered viral LinkedIn post generator with RAG system"

from .gary_bot import GaryBot
from .config import get_config, AppConfig
from .models import (
    TranscriptSegment,
    GoldStandardPost,
    RAGPost,
    GeneratedPostDraft,
    ViralSnippetCandidate,
    AppConfig as ModelsAppConfig
)

__all__ = [
    "GaryBot",
    "get_config",
    "AppConfig",
    "TranscriptSegment",
    "GoldStandardPost", 
    "RAGPost",
    "GeneratedPostDraft",
    "ViralSnippetCandidate",
    "ModelsAppConfig"
] 