import streamlit as st
import pandas as pd
from datetime import datetime

# Demo version of Gary Bot for public deployment
st.set_page_config(
    page_title="🚀 Gary Bot - Demo", 
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .demo-banner {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🚀 Gary Bot - Demo</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">AI-Powered Viral LinkedIn Post Generator for Gary Lin</p>', unsafe_allow_html=True)
    
    # Demo banner
    st.markdown("""
    <div class="demo-banner">
        <h3>🎭 Demo Version</h3>
        <p>This is a demonstration of Gary Bot's interface. The full version with AI capabilities runs locally with your own API keys.</p>
        <p><strong>🔗 Get the full version:</strong> <a href="https://github.com/tsawhneybuilds/garybot" target="_blank">GitHub Repository</a></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("🎛️ Control Panel")
        page = st.selectbox(
            "Navigate to:",
            ["📝 Generate Posts", "📊 Post History", "⚙️ Manage RAG", "📈 System Stats"]
        )
        
        st.markdown("---")
        st.subheader("📊 Demo Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Sample Posts", "12")
            st.metric("Gold Standard", "8")
        with col2:
            st.metric("Generated", "4")
            st.metric("Avg Likes", "127.3")
    
    # Main content
    if page == "📝 Generate Posts":
        demo_generate_page()
    elif page == "📊 Post History":
        demo_history_page()
    elif page == "⚙️ Manage RAG":
        demo_manage_page()
    elif page == "📈 System Stats":
        demo_stats_page()

def demo_generate_page():
    st.header("📝 Generate LinkedIn Posts")
    st.info("🎭 **Demo Mode:** Upload functionality disabled. In the full version, you can upload transcripts and generate viral LinkedIn posts.")
    
    # Mock file upload
    st.file_uploader("Upload Transcript", type=['txt'], disabled=True, help="Available in full version")
    
    # Sample viral candidates
    st.subheader("🎯 Sample Viral Snippet Candidates")
    
    sample_snippets = [
        {
            "rank": 1,
            "text": "The biggest mistake I made as a founder was thinking I needed to have all the answers. The truth is, the best leaders are the ones who ask the right questions and surround themselves with people smarter than them.",
            "similarity": 0.892
        },
        {
            "rank": 2, 
            "text": "We went from 0 to $1M ARR in 18 months. Here's the one thing that made the difference: we stopped building features our competitors had and started building what our customers actually needed.",
            "similarity": 0.847
        }
    ]
    
    for i, snippet in enumerate(sample_snippets):
        with st.expander(f"📋 Candidate #{snippet['rank']} (Similarity: {snippet['similarity']:.3f})", expanded=(i == 0)):
            st.markdown("**Snippet:**")
            st.markdown(f'<div style="padding: 1rem; border-radius: 10px; border: 1px solid #ddd; background-color: #f8f9fa;">{snippet["text"]}</div>', unsafe_allow_html=True)
            
            if st.button(f"✨ Generate Posts (Demo)", key=f"demo_gen_{i}", disabled=True):
                st.info("🎭 Post generation available in full version with API keys")

def demo_history_page():
    st.header("📊 Post History")
    st.info("🎭 **Demo Mode:** Showing sample post data")
    
    # Sample posts data
    sample_posts = [
        {
            "title": "Fundraising Lessons from Series A",
            "author": "Gary Lin",
            "content": "After raising our Series A, here are the 3 things I wish I knew before starting the process...",
            "likes": 234,
            "comments": 45,
            "created": "2024-01-15",
            "type": "Founder's Personal Story & Journey"
        },
        {
            "title": "Building Remote Culture at Explo",
            "author": "Gary Lin", 
            "content": "Remote work isn't just about Zoom calls. Here's how we built a culture that actually works...",
            "likes": 189,
            "comments": 32,
            "created": "2024-01-10",
            "type": "Internal Company Management & Culture"
        }
    ]
    
    for post in sample_posts:
        with st.expander(f"🌟 {post['title']} by {post['author']}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**📝 Content:** {post['content']}")
                st.markdown(f"**📂 Type:** {post['type']}")
                st.markdown(f"**📅 Created:** {post['created']}")
            
            with col2:
                st.metric("👍 Likes", post['likes'])
                st.metric("💬 Comments", post['comments'])
                st.metric("🔥 Total", post['likes'] + post['comments'])

def demo_manage_page():
    st.header("⚙️ Manage RAG System")
    st.info("🎭 **Demo Mode:** RAG management features shown for demonstration")
    
    st.subheader("➕ Add Gold Standard Post")
    with st.form("demo_add_post"):
        title = st.text_input("Title", placeholder="Demo mode - form disabled", disabled=True)
        author = st.selectbox("Author", ["Gary Lin", "Other"], disabled=True)
        post_text = st.text_area("Post Content", placeholder="Demo mode - form disabled", disabled=True)
        
        col1, col2 = st.columns(2)
        with col1:
            likes = st.number_input("Likes", disabled=True)
        with col2:
            comments = st.number_input("Comments", disabled=True)
        
        submitted = st.form_submit_button("Add to RAG (Demo)", disabled=True)
        if submitted:
            st.info("🎭 Available in full version")

def demo_stats_page():
    st.header("📈 System Statistics")
    st.info("🎭 **Demo Mode:** Showing sample analytics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Posts", "12")
    with col2:
        st.metric("Avg Likes/Post", "156.7")
    with col3:
        st.metric("Avg Comments/Post", "28.3")
    with col4:
        st.metric("Viral Score", "8.2/10")
    
    # Sample chart
    chart_data = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=30, freq='D'),
        'Engagement': [100 + i*5 + (i%7)*20 for i in range(30)]
    })
    
    st.subheader("📈 Engagement Trend")
    st.line_chart(chart_data.set_index('Date'))

if __name__ == "__main__":
    main() 