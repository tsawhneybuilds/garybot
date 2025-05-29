import chromadb
from chromadb.config import Settings
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from sentence_transformers import SentenceTransformer
from src.models import RAGPost
import json
import os

class RAGSystem:
    """
    Retrieval Augmented Generation system for storing and retrieving LinkedIn posts.
    Uses ChromaDB as the vector database.
    """
    
    def __init__(self, db_path: str = "./chroma_db", collection_name: str = "linkedin_posts", 
                 embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize the RAG system with ChromaDB.
        
        Args:
            db_path: Path to store the ChromaDB database
            collection_name: Name of the collection to store posts
            embedding_model: Sentence transformer model for embeddings
        """
        self.db_path = db_path
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model
        
        # Initialize sentence transformer
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except ValueError:
            # Collection doesn't exist, create it
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "LinkedIn posts for RAG system"}
            )
    
    def add_post(self, post: RAGPost) -> str:
        """
        Add a post to the RAG system.
        
        Args:
            post: RAGPost object to add
            
        Returns:
            ID of the added post
        """
        # Generate embedding if not provided
        if not post.embedding:
            post.embedding = self.embedding_model.encode([post.text])[0].tolist()
        
        # Prepare metadata
        metadata = {
            "title": post.title or "",
            "author": post.author or "",
            "keywords": json.dumps(post.keywords),
            "content_type": post.content_type or "",
            "source_snippet": post.source_snippet or "",
            "created_at": post.created_at.isoformat(),
            "likes": post.likes,
            "comments": post.comments,
            "is_gold_standard": post.is_gold_standard,
            "last_engagement_update_at": post.last_engagement_update_at.isoformat() if post.last_engagement_update_at else ""
        }
        
        # Add to ChromaDB
        self.collection.add(
            embeddings=[post.embedding],
            documents=[post.text],
            metadatas=[metadata],
            ids=[post.id]
        )
        
        return post.id
    
    def add_posts_batch(self, posts: List[RAGPost]) -> List[str]:
        """
        Add multiple posts to the RAG system in batch.
        
        Args:
            posts: List of RAGPost objects to add
            
        Returns:
            List of IDs of the added posts
        """
        if not posts:
            return []
        
        embeddings = []
        documents = []
        metadatas = []
        ids = []
        
        for post in posts:
            # Generate embedding if not provided
            if not post.embedding:
                post.embedding = self.embedding_model.encode([post.text])[0].tolist()
            
            embeddings.append(post.embedding)
            documents.append(post.text)
            ids.append(post.id)
            
            # Prepare metadata
            metadata = {
                "title": post.title or "",
                "author": post.author or "",
                "keywords": json.dumps(post.keywords),
                "content_type": post.content_type or "",
                "source_snippet": post.source_snippet or "",
                "created_at": post.created_at.isoformat(),
                "likes": post.likes,
                "comments": post.comments,
                "is_gold_standard": post.is_gold_standard,
                "last_engagement_update_at": post.last_engagement_update_at.isoformat() if post.last_engagement_update_at else ""
            }
            metadatas.append(metadata)
        
        # Add to ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        return ids
    
    def retrieve_similar_posts(self, query_text: str, top_k: int = 3, 
                              include_gold_standard_only: bool = False,
                              min_engagement_threshold: Optional[int] = None) -> List[RAGPost]:
        """
        Retrieve posts similar to the query text.
        
        Args:
            query_text: Text to find similar posts for
            top_k: Number of similar posts to return
            include_gold_standard_only: If True, only return gold standard posts
            min_engagement_threshold: Minimum total engagement (likes + comments) required
            
        Returns:
            List of similar RAGPost objects
        """
        # Generate embedding for query
        query_embedding = self.embedding_model.encode([query_text])[0].tolist()
        
        # Build where clause for filtering
        where_clause = {}
        if include_gold_standard_only:
            where_clause["is_gold_standard"] = True
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k * 2,  # Get more results to filter if needed
            where=where_clause if where_clause else None,
            include=["documents", "metadatas", "embeddings", "distances"]
        )
        
        # Convert results to RAGPost objects
        posts = []
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i]
            
            # Apply engagement threshold filter if specified
            if min_engagement_threshold is not None:
                total_engagement = metadata.get('likes', 0) + metadata.get('comments', 0)
                if total_engagement < min_engagement_threshold:
                    continue
            
            # Parse metadata
            keywords = json.loads(metadata.get('keywords', '[]'))
            created_at = datetime.fromisoformat(metadata['created_at'])
            last_engagement_update_at = None
            if metadata.get('last_engagement_update_at'):
                last_engagement_update_at = datetime.fromisoformat(metadata['last_engagement_update_at'])
            
            post = RAGPost(
                id=results['ids'][0][i],
                title=metadata.get('title') or None,
                author=metadata.get('author') or None,
                text=results['documents'][0][i],
                embedding=results['embeddings'][0][i] if results['embeddings'] else [],
                keywords=keywords,
                content_type=metadata.get('content_type'),
                source_snippet=metadata.get('source_snippet'),
                created_at=created_at,
                likes=metadata.get('likes', 0),
                comments=metadata.get('comments', 0),
                is_gold_standard=metadata.get('is_gold_standard', False),
                last_engagement_update_at=last_engagement_update_at
            )
            posts.append(post)
            
            # Stop once we have enough posts
            if len(posts) >= top_k:
                break
        
        return posts
    
    def update_post_engagement(self, post_id: str, likes: int, comments: int) -> bool:
        """
        Update the engagement metrics for a post.
        
        Args:
            post_id: ID of the post to update
            likes: New likes count
            comments: New comments count
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            # Get the current post
            results = self.collection.get(ids=[post_id], include=["metadatas"])
            if not results['ids']:
                return False
            
            # Update metadata
            metadata = results['metadatas'][0]
            metadata['likes'] = likes
            metadata['comments'] = comments
            metadata['last_engagement_update_at'] = datetime.utcnow().isoformat()
            
            # Update in ChromaDB
            self.collection.update(
                ids=[post_id],
                metadatas=[metadata]
            )
            
            return True
        except Exception as e:
            print(f"Error updating post engagement: {e}")
            return False
    
    def get_post_by_id(self, post_id: str) -> Optional[RAGPost]:
        """
        Retrieve a specific post by its ID.
        
        Args:
            post_id: ID of the post to retrieve
            
        Returns:
            RAGPost object if found, None otherwise
        """
        try:
            results = self.collection.get(
                ids=[post_id],
                include=["documents", "metadatas", "embeddings"]
            )
            
            if not results['ids']:
                return None
            
            metadata = results['metadatas'][0]
            keywords = json.loads(metadata.get('keywords', '[]'))
            created_at = datetime.fromisoformat(metadata['created_at'])
            last_engagement_update_at = None
            if metadata.get('last_engagement_update_at'):
                last_engagement_update_at = datetime.fromisoformat(metadata['last_engagement_update_at'])
            
            return RAGPost(
                id=results['ids'][0],
                title=metadata.get('title') or None,
                author=metadata.get('author') or None,
                text=results['documents'][0],
                embedding=results['embeddings'][0] if results['embeddings'] else [],
                keywords=keywords,
                content_type=metadata.get('content_type'),
                source_snippet=metadata.get('source_snippet'),
                created_at=created_at,
                likes=metadata.get('likes', 0),
                comments=metadata.get('comments', 0),
                is_gold_standard=metadata.get('is_gold_standard', False),
                last_engagement_update_at=last_engagement_update_at
            )
            
        except Exception as e:
            print(f"Error retrieving post {post_id}: {e}")
            return None
    
    def list_all_posts(self, limit: Optional[int] = None) -> List[RAGPost]:
        """
        List all posts in the RAG system.
        
        Args:
            limit: Maximum number of posts to return
            
        Returns:
            List of all RAGPost objects
        """
        try:
            # Get all posts
            results = self.collection.get(
                include=["documents", "metadatas", "embeddings"],
                limit=limit
            )
            
            posts = []
            for i in range(len(results['ids'])):
                metadata = results['metadatas'][i]
                keywords = json.loads(metadata.get('keywords', '[]'))
                created_at = datetime.fromisoformat(metadata['created_at'])
                last_engagement_update_at = None
                if metadata.get('last_engagement_update_at'):
                    last_engagement_update_at = datetime.fromisoformat(metadata['last_engagement_update_at'])
                
                post = RAGPost(
                    id=results['ids'][i],
                    title=metadata.get('title') or None,
                    author=metadata.get('author') or None,
                    text=results['documents'][i],
                    embedding=results['embeddings'][i] if results['embeddings'] else [],
                    keywords=keywords,
                    content_type=metadata.get('content_type'),
                    source_snippet=metadata.get('source_snippet'),
                    created_at=created_at,
                    likes=metadata.get('likes', 0),
                    comments=metadata.get('comments', 0),
                    is_gold_standard=metadata.get('is_gold_standard', False),
                    last_engagement_update_at=last_engagement_update_at
                )
                posts.append(post)
            
            return posts
            
        except Exception as e:
            print(f"Error listing posts: {e}")
            return []
    
    def delete_post(self, post_id: str) -> bool:
        """
        Delete a post from the RAG system.
        
        Args:
            post_id: ID of the post to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            self.collection.delete(ids=[post_id])
            return True
        except Exception as e:
            print(f"Error deleting post {post_id}: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            all_posts = self.list_all_posts()
            total_posts = len(all_posts)
            gold_standard_count = sum(1 for post in all_posts if post.is_gold_standard)
            total_likes = sum(post.likes for post in all_posts)
            total_comments = sum(post.comments for post in all_posts)
            
            return {
                "total_posts": total_posts,
                "gold_standard_posts": gold_standard_count,
                "generated_posts": total_posts - gold_standard_count,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "avg_likes_per_post": total_likes / total_posts if total_posts > 0 else 0,
                "avg_comments_per_post": total_comments / total_posts if total_posts > 0 else 0
            }
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {}
    
    def format_rag_context(self, posts: List[RAGPost]) -> str:
        """
        Format retrieved posts as context for the LLM.
        
        Args:
            posts: List of RAGPost objects to format
            
        Returns:
            Formatted string for LLM context
        """
        if not posts:
            return ""
        
        context_parts = []
        for i, post in enumerate(posts, 1):
            engagement_info = ""
            if post.likes > 0 or post.comments > 0:
                engagement_info = f" ({post.likes} likes, {post.comments} comments)"
            
            context_parts.append(f"Example {i}{engagement_info}:\n{post.text}")
        
        return "\n\n".join(context_parts) 