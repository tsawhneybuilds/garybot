# 🚀 Gary Bot - AI-Powered LinkedIn Post Generator

An intelligent LinkedIn content generator designed specifically for Gary Lin (Co-Founder of Explo) that uses RAG (Retrieval Augmented Generation) to create viral posts based on transcripts and high-performing content.

## 🎯 What Gary Bot Does

- **📝 Transcript Analysis**: Upload transcripts and automatically identify viral snippet candidates
- **🤖 AI Post Generation**: Generate multiple LinkedIn post variations using Gary's authentic voice
- **📊 RAG Learning System**: Learn from high-performing posts to improve future generations
- **✨ Post Rewriter**: Improve existing posts using style transfer from top performers
- **📈 Performance Analytics**: Track engagement and optimize content strategy
- **💾 Data Persistence**: Automatic backups ensure your content library is never lost

## 🏠 **Local Installation (Recommended)**

Gary Bot is designed as a **local application** for security and privacy. Your API keys and content data stay on your machine.

### Prerequisites
- Python 3.9-3.12 (avoid 3.13+ due to dependency issues)
- Git

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/tsawhneybuilds/garybot.git
   cd garybot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Groq API key
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

### Getting a Groq API Key
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Go to API Keys section
4. Create a new API key
5. Add it to your `.env` file

## 🌐 **Demo Deployment**

A demo version is available online that shows the interface without requiring API keys:

- **Demo URL**: [Your Netlify URL here]
- **Features**: Interface preview, sample data, no AI functionality
- **Purpose**: Showcase the tool's capabilities

## 🔧 **Usage**

### Command Line Interface
```bash
# Add sample posts with auto-enhancement
python add_posts_to_rag.py sample

# Interactive post management
python add_posts_to_rag.py list
python add_posts_to_rag.py delete

# Post rewriting
python add_posts_to_rag.py rewrite

# Backup management
python backup_manager.py create
python backup_manager.py list
```

### Web Interface
1. **Generate Posts**: Upload transcripts → Get viral candidates → Generate posts
2. **Post Rewriter**: Improve existing posts using high-performer styles
3. **Manage RAG**: Add gold standard posts, bulk operations, system cleanup
4. **Post History**: View, filter, and manage all generated content
5. **System Stats**: Analytics and performance metrics
6. **Settings**: Configuration and setup instructions

## 📊 **Gary's Content Types**

Gary Bot specializes in 5 specific content types:

1. **Founder's Personal Story & Journey**: Experiences from Palantir, Columbia, growing up
2. **Internal Company Management & Culture**: Behind-the-scenes at Explo, team news, challenges  
3. **Streamlining Data Delivery**: Overcoming data sharing challenges (Explo's core domain)
4. **Analytics Trends & Insights**: Industry knowledge and perspectives
5. **Building a SaaS/AI Company**: Fundraising, team building, PMF, selling to enterprises

## 💾 **Data Persistence & Backups**

Your RAG posts are automatically stored permanently in ChromaDB. Additional backup features:

- **Automatic Backups**: Create scheduled backups of your entire system
- **JSON Exports**: Human-readable exports for easy viewing/editing
- **Restore Functionality**: Restore from any backup point
- **Cloud Sync**: Backup to your preferred cloud storage

```bash
# Create backup
python backup_manager.py create

# Auto backup with cleanup (keeps 10 most recent)
python backup_manager.py auto

# List all backups
python backup_manager.py list

# Restore from backup
python backup_manager.py restore path/to/backup.zip --overwrite
```

## 🔒 **Security & Privacy**

- **Local Data**: All content and API keys stay on your machine
- **No Cloud Dependencies**: Works entirely offline after initial setup
- **Encrypted Storage**: ChromaDB provides secure local storage
- **API Key Protection**: Environment variables keep credentials safe

## 🚀 **Advanced Features**

### Auto-Enhancement
- **Keyword Extraction**: AI-powered analysis extracts 3-6 relevant business keywords
- **Content Classification**: Automatically categorizes posts into Gary's content types
- **Engagement Prediction**: Analyzes viral potential before posting

### Style Transfer
- **Reference Matching**: Find similar high-performing posts for style guidance
- **Multiple Variations**: Generate 1-5 rewritten versions with different approaches
- **Performance Analysis**: Compare original vs improved versions

### Bulk Operations
- **Multi-Select**: Choose multiple posts for batch operations
- **Bulk Delete**: Remove multiple posts with confirmation
- **System Cleanup**: Remove default/sample posts to start fresh

## 📈 **Performance Tracking**

- **Gary-Specific Stats**: Separate analytics for Gary Lin vs other authors
- **Engagement Metrics**: Track likes, comments, and total engagement
- **Content Type Performance**: See which content types perform best
- **Viral Score Analysis**: AI-powered engagement prediction

## 🛠 **Technical Architecture**

- **Backend**: Python, Groq API (Llama 3), ChromaDB
- **Frontend**: Streamlit web interface
- **AI Models**: Sentence Transformers for embeddings, spaCy for NLP
- **Storage**: Local ChromaDB with automatic persistence
- **APIs**: Groq for LLM, Hugging Face for embeddings

## 📝 **Contributing**

This is a personal tool for Gary Lin, but the architecture can be adapted for other creators:

1. Fork the repository
2. Modify `src/gary_lin_persona.py` for your voice/style
3. Update `src/config.py` with your content types
4. Customize the prompt templates in `src/content_generator.py`

## 📄 **License**

Private repository - All rights reserved.

## 🆘 **Support**

For issues or questions:
1. Check the Settings page in the web interface
2. Review the console output for error messages
3. Ensure your `.env` file is properly configured
4. Verify your Groq API key is valid

---

**🎯 Gary Bot helps you create authentic, engaging LinkedIn content that resonates with your audience while maintaining your unique founder voice.**