import chromadb
from chromadb.config import Settings
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from sentence_transformers import SentenceTransformer
from src.models import RAGPost, GuidelineDocument, Persona
import json
import os

class RAGSystem:
    """
    Retrieval Augmented Generation system for storing and retrieving LinkedIn posts and guideline documents.
    Uses ChromaDB as the vector database.
    """
    
    def __init__(self, db_path: str = "./chroma_db", collection_name: str = "linkedin_posts", 
                 guidelines_collection_name: str = "guidelines",
                 personas_collection_name: str = "personas",
                 embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize the RAG system with ChromaDB.
        
        Args:
            db_path: Path to store the ChromaDB database
            collection_name: Name of the collection to store posts
            guidelines_collection_name: Name of the collection to store guideline documents
            personas_collection_name: Name of the collection to store personas
            embedding_model: Sentence transformer model for embeddings
        """
        self.db_path = db_path
        self.collection_name = collection_name
        self.guidelines_collection_name = guidelines_collection_name
        self.personas_collection_name = personas_collection_name
        self.embedding_model_name = embedding_model
        
        # Initialize sentence transformer
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Get or create posts collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except ValueError:
            # Collection doesn't exist, create it
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "LinkedIn posts for RAG system"}
            )
            
        # Get or create guidelines collection
        try:
            self.guidelines_collection = self.client.get_collection(name=guidelines_collection_name)
        except ValueError:
            # Collection doesn't exist, create it
            self.guidelines_collection = self.client.create_collection(
                name=guidelines_collection_name,
                metadata={"description": "Guideline documents for post generation"}
            )
        
        # Get or create personas collection
        try:
            self.personas_collection = self.client.get_collection(name=personas_collection_name)
        except ValueError:
            # Collection doesn't exist, create it
            self.personas_collection = self.client.create_collection(
                name=personas_collection_name,
                metadata={"description": "Writing personas for different content styles"}
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
            "last_engagement_update_at": post.last_engagement_update_at.isoformat() if post.last_engagement_update_at else "",
            "persona_ids": json.dumps(post.persona_ids)
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
                "last_engagement_update_at": post.last_engagement_update_at.isoformat() if post.last_engagement_update_at else "",
                "persona_ids": json.dumps(post.persona_ids)
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
                              min_engagement_threshold: Optional[int] = None,
                              persona_id: Optional[str] = None) -> List[RAGPost]:
        """
        Retrieve posts similar to the query text.
        
        Args:
            query_text: Text to find similar posts for
            top_k: Number of similar posts to return
            include_gold_standard_only: If True, only return gold standard posts
            min_engagement_threshold: Minimum total engagement (likes + comments) required
            persona_id: If provided, only return posts associated with this persona
            
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
            
            # Parse persona_ids
            persona_ids = json.loads(metadata.get('persona_ids', '[]'))
            
            # Filter by persona if specified
            if persona_id is not None:
                # If post has no persona_ids, it applies to all personas
                # If post has persona_ids, check if our persona is included
                if persona_ids and persona_id not in persona_ids:
                    continue
            
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
                last_engagement_update_at=last_engagement_update_at,
                persona_ids=persona_ids
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
                last_engagement_update_at=last_engagement_update_at,
                persona_ids=json.loads(metadata.get('persona_ids', '[]'))
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
                    last_engagement_update_at=last_engagement_update_at,
                    persona_ids=json.loads(metadata.get('persona_ids', '[]'))
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
            posts: List of RAGPost objects
            
        Returns:
            Formatted context string
        """
        if not posts:
            return "No similar posts found."
        
        context_parts = []
        for i, post in enumerate(posts, 1):
            engagement = post.likes + post.comments
            context_parts.append(
                f"--- Post {i} ---\n"
                f"Title: {post.title or 'Untitled'}\n"
                f"Author: {post.author or 'Unknown'}\n"
                f"Engagement: {engagement} (👍 {post.likes}, 💬 {post.comments})\n"
                f"Content: {post.text}\n"
            )
        
        return "\n".join(context_parts)

    # === GUIDELINE DOCUMENT METHODS ===
    
    def add_guideline(self, guideline: GuidelineDocument) -> str:
        """
        Add a guideline document to the RAG system.
        
        Args:
            guideline: GuidelineDocument object to add
            
        Returns:
            ID of the added guideline
        """
        # Generate embedding if not provided
        if not guideline.embedding:
            guideline.embedding = self.embedding_model.encode([guideline.content])[0].tolist()
        
        # Prepare metadata
        metadata = {
            "title": guideline.title,
            "hook_type": guideline.hook_type,
            "section": guideline.section or "",
            "created_at": guideline.created_at.isoformat(),
            "priority": guideline.priority
        }
        
        # Add to ChromaDB
        self.guidelines_collection.add(
            embeddings=[guideline.embedding],
            documents=[guideline.content],
            metadatas=[metadata],
            ids=[guideline.id]
        )
        
        return guideline.id
    
    def add_guidelines_batch(self, guidelines: List[GuidelineDocument]) -> List[str]:
        """
        Add multiple guideline documents to the RAG system in batch.
        
        Args:
            guidelines: List of GuidelineDocument objects to add
            
        Returns:
            List of IDs of the added guidelines
        """
        if not guidelines:
            return []
        
        embeddings = []
        documents = []
        metadatas = []
        ids = []
        
        for guideline in guidelines:
            # Generate embedding if not provided
            if not guideline.embedding:
                guideline.embedding = self.embedding_model.encode([guideline.content])[0].tolist()
            
            embeddings.append(guideline.embedding)
            documents.append(guideline.content)
            ids.append(guideline.id)
            
            # Prepare metadata
            metadata = {
                "title": guideline.title,
                "hook_type": guideline.hook_type,
                "section": guideline.section or "",
                "created_at": guideline.created_at.isoformat(),
                "priority": guideline.priority
            }
            metadatas.append(metadata)
        
        # Add to ChromaDB
        self.guidelines_collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        return ids
    
    def retrieve_relevant_guidelines(self, query_text: str, top_k: int = 3,
                                   hook_type: Optional[str] = None,
                                   section: Optional[str] = None) -> List[GuidelineDocument]:
        """
        Retrieve guideline documents relevant to the query text.
        
        Args:
            query_text: Text to find relevant guidelines for
            top_k: Number of guidelines to return
            hook_type: Filter by hook type (e.g., "hooks", "templates")
            section: Filter by section (e.g., "curiosity", "storytelling")
            
        Returns:
            List of relevant GuidelineDocument objects
        """
        # Generate embedding for query
        query_embedding = self.embedding_model.encode([query_text])[0].tolist()
        
        # Build where clause for filtering
        where_clause = {}
        if hook_type:
            where_clause["hook_type"] = hook_type
        if section:
            where_clause["section"] = section
        
        # Query ChromaDB
        results = self.guidelines_collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause if where_clause else None,
            include=["documents", "metadatas", "embeddings", "distances"]
        )
        
        # Convert results to GuidelineDocument objects
        guidelines = []
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i]
            created_at = datetime.fromisoformat(metadata['created_at'])
            
            guideline = GuidelineDocument(
                id=results['ids'][0][i],
                title=metadata['title'],
                content=results['documents'][0][i],
                hook_type=metadata['hook_type'],
                section=metadata.get('section') or None,
                embedding=results['embeddings'][0][i] if results['embeddings'] else [],
                created_at=created_at,
                priority=metadata.get('priority', 1)
            )
            guidelines.append(guideline)
        
        # Sort by priority (higher first)
        guidelines.sort(key=lambda x: x.priority, reverse=True)
        return guidelines
    
    def list_all_guidelines(self, limit: Optional[int] = None) -> List[GuidelineDocument]:
        """
        Get all guideline documents from the system.
        
        Args:
            limit: Maximum number of guidelines to return
            
        Returns:
            List of all GuidelineDocument objects
        """
        # Get all documents from collection
        results = self.guidelines_collection.get(
            limit=limit,
            include=["documents", "metadatas", "embeddings"]
        )
        
        guidelines = []
        for i in range(len(results['ids'])):
            metadata = results['metadatas'][i]
            created_at = datetime.fromisoformat(metadata['created_at'])
            
            guideline = GuidelineDocument(
                id=results['ids'][i],
                title=metadata['title'],
                content=results['documents'][i],
                hook_type=metadata['hook_type'],
                section=metadata.get('section') or None,
                embedding=results['embeddings'][i] if results['embeddings'] else [],
                created_at=created_at,
                priority=metadata.get('priority', 1)
            )
            guidelines.append(guideline)
        
        # Sort by priority (higher first), then by creation date
        guidelines.sort(key=lambda x: (x.priority, x.created_at), reverse=True)
        return guidelines
    
    def delete_guideline(self, guideline_id: str) -> bool:
        """
        Delete a guideline document from the system.
        
        Args:
            guideline_id: ID of the guideline to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            self.guidelines_collection.delete(ids=[guideline_id])
            return True
        except Exception as e:
            print(f"Error deleting guideline {guideline_id}: {e}")
            return False
    
    def bulk_delete_guidelines(self, guideline_ids: List[str]) -> Dict[str, Any]:
        """
        Delete multiple guideline documents from the system.
        
        Args:
            guideline_ids: List of guideline IDs to delete
            
        Returns:
            Dictionary with deletion results
        """
        try:
            deleted_count = 0
            failed_count = 0
            
            for guideline_id in guideline_ids:
                success = self.delete_guideline(guideline_id)
                
                if success:
                    deleted_count += 1
                    print(f"✅ Deleted guideline: {guideline_id}")
                else:
                    failed_count += 1
                    print(f"❌ Failed to delete guideline: {guideline_id}")
            
            result = {
                "deleted_count": deleted_count,
                "failed_count": failed_count,
                "total_requested": len(guideline_ids),
                "success": deleted_count > 0
            }
            
            print(f"📊 Bulk guideline deletion complete: {deleted_count} deleted, {failed_count} failed")
            return result
            
        except Exception as e:
            print(f"❌ Error during bulk guideline deletion: {str(e)}")
            return {
                "deleted_count": 0,
                "failed_count": len(guideline_ids),
                "total_requested": len(guideline_ids),
                "success": False,
                "error": str(e)
            }
    
    def format_guidelines_context(self, guidelines: List[GuidelineDocument]) -> str:
        """
        Format retrieved guidelines as context for the LLM.
        
        Args:
            guidelines: List of GuidelineDocument objects
            
        Returns:
            Formatted context string
        """
        if not guidelines:
            return "No relevant guidelines found."
        
        context_parts = []
        for i, guideline in enumerate(guidelines, 1):
            context_parts.append(
                f"--- Guideline {i}: {guideline.title} ---\n"
                f"Type: {guideline.hook_type}\n"
                f"Section: {guideline.section or 'General'}\n"
                f"Content: {guideline.content}\n"
            )
        
        return "\n".join(context_parts)

    # === PERSONA METHODS ===
    
    def add_persona(self, persona: Persona) -> str:
        """
        Add a persona to the RAG system.
        
        Args:
            persona: Persona object to add
            
        Returns:
            ID of the added persona
        """
        # Generate embedding if not provided
        if not persona.embedding:
            persona.embedding = self.embedding_model.encode([persona.description])[0].tolist()
        
        # Prepare metadata with all persona fields
        metadata = {
            "name": persona.name,
            "description": persona.description,
            "voice_tone": persona.voice_tone,
            "content_types": json.dumps(persona.content_types),
            "style_guide": persona.style_guide,
            "example_hooks": json.dumps(persona.example_hooks),
            "target_audience": persona.target_audience,
            "created_at": persona.created_at.isoformat(),
            "is_default": persona.is_default,
            "is_active": persona.is_active
        }
        
        # Add to ChromaDB
        self.personas_collection.add(
            embeddings=[persona.embedding],
            documents=[persona.description],
            metadatas=[metadata],
            ids=[persona.id]
        )
        
        return persona.id
    
    def add_personas_batch(self, personas: List[Persona]) -> List[str]:
        """
        Add multiple personas to the RAG system in batch.
        
        Args:
            personas: List of Persona objects to add
            
        Returns:
            List of IDs of the added personas
        """
        if not personas:
            return []
        
        embeddings = []
        documents = []
        metadatas = []
        ids = []
        
        for persona in personas:
            # Generate embedding if not provided
            if not persona.embedding:
                persona.embedding = self.embedding_model.encode([persona.description])[0].tolist()
            
            embeddings.append(persona.embedding)
            documents.append(persona.description)
            ids.append(persona.id)
            
            # Prepare metadata
            metadata = {
                "name": persona.name,
                "description": persona.description,
                "voice_tone": persona.voice_tone,
                "content_types": json.dumps(persona.content_types),
                "style_guide": persona.style_guide,
                "example_hooks": json.dumps(persona.example_hooks),
                "target_audience": persona.target_audience,
                "created_at": persona.created_at.isoformat(),
                "is_default": persona.is_default,
                "is_active": persona.is_active
            }
            metadatas.append(metadata)
        
        # Add to ChromaDB
        self.personas_collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        return ids
    
    def retrieve_relevant_personas(self, query_text: str, top_k: int = 3) -> List[Persona]:
        """
        Retrieve personas relevant to the query text.
        
        Args:
            query_text: Text to find relevant personas for
            top_k: Number of personas to return
            
        Returns:
            List of relevant Persona objects
        """
        # Generate embedding for query
        query_embedding = self.embedding_model.encode([query_text])[0].tolist()
        
        # Query ChromaDB
        results = self.personas_collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "embeddings", "distances"]
        )
        
        # Convert results to Persona objects
        personas = []
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i]
            created_at = datetime.fromisoformat(metadata['created_at'])
            
            persona = Persona(
                id=results['ids'][0][i],
                name=metadata['name'],
                description=metadata['description'],
                voice_tone=metadata.get('voice_tone', ''),
                content_types=json.loads(metadata.get('content_types', '[]')),
                style_guide=metadata.get('style_guide', ''),
                example_hooks=json.loads(metadata.get('example_hooks', '[]')),
                target_audience=metadata.get('target_audience', ''),
                embedding=results['embeddings'][0][i] if results['embeddings'] else [],
                created_at=created_at,
                is_default=metadata.get('is_default', False),
                is_active=metadata.get('is_active', True)
            )
            personas.append(persona)
        
        return personas
    
    def list_all_personas(self, limit: Optional[int] = None) -> List[Persona]:
        """
        Get all personas from the system.
        
        Args:
            limit: Maximum number of personas to return
            
        Returns:
            List of all Persona objects
        """
        # Get all documents from collection
        results = self.personas_collection.get(
            limit=limit,
            include=["documents", "metadatas", "embeddings"]
        )
        
        personas = []
        for i in range(len(results['ids'])):
            metadata = results['metadatas'][i]
            created_at = datetime.fromisoformat(metadata['created_at'])
            
            persona = Persona(
                id=results['ids'][i],
                name=metadata['name'],
                description=metadata['description'],
                voice_tone=metadata.get('voice_tone', ''),
                content_types=json.loads(metadata.get('content_types', '[]')),
                style_guide=metadata.get('style_guide', ''),
                example_hooks=json.loads(metadata.get('example_hooks', '[]')),
                target_audience=metadata.get('target_audience', ''),
                embedding=results['embeddings'][i] if results['embeddings'] else [],
                created_at=created_at,
                is_default=metadata.get('is_default', False),
                is_active=metadata.get('is_active', True)
            )
            personas.append(persona)
        
        return personas
    
    def delete_persona(self, persona_id: str) -> bool:
        """
        Delete a persona from the system.
        
        Args:
            persona_id: ID of the persona to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            self.personas_collection.delete(ids=[persona_id])
            return True
        except Exception as e:
            print(f"Error deleting persona {persona_id}: {e}")
            return False
    
    def bulk_delete_personas(self, persona_ids: List[str]) -> Dict[str, Any]:
        """
        Delete multiple personas from the system.
        
        Args:
            persona_ids: List of persona IDs to delete
            
        Returns:
            Dictionary with deletion results
        """
        try:
            deleted_count = 0
            failed_count = 0
            
            for persona_id in persona_ids:
                success = self.delete_persona(persona_id)
                
                if success:
                    deleted_count += 1
                    print(f"✅ Deleted persona: {persona_id}")
                else:
                    failed_count += 1
                    print(f"❌ Failed to delete persona: {persona_id}")
            
            result = {
                "deleted_count": deleted_count,
                "failed_count": failed_count,
                "total_requested": len(persona_ids),
                "success": deleted_count > 0
            }
            
            print(f"📊 Bulk persona deletion complete: {deleted_count} deleted, {failed_count} failed")
            return result
            
        except Exception as e:
            print(f"❌ Error during bulk persona deletion: {str(e)}")
            return {
                "deleted_count": 0,
                "failed_count": len(persona_ids),
                "total_requested": len(persona_ids),
                "success": False,
                "error": str(e)
            }
    
    def format_personas_context(self, personas: List[Persona]) -> str:
        """
        Format retrieved personas as context for the LLM.
        
        Args:
            personas: List of Persona objects
            
        Returns:
            Formatted context string
        """
        if not personas:
            return "No relevant personas found."
        
        context_parts = []
        for i, persona in enumerate(personas, 1):
            context_parts.append(
                f"--- Persona {i}: {persona.name} ---\n"
                f"Description: {persona.description}\n"
            )
        
        return "\n".join(context_parts) 