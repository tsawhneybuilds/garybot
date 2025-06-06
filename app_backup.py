import streamlit as st
import pandas as pd
from typing import Optional, List, Dict, Any
import time
from datetime import datetime
import traceback

# Import our modules
from src.gary_bot import GaryBot
from src.config import get_config, validate_config, print_config_summary, AVAILABLE_GROQ_MODELS, AVAILABLE_OPENAI_MODELS, LLM_PROVIDERS, CONTENT_TYPES
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
        background-color: #18191A;
        color: #fff;
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
        config = get_effective_config()
        if not validate_effective_config(config):
            st.error("❌ Configuration validation failed. Please check your settings.")
            st.stop()
        
        return GaryBot(config)
    except Exception as e:
        st.error(f"❌ Failed to initialize GaryBot: {str(e)}")
        st.stop()

def clear_gary_bot_cache():
    """Clear the cached GaryBot instance when configuration changes."""
    if 'initialize_gary_bot' in st.session_state:
        del st.session_state['initialize_gary_bot']
    initialize_gary_bot.clear()

def get_effective_config():
    """Get configuration from session state overrides or environment variables."""
    config = get_config()
    
    # Override with session state values if they exist
    if hasattr(st.session_state, 'ui_llm_provider'):
        config.llm_provider = st.session_state.ui_llm_provider
    
    if hasattr(st.session_state, 'ui_groq_api_key') and st.session_state.ui_groq_api_key:
        config.groq_api_key = st.session_state.ui_groq_api_key
    
    if hasattr(st.session_state, 'ui_openai_api_key') and st.session_state.ui_openai_api_key:
        config.openai_api_key = st.session_state.ui_openai_api_key
        
    if hasattr(st.session_state, 'ui_groq_model'):
        config.llm_model = st.session_state.ui_groq_model
        
    if hasattr(st.session_state, 'ui_openai_model'):
        config.openai_model = st.session_state.ui_openai_model
    
    return config

def validate_effective_config(config):
    """Validate the effective configuration (including UI overrides)."""
    if config.llm_provider not in ["groq", "openai"]:
        return False
    
    if config.llm_provider == "groq" and not config.groq_api_key:
        return False
    
    if config.llm_provider == "openai" and not config.openai_api_key:
        return False
    
    return True

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
    """Main post generation page - focused on writing from ideas."""
    
    st.header("✍️ Write LinkedIn Posts")
    st.markdown("Transform your ideas and thoughts into engaging LinkedIn posts using different writing personas.")
    
    # Persona and Settings Section
    st.subheader("🎭 Writing Settings")
    
    try:
        # Get available personas
        all_personas = gary_bot.get_all_personas()
        default_persona = gary_bot.get_default_persona()
        
        if not all_personas:
            st.warning("⚠️ No personas found. Please set up personas in Settings first.")
            return
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Persona selection
            persona_options = {}
            for persona in all_personas:
                display_name = f"{persona.name}"
                if persona.is_default:
                    display_name += " (Default)"
                persona_options[display_name] = persona.id
            
            # Find default index
            default_index = 0
            if default_persona:
                for i, (display, pid) in enumerate(persona_options.items()):
                    if pid == default_persona.id:
                        default_index = i
                        break
            
            selected_persona_display = st.selectbox(
                "🎭 Writing Persona",
                list(persona_options.keys()),
                index=default_index,
                help="Choose the writing style and voice for your posts"
            )
            selected_persona_id = persona_options[selected_persona_display]
            selected_persona = gary_bot.get_persona_by_id(selected_persona_id)
        
        with col2:
            # Hooks toggle
            use_hooks = st.checkbox(
                "🪝 Use Writing Hooks", 
                value=True,
                help="Include writing hooks and templates to improve post quality"
            )
        
        with col3:
            # Number of variations
            num_variations = st.slider("Number of variations", 1, 5, 3)
        
        # Show selected persona info
        if selected_persona:
            with st.expander(f"👤 About {selected_persona.name}", expanded=False):
                st.markdown(f"**Description:** {selected_persona.description}")
                st.markdown(f"**Voice & Tone:** {selected_persona.voice_tone}")
                st.markdown(f"**Target Audience:** {selected_persona.target_audience}")
                if selected_persona.content_types:
                    st.markdown(f"**Specializes in:** {', '.join(selected_persona.content_types)}")
    
    except Exception as e:
        st.error(f"❌ Error loading personas: {str(e)}")
        return
    
    st.markdown("---")
    
    # Input Methods
    tab1, tab2 = st.tabs(["💡 From Ideas", "📄 From Transcript"])
    
    with tab1:
        st.subheader("💡 Write from Ideas & Thoughts")
        st.markdown("Enter your core idea, insight, or story and let the AI transform it into an engaging LinkedIn post.")
        
        # Idea input
        idea_input = st.text_area(
            "Enter your idea, insight, or story:",
            height=150,
            placeholder="e.g., 'I made a mistake that cost us $50k in revenue. Here's what I learned...' or 'Our team grew from 5 to 50 people this year. Scaling culture is harder than scaling code.' or just 'productivity tips for remote teams'"
        )
        
        if idea_input and st.button("✍️ Generate Posts from Idea", type="primary"):
            with st.spinner(f"✨ Writing posts using {selected_persona.name} style..."):
                try:
                    # Generate multiple variations using persona
                    variations = gary_bot.generate_multiple_variations(
                        idea_input, 
                        num_variations=num_variations,
                        persona_id=selected_persona_id,
                        use_hooks=use_hooks
                    )
                    
                    st.success(f"✅ Generated {len(variations)} post variations!")
                    
                    for i, post_text in enumerate(variations):
                        display_post_variation(gary_bot, post_text, idea_input, i, selected_persona)
                        
                except Exception as e:
                    st.error(f"❌ Error generating posts: {str(e)}")
    
    with tab2:
        st.subheader("📄 Write from Transcript")
        st.markdown("Upload a transcript and identify viral snippets to turn into posts.")
        
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
                                        generate_posts_for_snippet(gary_bot, candidate.text, num_variations, analysis_enabled, selected_persona_id, use_hooks)
                        
                        # Auto-generate from top candidate
                        if auto_generate and results['viral_candidates']:
                            st.markdown("---")
                            st.subheader("🤖 Auto-Generated from Top Candidate")
                            top_candidate = results['viral_candidates'][0]
                            generate_posts_for_snippet(gary_bot, top_candidate.text, num_variations, analysis_enabled, selected_persona_id, use_hooks)
                        
                    except Exception as e:
                        st.error(f"❌ Error processing transcript: {str(e)}")
                        st.error(traceback.format_exc())

