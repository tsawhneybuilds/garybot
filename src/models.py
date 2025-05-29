from typing import List, Optional, Dict
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

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
    embedding: List[float]
    keywords: List[str] = []
    content_type: Optional[str] = None
    source_snippet: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    likes: int = 0
    comments: int = 0
    is_gold_standard: bool = False  # If it was added as a gold standard example
    last_engagement_update_at: Optional[datetime] = None
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