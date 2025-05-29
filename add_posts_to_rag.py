#!/usr/bin/env python3
"""
Script to add posts to Gary Bot's RAG system programmatically.
Use this when you have multiple posts to add or want to automate the process.
"""

from src.gary_bot import GaryBot
from src.config import get_config, validate_config
import sys

def add_sample_posts(gary_bot):
    """Add some sample high-performing LinkedIn posts to the RAG system."""
    
    # Clear any existing default posts first
    print("🧹 Clearing existing default posts...")
    removed_count = gary_bot.clear_default_posts()
    if removed_count > 0:
        print(f"✅ Removed {removed_count} default posts")
    
    # Sample high-performing posts (replace with your actual posts)
    posts_to_add = [
        {
            "title": "The Truth About Raising Your First Round",
            "author": "Gary Lin",
            "text": """Here's the thing nobody tells you about raising your first round:

VCs don't invest in your product. They invest in your ability to execute through uncertainty.

I pitched 47 investors. Got 46 "no's." 

The one "yes" didn't come from having the perfect deck. It came from showing how we pivoted 3 times in 6 months and still grew 40% MoM.

Execution > perfection. Every. Single. Time.

What's one lesson you learned the hard way? 👇""",
            "likes": 2847,
            "comments": 156
        },
        {
            "title": "Most Meetings Are Just Procrastination",
            "author": "Gary Lin",
            "text": """Unpopular opinion: Most "urgent" meetings are just procrastination in disguise.

Real talk from the trenches:
• 80% of meetings could be a Slack message
• 15% could be an async video
• 5% actually need everyone in a room

Your time is your most valuable asset. Protect it like your revenue depends on it.

Because it does.

How do you guard your calendar? Drop your best tips below 👇""",
            "likes": 1923,
            "comments": 203
        },
        {
            "title": "To Every Founder Questioning Themselves",
            "author": "Gary Lin",
            "text": """To every founder reading this who's questioning if they're cut out for this:

You are.

I know because:
• You're here at 11 PM thinking about your customers
• You've failed fast and gotten back up faster
• You care more about solving problems than getting famous
• You're building something bigger than yourself

The doubts don't mean you're weak. They mean you're human.

Keep building. The world needs what you're creating.

Who's one founder that deserves more recognition? Tag them below 👇""",
            "likes": 3156,
            "comments": 289
        }
    ]
    
    print("🚀 Adding posts to Gary Bot's RAG system with auto-enhancement...")
    
    for i, post_data in enumerate(posts_to_add, 1):
        try:
            print(f"\n📝 Processing post {i}/3...")
            # Let the system automatically extract keywords and classify content type
            post_id = gary_bot.add_gold_standard_post(
                post_text=post_data["text"],
                keywords=None,  # Auto-extract
                likes=post_data["likes"],
                comments=post_data["comments"],
                content_type=None,  # Auto-classify
                title=post_data["title"],
                author=post_data["author"]
            )
            print(f"✅ Added post {i}/3 with ID: {post_id}")
        except Exception as e:
            print(f"❌ Error adding post {i}: {str(e)}")
    
    # Display updated stats
    stats = gary_bot.get_system_stats()
    rag_stats = stats.get("rag_stats", {})
    
    print("\n📊 Updated RAG System Stats:")
    print(f"   Total Posts: {rag_stats.get('total_posts', 0)}")
    print(f"   Gold Standard: {rag_stats.get('gold_standard_posts', 0)}")
    print(f"   Total Engagement: {rag_stats.get('total_likes', 0) + rag_stats.get('total_comments', 0)}")

