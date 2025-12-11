from typing import List, Dict
import uuid
import logging

logger = logging.getLogger(__name__)

def simple_chunk_text(text: str, max_chars: int = 800) -> List[str]:
    """Naive text chunker based on character length.

    For real-world RAG, you'd want:
    - Token-based chunking
    - Overlapping windows
    - Split by paragraphs / headings

    For now this keeps it simple and deterministic.
    """
    if not text:
        return []

    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end
    return chunks


def chunk_text_with_overlap(
    text: str,
    max_chars: int = 800,
    overlap_chars: int = 100
) -> List[str]:
    """Split text into chunks with overlap for better context.

    Args:
        text: Text to chunk
        max_chars: Maximum characters per chunk
        overlap_chars: Number of characters to overlap between chunks

    Returns:
        List of chunks with overlap
    """
    if not text or max_chars <= 0:
        return []

    chunks: List[str] = []
    start = 0
    
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunk = text[start:end].strip()
        
        if chunk:
            chunks.append(chunk)
        
        # Move start position for next chunk
        # If this is not the last chunk, move by (max_chars - overlap)
        if end < len(text):
            start = max(start + 1, end - overlap_chars)
        else:
            break
    
    return chunks


def create_chunks_with_metadata(
    text: str,
    url: str,
    title: str,
    max_chars: int = 800,
    overlap_chars: int = 100
) -> List[Dict]:
    """Create chunks with metadata (chunk_id, url, title, text).

    Args:
        text: Text to chunk
        url: Source URL
        title: Page title
        max_chars: Maximum characters per chunk
        overlap_chars: Characters to overlap between chunks

    Returns:
        List of dictionaries with chunk_id, url, title, and chunk_text
    """
    chunks = chunk_text_with_overlap(text, max_chars, overlap_chars)
    
    chunk_objects = []
    for idx, chunk in enumerate(chunks, 1):
        chunk_id = str(uuid.uuid4())
        
        chunk_obj = {
            "chunk_id": chunk_id,
            "url": url,
            "title": title,
            "chunk_text": chunk,
            "chunk_index": idx,
            "total_chunks": len(chunks),
            "char_length": len(chunk)
        }
        chunk_objects.append(chunk_obj)
    
    return chunk_objects
