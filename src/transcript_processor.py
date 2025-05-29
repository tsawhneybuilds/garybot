import re
import spacy
from typing import List, Optional
from src.models import TranscriptSegment

class TranscriptProcessor:
    """
    Handles transcription ingestion, cleaning, and segmentation.
    """
    
    def __init__(self):
        """Initialize the processor with spaCy model for sentence segmentation."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback to basic processing if spaCy model not available
            self.nlp = None
            print("Warning: spaCy model 'en_core_web_sm' not found. Using basic text processing.")
    
    def clean_text(self, text: str) -> str:
        """
        Clean the transcript text by removing timestamps, excessive filler words, etc.
        
        Args:
            text: Raw transcript text
            
        Returns:
            Cleaned text
        """
        # Remove timestamps like [00:00:00] or (00:00:00) or 00:00:00
        text = re.sub(r'\[?\(?\d{1,2}:\d{2}:\d{2}\]?\)?', '', text)
        
        # Remove speaker labels like "Speaker 1:" or "GARY:"
        text = re.sub(r'^[A-Z\s]+:', '', text, flags=re.MULTILINE)
        
        # Remove excessive filler words (configurable)
        filler_words = ['um', 'uh', 'like', 'you know', 'so', 'well']
        for filler in filler_words:
            # Remove when they appear as standalone words with word boundaries
            pattern = r'\b' + re.escape(filler) + r'\b'
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Clean up multiple spaces and newlines
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def segment_transcript(self, text: str, min_segment_length: int = 100, 
                          max_segment_length: int = 500, overlap: int = 50) -> List[str]:
        """
        Segment the transcript into meaningful chunks.
        
        Args:
            text: Cleaned transcript text
            min_segment_length: Minimum length for a segment (in characters)
            max_segment_length: Maximum length for a segment (in characters)
            overlap: Number of characters to overlap between segments
            
        Returns:
            List of text segments
        """
        if self.nlp:
            return self._segment_with_spacy(text, min_segment_length, max_segment_length, overlap)
        else:
            return self._segment_basic(text, min_segment_length, max_segment_length, overlap)
    
    def _segment_with_spacy(self, text: str, min_length: int, max_length: int, overlap: int) -> List[str]:
        """Segment using spaCy for better sentence boundary detection."""
        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        
        segments = []
        current_segment = ""
        
        i = 0
        while i < len(sentences):
            # Add sentences until we reach max_length or run out
            while i < len(sentences) and len(current_segment + sentences[i]) <= max_length:
                if current_segment:
                    current_segment += " "
                current_segment += sentences[i]
                i += 1
            
            # If we have a segment that meets minimum length, add it
            if len(current_segment) >= min_length:
                segments.append(current_segment.strip())
                
                # Handle overlap by backing up
                if overlap > 0 and i < len(sentences):
                    overlap_text = current_segment[-overlap:] if len(current_segment) > overlap else current_segment
                    current_segment = overlap_text
                else:
                    current_segment = ""
            else:
                # If segment is too short, keep building
                if i < len(sentences):
                    if current_segment:
                        current_segment += " "
                    current_segment += sentences[i]
                    i += 1
                else:
                    # Last segment, add it even if short
                    if current_segment.strip():
                        segments.append(current_segment.strip())
                    break
        
        # Add any remaining content
        if current_segment.strip() and current_segment.strip() not in segments:
            segments.append(current_segment.strip())
        
        return segments
    
    def _segment_basic(self, text: str, min_length: int, max_length: int, overlap: int) -> List[str]:
        """Basic segmentation using sentence splitting on periods."""
        # Split on sentence endings
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        segments = []
        current_segment = ""
        
        for i, sentence in enumerate(sentences):
            # Add sentence if it fits
            if len(current_segment + sentence) <= max_length:
                if current_segment:
                    current_segment += ". "
                current_segment += sentence
            else:
                # Current segment is full, save it if it meets min length
                if len(current_segment) >= min_length:
                    segments.append(current_segment.strip())
                    
                    # Start new segment with overlap
                    if overlap > 0:
                        overlap_text = current_segment[-overlap:] if len(current_segment) > overlap else current_segment
                        current_segment = overlap_text + ". " + sentence
                    else:
                        current_segment = sentence
                else:
                    # Segment too short, just add the sentence anyway
                    if current_segment:
                        current_segment += ". "
                    current_segment += sentence
        
        # Add the last segment
        if current_segment.strip():
            segments.append(current_segment.strip())
        
        return segments
    
    def process_transcript(self, file_content: str, transcript_id: Optional[str] = None) -> List[TranscriptSegment]:
        """
        Full processing pipeline: clean and segment transcript.
        
        Args:
            file_content: Raw transcript content
            transcript_id: Optional ID to associate with segments
            
        Returns:
            List of TranscriptSegment objects
        """
        # Clean the text
        cleaned_text = self.clean_text(file_content)
        
        # Segment the text
        segments = self.segment_transcript(cleaned_text)
        
        # Convert to TranscriptSegment objects
        transcript_segments = []
        for segment_text in segments:
            if len(segment_text.strip()) > 50:  # Only include meaningful segments
                transcript_segments.append(
                    TranscriptSegment(
                        text=segment_text.strip(),
                        source_transcript_id=transcript_id
                    )
                )
        
        return transcript_segments 