#!/usr/bin/env python3
"""
Test script for Step 7: REST API endpoints.

This script tests both main endpoints:
1. POST /crawl - Complete crawl + extract + chunk + embed + index pipeline
2. POST /ask - Complete retrieval + answer generation pipeline

Can be tested with:
- Curl commands (shown in script)
- Postman (import the examples)
- FastAPI Swagger UI at http://localhost:8000/docs
"""

import os
import sys
import json
import requests
import time
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TEST_URL = os.getenv("TEST_URL", "https://docs.python.org/3/")

def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*80)
    print(text)
    print("="*80)

def print_subheader(text):
    """Print a formatted subheader."""
    print("\n" + "-"*80)
    print(text)
    print("-"*80)

def test_crawl_endpoint():
    """Test the POST /crawl endpoint."""
    print_header("TEST 1: POST /api/crawl ENDPOINT")
    
    print("\n[Purpose]")
    print("This endpoint runs the complete crawl pipeline:")
    print("  1. Crawls the website")
    print("  2. Extracts and cleans content")
    print("  3. Creates chunks with metadata")
    print("  4. Generates embeddings")
    print("  5. Indexes in vector store")
    
    print_subheader("CURL Command")
    curl_cmd = f"""curl -X POST "{API_BASE_URL}/api/crawl" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "base_url": "{TEST_URL}",
    "max_pages": 5,
    "max_depth": 2,
    "max_chars_per_chunk": 800
  }}'"""
    print(curl_cmd)
    
    print_subheader("Python Request")
    payload = {
        "base_url": TEST_URL,
        "max_pages": 5,
        "max_depth": 2,
        "max_chars_per_chunk": 800
    }
    
    try:
        print(f"\nSending POST request to {API_BASE_URL}/api/crawl...")
        response = requests.post(
            f"{API_BASE_URL}/api/crawl",
            json=payload,
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Request successful!")
            print(f"\nResponse:")
            print(json.dumps(result, indent=2))
            
            print_subheader("Summary")
            print(f"Success: {result.get('success', False)}")
            print(f"Message: {result.get('message', 'N/A')}")
            print(f"Pages Crawled: {result.get('pages_crawled', 0)}")
            print(f"Chunks Created: {result.get('chunks_created', 0)}")
            print(f"Embeddings Created: {result.get('embeddings_created', 0)}")
            print(f"URLs Crawled:")
            for url in result.get('crawled_urls', []):
                print(f"  • {url}")
            
            return True
        else:
            print(f"\n❌ Request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
    
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection error: Could not connect to {API_BASE_URL}")
        print("   Make sure the FastAPI server is running: python main.py")
        return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

def test_ask_endpoint():
    """Test the POST /ask endpoint."""
    print_header("TEST 2: POST /api/ask ENDPOINT")
    
    print("\n[Purpose]")
    print("This endpoint runs the complete QA pipeline:")
    print("  1. Embeds the user's question")
    print("  2. Retrieves relevant chunks from vector store")
    print("  3. Generates answer using LLM with context")
    print("  4. Returns answer with source URLs")
    
    test_questions = [
        "What is Python?",
        "How do I install Python?",
    ]
    
    for question in test_questions:
        print_subheader(f"Question: {question}")
        
        print("\nCURL Command")
        curl_cmd = f"""curl -X POST "{API_BASE_URL}/api/ask" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "question": "{question}",
    "top_k": 5
  }}'"""
        print(curl_cmd)
        
        print("\nPython Request")
        payload = {
            "question": question,
            "top_k": 5
        }
        
        try:
            print(f"Sending POST request to {API_BASE_URL}/api/ask...")
            response = requests.post(
                f"{API_BASE_URL}/api/ask",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ Request successful!")
                print(f"\nResponse:")
                print(f"Question: {result.get('question', 'N/A')}")
                print(f"\nAnswer:\n{result.get('answer', 'N/A')}")
                print(f"\nSources ({result.get('num_sources', 0)}):")
                for source in result.get('sources', []):
                    print(f"  • {source}")
                print(f"\nChunks Used: {result.get('num_chunks_used', 0)}")
            else:
                print(f"\n❌ Request failed with status {response.status_code}")
                print(f"Error: {response.text}")
        
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Connection error: Could not connect to {API_BASE_URL}")
            print("   Make sure the FastAPI server is running: python main.py")
            return False
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            break

def show_additional_endpoints():
    """Show information about other available endpoints."""
    print_header("OTHER AVAILABLE ENDPOINTS")
    
    endpoints = [
        {
            "method": "GET",
            "path": "/api/kb/stats",
            "description": "Get statistics about the knowledge base",
            "example": f"curl {API_BASE_URL}/api/kb/stats"
        },
        {
            "method": "POST",
            "path": "/api/crawl/test",
            "description": "Test crawling without indexing",
            "body": {
                "base_url": TEST_URL,
                "max_pages": 5,
                "max_depth": 2
            }
        },
        {
            "method": "POST",
            "path": "/api/retrieval/test",
            "description": "Test retrieval without answer generation",
            "body": {
                "query": "What is Python?",
                "top_k": 5
            }
        },
        {
            "method": "POST",
            "path": "/api/query",
            "description": "Advanced query endpoint with granular control",
            "body": {
                "question": "What is Python?",
                "top_k": 5,
                "use_llm": True
            }
        }
    ]
    
    for idx, endpoint in enumerate(endpoints, 1):
        print(f"\n[{idx}] {endpoint['method']} {endpoint['path']}")
        print(f"    Description: {endpoint['description']}")
        if "body" in endpoint:
            print(f"    Example Body: {json.dumps(endpoint['body'], indent=6)}")
        if "example" in endpoint:
            print(f"    Example: {endpoint['example']}")

def show_postman_import():
    """Show Postman collection import information."""
    print_header("POSTMAN COLLECTION")
    
    print("\n[Endpoints Available in Postman/Swagger]")
    print("\n1. Crawl & Index:")
    print("   POST /api/crawl")
    print("\n2. Ask Question:")
    print("   POST /api/ask")
    print("\n3. Statistics:")
    print("   GET /api/kb/stats")
    print("\n4. Testing Endpoints:")
    print("   POST /api/crawl/test")
    print("   POST /api/retrieval/test")
    print("   POST /api/query (advanced)")
    
    print("\n[Access Swagger UI]")
    print(f"   Open: {API_BASE_URL}/docs")
    print("   All endpoints with interactive testing available")

def main():
    """Main test function."""
    print("\n" + "="*80)
    print("STEP 7: REST API ENDPOINTS TEST")
    print("="*80)
    
    print("\n[Configuration]")
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Test URL: {TEST_URL}")
    
    print("\n[Prerequisites]")
    print("1. FastAPI server must be running:")
    print("   $ python main.py")
    print("\n2. .env file must be configured with:")
    print("   - OPENAI_API_KEY")
    print("   - TEST_URL")
    
    # Check if server is running
    print("\n[Checking server status...]")
    try:
        response = requests.get(f"{API_BASE_URL}/docs", timeout=5)
        print("✓ FastAPI server is running")
        server_running = True
    except:
        print("✗ FastAPI server is NOT running")
        print("\nTo start the server, run:")
        print("  $ python main.py")
        server_running = False
    
    if not server_running:
        print("\nSkipping endpoint tests until server is running.")
        show_postman_import()
        return
    
    # Run tests
    crawl_success = test_crawl_endpoint()
    
    if crawl_success:
        # Give server a moment to process
        print("\n[Waiting for server to process...]")
        time.sleep(2)
        test_ask_endpoint()
    else:
        print("\n[Skipping /ask test since /crawl failed]")
    
    # Show additional info
    show_additional_endpoints()
    show_postman_import()
    
    print_header("TEST COMPLETE")
    print("\n✅ Step 7 - REST API Endpoints")
    print("\nYou can now use these endpoints for your RAG system:")
    print("  1. POST /api/crawl  - Index a new website")
    print("  2. POST /api/ask    - Ask questions about indexed content")
    print("\nFor interactive testing, visit:")
    print(f"  {API_BASE_URL}/docs")

if __name__ == "__main__":
    main()
