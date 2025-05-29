import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Optional, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from src.models import TranscriptSegment, GoldStandardPost, ViralSnippetCandidate

class ViralSnippetDetector:
    """
    Identifies potentially viral snippets by comparing transcript segments 
    to gold standard viral posts using semantic similarity.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the detector with a sentence transformer model.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.gold_standard_posts: List[GoldStandardPost] = []
        self.gold_standard_embeddings: Optional[np.ndarray] = None
    
    def add_gold_standard_posts(self, posts: List[GoldStandardPost]) -> None:
        """
        Add gold standard posts and compute their embeddings.
        
        Args:
            posts: List of gold standard posts to learn from
        """
        self.gold_standard_posts.extend(posts)
        self._compute_gold_standard_embeddings()
    
    def load_gold_standard_from_texts(self, post_texts: List[str], keywords_list: Optional[List[List[str]]] = None) -> None:
        """
        Create gold standard posts from text and compute embeddings.
        
        Args:
            post_texts: List of successful post texts
            keywords_list: Optional list of keywords for each post
        """
        if keywords_list is None:
            keywords_list = [[] for _ in post_texts]
        
        posts = []
        for i, text in enumerate(post_texts):
            keywords = keywords_list[i] if i < len(keywords_list) else []
            post = GoldStandardPost(
                text=text,
                keywords=keywords
            )
            posts.append(post)
        
        self.add_gold_standard_posts(posts)
    
    def _compute_gold_standard_embeddings(self) -> None:
        """Compute embeddings for all gold standard posts."""
        if not self.gold_standard_posts:
            return
        
        texts = [post.text for post in self.gold_standard_posts]
        embeddings = self.model.encode(texts)
        
        # Store embeddings in the posts
        for i, post in enumerate(self.gold_standard_posts):
            post.embedding = embeddings[i].tolist()
        
        self.gold_standard_embeddings = embeddings
    
    def identify_viral_snippets(self, segments: List[TranscriptSegment], 
                               top_k: int = 5, min_similarity: float = 0.3) -> List[ViralSnippetCandidate]:
        """
        Identify the most promising viral snippet candidates from transcript segments.
        
        Args:
            segments: List of transcript segments to analyze
            top_k: Number of top candidates to return
            min_similarity: Minimum similarity score to consider
            
        Returns:
            List of viral snippet candidates ranked by similarity score
        """
        if not self.gold_standard_posts or self.gold_standard_embeddings is None:
            raise ValueError("No gold standard posts loaded. Call add_gold_standard_posts() first.")
        
        # Get embeddings for all segments
        segment_texts = [segment.text for segment in segments]
        segment_embeddings = self.model.encode(segment_texts)
        
        # Compute similarity scores
        similarity_matrix = cosine_similarity(segment_embeddings, self.gold_standard_embeddings)
        
        # Find best matches for each segment
        candidates = []
        for i, segment in enumerate(segments):
            # Get the highest similarity score for this segment
            max_similarity_idx = np.argmax(similarity_matrix[i])
            max_similarity_score = similarity_matrix[i][max_similarity_idx]
            
            # Only consider if above minimum threshold
            if max_similarity_score >= min_similarity:
                most_similar_post = self.gold_standard_posts[max_similarity_idx]
                
                candidate = ViralSnippetCandidate(
                    text=segment.text,
                    similarity_score=float(max_similarity_score),
                    most_similar_post_id=most_similar_post.id,
                    most_similar_post_text=most_similar_post.text,
                    rank=0  # Will be set after sorting
                )
                candidates.append(candidate)
        
        # Sort by similarity score (descending) and assign ranks
        candidates.sort(key=lambda x: x.similarity_score, reverse=True)
        for i, candidate in enumerate(candidates):
            candidate.rank = i + 1
        
        # Return top_k candidates
        return candidates[:top_k]
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        embedding = self.model.encode([text])[0]
        return embedding.tolist()
    
    def find_similar_posts(self, text: str, top_k: int = 3) -> List[Tuple[GoldStandardPost, float]]:
        """
        Find the most similar gold standard posts to a given text.
        
        Args:
            text: Text to find similar posts for
            top_k: Number of similar posts to return
            
        Returns:
            List of tuples (post, similarity_score) sorted by similarity
        """
        if not self.gold_standard_posts or self.gold_standard_embeddings is None:
            return []
        
        # Get embedding for the input text
        text_embedding = self.model.encode([text])
        
        # Compute similarities
        similarities = cosine_similarity(text_embedding, self.gold_standard_embeddings)[0]
        
        # Get top_k most similar
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            post = self.gold_standard_posts[idx]
            similarity = similarities[idx]
            results.append((post, float(similarity)))
        
        return results

# Default gold standard posts to get started
DEFAULT_GOLD_STANDARD_POSTS = [
    "Here's the thing nobody tells you about raising Series A: The deck is just 10% of the battle. The other 90%? It's your ability to tell a story that makes investors lean forward in their seats. I remember our first pitch. Perfect slides. Terrible storytelling. We got nos across the board. Round two? Same data, different narrative. We raised $12M. The difference? We stopped talking about features and started talking about the future we were building. What story is your startup telling? #startups #fundraising #storytelling",
    
    "Unpopular opinion: Your first 10 employees matter more than your first 10 customers. Here's why: Customers can be replaced. Great people? They're irreplaceable. They become the DNA of everything you build after. When we were 8 people at Explo, I spent 60% of my time on hiring. Sounds crazy? Maybe. But those early hires became our leadership team. They shaped our culture, our product, our entire trajectory. Your first employees don't just work for your company - they ARE your company. Hire like your future depends on it. Because it does. #hiring #startups #culture",
    
    "3 years ago, we almost shut down Explo. Today, we're powering analytics for 500+ companies. What changed? We stopped building what we thought users wanted and started building what they actually needed. The pivot wasn't glamorous. We threw away 18 months of work. Cut our team in half. Started over. But sometimes the best path forward is admitting you're on the wrong path. If your startup feels stuck, ask yourself: Are you solving a real problem or just building cool technology? The answer might surprise you. #pivoting #startups #product",
    
    "The best advice I ever got came from a customer who hated our product. 'Gary, this isn't solving my problem. It's creating new ones.' Ouch. But he was right. Instead of defending our work, we listened. Really listened. That conversation led to our biggest feature overhaul and eventually our product-market fit. Your harshest critics often become your biggest advocates. But only if you're brave enough to hear them out. When was the last time you asked a customer what you're doing wrong? #feedback #productmarket #customers"
] 