from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.crawling.crawler import crawl_website
from app.text_extraction.extractor import extract_text_from_html
from app.chunking.chunker import simple_chunk_text, create_chunks_with_metadata
from app.embeddings.embedder import embed_texts
from app.vector_store.store import add_embeddings, get_collection_stats
from app.retrieval.retriever import retrieve_relevant_chunks, answer_question, get_knowledge_base_stats

router = APIRouter()

class IngestRequest(BaseModel):
    base_url: str
    max_pages: int = 50
    max_depth: int = 3
    max_chars_per_chunk: int = 800

class IngestResponse(BaseModel):
    pages_crawled: int
    chunks_created: int
    crawled_urls: List[str]

class CrawlTestRequest(BaseModel):
    base_url: str
    max_pages: int = 50
    max_depth: int = 3

class CrawlTestResponse(BaseModel):
    total_pages_crawled: int
    crawled_urls: List[str]

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5
    use_llm: bool = True  # Use LLM for answer generation

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[str]
    retrieved_chunks: List[dict]
    num_chunks: int

class KBStatsResponse(BaseModel):
    collection_name: str
    total_documents: int
    metadata: dict

class RetrievalTestRequest(BaseModel):
    query: str
    top_k: int = 5

class RetrievalTestResponse(BaseModel):
    query: str
    total_results: int
    results: List[dict]

class CrawlRequest(BaseModel):
    base_url: str
    max_pages: int = 50
    max_depth: int = 3
    max_chars_per_chunk: int = 800

class CrawlResponse(BaseModel):
    success: bool
    message: str
    pages_crawled: int
    chunks_created: int
    embeddings_created: int
    crawled_urls: List[str]

class AskRequest(BaseModel):
    question: str
    top_k: int = 5

class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[str]
    num_sources: int
    num_chunks_used: int

@router.post("/crawl/test", response_model=CrawlTestResponse)
async def test_crawl(payload: CrawlTestRequest) -> CrawlTestResponse:
    """Test the crawler by crawling a website and printing the URLs.
    
    This endpoint allows you to test the crawling functionality without
    running the full ingest pipeline. Useful for debugging and validation.
    """
    pages, crawled_urls = crawl_website(
        base_url=payload.base_url,
        max_pages=payload.max_pages,
        max_depth=payload.max_depth
    )
    
    if not crawled_urls:
        raise HTTPException(status_code=400, detail="No pages crawled. Check the URL or try again.")
    
    # Print crawled URLs to console
    print("\n" + "="*80)
    print(f"CRAWL TEST RESULTS: {payload.base_url}")
    print("="*80)
    for idx, url in enumerate(crawled_urls, 1):
        print(f"{idx}. {url}")
    print(f"\nTotal: {len(crawled_urls)} pages crawled")
    print("="*80 + "\n")
    
    return CrawlTestResponse(
        total_pages_crawled=len(crawled_urls),
        crawled_urls=crawled_urls
    )

@router.post("/ingest", response_model=IngestResponse)
async def ingest_website(payload: IngestRequest) -> IngestResponse:
    """Crawl + extract + chunk + embed + store.

    Run this once per website (or whenever you want to refresh the index).
    """
    pages, crawled_urls = crawl_website(
        base_url=payload.base_url,
        max_pages=payload.max_pages,
        max_depth=payload.max_depth
    )
    
    if not pages:
        raise HTTPException(status_code=400, detail="No pages crawled. Check the URL or try again.")

    all_chunks: List[str] = []
    all_chunk_objects: List[dict] = []
    metadatas: List[dict] = []

    for page in pages:
        url = page["url"]
        title = page.get("title", "Unknown")
        # Use pre-cleaned text from crawler
        text = page.get("cleaned_text", "")
        
        if not text:
            # Fallback to extraction if cleaned_text is not available
            html = page["html"]
            text = extract_text_from_html(html)
        
        # Create chunks with metadata and overlap
        chunk_objects = create_chunks_with_metadata(
            text=text,
            url=url,
            title=title,
            max_chars=payload.max_chars_per_chunk,
            overlap_chars=100
        )
        
        for chunk_obj in chunk_objects:
            all_chunks.append(chunk_obj["chunk_text"])
            all_chunk_objects.append(chunk_obj)
            metadatas.append({
                "source_url": url,
                "title": title,
                "chunk_id": chunk_obj["chunk_id"]
            })

    if not all_chunks:
        raise HTTPException(status_code=400, detail="No text chunks extracted from crawled pages.")

    embeddings = embed_texts(all_chunks)
    add_embeddings(embeddings, all_chunks, metadatas)

    return IngestResponse(
        pages_crawled=len(pages),
        chunks_created=len(all_chunks),
        crawled_urls=crawled_urls
    )

