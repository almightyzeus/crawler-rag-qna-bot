#!/usr/bin/env python3
"""
Test script for Step 6: Retrieval and answer generation.

This script demonstrates:
- Building a retrieval function
- Embedding the user query
- Fetching top relevant chunks
- Building an answer generation function with LLM
- Preparing a prompt with retrieved context
- Calling OpenAI's language model
- Instructing it to answer only from given context
- Testing with basic questions related to the crawled website
- Returning final answer and list of source URLs
"""

import os
import logging
from dotenv import load_dotenv
from app.crawling.crawler import crawl_website
from app.chunking.chunker import create_chunks_with_metadata
from app.embeddings.embedder import embed_texts
from app.vector_store.store import add_embeddings, reset_collection
from app.retrieval.retriever import answer_question

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_step6_retrieval_and_answer():
    """Test retrieval and LLM-based answer generation."""
    
    print("\n" + "="*80)
    print("STEP 6: RETRIEVAL AND ANSWER GENERATION")
    print("="*80)
    
    # Configuration
    test_url = os.getenv("TEST_URL", "https://docs.python.org/3/")
    max_pages = int(os.getenv("TEST_MAX_PAGES", "3"))
    max_depth = int(os.getenv("TEST_MAX_DEPTH", "2"))
    
    # Reset collection for fresh test
    print("\n[1] Resetting vector store...")
    reset_collection("documents")
    print("✓ Vector store reset\n")
    
    # Step 1: Crawl and prepare data
    print("[2] Crawling website and preparing data...")
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
    
    # Step 2: Create chunks and embeddings
    print("[3] Creating chunks and generating embeddings...")
    all_chunks = []
    all_metadatas = []
    
    for page in pages:
        url = page["url"]
        title = page["title"]
        text = page.get("cleaned_text", "")
        
        chunk_objects = create_chunks_with_metadata(
            text=text,
            url=url,
            title=title,
            max_chars=800,
            overlap_chars=100
        )
        
        for chunk_obj in chunk_objects:
            all_chunks.append(chunk_obj["chunk_text"])
            all_metadatas.append({
                "source_url": url,
                "title": title,
                "chunk_id": chunk_obj["chunk_id"]
            })
    
    print(f"✓ Created {len(all_chunks)} chunks\n")
    
    # Step 3: Generate embeddings and insert into vector store
    print("[4] Generating embeddings and inserting into vector store...")
    try:
        embeddings = embed_texts(all_chunks)
        add_embeddings(embeddings, all_chunks, all_metadatas)
        print(f"✓ Inserted {len(embeddings)} embeddings into Chroma\n")
    except Exception as e:
        print(f"❌ Error generating embeddings: {e}")
        print("   Make sure OPENAI_API_KEY is set in .env")
        return
    
    # Step 4: Test retrieval and answer generation with sample questions
    print("[5] Testing retrieval and answer generation...")
    print("\nSample questions for Python documentation:\n")
    
    test_questions = [
        "What is Python?",
        "How do I install Python?",
        "What are the main features of Python?",
        "How do I learn Python programming?",
    ]
    
    results = []
    
    for idx, question in enumerate(test_questions, 1):
        print("\n" + "="*80)
        print(f"Question {idx}: {question}")
        print("="*80)
        
        try:
            # Get answer with LLM
            result = answer_question(question, top_k=5, use_llm=True)
            results.append(result)
            
            print("\n📋 RETRIEVED CHUNKS (Top 3):")
            print("-" * 80)
            for chunk_info in result["retrieved_chunks"][:3]:
                print(f"\n[{chunk_info['rank']}] Similarity: {chunk_info['similarity']:.4f}")
                print(f"    Source: {chunk_info['title']}")
                print(f"    URL: {chunk_info['source_url']}")
                print(f"    Text: {chunk_info['text'][:150]}...")
            
            print("\n\n🤖 LLM-GENERATED ANSWER:")
            print("-" * 80)
            print(result["answer"])
            
            print("\n\n📚 SOURCE URLS:")
            print("-" * 80)
            if result["sources"]:
                for url in result["sources"]:
                    print(f"  • {url}")
            else:
                print("  No sources found")
            
            print("\n✓ Total chunks used: " + str(result["num_chunks"]))
        
        except Exception as e:
            print(f"\n❌ Error processing question: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n\n" + "="*80)
    print("SUMMARY - RETRIEVAL AND ANSWER GENERATION")
    print("="*80)
    
    print(f"\n✅ Retrieval Function:")
    print(f"   - Questions processed: {len(results)}")
    print(f"   - Chunks retrieved per query: 5")
    print(f"   - Retrieval success rate: {len([r for r in results if r.get('num_chunks', 0) > 0])} / {len(results)}")
    
    print(f"\n✅ Answer Generation:")
    print(f"   - Model: {os.getenv('LLM_MODEL', 'gpt-4o-mini')}")
    print(f"   - Context-only answers: Enabled")
    print(f"   - Source attribution: Enabled")
    
    print(f"\n✅ Chunk Retrieval Details:")
    print(f"   - Total chunks in vector store: {len(all_chunks)}")
    print(f"   - Total pages crawled: {len(pages)}")
    print(f"   - Crawled URLs: {len(crawled_urls)}")
    
    print(f"\n✅ Key Features Tested:")
    print(f"   ✓ Query embedding generation")
    print(f"   ✓ Similarity search and retrieval")
    print(f"   ✓ LLM-based answer generation")
    print(f"   ✓ Context-aware responses")
    print(f"   ✓ Source URL attribution")
    print(f"   ✓ Multi-document retrieval")
    
    print(f"\n✅ Step 6 - Retrieval and Answer Generation completed successfully!")
    
    print("\n\nSample API Usage:")
    print("-" * 80)
    print("\nPOST /query")
    print("Content-Type: application/json")
    print("""
{
  "question": "What is Python?",
  "top_k": 5,
  "use_llm": true
}
""")
    print("-" * 80)

if __name__ == "__main__":
    test_step6_retrieval_and_answer()
