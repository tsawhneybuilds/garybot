# 📋 Guidelines Setup Guide for Gary Bot

This guide shows you how to add guideline documents to Gary Bot's RAG system to improve post generation quality.

## 🎯 What Are Guidelines?

Guidelines are documents that help Gary Bot understand:
- **Writing hooks** (curiosity, storytelling, provocative)
- **Content templates** (structures, formats)
- **Style guides** (Gary's voice, tone, formatting)
- **General rules** (best practices, do's and don'ts)

## 🚀 Quick Setup

### Option 1: Use Built-in LinkedIn Hooks & Style Guide
```bash
# Run the guidelines script to add pre-built hooks
python add_guidelines.py
```

### Option 2: Web Interface
1. Open Gary Bot web app
2. Go to "⚙️ Manage RAG" → "📋 Guidelines" tab
3. Click "📚 Add LinkedIn Hooks & Style Guide"

## 📄 Adding Custom Guidelines

### Method 1: Upload Markdown File (Web Interface)
1. Create a markdown file with your guidelines
2. Upload via "⚙️ Manage RAG" → "📋 Guidelines" → "Upload Guidelines"
3. Specify document type (hooks/templates/style_guide/general)

### Method 2: Add Individual Guidelines (Web Interface)
Use the "➕ Add Individual Guideline" form to add one guideline at a time.

### Method 3: Script with Custom File
```bash
# Add guidelines from your markdown file
python add_guidelines.py your_guidelines.md
```

## 📝 Guideline Document Types

### 1. **hooks** - Writing Hooks & Openers
Examples:
- `"Need ideas for…" [topic]`
- `"I want to tell you a story about..."`
- `"Someone has to say this"`

### 2. **templates** - Content Structures
Examples:
- `Problem → Solution → Call to Action`
- `Story → Lesson → Application`
- `Question → Answer → Insight`

### 3. **style_guide** - Voice & Formatting
Examples:
- `Use bold, humorous, confident tone`
- `Keep paragraphs short for readability`
- `Use 1-3 relevant hashtags maximum`

### 4. **general** - Best Practices
Examples:
- `Always include a call to action`
- `Make the first line compelling`
- `Use numbers and specific details`

## 🎨 Guideline Priority Levels

- **Priority 3 (High)**: Core style rules, Gary's voice characteristics
- **Priority 2 (Medium)**: Writing hooks, proven templates
- **Priority 1 (Low)**: General tips, optional guidelines

Higher priority guidelines are retrieved first during post generation.

## 📋 Example Markdown File Format

```markdown
# LinkedIn Writing Guidelines

## Curiosity Hooks

1. "Need ideas for [topic]?"
2. "Did you know that [surprising fact]?"
3. "Wondering how to [solve problem]?"

## Story Starters

1. "I want to tell you a story about..."
2. "Imagine you're [scenario]..."
3. "It felt like a punch to the gut..."

## Gary Lin Style

- Use bold, confident but not arrogant tone
- Be people-first and empathetic
- Include vulnerability and authenticity
- Keep paragraphs short
- Use strategic emojis (not excessive)
```

## 🔧 How Guidelines Work in Post Generation

1. **User uploads transcript**
2. **Gary Bot identifies viral snippets**
3. **System retrieves relevant guidelines** based on content similarity
4. **Content generator uses both**:
   - Similar successful posts (RAG)
   - Relevant guidelines (hooks, templates, style)
5. **Generated post follows guidelines** while maintaining Gary's voice

## 📊 Managing Guidelines

### View Current Guidelines
- Web interface: "⚙️ Manage RAG" → "📋 Guidelines"
- Shows breakdown by type, priority, and content

### Update Guidelines
- Add new ones through web interface or script
- Delete outdated guidelines individually
- Bulk operations available

### Best Practices
1. **Start with built-ins**: Use the LinkedIn hooks & style guide
2. **Add gradually**: Test with a few custom guidelines first
3. **Monitor results**: See if generated posts improve
4. **Keep organized**: Use clear sections and priorities
5. **Update regularly**: Add new patterns as you discover them

## 🎯 Tips for Effective Guidelines

### Writing Good Hook Guidelines
```markdown
# Good
"Need ideas for [specific topic]?" - Creates curiosity and targets audience

# Better  
"Need ideas for B2B outbound sales? Here are 7 tactics that doubled my response rate"
```

### Creating Useful Templates
```markdown
# Structure Template
1. Hook (question/bold statement)
2. Story/Example (personal experience)
3. Lesson (what you learned)
4. Application (how others can use it)
5. Call to Action (engage audience)
```

### Style Guide Examples
```markdown
# Gary Lin Voice Characteristics
- Bold and confident, but never arrogant
- Humorous and witty, but always authentic
- Vulnerable and raw when sharing failures
- People-first approach to business advice
- Empathetic to founder struggles
```

## 🚀 Advanced Usage

### Programmatic Addition
```python
from src.rag_system import RAGSystem
from src.models import GuidelineDocument

rag_system = RAGSystem()

guideline = GuidelineDocument(
    id="",
    title="Curiosity Hook Template",
    content='"Need ideas for [topic]?" - Replace [topic] with specific audience need',
    document_type="hooks",
    section="curiosity",
    priority=2
)

rag_system.add_guideline(guideline)
```

### Batch Import
```python
# Add multiple guidelines at once
guidelines = [guideline1, guideline2, guideline3]
rag_system.add_guidelines_batch(guidelines)
```

## 📈 Measuring Success

After adding guidelines, monitor:
1. **Generated post quality** - Are they more engaging?
2. **Hook effectiveness** - Do posts start stronger?
3. **Voice consistency** - Do posts sound more like Gary?
4. **User feedback** - Are people happy with generated posts?

## 🛠️ Troubleshooting

### Guidelines Not Being Used
- Check priority levels (higher = more likely to be retrieved)
- Ensure content is substantial (>20 characters)
- Verify document type matches use case

### Too Many Guidelines
- Focus on highest priority ones
- Delete outdated or redundant guidelines
- Organize by clear sections

### Poor Quality Guidelines
- Be specific rather than generic
- Include examples and context
- Test with actual post generation

---

🎉 **You're all set!** Your Gary Bot will now use these guidelines to generate more targeted, engaging LinkedIn posts that sound authentically like Gary Lin.

For questions or issues, check the web interface logs or run the scripts with verbose output. 