def add_custom_post(gary_bot, text: str, keywords: list = None, likes: int = 0, comments: int = 0, 
                   content_type: str = None, title: str = None, author: str = None):
    """Add a single custom post to the RAG system with auto-enhancement."""
    
    try:
        print("🤖 Adding post with auto-enhancement...")
        post_id = gary_bot.add_gold_standard_post(
            post_text=text,
            keywords=keywords,  # Will auto-extract if None
            likes=likes,
            comments=comments,
            content_type=content_type,  # Will auto-classify if None
            title=title,
            author=author
        )
        print(f"✅ Successfully added post with ID: {post_id}")
        return post_id
    except Exception as e:
        print(f"❌ Error adding post: {str(e)}")
        return None

def clear_default_posts(gary_bot):
    """Clear all default posts from the system."""
    print("🧹 Clearing default posts...")
    removed_count = gary_bot.clear_default_posts()
    
    if removed_count > 0:
        print(f"✅ Removed {removed_count} default posts successfully!")
    else:
        print("ℹ️ No default posts found to remove.")

def delete_post_by_id():
    """Delete a specific post by ID."""
    config = get_config()
    gary_bot = GaryBot(config)
    
    # Show available posts
    posts = gary_bot.get_post_history()
    if not posts:
        print("ℹ️ No posts found in the system.")
        return
    
    print("\n📚 Available Posts:")
    print("-" * 80)
    for i, post in enumerate(posts[:20]):  # Show first 20
        title_display = post.title or post.text[:50] + "..."
        author_display = f" by {post.author}" if post.author else ""
        status = "🌟 Gold" if post.is_gold_standard else "📝 Generated"
        print(f"{i+1:2d}. [{status}] {title_display}{author_display}")
        print(f"    ID: {post.id} | Engagement: {post.likes}👍 {post.comments}💬")
        print()
    
    if len(posts) > 20:
        print(f"... and {len(posts) - 20} more posts")
    
    # Get post ID to delete
    post_id = input("\nEnter the post ID to delete: ").strip()
    if not post_id:
        print("❌ No post ID provided")
        return
    
    # Confirm deletion
    confirm = input(f"⚠️ Are you sure you want to delete post {post_id}? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Deletion cancelled")
        return
    
    # Delete the post
    success = gary_bot.delete_post(post_id)
    if success:
        print("✅ Post deleted successfully!")
    else:
        print("❌ Failed to delete post")

def delete_posts_interactive(gary_bot):
    """Interactive post deletion."""
    posts = gary_bot.get_post_history()
    
    if not posts:
        print("📝 No posts found in the system.")
        return
    
    print("📚 Available posts:")
    for i, post in enumerate(posts[:20]):  # Show first 20
        title = getattr(post, 'title', None)
        author = getattr(post, 'author', None)
        display = f"{title or post.text[:50]+'...'}"
        if author:
            display += f" (by {author})"
        
        print(f"{i+1}. {display}")
        print(f"   ID: {post.id}")
        print(f"   Type: {'Gold Standard' if post.is_gold_standard else 'Generated'}")
        print(f"   Engagement: {post.likes + post.comments}")
        print()
    
    try:
        choice = input("Enter post number to delete (or 'q' to quit): ").strip()
        if choice.lower() == 'q':
            return
        
        index = int(choice) - 1
        if 0 <= index < len(posts[:20]):
            post = posts[index]
            confirm = input(f"Delete '{post.title or post.text[:50]}...'? (y/N): ").strip().lower()
            if confirm == 'y':
                success = gary_bot.delete_post(post.id)
                if success:
                    print("✅ Post deleted successfully!")
                else:
                    print("❌ Failed to delete post")
            else:
                print("❌ Deletion cancelled")
        else:
            print("❌ Invalid post number")
    except ValueError:
        print("❌ Invalid input")

