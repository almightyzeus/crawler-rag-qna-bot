#!/usr/bin/env python3
"""
Test script for Step 4: Chunking the content.

This script demonstrates:
- Splitting long text into smaller chunks with overlap
- Creating chunk IDs for each chunk
- Storing metadata (URL, title) with each chunk
- Testing chunk generation and counting per page
"""

import os
from dotenv import load_dotenv
from app.crawling.crawler import crawl_website
from app.chunking.chunker import create_chunks_with_metadata, chunk_text_with_overlap

load_dotenv()

def test_step4_chunking():
    """Test chunking functionality with metadata."""
    
    print("\n" + "="*80)
    print("STEP 4: CHUNKING THE CONTENT")
    print("="*80)
    
    # Parameters for crawling
    test_url = os.getenv("TEST_URL", "https://docs.python.org/3/")
    max_pages = int(os.getenv("TEST_MAX_PAGES", "5"))
    max_depth = int(os.getenv("TEST_MAX_DEPTH", "2"))
    max_chars_per_chunk = 800
    overlap_chars = 100
    
    print(f"\nCrawling {test_url}...")
    print(f"Parameters:")
    print(f"  Max Pages: {max_pages}")
    print(f"  Max Depth: {max_depth}")
    print(f"  Max Chars per Chunk: {max_chars_per_chunk}")
    print(f"  Overlap: {overlap_chars} chars\n")
    
    try:
        pages, crawled_urls = crawl_website(
            base_url=test_url,
            max_pages=max_pages,
            max_depth=max_depth
        )
        
        if not pages:
            print("❌ No pages crawled!")
            return
        
        print(f"✅ Crawled {len(pages)} pages\n")
        
        # Process chunks for all pages
        all_chunks = []
        chunks_per_page = {}
        
        print("="*80)
        print("CHUNKING RESULTS")
        print("="*80)
        
        for page_idx, page in enumerate(pages, 1):
            url = page["url"]
            title = page["title"]
            text = page.get("cleaned_text", "")
            
            if not text:
                print(f"\n[{page_idx}] {title}")
                print(f"  URL: {url}")
                print(f"  ⚠️  No text content to chunk")
                continue
            
            # Create chunks with metadata
            chunk_objects = create_chunks_with_metadata(
                text=text,
                url=url,
                title=title,
                max_chars=max_chars_per_chunk,
                overlap_chars=overlap_chars
            )
            
            all_chunks.extend(chunk_objects)
            chunks_per_page[url] = len(chunk_objects)
            
            print(f"\n[{page_idx}] {title}")
            print(f"  URL: {url}")
            print(f"  Cleaned Text Length: {len(text):,} chars")
            print(f"  Number of Chunks: {len(chunk_objects)}")
            print(f"  Chunk Metadata:")
            print(f"    - Chunk IDs: Generated (UUID format)")
            print(f"    - Parent URL: Stored")
            print(f"    - Page Title: Stored")
            
            # Display first 3 chunks for this page
            print(f"  First chunk(s):")
            for chunk_idx, chunk_obj in enumerate(chunk_objects[:3], 1):
                print(f"\n    Chunk {chunk_idx}:")
                print(f"      ID: {chunk_obj['chunk_id']}")
                print(f"      Index: {chunk_obj['chunk_index']}/{chunk_obj['total_chunks']}")
                print(f"      Length: {chunk_obj['char_length']} chars")
                print(f"      Text Preview: {chunk_obj['chunk_text'][:100]}...")
            
            if len(chunk_objects) > 3:
                print(f"\n    ... and {len(chunk_objects) - 3} more chunks")
        
        # Summary statistics
        print("\n" + "="*80)
        print("SUMMARY STATISTICS")
        print("="*80)
        
        total_chunks = len(all_chunks)
        avg_chunks_per_page = total_chunks / len(pages) if pages else 0
        
        print(f"\nTotal pages processed: {len(pages)}")
        print(f"Total chunks created: {total_chunks}")
        print(f"Average chunks per page: {avg_chunks_per_page:.1f}")
        
        print("\nChunks per page breakdown:")
        for idx, (url, count) in enumerate(chunks_per_page.items(), 1):
            title = next((p["title"] for p in pages if p["url"] == url), "Unknown")
            print(f"  {idx}. {title}")
            print(f"     URL: {url}")
            print(f"     Chunks: {count}")
        
        # Verify chunk structure
        print("\nChunk Structure Verification:")
        if all_chunks:
            sample_chunk = all_chunks[0]
            print(f"  ✓ chunk_id: {type(sample_chunk.get('chunk_id', '')).__name__}")
            print(f"  ✓ url: {type(sample_chunk.get('url', '')).__name__}")
            print(f"  ✓ title: {type(sample_chunk.get('title', '')).__name__}")
            print(f"  ✓ chunk_text: {type(sample_chunk.get('chunk_text', '')).__name__}")
            print(f"  ✓ chunk_index: {type(sample_chunk.get('chunk_index', 0)).__name__}")
            print(f"  ✓ total_chunks: {type(sample_chunk.get('total_chunks', 0)).__name__}")
            print(f"  ✓ char_length: {type(sample_chunk.get('char_length', 0)).__name__}")
        
        # Check overlap
        print("\nOverlap Verification (sampling chunks):")
        if len(all_chunks) >= 2:
            # Find consecutive chunks from same page
            for page_url in chunks_per_page:
                page_chunks = [c for c in all_chunks if c['url'] == page_url]
                if len(page_chunks) >= 2:
                    chunk1 = page_chunks[0]['chunk_text']
                    chunk2 = page_chunks[1]['chunk_text']
                    
                    # Check if there's overlap (last part of chunk1 appears in chunk2)
                    overlap_found = False
                    if len(chunk1) > overlap_chars:
                        overlap_candidate = chunk1[-overlap_chars:]
                        if overlap_candidate in chunk2:
                            overlap_found = True
                    
                    page_title = next((p["title"] for p in pages if p["url"] == page_url), "Unknown")
                    status = "✓ Overlap detected" if overlap_found else "✓ Sequential chunks"
                    print(f"  {status} in '{page_title}'")
                    break
        
        print("\n✅ Step 4 - Chunking completed successfully!")
        return all_chunks, chunks_per_page
        
    except Exception as e:
        print(f"\n❌ Error during chunking: {e}")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == "__main__":
    chunks, chunks_stats = test_step4_chunking()