def display_post_variation(gary_bot: GaryBot, post_text: str, original_idea: str, variation_num: int, persona: any):
    """Display a single post variation with actions."""
    
    st.markdown(f"### ✍️ Post Variation {variation_num + 1}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Post preview
        st.markdown(f'<div class="post-preview">{post_text}</div>', unsafe_allow_html=True)
        
        # Edit option
        if st.checkbox(f"✏️ Edit Post {variation_num + 1}", key=f"edit_{variation_num}"):
            edited_post = st.text_area(f"Edit Post {variation_num + 1}", post_text, height=200, key=f"edited_{variation_num}")
            if st.button(f"💾 Save Edits", key=f"save_{variation_num}"):
                post_text = edited_post
                st.success("✅ Edits saved!")
    
    with col2:
        # Analysis
        st.markdown("**📊 Analysis**")
        if st.button(f"🔍 Analyze", key=f"analyze_{variation_num}"):
            with st.spinner("🔍 Analyzing..."):
                analysis = gary_bot.analyze_post_potential(post_text)
                
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
        
        if st.button(f"✅ Save as Gold Standard", key=f"save_{variation_num}", type="primary"):
            # Create save form
            with st.form(f"save_form_{variation_num}"):
                content_type = st.selectbox(f"Content Type", CONTENT_TYPES, key=f"content_type_{variation_num}")
                keywords_input = st.text_input(f"Keywords (comma-separated)", key=f"keywords_{variation_num}")
                
                # Persona assignment
                all_personas = gary_bot.get_all_personas()
                persona_options = ["All Personas"] + [p.name for p in all_personas]
                
                selected_personas = st.multiselect(
                    "Assign to Personas",
                    persona_options,
                    default=[persona.name] if persona else ["All Personas"],
                    help="Choose which personas this post applies to"
                )
                
                # Convert persona names to IDs
                persona_ids = []
                if "All Personas" not in selected_personas:
                    for persona_name in selected_personas:
                        for p in all_personas:
                            if p.name == persona_name:
                                persona_ids.append(p.id)
                                break
                
                if st.form_submit_button("💾 Save Post"):
                    try:
                        keywords = [k.strip() for k in keywords_input.split(",") if k.strip()] if keywords_input else []
                        
                        post_id = gary_bot.add_gold_standard_post(
                            post_text, 
                            keywords=keywords, 
                            likes=0, 
                            comments=0,
                            content_type=content_type,
                            title=f"Generated: {original_idea[:30]}...",
                            author="Gary Lin",
                            persona_ids=persona_ids
                        )
                        
                        st.success(f"✅ Post saved as gold standard with ID: {post_id}")
                        
                    except Exception as e:
                        st.error(f"❌ Error saving post: {str(e)}")
        
        if st.button(f"🔄 Regenerate", key=f"regen_{variation_num}"):
            feedback = st.text_input(f"Feedback for improvement", key=f"feedback_{variation_num}")
            if feedback:
                try:
                    new_post = gary_bot.regenerate_with_feedback(original_idea, post_text, feedback)
                    st.markdown("**🆕 Regenerated Post:**")
                    st.markdown(f'<div class="post-preview">{new_post}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ Error regenerating: {str(e)}")
    
    st.markdown("---")

def generate_posts_for_snippet(gary_bot: GaryBot, snippet: str, num_variations: int, analysis_enabled: bool, persona_id: str, use_hooks: bool):
    """Generate and display posts for a specific snippet with persona."""
    
    with st.spinner("✨ Generating LinkedIn posts..."):
        try:
            # Generate multiple variations using persona
            variations = gary_bot.generate_multiple_variations(
                snippet, 
                num_variations=num_variations,
                persona_id=persona_id,
                use_hooks=use_hooks
            )
            
            persona = gary_bot.get_persona_by_id(persona_id)
            
            for i, post_text in enumerate(variations):
                display_post_variation(gary_bot, post_text, snippet, i, persona)
                
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
        
        # Custom Instructions Section
        st.subheader("📝 Custom Rewrite Instructions")
        custom_instructions = st.text_area(
            "Add specific instructions for how you want your post rewritten:",
            height=100,
            placeholder="e.g., 'Make it more engaging with a strong hook', 'Add more personal storytelling', 'Include a clear call-to-action', 'Make it more concise and punchy'...",
            help="These instructions will be sent to the AI along with your post to guide the rewriting process"
        )
        
        # Generate button
        if st.button("✨ Rewrite Post", type="primary"):
            with st.spinner("🔄 Rewriting your post..."):
                try:
                    # Generate rewritten versions
                    rewritten_posts = gary_bot.rewrite_post_with_style(
                        original_post=original_post,
                        style_reference_id=style_reference_id,
                        content_type=content_type_filter,
                        num_variations=num_variations,
                        custom_instructions=custom_instructions
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
    st.markdown("Add gold standard posts, manage guideline documents, and control the knowledge base.")
    
    # Tab layout for better organization
    tab1, tab2, tab3 = st.tabs(["📝 Posts Management", "📋 Guidelines", "💾 Backup & System"])
    
    with tab3:
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
        
        # --- JSON Import Functionality ---
        st.markdown("---")
        st.subheader("📤 Import from JSON Backup")
        uploaded_json = st.file_uploader("Upload JSON Backup", type=["json"], key="import_json_backup")
        if uploaded_json is not None:
            try:
                import json
                from datetime import datetime
                backup_data = json.load(uploaded_json)
                num_posts = len(backup_data.get("posts", []))
                num_guidelines = len(backup_data.get("guidelines", []))
                export_time = backup_data.get("export_timestamp", "unknown time")
                st.info(f"Backup from: {export_time}")
                st.success(f"Will import {num_posts} posts and {num_guidelines} guidelines.")
                if st.button("🚀 Import Backup", key="import_json_btn"):
                    from src.rag_system import RAGSystem
                    from src.models import RAGPost, GuidelineDocument
                    rag_system = gary_bot.rag_system
                    posts_added, posts_failed = 0, 0
                    guidelines_added, guidelines_failed = 0, 0
                    # Import posts
                    for post_data in backup_data.get("posts", []):
                        try:
                            post = RAGPost(
                                id=post_data['id'],
                                title=post_data.get('title'),
                                author=post_data.get('author'),
                                text=post_data['text'],
                                embedding=None,
                                keywords=post_data.get('keywords', []),
                                content_type=post_data.get('content_type'),
                                source_snippet=post_data.get('source_snippet'),
                                created_at=datetime.fromisoformat(post_data['created_at']),
                                likes=post_data.get('likes', 0),
                                comments=post_data.get('comments', 0),
                                is_gold_standard=post_data.get('is_gold_standard', False),
                                last_engagement_update_at=datetime.fromisoformat(post_data['last_engagement_update_at']) if post_data.get('last_engagement_update_at') else None
                            )
                            rag_system.add_post(post)
                            posts_added += 1
                        except Exception as e:
                            posts_failed += 1
                    # Import guidelines
                    for guideline_data in backup_data.get("guidelines", []):
                        try:
                            guideline = GuidelineDocument(
                                id=guideline_data['id'],
                                title=guideline_data['title'],
                                content=guideline_data['content'],
                                document_type=guideline_data['document_type'],
                                section=guideline_data.get('section'),
                                embedding=None,
                                created_at=datetime.fromisoformat(guideline_data['created_at']),
                                priority=guideline_data.get('priority', 1)
                            )
                            rag_system.add_guideline(guideline)
                            guidelines_added += 1
                        except Exception as e:
                            guidelines_failed += 1
                    st.success(f"✅ Imported {posts_added} posts and {guidelines_added} guidelines!")
                    if posts_failed or guidelines_failed:
                        st.warning(f"⚠️ {posts_failed} posts and {guidelines_failed} guidelines failed to import.")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Failed to parse or import backup: {str(e)}")
        
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
            
            # Quick JSON Download (without saving to server)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Download JSON Backup", type="primary"):
                    with st.spinner("Preparing JSON download..."):
                        try:
                            from src.rag_system import RAGSystem
                            import json
                            
                            # Get all posts and guidelines
                            rag_system = RAGSystem(str(backup_system.db_path))
                            posts = rag_system.list_all_posts()
                            guidelines = rag_system.list_all_guidelines()
                            
                            # Prepare export data
                            posts_data = []
                            for post in posts:
                                post_dict = {
                                    "id": post.id,
                                    "title": post.title,
                                    "author": post.author,
                                    "text": post.text,
                                    "keywords": post.keywords,
                                    "content_type": post.content_type,
                                    "source_snippet": post.source_snippet,
                                    "created_at": post.created_at.isoformat(),
                                    "likes": post.likes,
                                    "comments": post.comments,
                                    "is_gold_standard": post.is_gold_standard,
                                    "last_engagement_update_at": post.last_engagement_update_at.isoformat() if post.last_engagement_update_at else None
                                }
                                posts_data.append(post_dict)
                            
                            guidelines_data = []
                            for guideline in guidelines:
                                guideline_dict = {
                                    "id": guideline.id,
                                    "title": guideline.title,
                                    "content": guideline.content,
                                    "document_type": guideline.document_type,
                                    "section": guideline.section,
                                    "created_at": guideline.created_at.isoformat(),
                                    "priority": guideline.priority
                                }
                                guidelines_data.append(guideline_dict)
                            
                            export_data = {
                                "export_timestamp": datetime.now().isoformat(),
                                "total_posts": len(posts_data),
                                "total_guidelines": len(guidelines_data),
                                "posts": posts_data,
                                "guidelines": guidelines_data
                            }
                            
                            # Convert to JSON string
                            json_content = json.dumps(export_data, indent=2, ensure_ascii=False)
                            
                            # Create download
                            st.download_button(
                                label="💾 Download Complete Backup (JSON)",
                                data=json_content,
                                file_name=f"gary_bot_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                            
                        except Exception as e:
                            st.error(f"❌ Download preparation failed: {str(e)}")
            
            with col2:
                st.info("📋 **JSON Backup includes:**\n• All posts with metadata\n• All guidelines\n• Engagement data\n• Creation timestamps")
            
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
                                # Download button
                                try:
                                    with open(backup['path'], 'rb') as f:
                                        backup_data = f.read()
                                    
                                    st.download_button(
                                        label="📥 Download",
                                        data=backup_data,
                                        file_name=backup['filename'],
                                        mime="application/octet-stream",
                                        key=f"download_{backup['filename']}"
                                    )
                                except Exception as e:
                                    st.error(f"❌ Can't download: {str(e)}")
                                
                                if st.button("🔄 Restore", key=f"restore_{backup['filename']}", help="⚠️ This will overwrite current data!"):
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
    
    with tab2:
        # Guidelines Management Section
        st.subheader("📋 Guideline Documents")
        st.markdown("Manage writing guidelines, hooks, and templates that guide post generation.")
        
        # Add Built-in Guidelines
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📚 Add LinkedIn Hooks & Style Guide", type="primary"):
                with st.spinner("Adding built-in guidelines..."):
                    try:
                        from src.models import GuidelineDocument
                        from add_guidelines import add_linkedin_hooks_guidelines
                        
                        added_ids = add_linkedin_hooks_guidelines(gary_bot.rag_system)
                        st.success(f"✅ Added {len(added_ids)} guideline documents!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error adding guidelines: {str(e)}")
        
        with col2:
            # File upload for custom guidelines
            uploaded_guidelines = st.file_uploader(
                "Upload Guidelines (Markdown)",
                type=['md', 'txt'],
                help="Upload a markdown file with your custom guidelines"
            )
        
        if uploaded_guidelines is not None:
            guidelines_content = str(uploaded_guidelines.read(), "utf-8")
            
            with st.expander("📄 Preview Uploaded Guidelines", expanded=False):
                st.markdown(guidelines_content[:1000] + "..." if len(guidelines_content) > 1000 else guidelines_content)
            
            # Guidelines metadata
            col1, col2, col3 = st.columns(3)
            with col1:
                doc_type = st.selectbox("Document Type", ["hooks", "templates", "style_guide", "general"])
            with col2:
                section = st.text_input("Section (Optional)", placeholder="e.g., curiosity, storytelling")
            with col3:
                priority = st.selectbox("Priority", [1, 2, 3], index=1, help="1=Low, 2=Medium, 3=High")
            
            if st.button("📝 Add Guidelines from File"):
                with st.spinner("Processing guidelines..."):
                    try:
                        from src.models import GuidelineDocument
                        import re
                        
                        # Simple parsing - split by lines and create guidelines
                        lines = guidelines_content.split('\n')
                        guidelines = []
                        current_section = section or "general"
                        
                        for line in lines:
                            line = line.strip()
                            if line and len(line) > 20:  # Only substantial content
                                # Check if it's a section header
                                if line.startswith('#'):
                                    current_section = line.lstrip('#').strip().lower().replace(' ', '_')
                                    continue
                                
                                guideline = GuidelineDocument(
                                    id="",
                                    title=f"{doc_type.title()} - {line[:50]}...",
                                    content=line,
                                    document_type=doc_type,
                                    section=current_section,
                                    priority=priority
                                )
                                guidelines.append(guideline)
                        
                        if guidelines:
                            added_ids = gary_bot.rag_system.add_guidelines_batch(guidelines)
                            st.success(f"✅ Added {len(added_ids)} guidelines from file!")
                            st.rerun()
                        else:
                            st.warning("❌ No substantial guidelines found in the file.")
                    except Exception as e:
                        st.error(f"❌ Error processing guidelines: {str(e)}")
        
        # Manual guideline addition
        st.markdown("---")
        st.subheader("➕ Add Individual Guideline")
        
        with st.form("add_guideline"):
            col1, col2 = st.columns(2)
            with col1:
                guideline_title = st.text_input("Title", placeholder="e.g., Curiosity Hook Template")
                guideline_type = st.selectbox("Type", ["hooks", "templates", "style_guide", "general"])
            with col2:
                guideline_section = st.text_input("Section", placeholder="e.g., curiosity, storytelling")
                guideline_priority = st.selectbox("Priority", [1, 2, 3], index=1)
            
            guideline_content = st.text_area("Content", height=150, 
                                           placeholder="Enter the guideline content, template, or rule...")
            
            if st.form_submit_button("✨ Add Guideline", type="primary"):
                if guideline_title and guideline_content:
                    try:
                        from src.models import GuidelineDocument
                        
                        guideline = GuidelineDocument(
                            id="",
                            title=guideline_title,
                            content=guideline_content,
                            document_type=guideline_type,
                            section=guideline_section or None,
                            priority=guideline_priority
                        )
                        
                        guideline_id = gary_bot.rag_system.add_guideline(guideline)
                        st.success(f"✅ Added guideline: {guideline_title}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error adding guideline: {str(e)}")
                else:
                    st.error("❌ Please provide both title and content.")
        
        # List existing guidelines
        st.markdown("---")
        st.subheader("📚 Current Guidelines")
        
        try:
            all_guidelines = gary_bot.rag_system.list_all_guidelines()
            
            if all_guidelines:
                # Statistics
                type_counts = {}
                for guideline in all_guidelines:
                    doc_type = guideline.document_type
                    type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
                
                st.markdown(f"**Total Guidelines: {len(all_guidelines)}**")
                cols = st.columns(len(type_counts))
                for i, (doc_type, count) in enumerate(type_counts.items()):
                    with cols[i]:
                        st.metric(doc_type.title(), count)
                
                # Filter options
                col1, col2 = st.columns(2)
                with col1:
                    filter_type = st.selectbox("Filter by Type", ["All"] + list(type_counts.keys()))
                with col2:
                    show_limit = st.selectbox("Show", [10, 25, 50, "All"], index=0)
                
                # Display guidelines
                filtered_guidelines = all_guidelines
                if filter_type != "All":
                    filtered_guidelines = [g for g in all_guidelines if g.document_type == filter_type]
                
                if show_limit != "All":
                    filtered_guidelines = filtered_guidelines[:int(show_limit)]
                
                # Bulk selection state
                bulk_selection_key = f"bulk_selected_guidelines_{filter_type}_{show_limit}"
                if bulk_selection_key not in st.session_state:
                    st.session_state[bulk_selection_key] = set()
                
                bulk_selected = st.session_state[bulk_selection_key]
                
                # Bulk action buttons
                st.markdown("### 🔧 Bulk Actions")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button("☑️ Select All Guidelines", key="select_all_guidelines"):
                        bulk_selected.update([g.id for g in filtered_guidelines])
                        st.session_state[bulk_selection_key] = bulk_selected
                        st.rerun()
                
                with col2:
                    if st.button("⬜ Clear Selection", key="clear_selection_guidelines"):
                        st.session_state[bulk_selection_key] = set()
                        st.rerun()
                
                with col3:
                    selected_count = len(bulk_selected)
                    st.metric("Selected Guidelines", selected_count)
                
                with col4:
                    if selected_count > 0:
                        if st.button(f"🗑️ Delete {selected_count} Guidelines", type="secondary", key="bulk_delete_guidelines"):
                            # Confirmation check
                            if st.session_state.get("confirm_bulk_delete_guidelines", False):
                                # Perform bulk deletion
                                with st.spinner(f"Deleting {selected_count} guidelines..."):
                                    result = gary_bot.rag_system.bulk_delete_guidelines(list(bulk_selected))
                                    
                                    if result["success"]:
                                        st.success(f"✅ Successfully deleted {result['deleted_count']} guidelines!")
                                        if result["failed_count"] > 0:
                                            st.warning(f"⚠️ Failed to delete {result['failed_count']} guidelines")
                                    else:
                                        st.error(f"❌ Failed to delete guidelines: {result.get('error', 'Unknown error')}")
                                    
                                    # Clear selection and confirmation
                                    st.session_state[bulk_selection_key] = set()
                                    st.session_state["confirm_bulk_delete_guidelines"] = False
                                    st.rerun()
                            else:
                                st.session_state["confirm_bulk_delete_guidelines"] = True
                                st.warning("⚠️ Click again to confirm bulk deletion")
                
                if selected_count > 0:
                    st.info(f"📌 {selected_count} guidelines selected for deletion. Use the 'Delete {selected_count} Guidelines' button above.")
                
                st.markdown("---")
                
                # Display guidelines with selection checkboxes
                for i, guideline in enumerate(filtered_guidelines):
                    # Selection checkbox and expander
                    col_check, col_expand = st.columns([1, 10])
                    
                    with col_check:
                        is_selected = st.checkbox(
                            "Select", 
                            value=guideline.id in bulk_selected,
                            key=f"select_guideline_{guideline.id}",
                            label_visibility="collapsed"
                        )
                        
                        # Update bulk selection
                        if is_selected and guideline.id not in bulk_selected:
                            bulk_selected.add(guideline.id)
                            st.session_state[bulk_selection_key] = bulk_selected
                        elif not is_selected and guideline.id in bulk_selected:
                            bulk_selected.discard(guideline.id)
                            st.session_state[bulk_selection_key] = bulk_selected
                    
                    with col_expand:
                        with st.expander(f"📋 {guideline.title} ({guideline.document_type})", expanded=False):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**Section:** {guideline.section or 'General'}")
                                st.markdown(f"**Priority:** {guideline.priority}")
                                st.markdown(f"**Content:**\n{guideline.content}")
                            with col2:
                                # Individual delete button
                                if st.button("🗑️ Delete", key=f"del_guideline_{i}"):
                                    if st.session_state.get(f"confirm_delete_guideline_{guideline.id}", False):
                                        if gary_bot.rag_system.delete_guideline(guideline.id):
                                            st.success("✅ Guideline deleted!")
                                            # Remove from bulk selection if it was selected
                                            bulk_selected.discard(guideline.id)
                                            st.session_state[bulk_selection_key] = bulk_selected
                                            st.rerun()
                                        else:
                                            st.error("❌ Failed to delete guideline")
                                    else:
                                        st.session_state[f"confirm_delete_guideline_{guideline.id}"] = True
                                        st.warning("⚠️ Click again to confirm deletion")
            else:
                st.info("📭 No guidelines found. Add some guidelines to help improve post generation!")
                
        except Exception as e:
            st.error(f"❌ Error loading guidelines: {str(e)}")
    
    with tab1:
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
                                
                                # Show persona assignments
                                try:
                                    if post.persona_ids:
                                        all_personas = gary_bot.get_all_personas()
                                        assigned_personas = [p.name for p in all_personas if p.id in post.persona_ids]
                                        if assigned_personas:
                                            st.markdown(f"**🎭 Personas:** {', '.join(assigned_personas)}")
                                        else:
                                            st.markdown(f"**🎭 Personas:** Unknown personas (IDs: {', '.join(post.persona_ids)})")
                                    else:
                                        st.markdown(f"**🎭 Personas:** All Personas")
                                except Exception as e:
                                    st.markdown(f"**🎭 Personas:** Error loading ({str(e)})")
                                
                                st.markdown(f"**📅 Created:** {post.created_at.strftime('%Y-%m-%d %H:%M')}")
                            
                            with col2:
                                st.markdown(f"**👍 Likes:** {post.likes}")
                                st.markdown(f"**💬 Comments:** {post.comments}")
                                st.markdown(f"**🔥 Engagement:** {post.likes + post.comments}")
                                
                                if post.is_gold_standard:
                                    st.success("🌟 Gold Standard")
                                
                                # Persona assignment section
                                st.markdown("**🎭 Manage Personas**")
                                
                                try:
                                    all_personas = gary_bot.get_all_personas()
                                    if all_personas:
                                        # Current assignments
                                        current_assignments = post.persona_ids if post.persona_ids else []
                                        current_persona_names = []
                                        if current_assignments:
                                            current_persona_names = [p.name for p in all_personas if p.id in current_assignments]
                                        
                                        # Create options list
                                        persona_options = ["All Personas"] + [p.name for p in all_personas]
                                        
                                        # Set default selection
                                        default_selection = current_persona_names if current_persona_names else ["All Personas"]
                                        
                                        new_persona_selection = st.multiselect(
                                            "Assign to Personas:",
                                            persona_options,
                                            default=default_selection,
                                            key=f"personas_{post.id}",
                                            help="Choose which personas this post applies to"
                                        )
                                        
                                        if st.button(f"💾 Update Personas", key=f"update_personas_{post.id}"):
                                            # Convert names to IDs
                                            new_persona_ids = []
                                            if "All Personas" not in new_persona_selection:
                                                for persona_name in new_persona_selection:
                                                    for p in all_personas:
                                                        if p.name == persona_name:
                                                            new_persona_ids.append(p.id)
                                                            break
                                            
                                            success = gary_bot.update_post_personas(post.id, new_persona_ids)
                                            if success:
                                                st.success("✅ Personas updated!")
                                                st.rerun()
                                            else:
                                                st.error("❌ Failed to update personas")
                                    else:
                                        st.info("No personas available")
                                        
                                except Exception as e:
                                    st.error(f"Error managing personas: {str(e)}")
                                
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
                st.metric("Avg Likes", f"{gary_stats.get('avg_likes_per_post', 0):.1f}")
            
            # Overall RAG Stats
            st.markdown("### 📊 Overall System")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Posts", rag_stats.get("total_posts", 0))
            with col2:
                st.metric("Total Authors", rag_stats.get("unique_authors", 0))
            with col3:
                st.metric("Total Engagement", rag_stats.get("total_engagement", 0))
            with col4:
                st.metric("Avg Engagement", f"{rag_stats.get('avg_engagement_per_post', 0):.1f}")
        
        except Exception as e:
            st.error(f"❌ Error loading stats: {str(e)}")
    
    st.markdown("---")

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
        effective_config = get_effective_config()
        
        col1, col2 = st.columns(2)
        with col1:
            # Show provider and model info
            if effective_config.llm_provider == "groq":
                st.info(f"**LLM Provider:** 🚀 Groq")
                st.info(f"**Groq Model:** {effective_config.llm_model}")
            elif effective_config.llm_provider == "openai":
                st.info(f"**LLM Provider:** 🧠 OpenAI")
                st.info(f"**OpenAI Model:** {effective_config.openai_model}")
            else:
                st.info(f"**LLM Provider:** {effective_config.llm_provider}")
            
            st.info(f"**Embedding Model:** {config.get('embedding_model', 'Unknown')}")
        with col2:
            st.info(f"**RAG Retrieval Count:** {config.get('rag_retrieval_count', 'Unknown')}")
            st.info(f"**Temperature:** {effective_config.default_temperature}")
            st.info(f"**Min Similarity:** {effective_config.min_similarity_threshold}")
            
            # Show configuration source
            ui_configured = any(hasattr(st.session_state, key) for key in ['ui_llm_provider', 'ui_groq_api_key', 'ui_openai_api_key'])
            config_source = "🎮 UI Configuration" if ui_configured else "📄 Environment Variables"
            st.info(f"**Config Source:** {config_source}")
        
        # Performance metrics (if we had them)
        st.subheader("📈 Performance Trends")
        st.info("📊 Performance analytics will be available as you use the system more.")
        
    except Exception as e:
        st.error(f"❌ Error loading system stats: {str(e)}")

def settings_page(gary_bot: GaryBot):
    """Settings and configuration page."""
    
    st.header("🔧 Settings")
    st.markdown("Configure Gary Bot settings and preferences directly in the UI - no .env file changes needed!")
    
    current_config = gary_bot.config
    
    # UI Configuration Section
    st.subheader("🎮 Live Configuration (No Restart Needed)")
    st.markdown("Configure your LLM provider and API keys directly here. Changes take effect immediately!")
    
    # Initialize session state if not exists
    if 'ui_llm_provider' not in st.session_state:
        st.session_state.ui_llm_provider = current_config.llm_provider
    if 'ui_groq_api_key' not in st.session_state:
        st.session_state.ui_groq_api_key = ""
    if 'ui_openai_api_key' not in st.session_state:
        st.session_state.ui_openai_api_key = ""
    if 'ui_groq_model' not in st.session_state:
        st.session_state.ui_groq_model = current_config.llm_model
    if 'ui_openai_model' not in st.session_state:
        st.session_state.ui_openai_model = current_config.openai_model
    
    # Provider Selection
    col1, col2 = st.columns([1, 2])
    
    with col1:
        provider_changed = False
        new_provider = st.selectbox(
            "🤖 Choose LLM Provider:",
            ["groq", "openai"],
            index=0 if st.session_state.ui_llm_provider == "groq" else 1,
            help="Groq is free, OpenAI requires credits"
        )
        
        if new_provider != st.session_state.ui_llm_provider:
            st.session_state.ui_llm_provider = new_provider
            provider_changed = True
    
    with col2:
        if st.session_state.ui_llm_provider == "groq":
            st.info("🚀 **Groq**: Free, fast inference with open-source models")
        else:
            st.info("🧠 **OpenAI**: Premium ChatGPT models (requires API credits)")
    
    # API Key Configuration
    st.markdown("### 🔑 API Key Configuration")
    
    if st.session_state.ui_llm_provider == "groq":
        # Groq Configuration
        col1, col2 = st.columns([2, 1])
        
        with col1:
            new_groq_key = st.text_input(
                "🚀 Groq API Key:",
                value=st.session_state.ui_groq_api_key,
                type="password",
                placeholder="gsk_your_groq_api_key_here",
                help="Get your free API key from console.groq.com"
            )
            
            if new_groq_key != st.session_state.ui_groq_api_key:
                st.session_state.ui_groq_api_key = new_groq_key
                provider_changed = True
        
        with col2:
            if st.button("🔗 Get Groq API Key", type="secondary"):
                st.markdown("**Get your free Groq API key:**")
                st.markdown("1. Visit [console.groq.com](https://console.groq.com)")
                st.markdown("2. Sign up for free")
                st.markdown("3. Go to API Keys section")
                st.markdown("4. Create a new API key")
                st.markdown("5. Paste it above")
        
        # Groq Model Selection
        groq_model = st.selectbox(
            "⚡ Groq Model:",
            list(AVAILABLE_GROQ_MODELS.keys()),
            index=list(AVAILABLE_GROQ_MODELS.keys()).index(st.session_state.ui_groq_model),
            format_func=lambda x: f"{x} - {AVAILABLE_GROQ_MODELS[x]}"
        )
        
        if groq_model != st.session_state.ui_groq_model:
            st.session_state.ui_groq_model = groq_model
            provider_changed = True
    
    else:  # OpenAI
        # OpenAI Configuration
        col1, col2 = st.columns([2, 1])
        
        with col1:
            new_openai_key = st.text_input(
                "🧠 OpenAI API Key:",
                value=st.session_state.ui_openai_api_key,
                type="password",
                placeholder="sk-your_openai_api_key_here",
                help="Get your API key from platform.openai.com"
            )
            
            if new_openai_key != st.session_state.ui_openai_api_key:
                st.session_state.ui_openai_api_key = new_openai_key
                provider_changed = True
        
        with col2:
            if st.button("🔗 Get OpenAI API Key", type="secondary"):
                st.markdown("**Get your OpenAI API key:**")
                st.markdown("1. Visit [platform.openai.com](https://platform.openai.com)")
                st.markdown("2. Sign up or log in")
                st.markdown("3. Go to API Keys section")
                st.markdown("4. Create a new API key")
                st.markdown("5. Paste it above")
        
        # OpenAI Model Selection
        openai_model = st.selectbox(
            "🧠 OpenAI Model:",
            list(AVAILABLE_OPENAI_MODELS.keys()),
            index=list(AVAILABLE_OPENAI_MODELS.keys()).index(st.session_state.ui_openai_model),
            format_func=lambda x: f"{x} - {AVAILABLE_OPENAI_MODELS[x]}"
        )
        
        if openai_model != st.session_state.ui_openai_model:
            st.session_state.ui_openai_model = openai_model
            provider_changed = True
        
        st.warning("⚠️ **Note**: OpenAI is a paid service. Make sure you have credits in your account.")
    
    # Clear cache if configuration changed
    if provider_changed:
        clear_gary_bot_cache()
        st.rerun()
    
    # Current Status
    st.markdown("### 📊 Current Status")
    
    effective_config = get_effective_config()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        provider_status = "✅" if validate_effective_config(effective_config) else "❌"
        st.metric("Provider", f"{provider_status} {effective_config.llm_provider.upper()}")
    
    with col2:
        if effective_config.llm_provider == "groq":
            api_status = "✅" if effective_config.groq_api_key else "❌"
            st.metric("Groq API Key", f"{api_status} {'Set' if effective_config.groq_api_key else 'Missing'}")
        else:
            api_status = "✅" if effective_config.openai_api_key else "❌"
            st.metric("OpenAI API Key", f"{api_status} {'Set' if effective_config.openai_api_key else 'Missing'}")
    
    with col3:
        model_name = effective_config.llm_model if effective_config.llm_provider == "groq" else effective_config.openai_model
        st.metric("Model", model_name)
    
    # Test Configuration
    if validate_effective_config(effective_config):
        if st.button("🧪 Test Current Configuration", type="primary"):
            try:
                with st.spinner("Testing configuration..."):
                    # Test basic functionality
                    test_result = gary_bot.content_generator.generate_post(
                        "This is a test to verify the LLM connection is working.",
                        temperature=0.3,
                        max_tokens=100
                    )
                    
                    st.success(f"✅ Configuration test successful!")
                    st.info(f"**Provider**: {effective_config.llm_provider.upper()}")
                    if effective_config.llm_provider == "groq":
                        st.info(f"**Model**: {effective_config.llm_model}")
                    else:
                        st.info(f"**Model**: {effective_config.openai_model}")
                    
                    with st.expander("📄 Test Response Preview"):
                        st.markdown(test_result[:200] + "..." if len(test_result) > 200 else test_result)
                    
            except Exception as e:
                st.error(f"❌ Configuration test failed: {str(e)}")
                st.markdown("**Possible solutions:**")
                st.markdown("• Check your API key is correct")
                st.markdown("• Verify your internet connection")
                st.markdown("• Make sure you have credits (for OpenAI)")
    else:
        st.error("❌ Configuration incomplete. Please add your API key above.")
    
    st.markdown("---")
    
    # Alternative: Environment Configuration
    st.subheader("📄 Alternative: Environment File Configuration")
    st.markdown("If you prefer to use environment variables instead of the UI configuration above:")
    
    with st.expander("📝 View .env File Template", expanded=False):
        st.markdown("""
        ```bash
        # Choose your provider
        LLM_PROVIDER=openai                 # or "groq"
        
        # API Keys (add the one you're using)
        GROQ_API_KEY=gsk_your_groq_key_here
        OPENAI_API_KEY=sk-your_openai_key_here
        
        # Model Selection (Groq Options)
        LLM_MODEL=llama3-70b-8192          # For Groq - Traditional
        # LLM_MODEL=deepseek-r1-distill-llama-70b  # For Groq - Latest reasoning model
        OPENAI_MODEL=gpt-4o                # For OpenAI - Latest flagship
        
        # Other Settings
        EMBEDDING_MODEL=all-MiniLM-L6-v2
        RAG_RETRIEVAL_COUNT=3
        DEFAULT_TEMPERATURE=0.7
        ```
        """)
        
        st.info("💡 **Tip**: UI configuration above takes precedence over .env file settings.")
    
    # Other Settings Display
    st.subheader("⚙️ Other Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Current Configuration:**")
        st.markdown(f"• Embedding Model: `{effective_config.embedding_model_name}`")
        st.markdown(f"• RAG Retrieval Count: `{effective_config.rag_retrieval_count}`")
        st.markdown(f"• Temperature: `{effective_config.default_temperature}`")
        st.markdown(f"• Min Similarity: `{effective_config.min_similarity_threshold}`")
    
    with col2:
        st.markdown("**System Information:**")
        st.markdown(f"• Database Path: `{effective_config.db_path}`")
        st.markdown(f"• Collection Name: `{effective_config.collection_name}`")
        st.markdown(f"• Max Tokens: `{effective_config.max_tokens}`")
        st.markdown(f"• Post Variations: `{effective_config.num_post_variations}`")
    
    st.markdown("---")
    
    # Environment File Example
    st.subheader("📄 Complete .env File Example")
    
    st.markdown("""
    Here's a complete example of what your `.env` file should look like:
    
    ```bash
    # LLM Provider (choose one)
    LLM_PROVIDER=groq                    # or "openai"
    
    # API Keys (add the one you're using)
    GROQ_API_KEY=gsk_your_groq_key_here
    OPENAI_API_KEY=sk-your_openai_key_here
    
    # Model Selection
    LLM_MODEL=llama3-70b-8192           # For Groq - Traditional
    # LLM_MODEL=deepseek-r1-distill-llama-70b  # For Groq - Latest reasoning model
    OPENAI_MODEL=gpt-4o                 # For OpenAI - Latest flagship
    
    # Other Settings
    EMBEDDING_MODEL=all-MiniLM-L6-v2
    RAG_RETRIEVAL_COUNT=3
    DEFAULT_TEMPERATURE=0.7
    ```
    """)
    
    st.info("💡 **Tip**: After updating your `.env` file, restart the application for changes to take effect.")
    
    # Quick Test Section
    st.subheader("🧪 Quick Test")
    if st.button("🔍 Test Current Configuration", type="primary"):
        try:
            with st.spinner("Testing configuration..."):
                # Test basic functionality
                test_result = gary_bot.content_generator.generate_post(
                    "This is a test to verify the LLM connection is working.",
                    temperature=0.3,
                    max_tokens=100
                )
                
                st.success(f"✅ Configuration test successful!")
                st.info(f"**Provider**: {effective_config.llm_provider.upper()}")
                if effective_config.llm_provider == "groq":
                    st.info(f"**Model**: {effective_config.llm_model}")
                else:
                    st.info(f"**Model**: {effective_config.openai_model}")
                
                with st.expander("📄 Test Response Preview"):
                    st.markdown(test_result[:200] + "..." if len(test_result) > 200 else test_result)
                    
        except Exception as e:
            st.error(f"❌ Configuration test failed: {str(e)}")
            st.markdown("**Possible solutions:**")
            st.markdown("• Check your API key is correct")
            st.markdown("• Verify your internet connection")
            st.markdown("• Make sure you have credits (for OpenAI)")
            st.markdown("• Restart the application after changing .env")

if __name__ == "__main__":
    main() 