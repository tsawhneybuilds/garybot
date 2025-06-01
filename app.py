import streamlit as st
import pandas as pd
from typing import Optional, List, Dict, Any
import time
from datetime import datetime
import traceback

# Import our modules
from src.gary_bot import GaryBot
from src.config import get_config, validate_config, print_config_summary, AVAILABLE_GROQ_MODELS, CONTENT_TYPES
from src.models import GeneratedPostDraft, ViralSnippetCandidate
from src.backup_system import BackupSystem

# Page configuration
st.set_page_config(
    page_title="🚀 Gary Bot - LinkedIn Post Generator", 
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
    
    .snippet-card {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin: 1rem 0;
        background-color: #f8f9fa;
    }
    
    .post-preview {
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #667eea;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .success-message {
        color: #28a745;
        font-weight: bold;
    }
    
    .warning-message {
        color: #ffc107;
        font-weight: bold;
    }
    
    .error-message {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_gary_bot():
    """Initialize GaryBot with caching to avoid reloading."""
    try:
        config = get_config()
        if not validate_config(config):
            st.error("❌ Configuration validation failed. Please check your environment variables.")
            st.stop()
        
        return GaryBot(config)
    except Exception as e:
        st.error(f"❌ Failed to initialize GaryBot: {str(e)}")
        st.stop()

def main():
    """Main application function."""
    
    # Header
    st.markdown('<h1 class="main-header">🚀 Gary Bot</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">AI-Powered Viral LinkedIn Post Generator for Gary Lin</p>', unsafe_allow_html=True)
    
    # Initialize GaryBot
    gary_bot = initialize_gary_bot()
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🎛️ Control Panel")
        
        page = st.selectbox(
            "Navigate to:",
            ["📝 Generate Posts", "✨ Post Rewriter", "📊 Post History", "⚙️ Manage RAG", "📈 System Stats", "🔧 Settings"]
        )
        
        st.markdown("---")
        
        # Quick stats
        st.subheader("📊 Gary Lin's Stats")
        try:
            stats = gary_bot.get_system_stats()
            gary_stats = stats.get("gary_stats", {})
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Gary's Posts", gary_stats.get("total_posts", 0))
                st.metric("Gold Standard", gary_stats.get("gold_standard_posts", 0))
            with col2:
                st.metric("Generated", gary_stats.get("generated_posts", 0))
                st.metric("Avg Likes", f"{gary_stats.get('avg_likes_per_post', 0):.1f}")
        except Exception as e:
            st.error(f"Error loading stats: {str(e)}")
    
    # Main content based on selected page
    if page == "📝 Generate Posts":
        generate_posts_page(gary_bot)
    elif page == "✨ Post Rewriter":
        post_rewriter_page(gary_bot)
    elif page == "📊 Post History":
        post_history_page(gary_bot)
    elif page == "⚙️ Manage RAG":
        manage_rag_page(gary_bot)
    elif page == "📈 System Stats":
        system_stats_page(gary_bot)
    elif page == "🔧 Settings":
        settings_page(gary_bot)

def generate_posts_page(gary_bot: GaryBot):
    """Main post generation page."""
    
    st.header("📝 Generate LinkedIn Posts")
    st.markdown("Upload a transcript and let Gary Bot identify the most viral snippets and generate engaging LinkedIn posts.")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload Transcript",
        type=['txt'],
        help="Upload a .txt file containing the transcript you want to analyze"
    )
    
    if uploaded_file is not None:
        # Read the file
        transcript_content = str(uploaded_file.read(), "utf-8")
        
        with st.expander("📄 View Raw Transcript", expanded=False):
            st.text_area("Raw Transcript", transcript_content, height=200, disabled=True)
        
        st.markdown("---")
        
        # Processing options
        col1, col2 = st.columns(2)
        with col1:
            auto_generate = st.checkbox("🤖 Auto-generate from top snippet", value=True)
            num_candidates = st.slider("Number of viral candidates to show", 1, 10, 5)
        
        with col2:
            num_variations = st.slider("Number of post variations", 1, 5, 3)
            analysis_enabled = st.checkbox("📊 Include viral analysis", value=True)
        
        if st.button("🚀 Process Transcript & Generate Posts", type="primary"):
            
            with st.spinner("🔄 Processing transcript..."):
                try:
                    # Run the full pipeline
                    results = gary_bot.full_pipeline(transcript_content)
                    
                    st.success(f"✅ Processed {results['segments_count']} segments and found {len(results['viral_candidates'])} viral candidates!")
                    
                    # Show viral candidates
                    st.subheader("🎯 Viral Snippet Candidates")
                    
                    if results['viral_candidates']:
                        for i, candidate in enumerate(results['viral_candidates'][:num_candidates]):
                            with st.expander(f"📋 Candidate #{candidate.rank} (Similarity: {candidate.similarity_score:.3f})", expanded=(i == 0)):
                                
                                st.markdown("**Snippet:**")
                                st.markdown(f'<div class="snippet-card">{candidate.text}</div>', unsafe_allow_html=True)
                                
                                if candidate.most_similar_post_text:
                                    st.markdown("**Most Similar Gold Standard Post:**")
                                    st.markdown(f"_{candidate.most_similar_post_text[:200]}..._")
                                
                                # Generate posts for this candidate
                                if st.button(f"✨ Generate Posts for Candidate {candidate.rank}", key=f"gen_{i}"):
                                    generate_posts_for_snippet(gary_bot, candidate.text, num_variations, analysis_enabled)
                    
                    # Auto-generate from top candidate
                    if auto_generate and results['viral_candidates']:
                        st.markdown("---")
                        st.subheader("🤖 Auto-Generated from Top Candidate")
                        top_candidate = results['viral_candidates'][0]
                        generate_posts_for_snippet(gary_bot, top_candidate.text, num_variations, analysis_enabled)
                    
                except Exception as e:
                    st.error(f"❌ Error processing transcript: {str(e)}")
                    st.error(traceback.format_exc())

def generate_posts_for_snippet(gary_bot: GaryBot, snippet: str, num_variations: int, analysis_enabled: bool):
    """Generate and display posts for a specific snippet."""
    
    with st.spinner("✨ Generating LinkedIn posts..."):
        try:
            # Generate multiple variations
            variations = gary_bot.generate_multiple_variations(snippet, num_variations)
            
            for i, post_text in enumerate(variations):
                st.markdown(f"### 📝 Post Variation {i + 1}")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Post preview
                    st.markdown(f'<div class="post-preview">{post_text}</div>', unsafe_allow_html=True)
                    
                    # Edit option
                    if st.checkbox(f"✏️ Edit Post {i + 1}", key=f"edit_{i}"):
                        edited_post = st.text_area(f"Edit Post {i + 1}", post_text, height=200, key=f"edited_{i}")
                        if st.button(f"💾 Save Edits", key=f"save_{i}"):
                            post_text = edited_post
                            st.success("✅ Edits saved!")
                
                with col2:
                    # Analysis
                    if analysis_enabled:
                        with st.spinner("🔍 Analyzing..."):
                            analysis = gary_bot.analyze_post_potential(post_text)
                            
                            st.markdown("**📊 Viral Analysis**")
                            st.metric("Viral Score", f"{analysis['score']}/10")
                            st.metric("Predicted Engagement", analysis['engagement'])
                            
                            if analysis['strengths']:
                                st.markdown("**💪 Strengths:**")
                                for strength in analysis['strengths']:
                                    st.markdown(f"• {strength}")
                            
                            if analysis['improvements']:
                                st.markdown("**🔧 Improvements:**")
                                for improvement in analysis['improvements']:
                                    st.markdown(f"• {improvement}")
                    
                    # Action buttons
                    st.markdown("**🎯 Actions**")
                    
                    if st.button(f"✅ Approve & Save", key=f"approve_{i}", type="primary"):
                        # Create draft object
                        draft = GeneratedPostDraft(
                            original_snippet=snippet,
                            draft_text=post_text,
                            suggested_hashtags=[],
                            rag_context_ids=[]
                        )
                        
                        # Content type selection
                        content_type = st.selectbox(f"Content Type for Post {i + 1}", CONTENT_TYPES, key=f"content_type_{i}")
                        
                        # Keywords
                        keywords_input = st.text_input(f"Keywords (comma-separated)", key=f"keywords_{i}")
                        keywords = [k.strip() for k in keywords_input.split(",") if k.strip()] if keywords_input else []
                        
                        post_id = gary_bot.approve_post(draft, keywords, content_type)
                        st.success(f"✅ Post approved and saved with ID: {post_id}")
                    
                    if st.button(f"🔄 Regenerate", key=f"regen_{i}"):
                        feedback = st.text_input(f"Feedback for improvement", key=f"feedback_{i}")
                        if feedback:
                            new_post = gary_bot.regenerate_with_feedback(snippet, post_text, feedback)
                            st.markdown("**🆕 Regenerated Post:**")
                            st.markdown(f'<div class="post-preview">{new_post}</div>', unsafe_allow_html=True)
                
                st.markdown("---")
                
        except Exception as e:
            st.error(f"❌ Error generating posts: {str(e)}")

def post_rewriter_page(gary_bot: GaryBot):
    """Post rewriting and style improvement page."""
    
    st.header("✨ Post Rewriter & Style Improver")
    st.markdown("Improve your existing LinkedIn posts by rewriting them to match the style of high-performing posts in your RAG system.")
    
    # Input section
    st.subheader("📝 Original Post")
    original_post = st.text_area(
        "Enter your post to improve:",
        height=200,
        placeholder="Paste your LinkedIn post here that you want to improve..."
    )
    
    if not original_post:
        st.info("👆 Enter a post above to get started with rewriting.")
        return
    
    # Style reference options
    st.subheader("🎨 Style Reference Options")
    
    # Get available posts for reference
    try:
        all_posts = gary_bot.get_post_history()
        if not all_posts:
            st.warning("⚠️ No posts found in your RAG system. Add some high-performing posts first to use as style references.")
            return
        
        # Filter to only gold standard posts with good engagement
        good_posts = [p for p in all_posts if p.is_gold_standard and (p.likes + p.comments) > 50]
        
        col1, col2 = st.columns(2)
        
        with col1:
            reference_option = st.selectbox(
                "Style Reference:",
                ["Auto-select best matches", "Choose specific post", "Filter by content type"],
                help="How to choose reference posts for style matching"
            )
        
        with col2:
            num_variations = st.slider("Number of variations", 1, 5, 3)
        
        # Reference selection based on option
        style_reference_id = None
        content_type_filter = None
        
        if reference_option == "Choose specific post":
            if good_posts:
                # Create a more readable display for post selection
                post_options = {}
                for post in good_posts[:10]:  # Limit to top 10 for UI
                    title = getattr(post, 'title', None)
                    author = getattr(post, 'author', None)
                    
                    display_name = f"{title or post.text[:50]+'...'}"
                    if author:
                        display_name += f" (by {author})"
                    display_name += f" - {post.likes + post.comments} engagement"
                    
                    post_options[display_name] = post.id
                
                selected_display = st.selectbox(
                    "Choose reference post:",
                    list(post_options.keys())
                )
                style_reference_id = post_options[selected_display]
                
                # Show preview of selected post
                selected_post = next(p for p in good_posts if p.id == style_reference_id)
                with st.expander("📖 Preview of reference post", expanded=False):
                    st.markdown(f'<div class="post-preview">{selected_post.text}</div>', unsafe_allow_html=True)
            else:
                st.warning("No high-engagement posts available for reference.")
                return
        
        elif reference_option == "Filter by content type":
            content_types = list(set([p.content_type for p in good_posts if p.content_type]))
            if content_types:
                content_type_filter = st.selectbox("Content type:", content_types)
                
                filtered_posts = [p for p in good_posts if p.content_type == content_type_filter]
                st.info(f"Found {len(filtered_posts)} posts of type '{content_type_filter}' to use as style reference.")
            else:
                st.warning("No content types available for filtering.")
                return
        
        # Generate button
        if st.button("✨ Rewrite Post", type="primary"):
            with st.spinner("🔄 Rewriting your post..."):
                try:
                    # Generate rewritten versions
                    rewritten_posts = gary_bot.rewrite_post_with_style(
                        original_post=original_post,
                        style_reference_id=style_reference_id,
                        content_type=content_type_filter,
                        num_variations=num_variations
                    )
                    
                    if rewritten_posts:
                        st.success(f"✅ Generated {len(rewritten_posts)} rewritten versions!")
                        
                        # Display results
                        st.subheader("🎯 Rewritten Versions")
                        
                        for i, rewritten in enumerate(rewritten_posts):
                            st.markdown(f"### ✨ Version {i + 1}")
                            
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f'<div class="post-preview">{rewritten}</div>', unsafe_allow_html=True)
                                
                                # Edit option
                                if st.checkbox(f"✏️ Edit Version {i + 1}", key=f"edit_rewrite_{i}"):
                                    edited_post = st.text_area(
                                        f"Edit Version {i + 1}", 
                                        rewritten, 
                                        height=200, 
                                        key=f"edited_rewrite_{i}"
                                    )
                                    if st.button(f"💾 Save Edits", key=f"save_rewrite_{i}"):
                                        rewritten = edited_post
                                        st.success("✅ Edits saved!")
                            
                            with col2:
                                st.markdown("**📊 Actions**")
                                
                                # Compare with original
                                if st.button(f"🔍 Compare", key=f"compare_{i}"):
                                    st.markdown("**Original vs Rewritten:**")
                                    
                                    col_orig, col_new = st.columns(2)
                                    with col_orig:
                                        st.markdown("**Original:**")
                                        st.markdown(f'<div style="padding: 1rem; background: #f0f0f0; border-radius: 5px;">{original_post}</div>', unsafe_allow_html=True)
                                    with col_new:
                                        st.markdown("**Rewritten:**")
                                        st.markdown(f'<div style="padding: 1rem; background: #e8f5e8; border-radius: 5px;">{rewritten}</div>', unsafe_allow_html=True)
                                
                                # Analyze potential
                                if st.button(f"📈 Analyze", key=f"analyze_rewrite_{i}"):
                                    with st.spinner("Analyzing..."):
                                        analysis = gary_bot.analyze_post_potential(rewritten)
                                        
                                        st.markdown("**🎯 Analysis**")
                                        st.metric("Viral Score", f"{analysis['score']}/10")
                                        st.metric("Predicted Engagement", analysis['engagement'])
                                        
                                        if analysis['strengths']:
                                            st.markdown("**💪 Strengths:**")
                                            for strength in analysis['strengths']:
                                                st.markdown(f"• {strength}")
                                
                                # Save as new post
                                if st.button(f"💾 Save as Gold Standard", key=f"save_gold_{i}"):
                                    try:
                                        # Author selection for saving
                                        save_author_option = st.selectbox(
                                            f"Author for Version {i+1}:",
                                            ["Gary Lin", "Other"],
                                            index=0,
                                            key=f"author_select_{i}"
                                        )
                                        
                                        if save_author_option == "Other":
                                            save_author = st.text_input(
                                                f"Enter author name for Version {i+1}:", 
                                                placeholder="e.g., John Doe...",
                                                key=f"author_input_{i}"
                                            )
                                        else:
                                            save_author = "Gary Lin"
                                        
                                        if st.button(f"✅ Confirm Save", key=f"confirm_save_{i}"):
                                            # Auto-extract metadata
                                            post_id = gary_bot.add_gold_standard_post(
                                                rewritten,
                                                likes=0,  # New post, no engagement yet
                                                comments=0,
                                                title=f"Rewritten: {original_post[:30]}...",
                                                author=save_author
                                            )
                                            st.success(f"✅ Saved as gold standard post: {post_id}")
                                    except Exception as e:
                                        st.error(f"❌ Error saving post: {str(e)}")
                            
                            st.markdown("---")
                    
                    else:
                        st.error("❌ Failed to generate rewritten versions.")
                        
                except Exception as e:
                    st.error(f"❌ Error rewriting post: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error loading posts: {str(e)}")