def rewrite_post_interactive(gary_bot):
    """Interactive post rewriting."""
    print("✨ Post Rewriter & Style Improver")
    print("-" * 40)
    
    # Get original post
    print("Enter your post to improve:")
    original_post = input("> ").strip()
    
    if not original_post:
        print("❌ Post content cannot be empty")
        return
    
    # Get available high-performing posts
    all_posts = gary_bot.get_post_history()
    good_posts = [p for p in all_posts if p.is_gold_standard and (p.likes + p.comments) > 50]
    
    if not good_posts:
        print("⚠️ No high-performing posts found for style reference.")
        print("Adding some high-engagement posts to your RAG system first is recommended.")
        return
    
    print(f"\n📊 Found {len(good_posts)} high-performing posts for style reference")
    
    # Style reference options
    print("\nStyle reference options:")
    print("1. Auto-select best matches")
    print("2. Choose specific post")
    print("3. Filter by content type")
    
    try:
        choice = int(input("Choose option (1-3): ").strip())
        
        style_reference_id = None
        content_type_filter = None
        
        if choice == 2:
            # Show available posts
            print("\nAvailable reference posts:")
            for i, post in enumerate(good_posts[:10]):
                title = getattr(post, 'title', None)
                author = getattr(post, 'author', None)
                display = f"{title or post.text[:50]+'...'}"
                if author:
                    display += f" (by {author})"
                display += f" - {post.likes + post.comments} engagement"
                
                print(f"{i+1}. {display}")
            
            ref_choice = int(input("Choose reference post number: ").strip()) - 1
            if 0 <= ref_choice < len(good_posts[:10]):
                style_reference_id = good_posts[ref_choice].id
            else:
                print("❌ Invalid choice, using auto-select")
        
        elif choice == 3:
            # Show content types
            content_types = list(set([p.content_type for p in good_posts if p.content_type]))
            if content_types:
                print("\nAvailable content types:")
                for i, ct in enumerate(content_types):
                    count = len([p for p in good_posts if p.content_type == ct])
                    print(f"{i+1}. {ct} ({count} posts)")
                
                ct_choice = int(input("Choose content type number: ").strip()) - 1
                if 0 <= ct_choice < len(content_types):
                    content_type_filter = content_types[ct_choice]
                else:
                    print("❌ Invalid choice, using auto-select")
            else:
                print("❌ No content types available, using auto-select")
        
        # Number of variations
        num_variations = int(input("Number of variations (1-5, default 3): ").strip() or "3")
        num_variations = max(1, min(5, num_variations))
        
        # Generate rewritten versions
        print(f"\n🔄 Generating {num_variations} rewritten versions...")
        rewritten_posts = gary_bot.rewrite_post_with_style(
            original_post=original_post,
            style_reference_id=style_reference_id,
            content_type=content_type_filter,
            num_variations=num_variations
        )
        
        if rewritten_posts:
            print(f"✅ Generated {len(rewritten_posts)} versions!")
            print("\n" + "="*60)
            
            for i, rewritten in enumerate(rewritten_posts):
                print(f"\n✨ VERSION {i+1}:")
                print("-" * 30)
                print(rewritten)
                print("-" * 30)
                
                # Option to save
                save = input(f"Save version {i+1} as gold standard post? (y/N): ").strip().lower()
                if save == 'y':
                    try:
                        post_id = gary_bot.add_gold_standard_post(
                            rewritten,
                            likes=0,
                            comments=0,
                            title=f"Rewritten: {original_post[:30]}..."
                        )
                        print(f"✅ Saved as gold standard post: {post_id}")
                    except Exception as e:
                        print(f"❌ Error saving post: {str(e)}")
        else:
            print("❌ Failed to generate rewritten versions")
            
    except (ValueError, KeyboardInterrupt):
        print("❌ Invalid input or cancelled")

def print_usage():
    """Print usage information."""
    print("\nUsage: python add_posts_to_rag.py [command]")
    print("\nCommands:")
    print("  sample   - Add sample posts with auto-enhancement")
    print("  clear    - Clear default posts from the system")
    print("  delete   - Delete specific posts interactively")
    print("  list     - List all posts in the system")
    print("  rewrite  - Rewrite/improve a post using style references")
    print("  (no cmd) - Interactive mode to add custom posts")

