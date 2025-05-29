import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AppConfig(BaseSettings):
    """Application configuration using Pydantic BaseSettings."""
    
    # API Keys
    groq_api_key: str = Field(..., env="GROQ_API_KEY")
    
    # Model Configuration
    llm_model: str = Field(default="llama3-70b-8192", env="LLM_MODEL")
    embedding_model_name: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    
    # RAG Configuration
    rag_retrieval_count: int = Field(default=3, env="RAG_RETRIEVAL_COUNT")
    
    # Database Configuration
    db_path: str = Field(default="./chroma_db", env="DB_PATH")
    collection_name: str = Field(default="linkedin_posts", env="COLLECTION_NAME")
    
    # Text Processing Configuration
    min_segment_length: int = Field(default=100, env="MIN_SEGMENT_LENGTH")
    max_segment_length: int = Field(default=500, env="MAX_SEGMENT_LENGTH")
    segment_overlap: int = Field(default=50, env="SEGMENT_OVERLAP")
    
    # Viral Detection Configuration
    min_similarity_threshold: float = Field(default=0.3, env="MIN_SIMILARITY_THRESHOLD")
    max_viral_candidates: int = Field(default=5, env="MAX_VIRAL_CANDIDATES")
    
    # Content Generation Configuration
    default_temperature: float = Field(default=0.7, env="DEFAULT_TEMPERATURE")
    max_tokens: int = Field(default=1000, env="MAX_TOKENS")
    num_post_variations: int = Field(default=3, env="NUM_POST_VARIATIONS")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }

def get_config() -> AppConfig:
    """
    Get application configuration.
    
    Returns:
        AppConfig instance with all settings
    """
    return AppConfig()

def validate_config(config: AppConfig) -> bool:
    """
    Validate that all required configuration is present.
    
    Args:
        config: AppConfig instance to validate
        
    Returns:
        True if configuration is valid, False otherwise
    """
    if not config.groq_api_key:
        print("❌ Error: GROQ_API_KEY is required but not set")
        return False
    
    if not config.groq_api_key.startswith("gsk_"):
        print("⚠️  Warning: GROQ_API_KEY doesn't appear to be in the correct format")
    
    print("✅ Configuration validated successfully")
    return True

def print_config_summary(config: AppConfig) -> None:
    """
    Print a summary of the current configuration.
    
    Args:
        config: AppConfig instance to summarize
    """
    print("🚀 Gary Bot Configuration Summary")
    print("=" * 40)
    print(f"LLM Model: {config.llm_model}")
    print(f"Embedding Model: {config.embedding_model_name}")
    print(f"RAG Retrieval Count: {config.rag_retrieval_count}")
    print(f"Database Path: {config.db_path}")
    print(f"Collection Name: {config.collection_name}")
    print(f"Segment Length: {config.min_segment_length}-{config.max_segment_length} chars")
    print(f"Similarity Threshold: {config.min_similarity_threshold}")
    print(f"Temperature: {config.default_temperature}")
    print(f"API Key: {'✅ Set' if config.groq_api_key else '❌ Missing'}")
    print("=" * 40)

# Available Groq models
AVAILABLE_GROQ_MODELS = {
    "llama3-70b-8192": "Llama 3 70B - High quality, slower",
    "llama3-8b-8192": "Llama 3 8B - Faster, good quality",
    "mixtral-8x7b-32768": "Mixtral 8x7B - Long context, versatile",
    "gemma-7b-it": "Gemma 7B - Instruction tuned",
}

# Available embedding models
AVAILABLE_EMBEDDING_MODELS = {
    "all-MiniLM-L6-v2": "Fast and lightweight (384 dimensions)",
    "all-mpnet-base-v2": "Higher quality (768 dimensions)",
    "all-MiniLM-L12-v2": "Balanced (384 dimensions)",
}

# Content type options - Gary Lin's 5 specific content types
CONTENT_TYPES = [
    "Founder's Personal Story & Journey",
    "Internal Company Management & Culture", 
    "Streamlining Data Delivery",
    "Analytics Trends & Insights",
    "Building a SaaS/AI Company"
]

# Default keywords for categorization
DEFAULT_KEYWORDS = [
    "startups", "entrepreneurship", "founders", "leadership", "product",
    "team", "culture", "growth", "fundraising", "pivoting", "hiring",
    "product-market-fit", "scaling", "vision", "strategy", "execution",
    "failure", "success", "learning", "mentorship", "community"
] 