from typing import List, Optional, Dict
from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from dataclasses import dataclass, field

class TranscriptSegment(BaseModel):
    text: str
    source_transcript_id: Optional[str] = None

class GoldStandardPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    embedding: Optional[List[float]] = None  # Store if pre-computed
    keywords: List[str] = []
    # Add any other relevant metadata for gold standard examples

class RAGPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: Optional[str] = None  # Title for the post
    author: Optional[str] = None  # Author of the post
    text: str
    embedding: Optional[List[float]] = None  # Made optional to match usage
    keywords: List[str] = []
    content_type: Optional[str] = None
    source_snippet: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    likes: int = 0
    comments: int = 0
    is_gold_standard: bool = False  # If it was added as a gold standard example
    last_engagement_update_at: Optional[datetime] = None
    persona_ids: List[str] = []  # Which personas this post applies to (empty = all personas)
    # Add reference to original transcript if applicable

class GeneratedPostDraft(BaseModel):
    original_snippet: str
    draft_text: str
    suggested_hashtags: List[str]
    rag_context_ids: List[str]  # IDs of posts used from RAG

class AppConfig(BaseModel):
    groq_api_key: str
    llm_model: str = "llama3-70b-8192"  # Default model on Groq
    embedding_model_name: str = "all-MiniLM-L6-v2"
    rag_retrieval_count: int = 3
    # Add other configurations as needed

class ViralSnippetCandidate(BaseModel):
    text: str
    similarity_score: float
    most_similar_post_id: Optional[str] = None
    most_similar_post_text: Optional[str] = None
    rank: int

@dataclass
class Hook:
    """A hook/template document stored in the RAG system (formerly GuidelineDocument)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    content: str = ""
    hook_type: str = "general"  # "curiosity", "story", "provocative", "general"
    section: Optional[str] = None
    embedding: List[float] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    priority: int = 1  # 1=Low, 2=Medium, 3=High

# Keep GuidelineDocument as alias for backward compatibility
GuidelineDocument = Hook

@dataclass
class Persona:
    """A writing persona for generating different styles of content."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""  # e.g., "Gary Lin - Founder Talk", "Technical Expert"
    description: str = ""  # Brief description of the persona
    voice_tone: str = ""  # Core personality and tone description
    content_types: List[str] = field(default_factory=list)  # Specialized content categories
    style_guide: str = ""  # Writing patterns, structure, and style rules
    example_hooks: List[str] = field(default_factory=list)  # Persona-specific hooks
    target_audience: str = ""  # Who they write for
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_default: bool = False  # Is this the default persona?
    is_active: bool = True  # Is this persona available for use?
    embedding: List[float] = field(default_factory=list)  # For RAG retrieval

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4()) 