#!/usr/bin/env python3
"""
Script to add guideline documents to Gary Bot's RAG system.
Supports parsing markdown files with sections and individual guidelines.
"""

import sys
import os
import re
from typing import List, Dict, Optional
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.rag_system import RAGSystem
from src.models import GuidelineDocument
from src.config import get_config

def parse_markdown_guidelines(file_path: str, document_type: str = "general") -> List[GuidelineDocument]:
    """
    Parse a markdown file and extract guidelines.
    
    Args:
        file_path: Path to the markdown file
        document_type: Type of document (e.g., "hooks", "templates", "style_guide")
    
    Returns:
        List of GuidelineDocument objects
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    guidelines = []
    
    # Split by main sections (## headers)
    sections = re.split(r'\n## ', content)
    
    for i, section in enumerate(sections):
        if i == 0:
            # First section might not have ## prefix
            if section.strip():
                section = section.lstrip('# \n')
        
        if not section.strip():
            continue
            
        lines = section.split('\n')
        section_title = lines[0].strip()
        section_content = '\n'.join(lines[1:]).strip()
        
        # If section has numbered/bulleted lists, split them into individual guidelines
        if re.search(r'^\d+\.', section_content, re.MULTILINE) or re.search(r'^[-*]', section_content, re.MULTILINE):
            # Extract individual items
            items = re.split(r'\n(?=\d+\.|\*|-)', section_content)
            
            for item in items:
                item = item.strip()
                if not item:
                    continue
                
                # Clean up numbering/bullets
                item = re.sub(r'^\d+\.\s*', '', item)
                item = re.sub(r'^[-*]\s*', '', item)
                
                if len(item) > 10:  # Only add substantial content
                    guideline = GuidelineDocument(
                        id="",  # Will be auto-generated
                        title=f"{section_title} - Item",
                        content=item,
                        document_type=document_type,
                        section=section_title.lower().replace(' ', '_'),
                        priority=1
                    )
                    guidelines.append(guideline)
        else:
            # Add entire section as one guideline
            if len(section_content) > 20:
                guideline = GuidelineDocument(
                    id="",  # Will be auto-generated
                    title=section_title,
                    content=section_content,
                    document_type=document_type,
                    section=section_title.lower().replace(' ', '_'),
                    priority=1
                )
                guidelines.append(guideline)
    
    return guidelines

def add_linkedin_hooks_guidelines(rag_system: RAGSystem) -> List[str]:
    """
    Add LinkedIn hooks and templates as guideline documents.
    
    Args:
        rag_system: RAG system instance
    
    Returns:
        List of added guideline IDs
    """
    
    # LinkedIn hooks for generating curiosity
    curiosity_hooks = [
        '"Need ideas for…" [e.g. B2B outbound sales]',
        '"Did you know that..." [e.g., a lot of growth marketers make this mistake]',
        '"Wondering how to..." [e.g., automatically contact people on LinkedIn]',
        '"This is one of the most fierce enemies of XYZ" [talk about a problem]',
        '"X Mistakes…"',
        '"X Tips…"',
        '"Are you ____ and not ____? Then this post is for you"',
        '"Do you think that _____ is out of reach?"',
        '"10 significant lies you\'re told about the world" → Reveal the truth',
        '"Doing _____ is like _____. Here\'s why 👇"',
        '"X ways to ____"',
        '"15 of the most useful X for Y" → Make the value simple and clear',
        '"Here are the 9 secrets to building an audience fast" → Show what\'s possible to do',
        '"7 genius marketing tactics to make you go viral:" → Educate. Use words like smart, genius, ambitious, and brilliant',
        '"The easiest way to make $9,000 every month." → Give a cheat code',
        '"It\'s hard to find good marketing stuff online. Here\'s my top 5" → Curate to make people\'s life easier',
        '"I don\'t have a degree, so I\'ve had to learn on my own" → Niche down so that people can identify',
        '"How to write a solid blog post in one hour." → Go bold and deliver the value, share the exact time frame',
        '"I was so impressed by X I thought I\'d share it." → Intrigue as if you discovered something crazy',
        'There are 2 types of [audience]:',
        'Quick tip to [do thing]:',
        'Quick hack to [do thing]:',
        '[advice] — here\'s how:',
        'Here\'s how you can [do a thing] for free:',
        '8 things that destroy [something your audience cares about]:',
        'Here are 4 lessons I learned the hard way:',
        'Here are 6 dead-simple ways to [do thing]:',
        'Here\'s how to [do thing] in 7 simple steps:',
        'How to [do thing] in 23.27 seconds:',
        'I tried [doing thing]. There were 5 weird results:',
        'These 5 traits are so underrated, yet they can skyrocket your career:'
    ]
    
    # Story starter hooks
    story_hooks = [
        '"I want to tell you a story how..." [e.g., lemlist achieved $1m in ARR]',
        '"Imagine you\'re..." [e.g., dealing with a 20% conversion drop]',
        '"It felt like a punch to the gut…" [share a lesson you learn the hard way]',
        '"I got fired."',
        '"I quit."',
        '"I turned down [x] dollars"',
        '"I lost everything."',
        '"I lost [x] dollars."',
        '"I gave up."',
        '"We were on the brink of failure."',
        '"My time was up."',
        '"My hands were shaking."',
        '"I couldn\'t believe it."',
        '"I wanted to cry."',
        '"There had to be another way."',
        '"I want to be honest for a second"',
        '"I have to talk about this."',
        '"They said no."',
        '"I never heard back from them."',
        '"They laughed at me."',
        '"It hurt."',
        '"It sucked."',
        '"I wanted it to be true."',
        '"I couldn\'t stop."',
        '"I broke down."',
        '"It was brutal."',
        '"Storytime... this is by far the craziest thing to ever happen"',
        '"You would not believe this"',
        '"I just gave my 2 weeks\' notice to quit my full-time job"',
        'I committed to [doing thing] [time] ago. Here are my results:'
    ]
    
    # Provocative hooks
    provocative_hooks = [
        '"You must have noticed it by now" [talk about a problem]',
        '"Someone has to say this"',
        '"Have you been here before?" [when you need feedback or when creating empathy]',
        '"I want to be real for a second."',
        '"It kills me to say this."',
        '"It hurts to say this."',
        '"I wish I didn\'t have to say this."',
        '"If you\'re a SaaS founder, you need to study Notion" → Niche down to make specific people comment',
        '"I stopped ____"',
        '"What do you wanna be when you grow up?" is one of the most useless questions → Create a "that\'s so true" moment',
        'Stop calling yourself a … if:',
        '[topic] is NOT about:',
        'Unpopular opinion: [share something controversial]'
    ]
    
    guidelines = []
    
    # Create guideline documents
    for hook in curiosity_hooks:
        guideline = GuidelineDocument(
            id="",
            title="Curiosity Hook",
            content=hook,
            document_type="hooks",
            section="curiosity",
            priority=2  # High priority for hooks
        )
        guidelines.append(guideline)
    
    for hook in story_hooks:
        guideline = GuidelineDocument(
            id="",
            title="Story Hook",
            content=hook,
            document_type="hooks",
            section="storytelling",
            priority=2
        )
        guidelines.append(guideline)
    
    for hook in provocative_hooks:
        guideline = GuidelineDocument(
            id="",
            title="Provocative Hook",
            content=hook,
            document_type="hooks",
            section="provocative",
            priority=2
        )
        guidelines.append(guideline)
    
    # Add Gary Lin specific style guidelines
    gary_style_guidelines = [
        GuidelineDocument(
            id="",
            title="Gary Lin Voice Characteristics",
            content="Use bold, humorous, confident but not arrogant tone. Be people-first, empathetic, genuine, witty, vulnerable, raw, relatable, and provocative without being negative.",
            document_type="style_guide",
            section="voice",
            priority=3  # Highest priority
        ),
        GuidelineDocument(
            id="",
            title="Gary Lin Content Types",
            content="Focus on founder philosophies, tough love advice, motivating rally cries, transparent reflections, and community-building content.",
            document_type="style_guide",
            section="content_types",
            priority=3
        ),
        GuidelineDocument(
            id="",
            title="Gary Lin Writing Style",
            content="Use storytelling, short paragraphs for readability, strategic emojis (not excessive), and 1-3 relevant hashtags. Keep it authentic and conversational.",
            document_type="style_guide",
            section="formatting",
            priority=3
        )
    ]
    
    guidelines.extend(gary_style_guidelines)
    
    # Add all guidelines to RAG system
    return rag_system.add_guidelines_batch(guidelines)

def main():
    """Main function to add guidelines to RAG system."""
    
    print("🔧 Adding guideline documents to Gary Bot RAG system...")
    
    # Initialize config and RAG system
    config = get_config()
    rag_system = RAGSystem(
        embedding_model=config.embedding_model_name
    )
    
    # Add built-in LinkedIn hooks and style guidelines
    print("📝 Adding LinkedIn hooks and Gary Lin style guidelines...")
    added_ids = add_linkedin_hooks_guidelines(rag_system)
    print(f"✅ Added {len(added_ids)} guideline documents")
    
    # Check if user provided a markdown file
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            print(f"📄 Parsing guidelines from {file_path}...")
            document_type = input("Enter document type (hooks/templates/style_guide/general): ").strip() or "general"
            
            guidelines = parse_markdown_guidelines(file_path, document_type)
            if guidelines:
                added_ids = rag_system.add_guidelines_batch(guidelines)
                print(f"✅ Added {len(added_ids)} guidelines from {file_path}")
            else:
                print("❌ No guidelines found in the file")
        else:
            print(f"❌ File not found: {file_path}")
    
    # Show current guidelines count
    all_guidelines = rag_system.list_all_guidelines()
    print(f"\n📊 Total guidelines in system: {len(all_guidelines)}")
    
    # Show breakdown by type
    type_counts = {}
    for guideline in all_guidelines:
        doc_type = guideline.document_type
        type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
    
    print("📋 Guidelines by type:")
    for doc_type, count in type_counts.items():
        print(f"   {doc_type}: {count}")
    
    print("\n🎉 Guidelines successfully added to Gary Bot!")
    print("💡 The bot will now use these guidelines when generating posts.")

if __name__ == "__main__":
    main() 