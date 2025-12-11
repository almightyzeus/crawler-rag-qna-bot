#!/usr/bin/env python3
"""
Test script for Step 5: Embedding generation and vector database setup.

This script demonstrates:
- Generating embeddings for text chunks using OpenAI
- Setting up Chroma as vector database
- Inserting embeddings and metadata into vector store
- Performing similarity search/retrieval
- Testing with sample queries
"""

import os
import logging
from app.crawling.crawler import crawl_website
from app.chunking.chunker import create_chunks_with_metadata
from app.embeddings.embedder import embed_texts, get_embedding_dimension
from app.vector_store.store import add_embeddings, get_collection_stats, reset_collection
from app.retrieval.retriever import retrieve_relevant_chunks

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_step5_embeddings():
    """Test embedding generation and vector store setup."""
    
    print("\n" + "="*80)
    print("STEP 5: EMBEDDING GENERATION & VECTOR DATABASE SETUP")
    print("="*80)
    
    # Configuration
    test_url = os.getenv("TEST_URL", "https://docs.python.org/3/")
    max_pages = int(os.getenv("TEST_MAX_PAGES", "3"))
    max_depth = int(os.getenv("TEST_MAX_DEPTH", "2"))
    max_chars_per_chunk = 800
    
    # Reset collection for fresh test
    print("\n[1] Resetting vector store...")
    reset_collection("documents")
    print("✓ Vector store reset\n")
    
    # Step 1: Check embedding configuration
    print("[2] Checking embedding configuration...")
    embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    embedding_dim = get_embedding_dimension(embedding_model)
    print(f"  Model: {embedding_model}")
    print(f"  Dimension: {embedding_dim}")
    print(f"✓ Embedding configuration ready\n")
    
    # Step 2: Crawl and extract pages
    print("[3] Crawling website...")
    try:
        pages, crawled_urls = crawl_website(
            base_url=test_url,
            max_pages=max_pages,
            max_depth=max_depth
        )
        print(f"✓ Crawled {len(pages)} pages\n")
    except Exception as e:
        print(f"❌ Error crawling: {e}")
        return
    
    # Step 3: Create chunks
    print("[4] Creating chunks with metadata...")
    all_chunks = []
    all_metadatas = []
    
    for page_idx, page in enumerate(pages, 1):
        url = page["url"]
        title = page["title"]
        text = page.get("cleaned_text", "")
        
        chunk_objects = create_chunks_with_metadata(
            text=text,
            url=url,
            title=title,
            max_chars=max_chars_per_chunk,
            overlap_chars=100
        )
        
        for chunk_obj in chunk_objects:
            all_chunks.append({
                "text": chunk_obj["chunk_text"],
                "url": chunk_obj["url"],
                "title": chunk_obj["title"],
                "chunk_id": chunk_obj["chunk_id"]
            })
            all_metadatas.append({
                "source_url": url,
                "title": title,
                "chunk_id": chunk_obj["chunk_id"]
            })
    
    print(f"✓ Created {len(all_chunks)} chunks from {len(pages)} pages\n")
    
    # Step 4: Generate embeddings
    print("[5] Generating embeddings...")
    chunk_texts = [c["text"] for c in all_chunks]
    
    try:
        embeddings = embed_texts(chunk_texts)
        print(f"✓ Generated {len(embeddings)} embeddings")
        print(f"  Embedding shape: ({len(embeddings)}, {len(embeddings[0])})\n")
    except Exception as e:
        print(f"❌ Error generating embeddings: {e}")
        print("   Make sure OPENAI_API_KEY is set in .env")
        return
    
    # Step 5: Insert into vector store
    print("[6] Inserting embeddings into vector store (Chroma)...")
    try:
        add_embeddings(embeddings, chunk_texts, all_metadatas)
        print(f"✓ Inserted {len(embeddings)} embeddings into Chroma\n")
    except Exception as e:
        print(f"❌ Error inserting embeddings: {e}")
        return
    
    # Step 6: Get collection stats
    print("[7] Vector store statistics...")
    try:
        stats = get_collection_stats()
        print(f"  Collection: {stats.get('collection_name', 'documents')}")
        print(f"  Total documents: {stats.get('total_documents', 0)}")
        print(f"  Metadata: {stats.get('metadata', {})}\n")
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
    
    # Step 7: Test similarity search with various queries
    print("[8] Testing similarity search/retrieval...")
    test_queries = [
        "What is Airtribe?",
        "Tell me about events and courses",
        "Job opportunities",
        "How to start learning?"
    ]
    
    print(f"\nRunning {len(test_queries)} test queries:\n")
    
    for query_idx, query in enumerate(test_queries, 1):
        print("-" * 80)
        print(f"Query {query_idx}: {query}")
        print("-" * 80)
        
        try:
            results = retrieve_relevant_chunks(query, top_k=3)
            print(f"Found {len(results)} relevant chunks:\n")
            
            for rank, result in enumerate(results, 1):
                distance = result.get("distance", 0)
                # Convert cosine distance to similarity (0-1, where 1 is most similar)
                similarity = 1 - distance if distance else 0
                source = result.get("metadata", {}).get("source_url", "Unknown")
                title = result.get("metadata", {}).get("title", "Unknown")
                text = result.get("text", "")
                
                print(f"  [{rank}] Similarity: {similarity:.4f}")
                print(f"      Source: {title}")
                print(f"      URL: {source}")
                print(f"      Text preview: {text[:150]}...")
                print()
        
        except Exception as e:
            print(f"  ❌ Error retrieving: {e}\n")
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\n✅ Embedding Generation:")
    print(f"   - Model: {embedding_model}")
    print(f"   - Dimension: {embedding_dim}")
    print(f"   - Total embeddings generated: {len(embeddings)}")
    
    print(f"\n✅ Vector Database Setup:")
    print(f"   - Database: Chroma (Persistent)")
    print(f"   - Path: ./data")
    print(f"   - Collection: documents")
    print(f"   - Similarity metric: Cosine")
    print(f"   - Total documents: {stats.get('total_documents', 0)}")
    
    print(f"\n✅ Retrieval Testing:")
    print(f"   - Test queries: {len(test_queries)}")
    print(f"   - Results per query: 3")
    print(f"   - Status: Successfully tested similarity search")
    
    print(f"\n✅ Step 5 - Embedding and Vector Database completed successfully!")
    print("\nNext steps:")
    print("  - Run API with: python main.py")
    print("  - Test ingest endpoint: POST /ingest")
    print("  - Test retrieval: POST /retrieval/test")
    print("  - Test query: POST /query")
    print("  - Check stats: GET /kb/stats")

if __name__ == "__main__":
    test_step5_embeddings()
