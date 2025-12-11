#!/usr/bin/env python3
"""
Test script for the website crawler.

This script demonstrates the crawler functionality without needing to run the full API.
You can use this to test crawling with different URLs and parameters.
"""

import os
from dotenv import load_dotenv
from app.crawling.crawler import crawl_website

load_dotenv()

def main():
    # Example 1: Crawl a test website
    print("\n" + "="*80)
    print("WEBSITE CRAWLER TEST")
    print("="*80)
    
    # You can modify these parameters for testing
    test_url = os.getenv("TEST_URL", "https://docs.python.org/3/")
    max_pages = int(os.getenv("TEST_MAX_PAGES", "20"))
    max_depth = int(os.getenv("TEST_MAX_DEPTH", "3"))
    
    print(f"\nParameters:")
    print(f"  Base URL: {test_url}")
    print(f"  Max Pages: {max_pages}")
    print(f"  Max Depth: {max_depth}")
    print(f"\nStarting crawl...\n")
    
    try:
        pages, crawled_urls = crawl_website(
            base_url=test_url,
            max_pages=max_pages,
            max_depth=max_depth
        )
        
        # Print results
        print("\n" + "="*80)
        print("CRAWL RESULTS")
        print("="*80)
        print(f"\nTotal pages crawled: {len(crawled_urls)}\n")
        
        print("Crawled URLs:")
        for idx, url in enumerate(crawled_urls, 1):
            print(f"  {idx}. {url}")
        
        print("\n" + "="*80)
        print("PAGE DETAILS")
        print("="*80)
        
        for idx, page in enumerate(pages, 1):
            print(f"\n[{idx}] {page['title']}")
            print(f"    URL: {page['url']}")
            print(f"    HTML size: {len(page['html'])} bytes")
        
        print("\n" + "="*80)
        print("TEST COMPLETED SUCCESSFULLY")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\nError during crawling: {e}")
        print("Please check the URL and try again.\n")

if __name__ == "__main__":
    main()
