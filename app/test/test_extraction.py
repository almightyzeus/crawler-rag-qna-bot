#!/usr/bin/env python3
"""
Test script for Step 3: Extracting and cleaning content.

This script demonstrates:
- HTML parsing and cleaning
- Removing navbars, footers, scripts, and cookie banners
- Extracting visible text only
- Removing noise and empty lines
- Storing cleaned text with URL and title
"""

import os
from dotenv import load_dotenv
from app.crawling.crawler import crawl_website
from app.text_extraction.extractor import extract_text_from_html, create_cleaned_page

load_dotenv()

def test_step3_extraction():
    """Test extraction and cleaning of crawled pages."""
    
    print("\n" + "="*80)
    print("STEP 3: EXTRACTING AND CLEANING CONTENT")
    print("="*80)
    
    # Parameters for crawling
    test_url = os.getenv("TEST_URL", "https://docs.python.org/3/")
    max_pages = int(os.getenv("TEST_MAX_PAGES", "5"))
    max_depth = int(os.getenv("TEST_MAX_DEPTH", "2"))
    
    print(f"\nCrawling {test_url} (max_pages={max_pages}, max_depth={max_depth})...")
    print("This will crawl pages and extract/clean their content.\n")
    
    try:
        pages, crawled_urls = crawl_website(
            base_url=test_url,
            max_pages=max_pages,
            max_depth=max_depth
        )
        
        print("\n" + "="*80)
        print("EXTRACTION RESULTS")
        print("="*80)
        print(f"\nTotal pages crawled: {len(crawled_urls)}\n")
        
        # Display cleaned content for each page
        for idx, page in enumerate(pages, 1):
            print("\n" + "-"*80)
            print(f"PAGE [{idx}/{len(pages)}]")
            print("-"*80)
            print(f"URL: {page['url']}")
            print(f"Title: {page['title']}")
            print(f"Cleaned Text Length: {page['text_length']} characters")
            print(f"\nCleaned Content (first 500 chars):")
            print("-"*40)
            
            cleaned_text = page['cleaned_text']
            if cleaned_text:
                # Display first 500 characters or full text if shorter
                display_text = cleaned_text[:500]
                if len(cleaned_text) > 500:
                    display_text += "\n... [truncated]"
                print(display_text)
            else:
                print("[No text content extracted]")
            
            print("\n" + "-"*40)
            print(f"Raw HTML Size: {len(page['html'])} bytes")
        
        # Summary statistics
        print("\n" + "="*80)
        print("SUMMARY STATISTICS")
        print("="*80)
        total_text_length = sum(page['text_length'] for page in pages)
        avg_text_length = total_text_length / len(pages) if pages else 0
        
        print(f"\nTotal pages processed: {len(pages)}")
        print(f"Total cleaned text: {total_text_length} characters")
        print(f"Average text per page: {avg_text_length:.0f} characters")
        
        print("\nCrawled URLs:")
        for idx, url in enumerate(crawled_urls, 1):
            title = next((p['title'] for p in pages if p['url'] == url), "Unknown")
            text_length = next((p['text_length'] for p in pages if p['url'] == url), 0)
            print(f"  {idx}. {url}")
            print(f"     Title: {title}")
            print(f"     Cleaned text: {text_length} chars\n")
        
        print("✅ Step 3 - Extraction and cleaning completed successfully!")
        return pages, crawled_urls
        
    except Exception as e:
        print(f"\n❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == "__main__":
    pages, urls = test_step3_extraction()
