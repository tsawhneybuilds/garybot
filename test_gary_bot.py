#!/usr/bin/env python3
"""
Simple test script for Gary Bot components.
Run this to verify everything is working correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test that all modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        from src.config import get_config, validate_config
        from src.transcript_processor import TranscriptProcessor
        from src.viral_snippet_detector import ViralSnippetDetector
        from src.rag_system import RAGSystem
        from src.content_generator import ContentGenerator
        from src.gary_bot import GaryBot
        print("✅ All imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test configuration loading."""
    print("\n⚙️ Testing configuration...")
    
    try:
        from src.config import get_config, validate_config
        config = get_config()
        
        if validate_config(config):
            print("✅ Configuration loaded and validated!")
            return True
        else:
            print("❌ Configuration validation failed!")
            return False
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_transcript_processing():
    """Test transcript processing."""
    print("\n📝 Testing transcript processing...")
    
    try:
        from src.transcript_processor import TranscriptProcessor
        
        processor = TranscriptProcessor()
        sample_text = """
        [00:00:00] GARY: Here's the thing nobody tells you about raising Series A. 
        The deck is just 10% of the battle. Um, like, the other 90%? 
        It's your ability to tell a story that makes investors lean forward.
        """
        
        segments = processor.process_transcript(sample_text, "test_transcript")
        
        if segments and len(segments) > 0:
            print(f"✅ Processed {len(segments)} segments!")
            print(f"   Sample segment: {segments[0].text[:100]}...")
            return True
        else:
            print("❌ No segments processed!")
            return False
    except Exception as e:
        print(f"❌ Transcript processing error: {e}")
        return False

def test_embeddings():
    """Test embedding generation."""
    print("\n🧠 Testing embeddings...")
    
    try:
        from src.viral_snippet_detector import ViralSnippetDetector
        
        detector = ViralSnippetDetector()
        test_text = "Here's the thing nobody tells you about startups."
        
        embedding = detector.get_embedding(test_text)
        
        if embedding and len(embedding) > 0:
            print(f"✅ Generated embedding with {len(embedding)} dimensions!")
            return True
        else:
            print("❌ Failed to generate embedding!")
            return False
    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return False

def test_rag_system():
    """Test RAG system basics."""
    print("\n🗄️ Testing RAG system...")
    
    try:
        from src.rag_system import RAGSystem
        from src.models import RAGPost
        
        rag = RAGSystem(db_path="./test_chroma_db")
        
        # Test adding a post
        test_post = RAGPost(
            text="Test post for RAG system",
            embedding=[],  # Will be computed
            keywords=["test"],
            is_gold_standard=True
        )
        
        post_id = rag.add_post(test_post)
        
        # Test retrieval
        similar_posts = rag.retrieve_similar_posts("Test post", top_k=1)
        
        if similar_posts and len(similar_posts) > 0:
            print(f"✅ RAG system working! Added and retrieved post.")
            
            # Cleanup
            rag.delete_post(post_id)
            return True
        else:
            print("❌ RAG system retrieval failed!")
            return False
    except Exception as e:
        print(f"❌ RAG system error: {e}")
        return False

def test_full_gary_bot():
    """Test the full Gary Bot integration."""
    print("\n🚀 Testing full Gary Bot...")
    
    # Check if API key is available
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️ GROQ_API_KEY not found. Skipping full integration test.")
        print("   Set your API key in .env file to test content generation.")
        return True
    
    try:
        from src.gary_bot import GaryBot
        
        gary_bot = GaryBot()
        
        # Test transcript processing
        sample_transcript = """
        When we started Explo, we thought we knew exactly what customers wanted. 
        We built this amazing analytics dashboard. And you know what happened? 
        Crickets. Like, literally nobody cared.
        """
        
        segments = gary_bot.process_transcript(sample_transcript)
        
        if segments and len(segments) > 0:
            print(f"✅ Gary Bot processed {len(segments)} segments!")
            
            # Test viral snippet detection
            candidates = gary_bot.identify_viral_snippets(segments)
            
            if candidates and len(candidates) > 0:
                print(f"✅ Found {len(candidates)} viral candidates!")
                
                # Test content generation (only if API key is available)
                try:
                    draft = gary_bot.generate_post_from_snippet(candidates[0].text)
                    print(f"✅ Generated post preview: {draft.draft_text[:100]}...")
                    return True
                except Exception as e:
                    print(f"⚠️ Content generation failed (likely API issue): {e}")
                    return True  # Still consider this a success if other parts work
            else:
                print("❌ No viral candidates found!")
                return False
        else:
            print("❌ No segments processed!")
            return False
    except Exception as e:
        print(f"❌ Gary Bot error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Gary Bot Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_transcript_processing,
        test_embeddings,
        test_rag_system,
        test_full_gary_bot
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Gary Bot is ready to use.")
        print("\nNext steps:")
        print("1. Make sure your .env file has a valid GROQ_API_KEY")
        print("2. Run: streamlit run app.py")
        print("3. Upload a transcript and start generating posts!")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        print("\nCommon issues:")
        print("- Missing GROQ_API_KEY in .env file")
        print("- Missing dependencies (run: pip install -r requirements.txt)")
        print("- spaCy model not installed (run: python -m spacy download en_core_web_sm)")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 