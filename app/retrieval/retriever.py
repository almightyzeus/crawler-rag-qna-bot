from typing import List, Dict, Any, Tuple
import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
from app.embeddings.embedder import embed_texts
from app.vector_store.store import query_embeddings, get_collection_stats

load_dotenv()

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI()

def retrieve_relevant_chunks(question: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Embed the question and retrieve the most relevant chunks from the vector store.

    Returns a list of dicts with:
    - 'id': Document ID
    - 'text': Chunk text
    - 'metadata': Source URL, title, chunk_id
    - 'distance': Similarity distance (lower is better)
    """
    if not question:
        logger.warning("Empty question provided")
        return []

    try:
        logger.info(f"Retrieving {top_k} chunks for query: {question[:50]}...")
        embeddings = embed_texts([question])
        query_embedding = embeddings[0]

        raw = query_embeddings(query_embedding, n_results=top_k)

        results: List[Dict[str, Any]] = []
        documents = raw.get("documents", [[]])[0]
        metadatas = raw.get("metadatas", [[]])[0]
        distances = raw.get("distances", [[]])[0] if raw.get("distances") else [None] * len(documents)
        ids = raw.get("ids", [[]])[0] if raw.get("ids") else [None] * len(documents)

        for doc_id, doc, meta, dist in zip(ids, documents, metadatas, distances):
            results.append(
                {
                    "id": doc_id,
                    "text": doc,
                    "metadata": meta,
                    "distance": dist,
                    "similarity": 1 - dist if dist else 0,  # Convert distance to similarity
                }
            )
        
        logger.info(f"✓ Retrieved {len(results)} relevant chunks")
        return results
    except Exception as e:
        logger.error(f"Error retrieving chunks: {e}")
        return []


def generate_answer_from_context(
    question: str,
    chunks: List[str],
    context_metadata: List[Dict[str, Any]] = None
) -> Tuple[str, List[str]]:
    """Generate an answer using OpenAI LLM with retrieved context.
    
    Args:
        question: The user's question
        chunks: List of relevant text chunks
        context_metadata: Metadata for each chunk (including source URLs)
    
    Returns:
        Tuple of (answer, source_urls)
    """
    if not chunks:
        logger.warning("No chunks provided for answer generation")
        return "I couldn't find any relevant information in the knowledge base.", []
    
    # Extract unique source URLs
    source_urls = set()
    if context_metadata:
        for meta in context_metadata:
            if isinstance(meta, dict) and "source_url" in meta:
                source_urls.add(meta["source_url"])
    
    # Prepare context string
    context = "\n\n".join(chunks)
    
    # Create the prompt
    system_prompt = """You are a helpful assistant that answers questions based only on the provided context. 
    
Rules:
1. Answer questions using ONLY the information provided in the context below
2. If the context doesn't contain information needed to answer the question, say "I don't have enough information to answer that."
3. Be concise and clear in your answers
4. If you reference specific information, mention where it comes from if relevant
5. Do not make up information or use knowledge outside the provided context"""
    
    user_message = f"""Context:
{context}

Question: {question}

Please answer the question based only on the context provided above."""
    
    try:
        logger.info(f"Generating answer for question: {question[:50]}...")
        logger.info(f"Using {len(chunks)} chunks as context")
        
        response = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,  # Lower temperature for more factual responses
            max_tokens=1000,
        )
        
        answer = response.choices[0].message.content
        logger.info(f"✓ Answer generated successfully")
        
        return answer, list(source_urls)
    
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        # Fallback to simple concatenation
        return "\n\n".join(chunks), list(source_urls)


def answer_question(
    question: str,
    top_k: int = 5,
    use_llm: bool = True
) -> Dict[str, Any]:
    """Complete retrieval + answer generation pipeline.
    
    Args:
        question: The user's question
        top_k: Number of chunks to retrieve
        use_llm: Whether to use LLM for answer generation (True) or return raw chunks (False)
    
    Returns:
        Dictionary with:
        - 'question': The original question
        - 'answer': Generated answer (or concatenated chunks if use_llm=False)
        - 'sources': List of source URLs
        - 'retrieved_chunks': List of relevant chunks with metadata
        - 'num_chunks': Number of chunks retrieved
    """
    if not question:
        logger.warning("Empty question provided")
        return {
            "question": question,
            "answer": "Please provide a valid question.",
            "sources": [],
            "retrieved_chunks": [],
            "num_chunks": 0,
            "error": "Empty question"
        }
    
    try:
        # Step 1: Retrieve relevant chunks
        retrieved = retrieve_relevant_chunks(question, top_k=top_k)
        
        if not retrieved:
            logger.warning(f"No chunks retrieved for question: {question}")
            return {
                "question": question,
                "answer": "I couldn't find any relevant information in the knowledge base.",
                "sources": [],
                "retrieved_chunks": [],
                "num_chunks": 0,
                "error": "No relevant chunks found"
            }
        
        # Extract chunks and metadata
        chunks = [r["text"] for r in retrieved]
        metadata = [r["metadata"] for r in retrieved]
        
        # Step 2: Generate answer
        if use_llm:
            answer, sources = generate_answer_from_context(question, chunks, metadata)
        else:
            answer = "\n\n".join(chunks)
            sources = list(set(m.get("source_url") for m in metadata if m and "source_url" in m))
        
        # Format retrieved chunks for response
        formatted_chunks = []
        for idx, result in enumerate(retrieved, 1):
            formatted_chunks.append({
                "rank": idx,
                "similarity": result.get("similarity", 0),
                "source_url": result.get("metadata", {}).get("source_url", ""),
                "title": result.get("metadata", {}).get("title", ""),
                "text": result.get("text", "")
            })
        
        logger.info(f"✓ Complete answer generation successful")
        
        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "retrieved_chunks": formatted_chunks,
            "num_chunks": len(chunks)
        }
    
    except Exception as e:
        logger.error(f"Error in answer_question: {e}")
        return {
            "question": question,
            "answer": "An error occurred while processing your question.",
            "sources": [],
            "retrieved_chunks": [],
            "num_chunks": 0,
            "error": str(e)
        }


def get_knowledge_base_stats() -> Dict[str, Any]:
    """Get statistics about the current knowledge base."""
    return get_collection_stats()
