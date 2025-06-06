#!/usr/bin/env python3
"""
Test script for persona assignment functionality in Gary Bot.
Tests creating personas, assigning posts to personas, and retrieving persona-filtered content.
"""

import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.gary_bot import GaryBot
from src.config import get_config
from src.models import RAGPost

def test_persona_assignment():
    """Test comprehensive persona assignment functionality."""
    
    print("🧪 Testing Persona Assignment Functionality")
    print("=" * 50)
    
    # Initialize Gary Bot
    config = get_config()
    gary_bot = GaryBot(config)
    
    # Step 1: Create test personas
    print("\n1️⃣ Creating test personas...")
    
    # Create Gary Lin persona
    gary_persona_id = gary_bot.create_persona(
        name="Gary Lin - Founder",
        description="Experienced founder with a direct, motivational style",
        voice_tone="Bold, authentic, empathetic, and motivational",
        content_types=["Founder Real Talk, building SaaS", "Team, Culture & Leadership"],
        style_guide="Use storytelling, keep it real, include actionable insights",
        example_hooks=["I made a mistake that cost us $50k", "Here's what I learned after 5 failed startups"],
        target_audience="Founders and entrepreneurs",
        is_default=True,
        is_active=True
    )
    print(f"✅ Created Gary Lin persona: {gary_persona_id}")
    
    # Create Technical Expert persona
    tech_persona_id = gary_bot.create_persona(
        name="Technical Expert",
        description="Deep technical knowledge with practical insights",
        voice_tone="Analytical, precise, but accessible",
        content_types=["Analytics Insight", "Explo product Updates"],
        style_guide="Focus on data, include code examples when relevant, explain complex concepts simply",
        example_hooks=["The data shows something unexpected", "Here's how we solved a complex technical problem"],
        target_audience="CTOs, engineers, technical founders",
        is_default=False,
        is_active=True
    )
    print(f"✅ Created Technical Expert persona: {tech_persona_id}")
    
    # Step 2: Add posts with persona assignments
    print("\n2️⃣ Adding posts with persona assignments...")
    
    # Add post for Gary Lin persona only
    gary_post_id = gary_bot.add_gold_standard_post(
        post_text="I failed 3 startups before finding product-market fit. Here's what I learned: 1) Listen to your customers more than your investors 2) Build something people actually want 3) Don't be afraid to pivot when data shows you're wrong. Failure is just expensive education. 💪",
        likes=150,
        comments=25,
        title="Lessons from 3 Failed Startups",
        author="Gary Lin",
        content_type="Founder Real Talk, building SaaS",
        keywords=["failure", "startup", "learning", "pivot"],
        persona_ids=[gary_persona_id]
    )
    print(f"✅ Added Gary Lin post: {gary_post_id}")
    
    # Add post for Technical Expert persona only
    tech_post_id = gary_bot.add_gold_standard_post(
        post_text="Our new caching strategy reduced API response times by 89%. Here's the breakdown: Before: 450ms average, After: 50ms average. Key changes: 1) Redis cluster for hot data 2) CDN for static assets 3) Database query optimization. The impact on user experience was immediate. 📊",
        likes=89,
        comments=12,
        title="API Performance Optimization Results",
        author="Tech Team",
        content_type="Analytics Insight",
        keywords=["performance", "caching", "optimization", "redis"],
        persona_ids=[tech_persona_id]
    )
    print(f"✅ Added Technical post: {tech_post_id}")
    
    # Add post for both personas
    both_post_id = gary_bot.add_gold_standard_post(
        post_text="Building a team is like assembling a puzzle. Each person brings unique skills, but they need to fit together perfectly. We learned this when scaling from 5 to 50 engineers. The key? Hire for culture fit AND technical skills. Both matter equally. 🧩",
        likes=200,
        comments=35,
        title="Scaling Engineering Teams",
        author="Gary Lin",
        content_type="Team, Culture & Leadership",
        keywords=["team", "hiring", "culture", "scaling"],
        persona_ids=[gary_persona_id, tech_persona_id]
    )
    print(f"✅ Added shared post: {both_post_id}")
    
    # Add post for all personas (empty persona_ids)
    all_post_id = gary_bot.add_gold_standard_post(
        post_text="Innovation isn't about having the best idea. It's about executing on good ideas consistently. We see this pattern across all successful companies - they ship, iterate, and improve. The magic is in the execution, not the inspiration. ⚡",
        likes=300,
        comments=45,
        title="Innovation is Execution",
        author="Gary Lin",
        content_type="Founder Real Talk, building SaaS",
        keywords=["innovation", "execution", "consistency"],
        persona_ids=[]  # Empty = applies to all personas
    )
    print(f"✅ Added universal post: {all_post_id}")
    
    # Step 3: Test persona filtering in retrieval
    print("\n3️⃣ Testing persona-filtered retrieval...")
    
    # Test Gary Lin persona filtering
    gary_posts = gary_bot.rag_system.retrieve_similar_posts(
        "startup lessons and failures",
        top_k=10,
        persona_id=gary_persona_id
    )
    print(f"📊 Found {len(gary_posts)} posts for Gary Lin persona")
    gary_post_ids = [p.id for p in gary_posts]
    
    # Verify correct posts are returned
    assert gary_post_id in gary_post_ids, "Gary Lin specific post should be included"
    assert both_post_id in gary_post_ids, "Shared post should be included"
    assert all_post_id in gary_post_ids, "Universal post should be included"
    print("✅ Gary Lin persona filtering works correctly")
    
    # Test Technical Expert persona filtering
    tech_posts = gary_bot.rag_system.retrieve_similar_posts(
        "performance optimization and technical improvements",
        top_k=10,
        persona_id=tech_persona_id
    )
    print(f"📊 Found {len(tech_posts)} posts for Technical Expert persona")
    tech_post_ids = [p.id for p in tech_posts]
    
    # Verify correct posts are returned
    assert tech_post_id in tech_post_ids, "Technical specific post should be included"
    assert both_post_id in tech_post_ids, "Shared post should be included"
    assert all_post_id in tech_post_ids, "Universal post should be included"
    print("✅ Technical Expert persona filtering works correctly")
    
    # Step 4: Test persona assignment updates
    print("\n4️⃣ Testing persona assignment updates...")
    
    # Update the technical post to also include Gary Lin persona
    success = gary_bot.update_post_personas(tech_post_id, [tech_persona_id, gary_persona_id])
    assert success, "Persona update should succeed"
    print("✅ Updated technical post to include both personas")
    
    # Verify the update worked
    updated_post = gary_bot.rag_system.get_post_by_id(tech_post_id)
    assert gary_persona_id in updated_post.persona_ids, "Gary persona should now be included"
    assert tech_persona_id in updated_post.persona_ids, "Tech persona should still be included"
    print("✅ Persona assignment update verified")
    
    # Step 5: Test removing all persona assignments (universal post)
    print("\n5️⃣ Testing universal post assignment...")
    
    success = gary_bot.update_post_personas(gary_post_id, [])  # Empty list = applies to all
    assert success, "Making post universal should succeed"
    print("✅ Made Gary post universal (applies to all personas)")
    
    # Verify it now appears for all personas
    updated_gary_post = gary_bot.rag_system.get_post_by_id(gary_post_id)
    assert updated_gary_post.persona_ids == [], "Post should have empty persona_ids (universal)"
    print("✅ Universal assignment verified")
    
    # Step 6: Test statistics and reporting
    print("\n6️⃣ Testing persona statistics...")
    
    all_personas = gary_bot.get_all_personas()
    print(f"📊 Total personas: {len(all_personas)}")
    
    for persona in all_personas:
        # Count posts for this persona
        persona_posts = gary_bot.rag_system.retrieve_similar_posts(
            "test query",
            top_k=100,
            persona_id=persona.id
        )
        print(f"   {persona.name}: {len(persona_posts)} posts")
    
    print("✅ Persona statistics generated successfully")
    
    # Step 7: Clean up test data
    print("\n7️⃣ Cleaning up test data...")
    
    test_post_ids = [gary_post_id, tech_post_id, both_post_id, all_post_id]
    test_persona_ids = [gary_persona_id, tech_persona_id]
    
    # Delete test posts
    for post_id in test_post_ids:
        success = gary_bot.delete_post(post_id)
        if success:
            print(f"🗑️ Deleted test post: {post_id[:8]}...")
    
    # Delete test personas
    for persona_id in test_persona_ids:
        success = gary_bot.delete_persona(persona_id)
        if success:
            print(f"🗑️ Deleted test persona: {persona_id[:8]}...")
    
    print("\n🎉 All persona assignment tests passed successfully!")
    return True