def post_history_page(gary_bot: GaryBot):
    """Post history and management page."""
    
    st.header("📊 Post History")
    st.markdown("View and manage all generated and approved posts.")
    
    try:
        posts = gary_bot.get_post_history(limit=50)
        
        if not posts:
            st.info("📝 No posts found. Generate some posts to see them here!")
            return
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_type = st.selectbox("Filter by Type", ["All", "Gold Standard", "Generated"], key="history_filter")
        with col2:
            sort_by = st.selectbox("Sort by", ["Creation Date", "Title", "Author", "Likes", "Comments", "Engagement"], key="history_sort")
        with col3:
            show_count = st.slider("Posts to show", 5, 50, 20, key="history_count")
        
        # Filter posts
        filtered_posts = posts
        if filter_type == "Gold Standard":
            filtered_posts = [p for p in posts if p.is_gold_standard]
        elif filter_type == "Generated":
            filtered_posts = [p for p in posts if not p.is_gold_standard]
        
        # Sort posts
        if sort_by == "Title":
            filtered_posts.sort(key=lambda p: getattr(p, 'title', None) or "Untitled", reverse=False)
        elif sort_by == "Author":
            filtered_posts.sort(key=lambda p: getattr(p, 'author', None) or "Unknown", reverse=False)
        elif sort_by == "Likes":
            filtered_posts.sort(key=lambda p: p.likes, reverse=True)
        elif sort_by == "Comments":
            filtered_posts.sort(key=lambda p: p.comments, reverse=True)
        elif sort_by == "Engagement":
            filtered_posts.sort(key=lambda p: p.likes + p.comments, reverse=True)
        
        # Display posts
        for i, post in enumerate(filtered_posts[:show_count]):
            # Safely get title and author
            post_title = getattr(post, 'title', None)
            post_author = getattr(post, 'author', None)
            
            with st.expander(
                f"{'🌟' if post.is_gold_standard else '📝'} {post_title or post.text[:50]+'...'} "
                f"{'by ' + post_author if post_author else ''} - {post.created_at.strftime('%Y-%m-%d %H:%M')}", 
                expanded=False
            ):
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if post_title:
                        st.markdown(f"**📋 Title:** {post_title}")
                    if post_author:
                        st.markdown(f"**👤 Author:** {post_author}")
                    
                    st.markdown("**📝 Post Content:**")
                    st.markdown(f'<div class="post-preview">{post.text}</div>', unsafe_allow_html=True)
                    
                    if post.source_snippet:
                        st.markdown("**📄 Original Snippet:**")
                        st.markdown(f"_{post.source_snippet[:200]}..._")
                    
                    if post.keywords:
                        st.markdown(f"**🏷️ Keywords:** {', '.join(post.keywords)}")
                    
                    if post.content_type:
                        st.markdown(f"**📂 Content Type:** {post.content_type}")
                    
                    st.markdown(f"**📅 Created:** {post.created_at.strftime('%Y-%m-%d %H:%M')}")
                
                with col2:
                    st.markdown("**📊 Metrics**")
                    st.metric("👍 Likes", post.likes)
                    st.metric("💬 Comments", post.comments)
                    st.metric("🔥 Engagement", post.likes + post.comments)
                    
                    if post.is_gold_standard:
                        st.success("🌟 Gold Standard")
                    
                    # Update engagement
                    st.markdown("**📈 Update Engagement**")
                    new_likes = st.number_input(f"Likes", value=post.likes, min_value=0, key=f"history_likes_{post.id}")
                    new_comments = st.number_input(f"Comments", value=post.comments, min_value=0, key=f"history_comments_{post.id}")
                    
                    if st.button(f"💾 Update", key=f"history_update_{post.id}"):
                        success = gary_bot.update_post_engagement(post.id, new_likes, new_comments)
                        if success:
                            st.success("✅ Engagement updated!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to update engagement")
                
    except Exception as e:
        st.error(f"❌ Error loading post history: {str(e)}")

