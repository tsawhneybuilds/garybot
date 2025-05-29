# 🚀 Gary Bot - AI-Powered LinkedIn Post Generator

An AI agent that analyzes long transcriptions, identifies potentially viral content snippets, and generates engaging LinkedIn posts in Gary Lin's distinct voice and style. The system incorporates a Retrieval Augmented Generation (RAG) system that learns from past successful posts and user-provided engagement data.

## 🎯 Overview

Gary Bot is designed specifically for **Gary Lin, Co-Founder of Explo**, to transform podcast transcripts, meeting notes, and other long-form content into viral LinkedIn posts that maintain his authentic voice and maximize engagement.

### Key Features

- 📝 **Intelligent Transcript Processing**: Cleans and segments transcripts for optimal analysis
- 🎯 **Viral Snippet Detection**: Uses semantic similarity to identify high-potential content pieces  
- 🤖 **AI-Powered Content Generation**: Leverages Groq's LLMs to create posts in Gary's voice
- 🧠 **RAG System**: Learns from successful posts to improve future generations
- 📊 **Viral Potential Analysis**: Scores and analyzes posts for engagement potential
- 💾 **Post Management**: Track engagement metrics and build knowledge base
- 🖥️ **Beautiful Web Interface**: Streamlit-based UI for easy interaction

## 🛠️ Technology Stack

- **Backend**: Python 3.9+
- **LLM**: Groq API (Llama 3, Mixtral models)
- **Embeddings**: Sentence Transformers
- **Vector Database**: ChromaDB
- **Web Framework**: Streamlit
- **NLP**: spaCy, NLTK
- **Data Models**: Pydantic

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd garybot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Get a Groq API Key

