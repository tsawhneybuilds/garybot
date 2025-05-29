from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from src.config import AppConfig, get_config
from src.transcript_processor import TranscriptProcessor
from src.viral_snippet_detector import ViralSnippetDetector, DEFAULT_GOLD_STANDARD_POSTS
from src.content_generator import ContentGenerator
from src.rag_system import RAGSystem
from src.models import (
    TranscriptSegment, 
    ViralSnippetCandidate, 
    GeneratedPostDraft, 
    RAGPost,
    GoldStandardPost
)

class GaryBot:
    """
    Main orchestrator class for the AI-powered LinkedIn post generator.
    Coordinates all modules to transform transcripts into viral LinkedIn posts.
    """
    
    def __init__(self, config: Optional[AppConfig] = None):
        """
        Initialize GaryBot with all necessary components.
        
        Args:
            config: Optional configuration object. If None, loads from environment.
        """
        self.config = config or get_config()
        
        # Track if system has been intentionally cleared
        self._system_cleared = False
        
        # Initialize components
        self.transcript_processor = TranscriptProcessor()
        self.viral_detector = ViralSnippetDetector(self.config.embedding_model_name)
        self.content_generator = ContentGenerator(
            api_key=self.config.groq_api_key,
            model=self.config.llm_model
        )
        self.rag_system = RAGSystem(
            db_path=self.config.db_path,
            collection_name=self.config.collection_name,
            embedding_model=self.config.embedding_model_name
        )
        
        # Initialize with default gold standard posts if RAG is empty and not cleared
        self._initialize_rag_if_empty()
    
    def _initialize_rag_if_empty(self) -> None:
        """Initialize RAG system with default gold standard posts if it's empty and not intentionally cleared."""
        # Don't auto-initialize if system was intentionally cleared
        if self._system_cleared:
            return
            
        stats = self.rag_system.get_collection_stats()
        
        if stats.get("total_posts", 0) == 0:
            print("📚 Initializing RAG system with default gold standard posts...")
            
            # Add default posts to RAG
            default_posts = []
            for post_text in DEFAULT_GOLD_STANDARD_POSTS:
                rag_post = RAGPost(
                    text=post_text,
                    embedding=[],  # Will be computed automatically
                    keywords=["startups", "entrepreneurship", "founders"],
                    content_type="Founder Philosophy",
                    is_gold_standard=True,
                    likes=100,  # Simulated engagement
                    comments=20
                )
                default_posts.append(rag_post)
            
            self.rag_system.add_posts_batch(default_posts)
            
            # Also add to viral detector
            self.viral_detector.load_gold_standard_from_texts(DEFAULT_GOLD_STANDARD_POSTS)
            
            print(f"✅ Added {len(default_posts)} default gold standard posts")
    
    def process_transcript(self, transcript_content: str, 
                          transcript_id: Optional[str] = None) -> List[TranscriptSegment]:
        """
        Process a transcript into clean, segmented pieces.
        
        Args:
            transcript_content: Raw transcript text
            transcript_id: Optional identifier for the transcript
            
        Returns:
            List of processed transcript segments
        """
        return self.transcript_processor.process_transcript(
            transcript_content, 
            transcript_id or str(uuid.uuid4())
        )
    
    def identify_viral_snippets(self, segments: List[TranscriptSegment]) -> List[ViralSnippetCandidate]:
        """
        Identify the most promising viral snippets from transcript segments.
        
        Args:
            segments: List of transcript segments
            
        Returns:
            List of viral snippet candidates ranked by potential
        """
        return self.viral_detector.identify_viral_snippets(
            segments,
            top_k=self.config.max_viral_candidates,
            min_similarity=self.config.min_similarity_threshold
        )
    
    def generate_post_from_snippet(self, snippet: str) -> GeneratedPostDraft:
        """
        Generate a LinkedIn post from a transcript snippet using RAG context.
        
        Args:
            snippet: Text snippet to base the post on
            
        Returns:
            Generated post draft with metadata
        """
        return self.content_generator.generate_post_with_rag(
            snippet, 
            self.rag_system, 
            self.config.rag_retrieval_count
        )
    
    def generate_multiple_variations(self, snippet: str, num_variations: int = 3) -> List[str]:
        """
        Generate multiple variations of a post for the same snippet.
        
        Args:
            snippet: Text snippet to base posts on
            num_variations: Number of variations to generate
            
        Returns:
            List of post variations
        """
        # Get RAG context
        similar_posts = self.rag_system.retrieve_similar_posts(snippet, top_k=self.config.rag_retrieval_count)
        rag_context = self.rag_system.format_rag_context(similar_posts)
        
        return self.content_generator.generate_multiple_posts(
            snippet,
            rag_context,
            num_variations,
            self.config.default_temperature
        )
    
    def approve_post(self, draft: GeneratedPostDraft, keywords: Optional[List[str]] = None,
                    content_type: Optional[str] = None) -> str:
        """
        Approve a generated post and add it to the RAG system.
        
        Args:
            draft: Generated post draft to approve
            keywords: Optional keywords to associate with the post
            content_type: Optional content type classification
            
        Returns:
            ID of the approved post in RAG system
        """
        # Create RAGPost from draft
        rag_post = RAGPost(
            text=draft.draft_text,
            embedding=[],  # Will be computed automatically
            keywords=keywords or draft.suggested_hashtags,
            content_type=content_type,
            source_snippet=draft.original_snippet,
            is_gold_standard=False
        )
        
        # Add to RAG system
        post_id = self.rag_system.add_post(rag_post)
        
        print(f"✅ Post approved and added to RAG system with ID: {post_id}")
        return post_id
    
    def update_post_engagement(self, post_id: str, likes: int, comments: int) -> bool:
        """
        Update engagement metrics for a post.
        
        Args:
            post_id: ID of the post to update
            likes: Number of likes
            comments: Number of comments
            
        Returns:
            True if update was successful
        """
        success = self.rag_system.update_post_engagement(post_id, likes, comments)
        if success:
            print(f"✅ Updated engagement for post {post_id}: {likes} likes, {comments} comments")
        else:
            print(f"❌ Failed to update engagement for post {post_id}")
        return success
    
    def add_gold_standard_post(self, post_text: str, keywords: Optional[List[str]] = None,
                              likes: int = 0, comments: int = 0, content_type: Optional[str] = None,
                              title: Optional[str] = None, author: Optional[str] = None) -> str:
        """
        Add a new gold standard post to both RAG system and viral detector.
        Automatically extracts keywords and classifies content type if not provided.
        
        Args:
            post_text: Text of the successful post
            keywords: Keywords to associate with the post (auto-extracted if None)
            likes: Number of likes the post received
            comments: Number of comments the post received
            content_type: Content type classification (auto-classified if None)
            title: Optional title for the post
            author: Optional author of the post
            
        Returns:
            ID of the added post
        """
        # Auto-extract keywords and content type if not provided
        if keywords is None or content_type is None:
            extracted_data = self._extract_post_metadata(post_text)
            keywords = keywords or extracted_data.get("keywords", [])
            content_type = content_type or extracted_data.get("content_type", "General")
        
        # Add to RAG system
        rag_post = RAGPost(
            text=post_text,
            title=title,
            author=author,
            embedding=[],
            keywords=keywords,
            content_type=content_type,
            is_gold_standard=True,
            likes=likes,
            comments=comments
        )
        post_id = self.rag_system.add_post(rag_post)
        
        # Add to viral detector
        gold_post = GoldStandardPost(
            text=post_text,
            keywords=keywords
        )
        self.viral_detector.add_gold_standard_posts([gold_post])
        
        print(f"✅ Added gold standard post with ID: {post_id}")
        if title:
            print(f"   Title: {title}")
        if author:
            print(f"   Author: {author}")
        print(f"   Keywords: {', '.join(keywords)}")
        print(f"   Content Type: {content_type}")
        return post_id
    
    def _extract_post_metadata(self, post_text: str) -> Dict[str, Any]:
        """
        Extract keywords and classify content type from a LinkedIn post using LLM.
        
        Args:
            post_text: The LinkedIn post text to analyze
            
        Returns:
            Dictionary with extracted keywords and content type
        """
        from src.config import CONTENT_TYPES, DEFAULT_KEYWORDS
        
        content_types_str = ", ".join(CONTENT_TYPES)
        
        extraction_prompt = f"""
        Analyze this LinkedIn post and extract relevant information:

        **Post:**
        {post_text}

        Please provide:
        1. **Keywords** (3-6 relevant keywords from business/startup domain)
        2. **Content Type** (choose the best fit from: {content_types_str})

        Consider Gary Lin's voice and typical LinkedIn content themes like:
        - Startups, entrepreneurship, founders, leadership
        - Product development, team building, culture
        - Fundraising, growth, scaling, strategy
        - Personal stories, lessons learned, advice

        Format your response as:
        KEYWORDS: keyword1, keyword2, keyword3, keyword4
        CONTENT_TYPE: [chosen type]
        """
        
        try:
            chat_completion = self.content_generator.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": extraction_prompt
                    }
                ],
                model=self.content_generator.model,
                temperature=0.3,  # Lower temperature for consistent extraction
                max_tokens=200,
                top_p=1,
                stream=False
            )
            
            response_text = chat_completion.choices[0].message.content.strip()
            return self._parse_metadata_response(response_text)
            
        except Exception as e:
            print(f"⚠️ Error extracting metadata, using defaults: {str(e)}")
            return {
                "keywords": ["startups", "entrepreneurship", "founders"],
                "content_type": "General"
            }
    
    def _parse_metadata_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse the LLM response for keywords and content type.
        
        Args:
            response_text: Raw response from LLM
            
        Returns:
            Parsed metadata dictionary
        """
        import re
        from src.config import CONTENT_TYPES
        
        try:
            # Extract keywords
            keywords_match = re.search(r'KEYWORDS:\s*(.+)', response_text, re.IGNORECASE)
            keywords = []
            if keywords_match:
                keywords_text = keywords_match.group(1)
                keywords = [k.strip() for k in keywords_text.split(',') if k.strip()]
            
            # Extract content type
            content_type_match = re.search(r'CONTENT_TYPE:\s*(.+)', response_text, re.IGNORECASE)
            content_type = "General"
            if content_type_match:
                extracted_type = content_type_match.group(1).strip()
                # Find the best match from available content types
                for ct in CONTENT_TYPES:
                    if ct.lower() in extracted_type.lower() or extracted_type.lower() in ct.lower():
                        content_type = ct
                        break
            
            return {
                "keywords": keywords[:6],  # Limit to 6 keywords
                "content_type": content_type
            }
            
        except Exception as e:
            print(f"⚠️ Error parsing metadata response: {str(e)}")
            return {
                "keywords": ["startups", "entrepreneurship"],
                "content_type": "General"
            }
    
    def analyze_post_potential(self, post_text: str) -> Dict[str, Any]:
        """
        Analyze the viral potential of a post.
        
        Args:
            post_text: Text of the post to analyze
            
        Returns:
            Analysis results with score, strengths, and improvements
        """
        return self.content_generator.analyze_post_potential(post_text)
    
    def regenerate_with_feedback(self, original_snippet: str, previous_draft: str, 
                                feedback: str) -> str:
        """
        Regenerate a post based on user feedback.
        
        Args:
            original_snippet: Original transcript snippet
            previous_draft: Previously generated draft
            feedback: User feedback on improvements needed
            
        Returns:
            Revised post text
        """
        # Get RAG context
        similar_posts = self.rag_system.retrieve_similar_posts(original_snippet, top_k=self.config.rag_retrieval_count)
        rag_context = self.rag_system.format_rag_context(similar_posts)
        
        return self.content_generator.regenerate_with_feedback(
            original_snippet,
            previous_draft,
            feedback,
            rag_context
        )
    
    def get_post_history(self, limit: Optional[int] = None) -> List[RAGPost]:
        """
        Get history of all posts in the system.
        
        Args:
            limit: Maximum number of posts to return
            
        Returns:
            List of posts sorted by creation date (newest first)
        """
        posts = self.rag_system.list_all_posts(limit)
        # Sort by creation date, newest first
        posts.sort(key=lambda p: p.created_at, reverse=True)
        return posts
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the system.
        
        Returns:
            Dictionary with system statistics
        """
        rag_stats = self.rag_system.get_collection_stats()
        
        return {
            "rag_stats": rag_stats,
            "gary_stats": self.get_gary_lin_stats(),
            "viral_detector_posts": len(self.viral_detector.gold_standard_posts),
            "config": {
                "llm_model": self.config.llm_model,
                "embedding_model": self.config.embedding_model_name,
                "rag_retrieval_count": self.config.rag_retrieval_count
            }
        }
    
    def get_gary_lin_stats(self) -> Dict[str, Any]:
        """
        Get statistics filtered for Gary Lin's posts only.
        
        Returns:
            Dictionary with Gary Lin specific statistics
        """
        try:
            all_posts = self.rag_system.list_all_posts()
            
            # Filter for Gary Lin's posts only
            gary_posts = [post for post in all_posts if getattr(post, 'author', None) == 'Gary Lin']
            
            if not gary_posts:
                return {
                    "total_posts": 0,
                    "gold_standard_posts": 0,
                    "generated_posts": 0,
                    "total_likes": 0,
                    "total_comments": 0,
                    "avg_likes_per_post": 0,
                    "avg_comments_per_post": 0,
                    "total_engagement": 0
                }
            
            # Calculate stats for Gary's posts
            gold_standard_count = sum(1 for post in gary_posts if post.is_gold_standard)
            generated_count = len(gary_posts) - gold_standard_count
            total_likes = sum(post.likes for post in gary_posts)
            total_comments = sum(post.comments for post in gary_posts)
            
            return {
                "total_posts": len(gary_posts),
                "gold_standard_posts": gold_standard_count,
                "generated_posts": generated_count,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "avg_likes_per_post": total_likes / len(gary_posts) if gary_posts else 0,
                "avg_comments_per_post": total_comments / len(gary_posts) if gary_posts else 0,
                "total_engagement": total_likes + total_comments
            }
            
        except Exception as e:
            print(f"❌ Error calculating Gary Lin stats: {str(e)}")
            return {
                "total_posts": 0,
                "gold_standard_posts": 0,
                "generated_posts": 0,
                "total_likes": 0,
                "total_comments": 0,
                "avg_likes_per_post": 0,
                "avg_comments_per_post": 0,
                "total_engagement": 0
            }
    
    def full_pipeline(self, transcript_content: str) -> Dict[str, Any]:
        """
        Run the complete pipeline from transcript to post generation.
        
        Args:
            transcript_content: Raw transcript text
            
        Returns:
            Dictionary with all pipeline results
        """
        # Process transcript
        segments = self.process_transcript(transcript_content)
        
        # Identify viral snippets
        viral_candidates = self.identify_viral_snippets(segments)
        
        # Generate posts for top candidates
        generated_posts = []
        for candidate in viral_candidates[:3]:  # Top 3 candidates
            try:
                draft = self.generate_post_from_snippet(candidate.text)
                analysis = self.analyze_post_potential(draft.draft_text)
                
                generated_posts.append({
                    "candidate": candidate,
                    "draft": draft,
                    "analysis": analysis
                })
            except Exception as e:
                print(f"Error generating post for candidate: {e}")
        
        return {
            "segments_count": len(segments),
            "viral_candidates": viral_candidates,
            "generated_posts": generated_posts,
            "top_candidate": viral_candidates[0] if viral_candidates else None
        }
    
    def clear_default_posts(self) -> int:
        """
        Remove all default/sample posts from the system.
        
        Returns:
            Number of posts removed
        """
        try:
            # Set flag to prevent auto-reinitialization
            self._system_cleared = True
            
            # Get all posts
            all_posts = self.rag_system.list_all_posts()
            
            # Identify default posts (those with generic keywords or low engagement)
            default_post_ids = []
            for post in all_posts:
                # Check if it's likely a default post
                is_default = (
                    post.is_gold_standard and 
                    post.likes <= 100 and  # Low simulated engagement
                    set(post.keywords).issubset({"startups", "entrepreneurship", "founders"})
                )
                if is_default:
                    default_post_ids.append(post.id)
            
            # Remove from RAG system
            removed_count = 0
            for post_id in default_post_ids:
                if self.rag_system.delete_post(post_id):
                    removed_count += 1
            
            # Clear viral detector's gold standard posts and reload from remaining RAG posts
            remaining_posts = self.rag_system.list_all_posts()
            gold_standard_texts = [post.text for post in remaining_posts if post.is_gold_standard]
            self.viral_detector.load_gold_standard_from_texts(gold_standard_texts)
            
            print(f"✅ Removed {removed_count} default posts from the system")
            print("🔒 System marked as cleared - won't auto-add default posts")
            return removed_count
            
        except Exception as e:
            print(f"❌ Error clearing default posts: {str(e)}")
            return 0
    
    def delete_post(self, post_id: str) -> bool:
        """
        Delete a specific post from the system.
        
        Args:
            post_id: ID of the post to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            # Get the post first to check if it's gold standard
            posts = self.rag_system.list_all_posts()
            post_to_delete = None
            for post in posts:
                if post.id == post_id:
                    post_to_delete = post
                    break
            
            if not post_to_delete:
                print(f"❌ Post with ID {post_id} not found")
                return False
            
            # Remove from RAG system
            success = self.rag_system.delete_post(post_id)
            
            if success:
                # If it was a gold standard post, reload viral detector
                if post_to_delete.is_gold_standard:
                    remaining_posts = self.rag_system.list_all_posts()
                    gold_standard_texts = [post.text for post in remaining_posts if post.is_gold_standard]
                    self.viral_detector.load_gold_standard_from_texts(gold_standard_texts)
                    
                    # If no posts remain, mark system as cleared
                    if len(remaining_posts) == 0:
                        self._system_cleared = True
                        print("🔒 System marked as cleared - won't auto-add default posts")
                
                print(f"✅ Successfully deleted post: {post_to_delete.title or post_to_delete.text[:50]}...")
                return True
            else:
                print(f"❌ Failed to delete post with ID {post_id}")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting post: {str(e)}")
            return False
    
    def bulk_delete_posts(self, post_ids: List[str]) -> Dict[str, Any]:
        """
        Delete multiple posts from the system.
        
        Args:
            post_ids: List of post IDs to delete
            
        Returns:
            Dictionary with deletion results
        """
        try:
            deleted_count = 0
            failed_count = 0
            deleted_gold_standards = False
            
            for post_id in post_ids:
                # Get the post first to check if it's gold standard
                posts = self.rag_system.list_all_posts()
                post_to_delete = None
                for post in posts:
                    if post.id == post_id:
                        post_to_delete = post
                        break
                
                if not post_to_delete:
                    print(f"❌ Post with ID {post_id} not found")
                    failed_count += 1
                    continue
                
                # Track if we're deleting gold standard posts
                if post_to_delete.is_gold_standard:
                    deleted_gold_standards = True
                
                # Remove from RAG system
                success = self.rag_system.delete_post(post_id)
                
                if success:
                    deleted_count += 1
                    print(f"✅ Deleted post: {post_to_delete.title or post_to_delete.text[:50]}...")
                else:
                    failed_count += 1
                    print(f"❌ Failed to delete post with ID {post_id}")
            
            # If we deleted any gold standard posts, reload viral detector
            if deleted_gold_standards:
                remaining_posts = self.rag_system.list_all_posts()
                gold_standard_texts = [post.text for post in remaining_posts if post.is_gold_standard]
                self.viral_detector.load_gold_standard_from_texts(gold_standard_texts)
                print("🔄 Reloaded viral detector with remaining gold standard posts")
                
                # If no posts remain, mark system as cleared
                if len(remaining_posts) == 0:
                    self._system_cleared = True
                    print("🔒 System marked as cleared - won't auto-add default posts")
            
            result = {
                "deleted_count": deleted_count,
                "failed_count": failed_count,
                "total_requested": len(post_ids),
                "success": deleted_count > 0
            }
            
            print(f"📊 Bulk deletion complete: {deleted_count} deleted, {failed_count} failed")
            return result
            
        except Exception as e:
            print(f"❌ Error during bulk deletion: {str(e)}")
            return {
                "deleted_count": 0,
                "failed_count": len(post_ids),
                "total_requested": len(post_ids),
                "success": False,
                "error": str(e)
            }
    
    def reset_system_for_defaults(self) -> bool:
        """
        Reset the system to allow default posts to be added again.
        
        Returns:
            True if reset was successful
        """
        try:
            self._system_cleared = False
            print("🔓 System reset - default posts can be added again")
            
            # Check if we need to initialize with defaults now
            stats = self.rag_system.get_collection_stats()
            if stats.get("total_posts", 0) == 0:
                self._initialize_rag_if_empty()
            
            return True
        except Exception as e:
            print(f"❌ Error resetting system: {str(e)}")
            return False
    
    def rewrite_post_with_style(self, original_post: str, style_reference_id: Optional[str] = None,
                               content_type: Optional[str] = None, num_variations: int = 1) -> List[str]:
        """
        Rewrite an existing post to match the style of high-performing posts in the RAG system.
        
        Args:
            original_post: The post text to rewrite/improve
            style_reference_id: Optional specific post ID to use as style reference
            content_type: Optional content type to focus on for style matching
            num_variations: Number of rewritten variations to generate
            
        Returns:
            List of rewritten post variations
        """
        try:
            # Get style reference posts
            if style_reference_id:
                # Use specific post as reference
                all_posts = self.rag_system.list_all_posts()
                reference_posts = [post for post in all_posts if post.id == style_reference_id]
                if not reference_posts:
                    print(f"❌ Reference post with ID {style_reference_id} not found")
                    return [original_post]
                style_context = self.rag_system.format_rag_context(reference_posts)
            else:
                # Find similar high-performing posts
                similar_posts = self.rag_system.retrieve_similar_posts(
                    original_post, 
                    top_k=self.config.rag_retrieval_count
                )
                
                # Filter by content type if specified
                if content_type:
                    similar_posts = [post for post in similar_posts if post.content_type == content_type]
                
                # Sort by engagement and take top performers
                similar_posts.sort(key=lambda p: p.likes + p.comments, reverse=True)
                style_context = self.rag_system.format_rag_context(similar_posts[:3])
            
            # Generate rewritten versions
            rewritten_posts = []
            for i in range(num_variations):
                rewritten = self._generate_style_rewrite(original_post, style_context, variation_num=i+1)
                rewritten_posts.append(rewritten)
            
            return rewritten_posts
            
        except Exception as e:
            print(f"❌ Error rewriting post: {str(e)}")
            return [original_post]
    
    def _generate_style_rewrite(self, original_post: str, style_context: str, variation_num: int = 1) -> str:
        """
        Generate a rewritten version of a post using style references.
        
        Args:
            original_post: The original post to rewrite
            style_context: Context from high-performing posts for style reference
            variation_num: Variation number for different approaches
            
        Returns:
            Rewritten post text
        """
        from src.gary_lin_persona import GARY_LIN_PERSONA, CONTENT_GENERATION_INSTRUCTIONS
        
        # Different rewriting approaches for variations
        approaches = [
            "Rewrite this post to be more engaging and viral while maintaining the core message",
            "Make this post more compelling and attention-grabbing like the reference posts",
            "Improve this post's structure and flow to match high-performing LinkedIn content"
        ]
        
        approach = approaches[(variation_num - 1) % len(approaches)]
        
        rewrite_prompt = f"""
{GARY_LIN_PERSONA}