def interactive_mode(gary_bot):
    """Interactive mode for adding custom posts."""
    print("🤖 Gary Bot - Add Post to RAG System (Auto-Enhanced)")
    print("-" * 50)
    
    # Basic post info
    title = input("Enter post title (optional): ").strip() or None
    
    # Author selection
    print("\nAuthor selection:")
    print("1. Gary Lin (default)")
    print("2. Other")
    
    try:
        author_choice = input("Choose author (1 or 2, default 1): ").strip() or "1"
        if author_choice == "2":
            author = input("Enter author name: ").strip()
            if not author:
                author = "Unknown"
            print(f"⚠️ Note: Posts by '{author}' will not be included in Gary Lin's stats")
        else:
            author = "Gary Lin"
            print("✅ Selected Gary Lin as author")
    except:
        author = "Gary Lin"
        print("✅ Defaulting to Gary Lin as author")
    
    text = input("\nEnter post content:\n> ").strip()
    
    if not text:
        print("❌ Post content cannot be empty")
        return
    
    # Ask if user wants to provide manual metadata
    use_auto = input("\nUse automatic keyword extraction and content classification? (Y/n): ").strip().lower()
    
    if use_auto in ['', 'y', 'yes']:
        # Use auto-enhancement
        try:
            likes = int(input("Enter likes count (default 0): ") or "0")
            comments = int(input("Enter comments count (default 0): ") or "0")
        except ValueError:
            likes = comments = 0
        
        add_custom_post(gary_bot, text, None, likes, comments, None, title, author)
    else:
        # Manual mode
        keywords_input = input("Enter keywords (comma-separated): ").strip()
        keywords = [k.strip() for k in keywords_input.split(",") if k.strip()] if keywords_input else None
        
        content_type = input("Enter content type: ").strip() or None
        
        try:
            likes = int(input("Enter likes count (default 0): ") or "0")
            comments = int(input("Enter comments count (default 0): ") or "0")
        except ValueError:
            likes = comments = 0
        
        add_custom_post(gary_bot, text, keywords, likes, comments, content_type, title, author)

def list_all_posts(gary_bot):
    """List all posts in the system."""
    posts = gary_bot.get_post_history()
    
    if not posts:
        print("ℹ️ No posts found in the system.")
    else:
        print(f"\n📚 Found {len(posts)} posts:")
        print("-" * 80)
        for i, post in enumerate(posts):
            title_display = post.title or post.text[:50] + "..."
            author_display = f" by {post.author}" if post.author else ""
            status = "🌟 Gold" if post.is_gold_standard else "📝 Generated"
            print(f"{i+1:2d}. [{status}] {title_display}{author_display}")
            print(f"    ID: {post.id}")
            print(f"    Created: {post.created_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"    Engagement: {post.likes}👍 {post.comments}💬")
            if post.keywords:
                print(f"    Keywords: {', '.join(post.keywords)}")
            if post.content_type:
                print(f"    Content Type: {post.content_type}")
            print()

def main():
    """Main function for the CLI tool."""
    print("🚀 Gary Bot - RAG Post Management Tool")
    print("=" * 50)
    
    # Initialize Gary Bot
    config = get_config()
    if not validate_config(config):
        print("❌ Configuration validation failed. Please check your environment variables.")
        return
    
    gary_bot = GaryBot(config)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "sample":
            add_sample_posts(gary_bot)
        elif command == "clear":
            clear_default_posts(gary_bot)
        elif command == "delete":
            delete_posts_interactive(gary_bot)
        elif command == "list":
            list_all_posts(gary_bot)
        elif command == "rewrite":
            rewrite_post_interactive(gary_bot)
        else:
            print(f"❌ Unknown command: {command}")
            print_usage()
    else:
        # Interactive mode
        interactive_mode(gary_bot)

if __name__ == "__main__":
    main() 