@router.post("/query", response_model=QueryResponse)
async def query_knowledge_base(payload: QueryRequest) -> QueryResponse:
    """Ask a question against the ingested knowledge base.

    This endpoint:
    1. Embeds the user's question
    2. Retrieves top relevant chunks from vector store
    3. Uses LLM to generate an answer based on retrieved context
    4. Returns answer with source URLs and retrieved chunks
    
    Parameters:
    - question: The user's question
    - top_k: Number of chunks to retrieve (default: 5)
    - use_llm: Whether to use LLM for answer generation (default: True)
    """
    result = answer_question(payload.question, top_k=payload.top_k, use_llm=payload.use_llm)
    
    return QueryResponse(
        question=result["question"],
        answer=result["answer"],
        sources=result["sources"],
        retrieved_chunks=result["retrieved_chunks"],
        num_chunks=result["num_chunks"]
    )

@router.get("/kb/stats", response_model=KBStatsResponse)
async def get_kb_stats() -> KBStatsResponse:
    """Get statistics about the knowledge base (vector store)."""
    stats = get_knowledge_base_stats()
    return KBStatsResponse(**stats)

@router.post("/retrieval/test", response_model=RetrievalTestResponse)
async def test_retrieval(payload: RetrievalTestRequest) -> RetrievalTestResponse:
    """Test similarity search by retrieving chunks for a query.
    
    This endpoint allows you to test the retrieval/similarity search
    without running the full query endpoint.
    """
    results = retrieve_relevant_chunks(payload.query, top_k=payload.top_k)
    
    # Format results for response
    formatted_results = []
    for idx, result in enumerate(results, 1):
        formatted_results.append({
            "rank": idx,
            "id": result.get("id", ""),
            "distance": result.get("distance", 0),
            "source_url": result.get("metadata", {}).get("source_url", ""),
            "title": result.get("metadata", {}).get("title", ""),
            "text_preview": result.get("text", "")[:200] + "..." if len(result.get("text", "")) > 200 else result.get("text", "")
        })
    
    return RetrievalTestResponse(
        query=payload.query,
        total_results=len(formatted_results),
        results=formatted_results
    )

