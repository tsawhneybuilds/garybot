from groq import Groq
from typing import List, Optional
import re
from src.models import GeneratedPostDraft, RAGPost
from src.gary_lin_persona import get_gary_lin_prompt
from src.rag_system import RAGSystem

class ContentGenerator:
    """
    Generates LinkedIn posts using Groq LLM in Gary Lin's voice.
    """
    
    def __init__(self, api_key: str, model: str = "llama3-70b-8192"):
        """
        Initialize the content generator with Groq API.
        
        Args:
            api_key: Groq API key
            model: LLM model to use
        """
        self.client = Groq(api_key=api_key)
        self.model = model
    
    def generate_post(self, snippet: str, rag_context: str = "", 
                     temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        Generate a LinkedIn post based on a transcript snippet.
        
        Args:
            snippet: Transcript snippet to base the post on
            rag_context: Context from similar posts in RAG system
            temperature: Sampling temperature for generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated LinkedIn post text
        """
        # Construct the prompt
        prompt = get_gary_lin_prompt(snippet, rag_context)
        
        try:
            # Call Groq API
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                stream=False
            )
            
            # Extract the generated content
            generated_text = chat_completion.choices[0].message.content.strip()
            
            # Clean up the response
            cleaned_text = self._clean_generated_text(generated_text)
            
            return cleaned_text
            
        except Exception as e:
            raise Exception(f"Error generating content with Groq: {str(e)}")
    
    def generate_multiple_posts(self, snippet: str, rag_context: str = "", 
                               num_variations: int = 3, temperature: float = 0.8) -> List[str]:
        """
        Generate multiple variations of a LinkedIn post.
        
        Args:
            snippet: Transcript snippet to base the post on
            rag_context: Context from similar posts in RAG system
            num_variations: Number of variations to generate
            temperature: Sampling temperature for generation
            
        Returns:
            List of generated LinkedIn post variations
        """
        posts = []
        
        for i in range(num_variations):
            try:
                # Adjust temperature slightly for each variation
                var_temperature = temperature + (i * 0.1)
                post = self.generate_post(snippet, rag_context, temperature=var_temperature)
                posts.append(post)
            except Exception as e:
                print(f"Error generating variation {i+1}: {str(e)}")
                continue
        
        return posts
    
    def generate_post_with_rag(self, snippet: str, rag_system: RAGSystem, 
                              num_rag_examples: int = 3) -> GeneratedPostDraft:
        """
        Generate a post using RAG system for context.
        
        Args:
            snippet: Transcript snippet to base the post on
            rag_system: RAG system instance for retrieving context
            num_rag_examples: Number of similar posts to retrieve for context
            
        Returns:
            GeneratedPostDraft object with the generated post and metadata
        """
        # Retrieve similar posts from RAG
        similar_posts = rag_system.retrieve_similar_posts(snippet, top_k=num_rag_examples)
        
        # Format RAG context
        rag_context = rag_system.format_rag_context(similar_posts)
        
        # Generate the post
        generated_text = self.generate_post(snippet, rag_context)
        
        # Extract hashtags
        hashtags = self._extract_hashtags(generated_text)
        
        # Create the draft object
        draft = GeneratedPostDraft(
            original_snippet=snippet,
            draft_text=generated_text,
            suggested_hashtags=hashtags,
            rag_context_ids=[post.id for post in similar_posts]
        )
        
        return draft
    
    def _clean_generated_text(self, text: str) -> str:
        """
        Clean up the generated text to ensure it's properly formatted.
        
        Args:
            text: Raw generated text
            
        Returns:
            Cleaned text
        """
        # Remove any leading/trailing whitespace
        text = text.strip()
        
        # Remove any "LinkedIn post:" or similar prefixes that might be generated
        prefixes_to_remove = [
            "LinkedIn post:",
            "LinkedIn Post:",
            "Here's the LinkedIn post:",
            "Here's the post:",
            "Post:",
            "Draft:"
        ]
        
        for prefix in prefixes_to_remove:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        
        # Ensure proper line breaks (not too many, not too few)
        text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 consecutive newlines
        
        # Clean up excessive spaces
        text = re.sub(r' {2,}', ' ', text)
        
        return text
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """
        Extract hashtags from generated text.
        
        Args:
            text: Text to extract hashtags from
            
        Returns:
            List of hashtags (without the # symbol)
        """
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, text)
        return hashtags
    
    def regenerate_with_feedback(self, original_snippet: str, previous_draft: str, 
                                feedback: str, rag_context: str = "") -> str:
        """
        Regenerate a post based on user feedback.
        
        Args:
            original_snippet: Original transcript snippet
            previous_draft: Previously generated draft
            feedback: User feedback on what to improve
            rag_context: RAG context for inspiration
            
        Returns:
            Revised LinkedIn post
        """
        # Create a feedback-aware prompt
        newline = '\n'
        rag_section = f'**For inspiration, here are some similar successful posts:**{newline}{rag_context}{newline}' if rag_context else ''
        
        feedback_prompt = f"""
        Based on the following transcript snippet, I previously generated this LinkedIn post:

        **Previous Draft:**
        {previous_draft}

        **User Feedback:**
        {feedback}

        Please revise the post based on this feedback while maintaining Gary Lin's authentic voice and style.

        **Original Transcript Snippet:**
        "{original_snippet}"
        
        {rag_section}
        
        Write an improved LinkedIn post that addresses the feedback:
        """
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": feedback_prompt
                    }
                ],
                model=self.model,
                temperature=0.7,
                max_tokens=1000,
                top_p=1,
                stream=False
            )
            
            generated_text = chat_completion.choices[0].message.content.strip()
            return self._clean_generated_text(generated_text)
            
        except Exception as e:
            raise Exception(f"Error regenerating content with feedback: {str(e)}")
    
    def analyze_post_potential(self, post_text: str) -> dict:
        """
        Analyze the viral potential of a post using the LLM.
        
        Args:
            post_text: LinkedIn post text to analyze
            
        Returns:
            Dictionary with analysis results
        """
        analysis_prompt = f"""
        As an expert in viral LinkedIn content, analyze this post for its viral potential. Consider factors like:
        - Hook strength
        - Storytelling elements
        - Emotional resonance
        - Actionability
        - Shareability
        - Gary Lin's authentic voice

        **Post to analyze:**
        {post_text}

        Provide:
        1. Viral Potential Score (1-10)
        2. Strengths (bullet points)
        3. Areas for improvement (bullet points)
        4. Predicted engagement level (Low/Medium/High)

        Format your response as:
        SCORE: [number]
        STRENGTHS:
        - [point 1]
        - [point 2]
        IMPROVEMENTS:
        - [point 1]  
        - [point 2]
        ENGAGEMENT: [level]
        """
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                model=self.model,
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=500,
                top_p=1,
                stream=False
            )
            
            analysis_text = chat_completion.choices[0].message.content.strip()
            
            # Parse the analysis
            return self._parse_analysis(analysis_text)
            
        except Exception as e:
            print(f"Error analyzing post potential: {str(e)}")
            return {
                "score": 5,
                "strengths": ["Unable to analyze"],
                "improvements": ["Analysis failed"],
                "engagement": "Unknown"
            }
    
    def _parse_analysis(self, analysis_text: str) -> dict:
        """
        Parse the LLM analysis response into structured data.
        
        Args:
            analysis_text: Raw analysis text from LLM
            
        Returns:
            Parsed analysis dictionary
        """
        try:
            # Extract score
            score_match = re.search(r'SCORE:\s*(\d+)', analysis_text)
            score = int(score_match.group(1)) if score_match else 5
            
            # Extract strengths
            strengths_section = re.search(r'STRENGTHS:(.*?)(?=IMPROVEMENTS:|$)', analysis_text, re.DOTALL)
            strengths = []
            if strengths_section:
                strengths_text = strengths_section.group(1)
                strengths = [line.strip().lstrip('- ') for line in strengths_text.split('\n') if line.strip().startswith('-')]
            
            # Extract improvements
            improvements_section = re.search(r'IMPROVEMENTS:(.*?)(?=ENGAGEMENT:|$)', analysis_text, re.DOTALL)
            improvements = []
            if improvements_section:
                improvements_text = improvements_section.group(1)
                improvements = [line.strip().lstrip('- ') for line in improvements_text.split('\n') if line.strip().startswith('-')]
            
            # Extract engagement
            engagement_match = re.search(r'ENGAGEMENT:\s*(\w+)', analysis_text)
            engagement = engagement_match.group(1) if engagement_match else "Medium"
            
            return {
                "score": score,
                "strengths": strengths,
                "improvements": improvements,
                "engagement": engagement
            }
            
        except Exception as e:
            print(f"Error parsing analysis: {str(e)}")
            return {
                "score": 5,
                "strengths": ["Analysis parsing failed"],
                "improvements": ["Could not parse feedback"],
                "engagement": "Unknown"
            } 