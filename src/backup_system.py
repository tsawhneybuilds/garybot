import os
import shutil
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import zipfile
from src.rag_system import RAGSystem
from src.models import RAGPost

class BackupSystem:
    """
    Backup system for ChromaDB data to ensure RAG posts are never lost.
    """
    
    def __init__(self, db_path: str = "./chroma_db", backup_dir: str = "./backups"):
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, include_embeddings: bool = False) -> str:
        """
        Create a backup of the ChromaDB data.
        
        Args:
            include_embeddings: Whether to include embeddings in JSON backup
            
        Returns:
            Path to the created backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"garybot_backup_{timestamp}"
        backup_path = self.backup_dir / f"{backup_name}.zip"
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Backup the entire ChromaDB directory
            if self.db_path.exists():
                for file_path in self.db_path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(self.db_path.parent)
                        zipf.write(file_path, arcname)
            
            # Create a JSON export of all posts for human readability
            try:
                rag_system = RAGSystem(str(self.db_path))
                posts = rag_system.list_all_posts()
                
                posts_data = []
                for post in posts:
                    post_dict = {
                        "id": post.id,
                        "title": post.title,
                        "author": post.author,
                        "text": post.text,
                        "keywords": post.keywords,
                        "content_type": post.content_type,
                        "source_snippet": post.source_snippet,
                        "created_at": post.created_at.isoformat(),
                        "likes": post.likes,
                        "comments": post.comments,
                        "is_gold_standard": post.is_gold_standard,
                        "last_engagement_update_at": post.last_engagement_update_at.isoformat() if post.last_engagement_update_at else None
                    }
                    
                    if include_embeddings and post.embedding:
                        post_dict["embedding"] = post.embedding
                    
                    posts_data.append(post_dict)
                
                # Add JSON export to backup
                json_data = {
                    "backup_timestamp": timestamp,
                    "total_posts": len(posts_data),
                    "posts": posts_data
                }
                
                json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
                zipf.writestr(f"{backup_name}_posts.json", json_str)
                
            except Exception as e:
                print(f"Warning: Could not create JSON export: {e}")
        
        print(f"✅ Backup created: {backup_path}")
        return str(backup_path)
    
    def restore_backup(self, backup_path: str, overwrite: bool = False) -> bool:
        """
        Restore from a backup file.
        
        Args:
            backup_path: Path to the backup zip file
            overwrite: Whether to overwrite existing data
            
        Returns:
            True if restore was successful
        """
        backup_file = Path(backup_path)
        if not backup_file.exists():
            print(f"❌ Backup file not found: {backup_path}")
            return False
        
        if self.db_path.exists() and not overwrite:
            print(f"❌ Database already exists at {self.db_path}. Use overwrite=True to replace.")
            return False
        
        try:
            # Remove existing database if overwriting
            if self.db_path.exists() and overwrite:
                shutil.rmtree(self.db_path)
            
            # Extract backup
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                zipf.extractall(self.db_path.parent)
            
            print(f"✅ Backup restored from: {backup_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error restoring backup: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups.
        
        Returns:
            List of backup information dictionaries
        """
        backups = []
        for backup_file in self.backup_dir.glob("garybot_backup_*.zip"):
            stat = backup_file.stat()
            backups.append({
                "filename": backup_file.name,
                "path": str(backup_file),
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x["created_at"], reverse=True)
        return backups
    
    def auto_backup(self, max_backups: int = 10) -> str:
        """
        Create an automatic backup and clean up old ones.
        
        Args:
            max_backups: Maximum number of backups to keep
            
        Returns:
            Path to the created backup
        """
        # Create new backup
        backup_path = self.create_backup()
        
        # Clean up old backups
        backups = self.list_backups()
        if len(backups) > max_backups:
            for old_backup in backups[max_backups:]:
                try:
                    os.remove(old_backup["path"])
                    print(f"🗑️  Removed old backup: {old_backup['filename']}")
                except Exception as e:
                    print(f"Warning: Could not remove old backup {old_backup['filename']}: {e}")
        
        return backup_path
    
    def export_posts_json(self, output_path: Optional[str] = None, include_embeddings: bool = False) -> str:
        """
        Export all posts to a JSON file for easy viewing/editing.
        
        Args:
            output_path: Path for the JSON file (auto-generated if None)
            include_embeddings: Whether to include embeddings
            
        Returns:
            Path to the created JSON file
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.backup_dir / f"posts_export_{timestamp}.json"
        
        try:
            rag_system = RAGSystem(str(self.db_path))
            posts = rag_system.list_all_posts()
            
            posts_data = []
            for post in posts:
                post_dict = {
                    "id": post.id,
                    "title": post.title,
                    "author": post.author,
                    "text": post.text,
                    "keywords": post.keywords,
                    "content_type": post.content_type,
                    "source_snippet": post.source_snippet,
                    "created_at": post.created_at.isoformat(),
                    "likes": post.likes,
                    "comments": post.comments,
                    "is_gold_standard": post.is_gold_standard,
                    "last_engagement_update_at": post.last_engagement_update_at.isoformat() if post.last_engagement_update_at else None
                }
                
                if include_embeddings and post.embedding:
                    post_dict["embedding"] = post.embedding
                
                posts_data.append(post_dict)
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_posts": len(posts_data),
                "posts": posts_data
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Posts exported to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ Error exporting posts: {e}")
            raise 