@router.post("/crawl", response_model=CrawlResponse)
async def crawl_and_index(payload: CrawlRequest) -> CrawlResponse:
    """Step 7: POST /crawl endpoint
    
    Complete pipeline endpoint that:
    1. Crawls the website from the given URL
    2. Extracts and cleans text from HTML
    3. Creates chunks with metadata
    4. Generates embeddings for each chunk
    5. Indexes everything in the vector store
    
    Returns:
    - Success status
    - Number of pages crawled
    - Number of chunks created
    - Number of embeddings created
    - List of crawled URLs
    """
    try:
        print("\n" + "="*80)
        print(f"[CRAWL PIPELINE] Starting crawl for: {payload.base_url}")
        print("="*80)
        
        # Step 1: Crawl website
        print(f"\n[1/5] Crawling website...")
        pages, crawled_urls = crawl_website(
            base_url=payload.base_url,
            max_pages=payload.max_pages,
            max_depth=payload.max_depth
        )
        
        if not pages:
            raise HTTPException(
                status_code=400,
                detail="No pages crawled. Check the URL or try again."
            )
        
        print(f"✓ Crawled {len(pages)} pages")
        
        # Step 2: Extract, chunk, and prepare embeddings
        print(f"\n[2/5] Extracting and chunking content...")
        all_chunks: List[str] = []
        all_metadatas: List[dict] = []
        
        for page in pages:
            url = page["url"]
            title = page.get("title", "Unknown")
            text = page.get("cleaned_text", "")
            
            if not text:
                html = page["html"]
                text = extract_text_from_html(html)
            
            chunk_objects = create_chunks_with_metadata(
                text=text,
                url=url,
                title=title,
                max_chars=payload.max_chars_per_chunk,
                overlap_chars=100
            )
            
            for chunk_obj in chunk_objects:
                all_chunks.append(chunk_obj["chunk_text"])
                all_metadatas.append({
                    "source_url": url,
                    "title": title,
                    "chunk_id": chunk_obj["chunk_id"]
                })
        
        if not all_chunks:
            raise HTTPException(
                status_code=400,
                detail="No text chunks extracted from crawled pages."
            )
        
        print(f"✓ Created {len(all_chunks)} chunks from {len(pages)} pages")
        
        # Step 3: Generate embeddings
        print(f"\n[3/5] Generating embeddings...")
        embeddings = embed_texts(all_chunks)
        print(f"✓ Generated {len(embeddings)} embeddings")
        
        # Step 4: Index in vector store
        print(f"\n[4/5] Indexing in vector store...")
        add_embeddings(embeddings, all_chunks, all_metadatas)
        print(f"✓ Indexed {len(embeddings)} embeddings in Chroma")
        
        # Step 5: Get final stats
        print(f"\n[5/5] Final statistics...")
        stats = get_knowledge_base_stats()
        print(f"✓ Vector store now contains {stats.get('total_documents', 0)} documents")
        
        print("\n" + "="*80)
        print("✅ [CRAWL PIPELINE] Completed successfully!")
        print("="*80 + "\n")
        
        return CrawlResponse(
            success=True,
            message=f"Successfully crawled and indexed {len(pages)} pages with {len(all_chunks)} chunks",
            pages_crawled=len(pages),
            chunks_created=len(all_chunks),
            embeddings_created=len(embeddings),
            crawled_urls=crawled_urls
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n❌ Error in crawl pipeline: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error during crawling: {str(e)}"
        )

@router.post("/ask", response_model=AskResponse)
async def ask_question(payload: AskRequest) -> AskResponse:
    """Step 7: POST /ask endpoint
    
    Complete QA pipeline endpoint that:
    1. Embeds the user's question
    2. Retrieves top relevant chunks from vector store
    3. Generates final answer using LLM with context
    4. Returns answer with source URLs
    
    Parameters:
    - question: The user's question
    - top_k: Number of chunks to retrieve (default: 5)
    
    Returns:
    - The user's question
    - Generated answer based on context
    - List of source URLs
    - Number of sources
    - Number of chunks used
    """
    try:
        print("\n" + "="*80)
        print(f"[ASK PIPELINE] Question: {payload.question}")
        print("="*80)
        
        # Run complete answer generation pipeline
        result = answer_question(
            payload.question,
            top_k=payload.top_k,
            use_llm=True
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to process question")
            )
        
        print(f"\n✓ Retrieved {result['num_chunks']} chunks")
        print(f"✓ Generated answer using LLM")
        print(f"✓ Found {len(result['sources'])} source URLs")
        
        print("\n" + "="*80)
        print("✅ [ASK PIPELINE] Completed successfully!")
        print("="*80 + "\n")
        
        return AskResponse(
            question=result["question"],
            answer=result["answer"],
            sources=result["sources"],
            num_sources=len(result["sources"]),
            num_chunks_used=result["num_chunks"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n❌ Error in ask pipeline: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )