#!/usr/bin/env python3
"""
Script to restore Gary Bot data from a JSON backup file.
"""

import sys
import json
import os
from datetime import datetime
from typing import List, Dict, Any

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.rag_system import RAGSystem
from src.models import RAGPost, GuidelineDocument
from src.config import get_config

def restore_from_json(json_file_path: str, overwrite: bool = False) -> Dict[str, Any]:
    """
    Restore Gary Bot data from a JSON backup file.
    
    Args:
        json_file_path: Path to the JSON backup file
        overwrite: Whether to overwrite existing data
        
    Returns:
        Dictionary with restoration results
    """
    
    if not os.path.exists(json_file_path):
        print(f"❌ Error: File not found: {json_file_path}")
        return {"success": False, "error": "File not found"}
    
    try:
        # Load JSON data
        with open(json_file_path, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        print(f"📄 Loaded backup from {backup_data.get('export_timestamp', 'unknown time')}")
        print(f"📊 Contains: {backup_data.get('total_posts', 0)} posts, {backup_data.get('total_guidelines', 0)} guidelines")
        
        # Initialize RAG system
        config = get_config()
        rag_system = RAGSystem(config.db_path)
        
        result = {
            "success": True,
            "posts_added": 0,
            "posts_failed": 0,
            "guidelines_added": 0,
            "guidelines_failed": 0
        }
        
        # Restore posts
        if 'posts' in backup_data:
            print(f"\n📝 Restoring {len(backup_data['posts'])} posts...")
            
            for post_data in backup_data['posts']:
                try:
                    # Convert back to RAGPost object
                    post = RAGPost(
                        id=post_data['id'],
                        title=post_data.get('title'),
                        author=post_data.get('author'),
                        text=post_data['text'],
                        embedding=None,  # Will be regenerated
                        keywords=post_data.get('keywords', []),
                        content_type=post_data.get('content_type'),
                        source_snippet=post_data.get('source_snippet'),
                        created_at=datetime.fromisoformat(post_data['created_at']),
                        likes=post_data.get('likes', 0),
                        comments=post_data.get('comments', 0),
                        is_gold_standard=post_data.get('is_gold_standard', False),
                        last_engagement_update_at=datetime.fromisoformat(post_data['last_engagement_update_at']) if post_data.get('last_engagement_update_at') else None
                    )
                    
                    # Add to RAG system
                    rag_system.add_post(post)
                    result["posts_added"] += 1
                    print(f"✅ Added post: {post.title or post.text[:50]}...")
                    
                except Exception as e:
                    result["posts_failed"] += 1
                    print(f"❌ Failed to add post: {str(e)}")
        
        # Restore guidelines
        if 'guidelines' in backup_data:
            print(f"\n📋 Restoring {len(backup_data['guidelines'])} guidelines...")
            
            for guideline_data in backup_data['guidelines']:
                try:
                    # Convert back to GuidelineDocument object
                    guideline = GuidelineDocument(
                        id=guideline_data['id'],
                        title=guideline_data['title'],
                        content=guideline_data['content'],
                        document_type=guideline_data['document_type'],
                        section=guideline_data.get('section'),
                        embedding=None,  # Will be regenerated
                        created_at=datetime.fromisoformat(guideline_data['created_at']),
                        priority=guideline_data.get('priority', 1)
                    )
                    
                    # Add to RAG system
                    rag_system.add_guideline(guideline)
                    result["guidelines_added"] += 1
                    print(f"✅ Added guideline: {guideline.title}")
                    
                except Exception as e:
                    result["guidelines_failed"] += 1
                    print(f"❌ Failed to add guideline: {str(e)}")
        
        print(f"\n🎉 Restoration complete!")
        print(f"📊 Results:")
        print(f"   Posts: {result['posts_added']} added, {result['posts_failed']} failed")
        print(f"   Guidelines: {result['guidelines_added']} added, {result['guidelines_failed']} failed")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during restoration: {str(e)}")
        return {"success": False, "error": str(e)}

def main():
    """Main function for the restore script."""
    
    if len(sys.argv) < 2:
        print("📖 Usage: python restore_from_json.py <json_backup_file>")
        print("📖 Example: python restore_from_json.py gary_bot_backup_20231201_120000.json")
        return
    
    json_file = sys.argv[1]
    
    print("🔄 Gary Bot - JSON Backup Restoration")
    print("=" * 50)
    
    # Confirm restoration
    confirm = input(f"⚠️ This will add data from {json_file} to your RAG system. Continue? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Restoration cancelled")
        return
    
    # Perform restoration
    result = restore_from_json(json_file)
    
    if result["success"]:
        print("✅ Restoration completed successfully!")
    else:
        print(f"❌ Restoration failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main() 