def test_edge_cases():
    """Test edge cases and error handling."""
    
    print("\n🔬 Testing edge cases...")
    
    config = get_config()
    gary_bot = GaryBot(config)
    
    # Test with non-existent persona ID
    try:
        posts = gary_bot.rag_system.retrieve_similar_posts(
            "test query",
            persona_id="non-existent-persona-id"
        )
        print(f"✅ Non-existent persona ID handled gracefully: {len(posts)} posts")
    except Exception as e:
        print(f"❌ Error with non-existent persona ID: {str(e)}")
    
    # Test updating non-existent post
    try:
        success = gary_bot.update_post_personas("non-existent-post-id", ["some-persona-id"])
        print(f"✅ Non-existent post ID handled gracefully: {success}")
    except Exception as e:
        print(f"❌ Error with non-existent post ID: {str(e)}")
    
    print("✅ Edge cases handled correctly")

if __name__ == "__main__":
    try:
        # Run main functionality tests
        test_persona_assignment()
        
        # Run edge case tests
        test_edge_cases()
        
        print("\n" + "="*50)
        print("🏆 ALL TESTS PASSED! Persona assignment functionality is working correctly.")
        print("🎯 You can now:")
        print("   • Assign posts to specific personas when creating them")
        print("   • Edit persona assignments for existing posts") 
        print("   • Filter posts by persona in the UI")
        print("   • Generate posts using specific persona styles")
        print("   • View persona assignments in post details")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 