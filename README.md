# 🚀 Gary Bot - AI-Powered LinkedIn Post Generator

An intelligent LinkedIn post generator designed specifically for Gary Lin (Co-Founder of Explo) that uses RAG (Retrieval Augmented Generation) to create viral content based on high-performing posts.

## ✨ Features

- **🎯 Viral Snippet Detection**: Analyzes transcripts to identify the most engaging content
- **🤖 AI-Powered Generation**: Creates multiple post variations using Groq's Llama 3 models
- **📚 RAG Learning System**: Learns from gold standard posts to improve future generations
- **✨ Post Rewriter**: Improve existing posts using style from high-performing content
- **📊 Performance Analytics**: Track engagement and optimize content strategy
- **💾 Backup System**: Comprehensive data protection and recovery
- **🎨 Beautiful UI**: Modern Streamlit interface with intuitive navigation

## 🏗️ Architecture

- **LLM**: Groq API (Llama 3 70B/8B models)
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Database**: ChromaDB for RAG storage
- **Frontend**: Streamlit web application
- **NLP**: spaCy for text processing

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/garybot.git
cd garybot
```

### 2. Set Up Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Configure Environment Variables
Create a `.env` file in the project root:
```bash
GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL=llama3-70b-8192
EMBEDDING_MODEL=all-MiniLM-L6-v2
RAG_RETRIEVAL_COUNT=3
DEFAULT_TEMPERATURE=0.7
MIN_SIMILARITY_THRESHOLD=0.3
```

**Get your Groq API key:**
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy it to your `.env` file

### 4. Run the Application
```bash
streamlit run app.py
```

## 🌐 Deployment on Google Cloud

### Google App Engine (PaaS) Deployment

Gary Bot is configured for Google App Engine, Google's fully managed Platform-as-a-Service.

#### Prerequisites
- Google Cloud account with billing enabled
- Google Cloud CLI installed (`gcloud`)

#### Step-by-Step Deployment

1. **Install Google Cloud CLI** (if not already installed):
   ```bash
   # macOS
   brew install google-cloud-sdk
   
   # Or download from: https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticate with Google Cloud**:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Update Environment Variables in `app.yaml`**:
   Edit the `app.yaml` file and replace with your actual values:
   ```yaml
   env_variables:
     GROQ_API_KEY: "your_actual_groq_api_key"
     LLM_MODEL: "llama3-70b-8192"
     EMBEDDING_MODEL: "all-MiniLM-L6-v2"
     RAG_RETRIEVAL_COUNT: "3"
     DEFAULT_TEMPERATURE: "0.7"
     MIN_SIMILARITY_THRESHOLD: "0.3"
   ```

4. **Deploy to App Engine**:
   ```bash
   gcloud app deploy
   ```

5. **Open Your App**:
   ```bash
   gcloud app browse
   ```

#### Configuration Notes
- **Runtime**: Python 3.11
- **Auto-scaling**: 0-10 instances based on traffic
- **Resources**: 2 CPU cores, 4GB RAM per instance
- **Cost**: Pay only for what you use

### Security Notes
- ✅ Environment variables are securely stored in Google Cloud
- ✅ API keys are never exposed in the codebase
- ✅ Database files are excluded from version control
- ✅ Backup files are gitignored for security

## 📖 Usage Guide

### Adding Gold Standard Posts
1. Navigate to "⚙️ Manage RAG"
2. Use the "Add Gold Standard Post" form
3. Enable auto-enhancement for automatic keyword/content type extraction
4. Posts are automatically categorized into Gary's 5 content types

### Generating New Posts
1. Go to "📝 Generate Posts"
2. Upload a transcript (.txt file)
3. Review viral snippet candidates
4. Generate multiple variations
5. Approve and save the best posts

### Rewriting Existing Posts
1. Visit "✨ Post Rewriter"
2. Paste your existing post
3. Choose style reference options
4. Generate improved versions
5. Save the best rewritten posts

### Managing Content
- **Post History**: View all posts with filtering and sorting
- **Bulk Operations**: Select and delete multiple posts
- **Engagement Tracking**: Update likes/comments for performance analysis
- **Backup System**: Create and restore data backups

## 🎯 Gary's Content Types

The system automatically categorizes content into Gary Lin's 5 specific types:

1. **Founder's Personal Story & Journey**: Experiences from Palantir, Columbia, growing up
2. **Internal Company Management & Culture**: Behind-the-scenes at Explo, team news, challenges  
3. **Streamlining Data Delivery**: Overcoming data sharing challenges (Explo's core domain)
4. **Analytics Trends & Insights**: Industry knowledge and perspectives
5. **Building a SaaS/AI Company**: Fundraising, team building, PMF, selling to enterprises

## 🔧 Configuration

### Available Models
- **llama3-70b-8192**: High quality, slower (recommended)
- **llama3-8b-8192**: Faster, good quality
- **mixtral-8x7b-32768**: Long context, versatile
- **gemma-7b-it**: Instruction tuned

### Key Settings
- `RAG_RETRIEVAL_COUNT`: Number of similar posts to retrieve (default: 3)
- `DEFAULT_TEMPERATURE`: Creativity level 0-1 (default: 0.7)
- `MIN_SIMILARITY_THRESHOLD`: Minimum similarity for viral detection (default: 0.3)

## 💾 Data Management

### Backup System
- **Manual Backups**: Create on-demand backups
- **Auto Backups**: Scheduled backups with cleanup
- **JSON Export**: Human-readable data exports
- **Restore**: Recover from any backup point

### Data Persistence
- ChromaDB automatically persists in `./chroma_db/`
- Backups stored in `./backups/`
- All sensitive data excluded from git

## 🛠️ Development

### Project Structure
```
garybot/
├── src/
│   ├── gary_bot.py          # Main bot orchestrator
│   ├── content_generator.py # LLM-powered content generation
│   ├── viral_snippet_detector.py # RAG and similarity detection
│   ├── models.py           # Data models
│   ├── config.py           # Configuration management
│   └── backup_system.py    # Data backup and recovery
├── app.py                  # Streamlit web interface
├── add_posts_to_rag.py     # CLI interface
├── backup_manager.py       # Standalone backup tool
└── requirements.txt        # Python dependencies
```

### CLI Commands
```bash
# Add sample posts
python add_posts_to_rag.py sample

# Clear default posts
python add_posts_to_rag.py clear

# Interactive post deletion
python add_posts_to_rag.py delete

# List all posts
python add_posts_to_rag.py list

# Rewrite existing posts
python add_posts_to_rag.py rewrite

# Backup management
python backup_manager.py create
python backup_manager.py list
python backup_manager.py restore
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues or questions:
1. Check the GitHub Issues page
2. Review the configuration guide
3. Ensure all environment variables are set correctly
4. Verify your Groq API key is valid

---

**Built with ❤️ for viral LinkedIn content generation**