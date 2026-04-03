"""
Text Processing Service
Cleans raw transcript text and splits it into overlapping chunks
for embedding and retrieval.
"""

import re
import logging

logger = logging.getLogger(__name__)

# Chunk configuration
CHUNK_SIZE = 500        # characters per chunk
CHUNK_OVERLAP = 80      # overlap between consecutive chunks


def clean_transcript(text: str) -> str:
    """
    Clean raw transcript text:
    - Remove repeated whitespace/newlines
    - Remove common filler words (lightly)
    - Normalize punctuation
    """
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Remove music/sound notation artifacts
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\(.*?\)", "", text)

    # Remove repeated punctuation
    text = re.sub(r"\.{2,}", ".", text)
    text = re.sub(r"\?{2,}", "?", text)

    # Normalize apostrophes
    text = text.replace("\u2019", "'").replace("\u2018", "'")

    # Light filler word removal (only standalone)
    fillers = [r"\bum\b", r"\buh\b", r"\blike\b(?=\s+\b(I|we|so|and)\b)", r"\byou know\b"]
    for filler in fillers:
        text = re.sub(filler, "", text, flags=re.IGNORECASE)

    # Re-collapse whitespace after removals
    text = re.sub(r"\s+", " ", text).strip()

    return text


def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Split text into overlapping character-level chunks.
    Returns a list of chunk strings.
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)

        # Try to end at a sentence boundary (. ? !)
        if end < text_length:
            for sep in [".", "?", "!", "\n"]:
                last_sep = text.rfind(sep, start, end)
                if last_sep > start + (chunk_size // 2):
                    end = last_sep + 1
                    break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Critical: Break if we reached the end of the text
        if end >= text_length:
            break

        # Advance start, ensuring we move forward
        new_start = end - overlap
        if new_start <= start:
            start = end 
        else:
            start = new_start

    logger.info(f"Split transcript into {len(chunks)} chunks (size={chunk_size}, overlap={overlap})")
    return chunks


def process_transcript(transcript: str) -> list[str]:
    """
    Full processing pipeline:
    1. Clean transcript
    2. Split into chunks
    Returns list of text chunks ready for embedding.
    """
    cleaned = clean_transcript(transcript)
    logger.info(f"Cleaned transcript: {len(cleaned)} chars")

    chunks = split_into_chunks(cleaned)
    return chunks