{CONTENT_GENERATION_INSTRUCTIONS}

**TASK: POST STYLE IMPROVEMENT**

You need to rewrite and improve an existing LinkedIn post to match the style and engagement level of high-performing posts.

**ORIGINAL POST TO IMPROVE:**
{original_post}

**HIGH-PERFORMING REFERENCE POSTS FOR STYLE:**
{style_context}

**IMPROVEMENT APPROACH:**
{approach}

**INSTRUCTIONS:**
1. Analyze the style elements that make the reference posts engaging (hooks, structure, tone, etc.)
2. Rewrite the original post incorporating these successful elements
3. Maintain the original message and key points
4. Make it more viral and engaging
5. Use Gary Lin's authentic voice and perspective
6. Keep it LinkedIn-appropriate and professional yet engaging

**REWRITTEN POST:**
"""

        try:
            chat_completion = self.content_generator.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": rewrite_prompt
                    }
                ],
                model=self.content_generator.model,
                temperature=0.8,  # Higher creativity for rewriting
                max_tokens=500,
                top_p=1,
                stream=False
            )
            
            rewritten_post = chat_completion.choices[0].message.content.strip()
            
            # Clean up the response
            if rewritten_post.startswith("**REWRITTEN POST:**"):
                rewritten_post = rewritten_post.replace("**REWRITTEN POST:**", "").strip()
            
            return rewritten_post
            
        except Exception as e:
            print(f"❌ Error generating rewrite: {str(e)}")
            return original_post 