def manage_rag_page(gary_bot: GaryBot):
    """RAG system management page."""
    
    st.header("⚙️ Manage RAG System")
    st.markdown("Add gold standard posts and manage the knowledge base.")
    
    # Clear default posts section
    st.subheader("🧹 System Cleanup")
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("**Remove Default Posts:** Clear sample/default posts to start fresh with your own content.")
    
    with col2:
        if st.button("🗑️ Clear Default Posts", type="secondary"):
            with st.spinner("Removing default posts..."):
                removed_count = gary_bot.clear_default_posts()
                if removed_count > 0:
                    st.success(f"✅ Removed {removed_count} default posts!")
                    st.rerun()
                else:
                    st.info("ℹ️ No default posts found to remove.")
    
    with col3:
        if st.button("🔄 Reset System", type="secondary"):
            with st.spinner("Resetting system..."):
                success = gary_bot.reset_system_for_defaults()
                if success:
                    st.success("✅ System reset! Default posts can be added again.")
                    st.rerun()
                else:
                    st.error("❌ Failed to reset system.")
    
    st.markdown("---")
    
    # Backup System Section
    st.subheader("💾 Backup & Data Protection")
    st.markdown("**Protect your RAG data:** Create backups to ensure your posts are never lost.")
    
    try:
        config = get_config()
        backup_system = BackupSystem(config.db_path)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📦 Create Backup", type="primary"):
                with st.spinner("Creating backup..."):
                    try:
                        backup_path = backup_system.create_backup()
                        st.success(f"✅ Backup created successfully!")
                        st.info(f"📁 Saved to: {backup_path}")
                    except Exception as e:
                        st.error(f"❌ Backup failed: {str(e)}")
        
        with col2:
            if st.button("🔄 Auto Backup", type="secondary"):
                with st.spinner("Creating auto backup with cleanup..."):
                    try:
                        backup_path = backup_system.auto_backup(max_backups=10)
                        st.success(f"✅ Auto backup completed!")
                        st.info(f"📁 Latest backup: {backup_path}")
                    except Exception as e:
                        st.error(f"❌ Auto backup failed: {str(e)}")
        
        with col3:
            if st.button("📄 Export JSON", type="secondary"):
                with st.spinner("Exporting posts to JSON..."):
                    try:
                        export_path = backup_system.export_posts_json()
                        st.success(f"✅ Posts exported!")
                        st.info(f"📁 Saved to: {export_path}")
                    except Exception as e:
                        st.error(f"❌ Export failed: {str(e)}")
        
        # List existing backups
        with st.expander("📋 View Existing Backups", expanded=False):
            try:
                backups = backup_system.list_backups()
                if backups:
                    st.markdown(f"**Found {len(backups)} backup(s):**")
                    for backup in backups[:10]:  # Show latest 10
                        col_info, col_action = st.columns([3, 1])
                        with col_info:
                            st.markdown(f"• **{backup['filename']}** ({backup['size_mb']} MB)")
                            st.caption(f"Created: {backup['created_at']}")
                        with col_action:
                            if st.button("📥 Restore", key=f"restore_{backup['filename']}", help="⚠️ This will overwrite current data!"):
                                if st.session_state.get(f"confirm_restore_{backup['filename']}", False):
                                    with st.spinner("Restoring backup..."):
                                        try:
                                            success = backup_system.restore_backup(backup['path'], overwrite=True)
                                            if success:
                                                st.success("✅ Backup restored successfully!")
                                                st.info("🔄 Please refresh the page to see changes.")
                                            else:
                                                st.error("❌ Failed to restore backup")
                                        except Exception as e:
                                            st.error(f"❌ Restore failed: {str(e)}")
                                        st.session_state[f"confirm_restore_{backup['filename']}"] = False
                                else:
                                    st.session_state[f"confirm_restore_{backup['filename']}"] = True
                                    st.warning("⚠️ Click again to confirm restore (will overwrite current data)")
                else:
                    st.info("📭 No backups found. Create your first backup above!")
            except Exception as e:
                st.error(f"❌ Error listing backups: {str(e)}")
                
    except Exception as e:
        st.error(f"❌ Error initializing backup system: {str(e)}")
    
    st.markdown("---")
    
    # Add new gold standard post
    st.subheader("➕ Add Gold Standard Post")
    st.markdown("🤖 **Smart Features:** Keywords and content type will be automatically extracted if not provided!")
    
    with st.form("add_gold_standard"):
        # Title and Author
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Title (Optional)", placeholder="Give your post a memorable title...")
        with col2:
            # Author dropdown with Gary Lin as default
            author_option = st.selectbox(
                "Author",
                ["Gary Lin", "Other"],
                index=0,
                help="Select author - only Gary Lin's posts will be included in stats"
            )
            
            if author_option == "Other":
                author = st.text_input("Enter author name:", placeholder="e.g., John Doe...")
            else:
                author = "Gary Lin"
        
        # Post content
        post_text = st.text_area("Post Content", height=200, placeholder="Enter a high-performing LinkedIn post...")
        
        # Engagement metrics
        col1, col2 = st.columns(2)
        with col1:
            likes = st.number_input("Likes", min_value=0, value=0, key="add_likes")
        with col2:
            comments = st.number_input("Comments", min_value=0, value=0, key="add_comments")
        
        # Advanced options in an expander
        with st.expander("🔧 Advanced Options (Optional)", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                manual_keywords = st.text_input("Manual Keywords (comma-separated)", 
                                               placeholder="Leave empty for auto-extraction")
            with col2:
                manual_content_type = st.selectbox("Manual Content Type", 
                                                  ["Auto-detect"] + CONTENT_TYPES)
        
        submitted = st.form_submit_button("✨ Add to RAG System (Auto-Enhanced)", type="primary")
        
        if submitted and post_text:
            try:
                with st.spinner("🤖 Analyzing post and extracting metadata..."):
                    # Prepare parameters
                    keywords_list = None
                    content_type = None
                    
                    # Use manual inputs if provided
                    if 'manual_keywords' in locals() and manual_keywords:
                        keywords_list = [k.strip() for k in manual_keywords.split(",") if k.strip()]
                    
                    if 'manual_content_type' in locals() and manual_content_type != "Auto-detect":
                        content_type = manual_content_type
                    
                    # Add the post (will auto-extract if keywords/content_type are None)
                    post_id = gary_bot.add_gold_standard_post(
                        post_text, 
                        keywords=keywords_list, 
                        likes=likes, 
                        comments=comments,
                        content_type=content_type,
                        title=title if title else None,
                        author=author if author else None
                    )
                    
                    st.success(f"✅ Successfully added gold standard post!")
                    st.info("🤖 Check the console output above for extracted keywords and content type.")
                    
            except Exception as e:
                st.error(f"❌ Error adding post: {str(e)}")
    
    st.markdown("---")
    
    # Post Management Section
    st.subheader("📚 Post Management")
    
    try:
        all_posts = gary_bot.get_post_history()
        
        if all_posts:
            # Filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_type = st.selectbox("Filter by Type", ["All", "Gold Standard", "Generated"], key="manage_filter")
            with col2:
                sort_by = st.selectbox("Sort by", ["Creation Date", "Title", "Author", "Engagement"], key="manage_sort")
            with col3:
                show_count = st.slider("Posts to show", 5, 50, 10, key="manage_count")
            
            # Filter posts
            filtered_posts = all_posts
            if filter_type == "Gold Standard":
                filtered_posts = [p for p in all_posts if p.is_gold_standard]
            elif filter_type == "Generated":
                filtered_posts = [p for p in all_posts if not p.is_gold_standard]
            
            # Sort posts
            if sort_by == "Title":
                filtered_posts.sort(key=lambda p: getattr(p, 'title', None) or "Untitled", reverse=False)
            elif sort_by == "Author":
                filtered_posts.sort(key=lambda p: getattr(p, 'author', None) or "Unknown", reverse=False)
            elif sort_by == "Engagement":
                filtered_posts.sort(key=lambda p: p.likes + p.comments, reverse=True)
            
            # Bulk selection section
            st.markdown("---")
            st.subheader("🔽 Bulk Selection & Actions")
            
            # Initialize session state for bulk selection
            if f"bulk_selected_posts_{filter_type}_{sort_by}" not in st.session_state:
                st.session_state[f"bulk_selected_posts_{filter_type}_{sort_by}"] = set()
            
            bulk_selected = st.session_state[f"bulk_selected_posts_{filter_type}_{sort_by}"]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("☑️ Select All", key="select_all"):
                    bulk_selected.update([post.id for post in filtered_posts[:show_count]])
                    st.session_state[f"bulk_selected_posts_{filter_type}_{sort_by}"] = bulk_selected
                    st.rerun()
            
            with col2:
                if st.button("⬜ Clear Selection", key="clear_selection"):
                    st.session_state[f"bulk_selected_posts_{filter_type}_{sort_by}"] = set()
                    st.rerun()
            
            with col3:
                selected_count = len(bulk_selected)
                st.metric("Selected Posts", selected_count)
            
            with col4:
                if selected_count > 0:
                    if st.button(f"🗑️ Delete {selected_count} Posts", type="secondary", key="bulk_delete"):
                        # Confirmation check
                        if st.session_state.get("confirm_bulk_delete", False):
                            # Perform bulk deletion using the new method
                            with st.spinner(f"Deleting {selected_count} posts..."):
                                result = gary_bot.bulk_delete_posts(list(bulk_selected))
                                
                                if result["success"]:
                                    st.success(f"✅ Successfully deleted {result['deleted_count']} posts!")
                                    if result["failed_count"] > 0:
                                        st.warning(f"⚠️ Failed to delete {result['failed_count']} posts")
                                else:
                                    st.error(f"❌ Failed to delete posts: {result.get('error', 'Unknown error')}")
                                
                                # Clear selection and confirmation
                                st.session_state[f"bulk_selected_posts_{filter_type}_{sort_by}"] = set()
                                st.session_state["confirm_bulk_delete"] = False
                                st.rerun()
                        else:
                            st.session_state["confirm_bulk_delete"] = True
                            st.warning("⚠️ Click again to confirm bulk deletion")
            
            if selected_count > 0:
                st.info(f"📌 {selected_count} posts selected for deletion. Use the 'Delete {selected_count} Posts' button above.")
            
            st.markdown("---")
            
            # Display posts with selection checkboxes
            for i, post in enumerate(filtered_posts[:show_count]):
                # Safely get title and author
                post_title = getattr(post, 'title', None)
                post_author = getattr(post, 'author', None)
                
                # Selection checkbox in the expander title area
                col_check, col_expand = st.columns([1, 10])
                
                with col_check:
                    is_selected = st.checkbox(
                        "Select", 
                        value=post.id in bulk_selected,
                        key=f"select_post_{post.id}",
                        label_visibility="collapsed"
                    )
                    
                    # Update bulk selection
                    if is_selected and post.id not in bulk_selected:
                        bulk_selected.add(post.id)
                        st.session_state[f"bulk_selected_posts_{filter_type}_{sort_by}"] = bulk_selected
                    elif not is_selected and post.id in bulk_selected:
                        bulk_selected.discard(post.id)
                        st.session_state[f"bulk_selected_posts_{filter_type}_{sort_by}"] = bulk_selected
                
                with col_expand:
                    with st.expander(
                        f"{'🌟' if post.is_gold_standard else '📝'} {post_title or post.text[:50]+'...'} "
                        f"{'by ' + post_author if post_author else ''}", 
                        expanded=False
                    ):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            if post_title:
                                st.markdown(f"**📋 Title:** {post_title}")
                            if post_author:
                                st.markdown(f"**👤 Author:** {post_author}")
                            
                            st.markdown("**📝 Content:**")
                            st.markdown(f'<div class="post-preview">{post.text}</div>', unsafe_allow_html=True)
                            
                            if post.keywords:
                                st.markdown(f"**🏷️ Keywords:** {', '.join(post.keywords)}")
                            if post.content_type:
                                st.markdown(f"**📂 Type:** {post.content_type}")
                            
                            st.markdown(f"**📅 Created:** {post.created_at.strftime('%Y-%m-%d %H:%M')}")
                        
                        with col2:
                            st.markdown("**📊 Metrics**")
                            st.metric("👍 Likes", post.likes)
                            st.metric("💬 Comments", post.comments)
                            st.metric("🔥 Total", post.likes + post.comments)
                            
                            if post.is_gold_standard:
                                st.success("🌟 Gold Standard")
                            
                            # Action buttons
                            st.markdown("**⚡ Actions**")
                            
                            # Update engagement - use checkbox instead of expander
                            show_engagement_form = st.checkbox("📈 Update Engagement", key=f"show_engagement_{post.id}")
                            if show_engagement_form:
                                new_likes = st.number_input("Likes", value=post.likes, min_value=0, key=f"edit_likes_{post.id}")
                                new_comments = st.number_input("Comments", value=post.comments, min_value=0, key=f"edit_comments_{post.id}")
                                
                                if st.button("💾 Update", key=f"update_{post.id}"):
                                    success = gary_bot.update_post_engagement(post.id, new_likes, new_comments)
                                    if success:
                                        st.success("✅ Updated!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to update")
                            
                            # Individual delete button
                            if st.button("🗑️ Delete Post", key=f"delete_{post.id}", type="secondary"):
                                if st.session_state.get(f"confirm_delete_{post.id}", False):
                                    success = gary_bot.delete_post(post.id)
                                    if success:
                                        st.success("✅ Post deleted!")
                                        # Remove from bulk selection if it was selected
                                        bulk_selected.discard(post.id)
                                        st.session_state[f"bulk_selected_posts_{filter_type}_{sort_by}"] = bulk_selected
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to delete")
                                else:
                                    st.session_state[f"confirm_delete_{post.id}"] = True
                                    st.warning("⚠️ Click again to confirm deletion")
        else:
            st.info("📝 No posts found. Add some posts to see them here!")
    
    except Exception as e:
        st.error(f"❌ Error loading posts: {str(e)}")
    
    st.markdown("---")
    
    # RAG Statistics
    st.subheader("📊 RAG Statistics")
    
    try:
        stats = gary_bot.get_system_stats()
        rag_stats = stats.get("rag_stats", {})
        gary_stats = stats.get("gary_stats", {})
        
        # Gary Lin's Stats
        st.markdown("### 🎯 Gary Lin's Performance")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Gary's Posts", gary_stats.get("total_posts", 0))
        with col2:
            st.metric("Gold Standard", gary_stats.get("gold_standard_posts", 0))
        with col3:
            st.metric("Generated Posts", gary_stats.get("generated_posts", 0))
        with col4:
            st.metric("Total Engagement", gary_stats.get("total_engagement", 0))
        
        # Overall System Stats
        st.markdown("### 📈 Overall System Stats")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("All Posts", rag_stats.get("total_posts", 0))
        with col2:
            st.metric("All Gold Standard", rag_stats.get("gold_standard_posts", 0))
        with col3:
            st.metric("All Generated", rag_stats.get("generated_posts", 0))
        with col4:
            st.metric("All Engagement", rag_stats.get("total_likes", 0) + rag_stats.get("total_comments", 0))
        
        # Show breakdown by author if there are non-Gary posts
        all_posts = gary_bot.get_post_history()
        authors = set(getattr(post, 'author', 'Unknown') for post in all_posts)
        if len(authors) > 1:
            st.markdown("### 👥 Posts by Author")
            author_breakdown = {}
            for author in authors:
                author_posts = [post for post in all_posts if getattr(post, 'author', 'Unknown') == author]
                author_breakdown[author] = {
                    "count": len(author_posts),
                    "engagement": sum(post.likes + post.comments for post in author_posts)
                }
            
            for author, data in author_breakdown.items():
                st.metric(f"{author}", f"{data['count']} posts", f"{data['engagement']} engagement")
        
    except Exception as e:
        st.error(f"❌ Error loading RAG stats: {str(e)}")

def system_stats_page(gary_bot: GaryBot):
    """System statistics and analytics page."""
    
    st.header("📈 System Statistics")
    st.markdown("Comprehensive analytics and performance metrics.")
    
    try:
        stats = gary_bot.get_system_stats()
        
        # Overview metrics
        st.subheader("📊 Overview")
        rag_stats = stats.get("rag_stats", {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Posts", rag_stats.get("total_posts", 0))
        with col2:
            st.metric("Avg Likes/Post", f"{rag_stats.get('avg_likes_per_post', 0):.1f}")
        with col3:
            st.metric("Avg Comments/Post", f"{rag_stats.get('avg_comments_per_post', 0):.1f}")
        with col4:
            st.metric("Viral Detector Posts", stats.get("viral_detector_posts", 0))
        
        # Configuration
        st.subheader("⚙️ Current Configuration")
        config = stats.get("config", {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**LLM Model:** {config.get('llm_model', 'Unknown')}")
            st.info(f"**Embedding Model:** {config.get('embedding_model', 'Unknown')}")
        with col2:
            st.info(f"**RAG Retrieval Count:** {config.get('rag_retrieval_count', 'Unknown')}")
        
        # Performance metrics (if we had them)
        st.subheader("📈 Performance Trends")
        st.info("📊 Performance analytics will be available as you use the system more.")
        
    except Exception as e:
        st.error(f"❌ Error loading system stats: {str(e)}")

def settings_page(gary_bot: GaryBot):
    """Settings and configuration page."""
    
    st.header("🔧 Settings")
    st.markdown("Configure Gary Bot settings and preferences.")
    
    # Model settings
    st.subheader("🤖 Model Configuration")
    
    current_config = gary_bot.config
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Current LLM Model:**")
        st.info(current_config.llm_model)
        
        st.markdown("**Available Models:**")
        for model, description in AVAILABLE_GROQ_MODELS.items():
            st.markdown(f"• **{model}**: {description}")
    
    with col2:
        st.markdown("**Current Embedding Model:**")
        st.info(current_config.embedding_model_name)
        
        st.markdown("**Current Settings:**")
        st.markdown(f"• RAG Retrieval Count: {current_config.rag_retrieval_count}")
        st.markdown(f"• Temperature: {current_config.default_temperature}")
        st.markdown(f"• Min Similarity: {current_config.min_similarity_threshold}")
    
    st.markdown("---")
    
    # Environment setup instructions
    st.subheader("🔧 Setup Instructions")
    
    st.markdown("""
    To configure Gary Bot, create a `.env` file in the project root with the following variables:
    
    ```bash
    GROQ_API_KEY=your_groq_api_key_here
    LLM_MODEL=llama3-70b-8192
    EMBEDDING_MODEL=all-MiniLM-L6-v2
    RAG_RETRIEVAL_COUNT=3
    DEFAULT_TEMPERATURE=0.7
    MIN_SIMILARITY_THRESHOLD=0.3
    ```
    
    **Getting a Groq API Key:**
    1. Visit [console.groq.com](https://console.groq.com)
    2. Sign up or log in
    3. Go to API Keys section
    4. Create a new API key
    5. Copy it to your `.env` file
    """)
    
    # System info
    st.subheader("ℹ️ System Information")
    st.markdown(f"**Database Path:** `{current_config.db_path}`")
    st.markdown(f"**Collection Name:** `{current_config.collection_name}`")

if __name__ == "__main__":
    main() 