1. Visit [console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Create a new API key
4. Copy the key (starts with `gsk_`)

### 3. Configure Environment

Create a `.env` file in the project root:

```bash
GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL=llama3-70b-8192
EMBEDDING_MODEL=all-MiniLM-L6-v2
RAG_RETRIEVAL_COUNT=3
DEFAULT_TEMPERATURE=0.7
MIN_SIMILARITY_THRESHOLD=0.3
```

### 4. Install spaCy Model (Optional but Recommended)

```bash
python -m spacy download en_core_web_sm
```

### 5. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### 1. Generate Posts

1. Navigate to **"📝 Generate Posts"**
2. Upload a `.txt` transcript file
3. Configure generation options:
   - Number of viral candidates to analyze
   - Number of post variations to generate
   - Enable viral analysis
4. Click **"🚀 Process Transcript & Generate Posts"**
5. Review viral snippet candidates
6. Generate and refine posts
7. Approve and save successful posts

### 2. Manage Post History

1. Go to **"📊 Post History"**
2. View all generated and approved posts
3. Update engagement metrics (likes, comments)
4. Filter and sort posts by various criteria
5. Track performance over time

### 3. Manage RAG System

1. Visit **"⚙️ Manage RAG"**
2. Add gold standard posts from Gary's successful content
3. Include engagement metrics for better learning
4. View RAG system statistics

### 4. Monitor System Stats

1. Check **"📈 System Stats"** for analytics
2. View performance metrics
3. Monitor system health

## 🧠 How It Works

### 1. Transcript Processing
- Cleans timestamps, filler words, speaker labels
- Segments into meaningful chunks using spaCy
- Maintains context with overlapping segments

### 2. Viral Snippet Detection
- Compares transcript segments to gold standard posts
- Uses semantic similarity (cosine similarity) with embeddings
- Ranks segments by viral potential

### 3. Content Generation
- Retrieves similar posts from RAG system for context
- Uses Gary Lin's detailed persona prompt
- Generates multiple variations with different temperatures
- Maintains authentic voice and style

### 4. RAG System Learning
- Stores approved posts with metadata
- Tracks engagement metrics over time
- Improves future generations through similarity matching
- Builds comprehensive knowledge base

## 🎨 Gary Lin's Voice & Style

The AI is trained to capture Gary's distinctive voice:

**Voice & Tone:**
- Bold, humorous, community-minded
- Confident but not arrogant
- Smart but not dry
- People-first, empathetic, encouraging
- Genuine, witty, vulnerable, raw, relatable
- A bit provocative (without being negative)
- Punchy, honest, warm, clear point of view

**Content Types:**
- Founder philosophies
- Tough love advice
- Motivating rally cries
- Transparent reflections
- Funny startup observations
- Product milestones
- Team spotlights

## 🔧 Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | Required | Your Groq API key |
| `LLM_MODEL` | `llama3-70b-8192` | Groq model to use |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `RAG_RETRIEVAL_COUNT` | `3` | Number of similar posts to retrieve |
| `DEFAULT_TEMPERATURE` | `0.7` | LLM generation temperature |
| `MIN_SIMILARITY_THRESHOLD` | `0.3` | Minimum similarity for viral candidates |

### Available Models

**Groq LLM Models:**
- `llama3-70b-8192` - High quality, slower
- `llama3-8b-8192` - Faster, good quality  
- `mixtral-8x7b-32768` - Long context, versatile
- `gemma-7b-it` - Instruction tuned

**Embedding Models:**
- `all-MiniLM-L6-v2` - Fast and lightweight (384 dimensions)
- `all-mpnet-base-v2` - Higher quality (768 dimensions)
- `all-MiniLM-L12-v2` - Balanced (384 dimensions)

## 📁 Project Structure

```
garybot/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── env_example.txt       # Environment variables example
├── README.md             # This file
├── src/                  # Core modules
│   ├── __init__.py
│   ├── gary_bot.py       # Main orchestrator class
│   ├── config.py         # Configuration management
│   ├── models.py         # Pydantic data models
│   ├── gary_lin_persona.py # Gary Lin's voice prompt
│   ├── transcript_processor.py # Text cleaning & segmentation
│   ├── viral_snippet_detector.py # Viral content detection
│   ├── content_generator.py # LLM-based post generation
│   └── rag_system.py     # Vector database & retrieval
└── chroma_db/            # ChromaDB storage (created automatically)
```

## 🔍 API Reference

### GaryBot Class

```python
from src import GaryBot

# Initialize
gary_bot = GaryBot()

# Process transcript
segments = gary_bot.process_transcript(transcript_content)

# Find viral snippets  
candidates = gary_bot.identify_viral_snippets(segments)

# Generate post
draft = gary_bot.generate_post_from_snippet(snippet_text)

# Approve and save
post_id = gary_bot.approve_post(draft, keywords=["startups"], content_type="Founder Philosophy")

# Update engagement
gary_bot.update_post_engagement(post_id, likes=100, comments=20)
```

## 🤝 Contributing

This is a custom solution for Gary Lin. For improvements or bug fixes:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 Example Workflow

1. **Upload Transcript**: Upload a podcast transcript or meeting notes
2. **Review Candidates**: System identifies top 5 viral snippet candidates
3. **Generate Variations**: Create 3 variations of LinkedIn posts for top candidate
4. **Analyze Potential**: AI scores each post for viral potential (1-10)
5. **Edit & Refine**: Make manual edits if needed
6. **Approve & Save**: Add to RAG system with keywords and content type
7. **Track Performance**: Update with real engagement metrics later
8. **Learn & Improve**: System learns from successful posts for future generations

## 🛡️ Privacy & Security

- All data is stored locally in ChromaDB
- Transcripts are processed locally
- Only text is sent to Groq API for generation
- No personal data is permanently stored in external services
- API keys are handled securely through environment variables

## 📞 Support

For issues, questions, or feature requests related to this Gary Lin-specific implementation, please create an issue in the repository.

---

**Built for Gary Lin, Co-Founder of Explo** 🚀

*"Your first 10 employees matter more than your first 10 customers. Here's why: Customers can be replaced. Great people? They're irreplaceable."* - Gary Lin 