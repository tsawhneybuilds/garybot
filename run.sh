#!/bin/bash

# Gary Bot Quick Start Script
echo "🚀 Starting Gary Bot..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Creating .env file from template..."
    
    if [ -f env_example.txt ]; then
        cp env_example.txt .env
        echo "✅ Created .env file. Please edit it with your actual API key:"
        echo "   nano .env"
        echo ""
        echo "🔑 Get your Groq API key from: https://console.groq.com"
        echo "💡 Then run this script again."
        exit 1
    else
        echo "❌ Template file not found. Please create .env manually."
        exit 1
    fi
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Download spaCy model
echo "🧠 Downloading spaCy model..."
python -m spacy download en_core_web_sm

# Run tests
echo "🧪 Running tests..."
python test_gary_bot.py

# Check if tests passed
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup complete! Starting Gary Bot..."
    echo "🌐 Opening in browser at http://localhost:8501"
    echo ""
    echo "📖 Usage:"
    echo "1. Upload a transcript file (.txt)"
    echo "2. Let Gary Bot find viral snippets"
    echo "3. Generate engaging LinkedIn posts"
    echo "4. Approve and save successful posts"
    echo ""
    
    # Start Streamlit app
    streamlit run app.py
else
    echo "❌ Tests failed. Please check the error messages and fix issues before running."
    echo "💡 Common fixes:"
    echo "   - Add your GROQ_API_KEY to .env file"
    echo "   - Run: pip install -r requirements.txt"
    echo "   - Run: python -m spacy download en_core_web_sm"
fi 