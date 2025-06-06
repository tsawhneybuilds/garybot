import os
import json
from typing import Optional, List
from datetime import datetime
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AppConfig(BaseSettings):
    """Application configuration using Pydantic BaseSettings."""
    
    # API Keys
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    
    # LLM Provider Selection
    llm_provider: str = Field(default="groq", env="LLM_PROVIDER")  # "groq" or "openai"
    
    # Model Configuration
    llm_model: str = Field(default="llama3-70b-8192", env="LLM_MODEL")
    openai_model: str = Field(default="gpt-4o", env="OPENAI_MODEL")  # Updated to latest flagship model
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
    """Get configuration from environment variables."""
    return AppConfig()

def validate_config(config: AppConfig) -> bool:
    """
    Validate that all required configuration is present.
    
    Args:
        config: AppConfig instance to validate
        
    Returns:
        True if configuration is valid, False otherwise
    """
    # Validate provider selection
    if config.llm_provider not in ["groq", "openai"]:
        print(f"❌ Error: LLM_PROVIDER must be 'groq' or 'openai', got '{config.llm_provider}'")
        return False
    
    # Validate API keys based on provider
    if config.llm_provider == "groq":
        if not config.groq_api_key:
            print("❌ Error: GROQ_API_KEY is required when using Groq provider")
            return False
        
        if not config.groq_api_key.startswith("gsk_"):
            print("⚠️  Warning: GROQ_API_KEY doesn't appear to be in the correct format")
    
    elif config.llm_provider == "openai":
        if not config.openai_api_key:
            print("❌ Error: OPENAI_API_KEY is required when using OpenAI provider")
            return False
        
        if not config.openai_api_key.startswith("sk-"):
            print("⚠️  Warning: OPENAI_API_KEY doesn't appear to be in the correct format")
    
    print(f"✅ Configuration validated successfully (Provider: {config.llm_provider})")
    return True

def print_config_summary(config: AppConfig) -> None:
    """
    Print a summary of the current configuration.
    
    Args:
        config: AppConfig instance to summarize
    """
    print("🚀 Gary Bot Configuration Summary")
    print("=" * 40)
    print(f"LLM Provider: {config.llm_provider.upper()}")
    if config.llm_provider == "groq":
        print(f"Groq Model: {config.llm_model}")
        print(f"Groq API Key: {'✅ Set' if config.groq_api_key else '❌ Missing'}")
    elif config.llm_provider == "openai":
        print(f"OpenAI Model: {config.openai_model}")
        print(f"OpenAI API Key: {'✅ Set' if config.openai_api_key else '❌ Missing'}")
    print(f"Embedding Model: {config.embedding_model_name}")
    print(f"RAG Retrieval Count: {config.rag_retrieval_count}")
    print(f"Database Path: {config.db_path}")
    print(f"Collection Name: {config.collection_name}")
    print(f"Segment Length: {config.min_segment_length}-{config.max_segment_length} chars")
    print(f"Similarity Threshold: {config.min_similarity_threshold}")
    print(f"Temperature: {config.default_temperature}")
    print("=" * 40)

# Available Groq models
AVAILABLE_GROQ_MODELS = {
    "deepseek-r1-distill-llama-70b": "DeepSeek R1 Distill Llama 70B - Latest reasoning model",
    "llama3-70b-8192": "Llama 3 70B - High quality, slower",
    "llama3-8b-8192": "Llama 3 8B - Faster, good quality",
    "mixtral-8x7b-32768": "Mixtral 8x7B - Long context, versatile",
    "gemma-7b-it": "Gemma 7B - Instruction tuned",
}

# Available OpenAI models
AVAILABLE_OPENAI_MODELS = {
    "gpt-4o": "GPT-4o - Latest flagship model (Recommended)",
    "gpt-4o-mini": "GPT-4o Mini - Fast and cost-effective",
    "gpt-4-turbo": "GPT-4 Turbo - Balanced performance",
    "gpt-3.5-turbo": "GPT-3.5 Turbo - Fast and affordable",
}

# LLM Provider options
LLM_PROVIDERS = {
    "groq": "Groq (Default) - Fast inference, open source models",
    "openai": "OpenAI - ChatGPT models (requires API key)",
}

# Available embedding models
AVAILABLE_EMBEDDING_MODELS = {
    "all-MiniLM-L6-v2": "Fast and lightweight (384 dimensions)",
    "all-mpnet-base-v2": "Higher quality (768 dimensions)",
    "all-MiniLM-L12-v2": "Balanced (384 dimensions)",
}

def load_content_types() -> List[str]:
    """Load content types from JSON file."""
    content_types_file = "content_types.json"
    
    try:
        if os.path.exists(content_types_file):
            with open(content_types_file, 'r') as f:
                data = json.load(f)
                return data.get("content_types", [])
        else:
            # Create default file if it doesn't exist
            default_types = [
                "Founder Real Talk, building SaaS",
                "Event Moments & Ecosystem Takes", 
                "Memes & Fun",
                "Team, Culture & Leadership",
                "Analytics Insight",
                "Explo product Updates"
            ]
            save_content_types(default_types)
            return default_types
    except Exception as e:
        print(f"Error loading content types: {e}")
        # Return fallback content types
        return [
            "Founder Real Talk, building SaaS",
            "Event Moments & Ecosystem Takes",
            "Memes & Fun", 
            "Team, Culture & Leadership",
            "Analytics Insight",
            "Explo product Updates"
        ]

def save_content_types(content_types: List[str]) -> bool:
    """Save content types to JSON file."""
    content_types_file = "content_types.json"
    
    try:
        data = {
            "content_types": content_types,
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "version": "1.0"
        }
        
        with open(content_types_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving content types: {e}")
        return False

def add_content_type(new_type: str) -> bool:
    """Add a new content type."""
    current_types = load_content_types()
    if new_type not in current_types:
        current_types.append(new_type)
        return save_content_types(current_types)
    return False

def remove_content_type(type_to_remove: str) -> bool:
    """Remove a content type."""
    current_types = load_content_types()
    if type_to_remove in current_types:
        current_types.remove(type_to_remove)
        return save_content_types(current_types)
    return False

def update_content_type(old_type: str, new_type: str) -> bool:
    """Update an existing content type."""
    current_types = load_content_types()
    if old_type in current_types:
        index = current_types.index(old_type)
        current_types[index] = new_type
        return save_content_types(current_types)
    return False

def reload_content_types() -> List[str]:
    """Reload content types from file and update the global CONTENT_TYPES."""
    global CONTENT_TYPES
    CONTENT_TYPES = load_content_types()
    return CONTENT_TYPES

# Content type options - Gary Lin's 6 content verticals
CONTENT_TYPES = load_content_types()

# Default keywords for categorization
DEFAULT_KEYWORDS = [
    "startups", "entrepreneurship", "founders", "leadership", "product",
    "team", "culture", "growth", "fundraising", "pivoting", "hiring",
    "product-market-fit", "scaling", "vision", "strategy", "execution",
    "failure", "success", "learning", "mentorship", "community"
] 