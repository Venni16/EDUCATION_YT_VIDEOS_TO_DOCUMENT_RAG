"""
Agentic RAG Pipeline (ReAct-style)
Orchestrates the full pipeline:
  Step 1 → Identify main topics from transcript overview
  Step 2 → For each topic: retrieve relevant chunks + generate section
  Step 3 → Generate abstract
  Step 4 → Generate key takeaways + conclusion
  Step 5 → Assemble final structured document
"""

import logging
from .vector_service import VectorStore
from .llm_service import call_llm, call_llm_for_list

logger = logging.getLogger(__name__)

MAX_SECTIONS = 5            # max sections to generate
RETRIEVAL_K = 5             # chunks to retrieve per topic
OVERVIEW_CHARS = 2000       # chars from start of transcript for topic identification


def _build_context(chunks: list[str], max_chars: int = 3000) -> str:
    """Join chunks into a single context string, respecting a char limit."""
    context = "\n\n".join(chunks)
    return context[:max_chars]


# ──────────────────────────────────────────
# TOOL 1 — Topic Identification
# ──────────────────────────────────────────
def tool_identify_topics(overview_text: str, title: str) -> list[str]:
    """
    ReAct Thought: "I need to identify the main topics covered in this video."
    Action: Call LLM with overview prompt.
    Observation: Get list of 4–5 topic strings.
    """
    logger.info("[AGENT] Tool: identify_topics")
    prompt = f"""You are an expert educator analyzing a YouTube video titled: "{title}"

Here is the beginning of the video transcript:
\"\"\"{overview_text[:OVERVIEW_CHARS]}\"\"\"

Task: Identify the {MAX_SECTIONS} most important topics or concepts covered in this video.
Return ONLY a numbered list of short topic names (3–6 words each).
Do not add explanations. Example format:
1. Introduction to Neural Networks
2. How Backpropagation Works
"""
    topics = call_llm_for_list(prompt, max_tokens=300)
    topics = topics[:MAX_SECTIONS]
    logger.info(f"[AGENT] Identified {len(topics)} topics: {topics}")
    return topics


# ──────────────────────────────────────────
# TOOL 2 — Section Generation
# ──────────────────────────────────────────
def tool_generate_section(topic: str, chunks: list[str], title: str) -> str:
    """
    ReAct Thought: "I need to write a detailed section about this topic."
    Action: Retrieve relevant chunks → call LLM to generate section.
    Observation: Markdown-formatted section text.
    """
    logger.info(f"[AGENT] Tool: generate_section → '{topic}'")
    context = _build_context(chunks)
    prompt = f"""You are writing a section of a professional educational document about the YouTube video: "{title}"

Section topic: {topic}

Relevant transcript excerpts:
\"\"\"{context}\"\"\"

Write a detailed, well-structured section for this topic. Use:
- A clear opening paragraph explaining the concept
- 2–4 bullet points with key details or examples
- A brief closing sentence

Use plain Markdown. Be educational and precise. No generic filler. Minimum 150 words.
"""
    return call_llm(prompt, max_tokens=700, temperature=0.4)


# ──────────────────────────────────────────
# TOOL 3 — Abstract Generation
# ──────────────────────────────────────────
def tool_generate_abstract(title: str, topics: list[str], overview_text: str) -> str:
    """generate a concise abstract / executive summary."""
    logger.info("[AGENT] Tool: generate_abstract")
    topics_str = "\n".join(f"- {t}" for t in topics)
    prompt = f"""You are writing an abstract for a professional document based on the YouTube video: "{title}"

Main topics covered:
{topics_str}

Transcript overview:
\"\"\"{overview_text[:1500]}\"\"\"

Write a concise abstract (2–3 paragraphs, ~150 words) summarizing:
1. What the video is about
2. The key concepts it covers
3. Who would benefit from watching it

Plain text only, no bullet points, no headers.
"""
    return call_llm(prompt, max_tokens=400, temperature=0.3)


# ──────────────────────────────────────────
# TOOL 4 — Key Takeaways
# ──────────────────────────────────────────
def tool_generate_takeaways(title: str, topics: list[str], vector_store: VectorStore) -> list[str]:
    """Generate 5–7 key takeaways from the video."""
    logger.info("[AGENT] Tool: generate_takeaways")
    chunks = vector_store.retrieve("most important lessons key takeaways", k=5)
    context = _build_context(chunks, max_chars=2000)
    topics_str = ", ".join(topics)
    prompt = f"""Based on the YouTube video "{title}" covering: {topics_str}

Relevant transcript excerpts:
\"\"\"{context}\"\"\"

List exactly 6 key takeaways a viewer should remember after watching this video.
Each takeaway should be a complete, actionable sentence (15–25 words).
Return ONLY a numbered list, no titles or explanations.
"""
    return call_llm_for_list(prompt, max_tokens=400)


# ──────────────────────────────────────────
# TOOL 5 — Conclusion
# ──────────────────────────────────────────
def tool_generate_conclusion(title: str, topics: list[str], abstract: str) -> str:
    """Generate a conclusion paragraph."""
    logger.info("[AGENT] Tool: generate_conclusion")
    topics_str = "\n".join(f"- {t}" for t in topics)
    prompt = f"""You are concluding a professional educational document for the video: "{title}"

Topics covered:
{topics_str}

Document abstract:
\"\"\"{abstract}\"\"\"

Write a strong conclusion paragraph (100–150 words) that:
- Summarizes the core learning outcomes
- Motivates the reader to apply the knowledge
- Ends with an inspiring or thought-provoking sentence

Plain text only, no headers.
"""
    return call_llm(prompt, max_tokens=350, temperature=0.5)


# ──────────────────────────────────────────
# MAIN AGENT PIPELINE
# ──────────────────────────────────────────
def run_agent_pipeline(
    title: str,
    chunks: list[str],
    vector_store: VectorStore,
) -> dict:
    """
    Full ReAct-style agentic pipeline.
    Returns a dict with all document components.
    """
    logger.info(f"[AGENT] Starting pipeline for: '{title}'")
    overview_text = _build_context(vector_store.get_overview_chunks(n=8), max_chars=3000)

    # Step 1 — Identify topics
    topics = tool_identify_topics(overview_text, title)
    if not topics:
        topics = ["Introduction", "Core Concepts", "Key Details", "Examples", "Summary"]

    # Step 2 — Generate each section
    sections = {}
    for topic in topics:
        relevant_chunks = vector_store.retrieve(topic, k=RETRIEVAL_K)
        section_content = tool_generate_section(topic, relevant_chunks, title)
        sections[topic] = section_content

    # Step 3 — Abstract
    abstract = tool_generate_abstract(title, topics, overview_text)

    # Step 4 — Key Takeaways
    takeaways = tool_generate_takeaways(title, topics, vector_store)

    # Step 5 — Conclusion
    conclusion = tool_generate_conclusion(title, topics, abstract)

    logger.info("[AGENT] Pipeline complete.")
    return {
        "title": title,
        "topics": topics,
        "abstract": abstract,
        "sections": sections,       # dict: { topic_name: content }
        "takeaways": takeaways,     # list of strings
        "conclusion": conclusion,
    }
