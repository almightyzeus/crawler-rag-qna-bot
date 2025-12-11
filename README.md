# Q&A Support Bot - RAG-Based Question Answering System

An Retrieval-Augmented Generation (RAG) system that crawls websites, extracts and chunks content, generates embeddings, and answers questions based on indexed knowledge using an LLM.

## Project Overview

This system implements a complete RAG pipeline with seven key components:

1. **Web Crawling** - Crawl websites with configurable depth and page limits
2. **Text Extraction** - Clean HTML and extract readable content
3. **Content Chunking** - Split text into overlapping chunks with metadata
4. **Embedding Generation** - Create vector embeddings using OpenAI API
5. **Vector Storage** - Persist embeddings in Chroma vector database
6. **Semantic Retrieval** - Find relevant chunks using similarity search
7. **Answer Generation** - Generate answers using GPT-4 based on retrieved context

The system provides a REST API for crawling websites and asking questions about indexed content.

---

## Project Structure

```
qa_support_bot_rag/
├── app/
│   ├── api/
│   │   └── routes.py                 # REST API endpoints
│   ├── crawling/
│   │   └── crawler.py                # Website crawler with depth/page limits
│   ├── text_extraction/
│   │   └── extractor.py              # HTML parsing and text cleaning
│   ├── chunking/
│   │   └── chunker.py                # Text chunking with overlap
│   ├── embeddings/
│   │   └── embedder.py               # OpenAI embedding generation
│   ├── vector_store/
│   │   └── store.py                  # Chroma vector database wrapper
│   ├── retrieval/
│   │   └── retriever.py              # Semantic search and answer generation
│   ├── test/
│   │   ├── test_crawler.py           # Crawler unit tests
│   │   ├── test_extraction.py        # Text extraction tests
│   │   ├── test_chunking.py          # Chunking tests
│   │   ├── test_embeddings.py        # Embedding generation tests
│   │   ├── test_retrieval_and_answer.py  # Retrieval and LLM tests
│   │   └── test_api_endpoints.py     # API endpoint tests
│   └── config.py                     # Configuration management
├── data/                             # Persistent Chroma database
├── main.py                           # FastAPI application entry point
├── requirements.txt                  # Python dependencies
├── .env                              # Environment variables (not in git)
├── .gitignore                        # Git ignore rules
└── README.md                         # This file
```

---

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- OpenAI API key (get one at https://platform.openai.com/api-keys)

---

## Setup Instructions

### Step 1: Clone or navigate to the project directory

```bash
cd qa_support_bot_rag
```

### Step 2: Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure environment variables

Create a `.env` file in the project root:

```bash
cp .env.example .env  # if .env.example exists
# OR create manually
touch .env
```

Edit `.env` with the following:

```env
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
TEST_URL=https://docs.python.org/3/
TEST_MAX_PAGES=20
TEST_MAX_DEPTH=3
```

Replace `your_openai_api_key_here` with your actual OpenAI API key.

---

## Running the Crawler

### Start the API Server

```bash
python main.py
```

The server starts on `http://localhost:8000`

Access the interactive API documentation at: `http://localhost:8000/docs`

### Crawl a Website

Use the `/api/crawl` endpoint to crawl and index a website. You need to provide the URL to crawl:

```bash
curl -X POST "http://localhost:8000/api/crawl" \
  -H "Content-Type: application/json" \
  -d '{
    "base_url": "https://docs.python.org/3/",
    "max_pages": 20,
    "max_depth": 3,
    "max_chars_per_chunk": 800
  }'
```

This will:
1. Crawl the website specified in `TEST_URL` (or https://docs.python.org/3/)
2. Extract and clean text from each page
3. Split content into overlapping chunks
4. Generate vector embeddings
5. Store embeddings in the Chroma vector database

**Response:**
```json
{
  "success": true,
  "message": "Successfully crawled and indexed 3 pages with 10 chunks",
  "pages_crawled": 3,
  "chunks_created": 10,
  "embeddings_created": 10,
  "crawled_urls": ["https://docs.python.org/3/", "..."]
}
```

---

## Testing the /ask Endpoint

### Prerequisites

Before asking questions, you must first crawl and index a website using the `/api/crawl` endpoint (see section above).

### Basic Question

Ask a question about the indexed content:

```bash
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Python?"}'
```

**Response:**
```json
{
  "question": "What is Python?",
  "answer": "Python is a high-level programming language...",
  "sources": ["https://docs.python.org/3/", "https://docs.python.org/3/tutorial/"],
  "num_sources": 2,
  "num_chunks_used": 3
}
```

### More Example Questions

```bash
# Python syntax
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I define a function in Python?"}'

# Data structures
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the differences between lists and tuples?"}'

# Standard library
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I work with JSON in Python?"}'
```

---

## Example Questions and Answers

### Question 1: "How do I create a virtual environment in Python?"

**Answer:** A virtual environment is a self-contained Python installation that allows you to manage dependencies for specific projects. You can create one using:
```bash
python -m venv environment_name
```
This isolates packages for your project, preventing conflicts with system Python.

### Question 2: "What are decorators in Python?"

**Answer:** Decorators are functions that modify or enhance other functions or classes without permanently changing their source code. They use the `@decorator_name` syntax and are commonly used for logging, caching, and access control.

### Question 3: "How does exception handling work?"

**Answer:** Python uses `try`, `except`, `else`, and `finally` blocks for exception handling. Code in the `try` block executes first; if an error occurs, the matching `except` block catches it. The `finally` block always runs, regardless of whether an exception occurred.

### Question 4: "What is list comprehension?"

**Answer:** List comprehension provides a concise way to create lists. The syntax `[x*2 for x in range(5)]` creates a new list by applying an expression to each item in an iterable, much more readable than equivalent loop-based approaches.

---

## Testing the System

Test scripts are located in `app/test/`. Run all tests with:

```bash
# Install pytest if needed
pip install pytest

# Run all tests
pytest app/test/ -v

# Run specific test file
pytest app/test/test_api_endpoints.py -v

# Run with coverage report
pytest app/test/ --cov=app --cov-report=html
```

### Individual Test Modules

Each component has dedicated tests:

**Crawler Tests** (`app/test/test_crawler.py`)
- Tests website crawling with depth/page limits
- Validates URL filtering and link extraction
- Checks for proper HTML handling

```bash
pytest app/test/test_crawler.py -v
```

**Text Extraction Tests** (`app/test/test_extraction.py`)
- Tests HTML cleaning and text extraction
- Validates removal of scripts, styles, and navigation elements
- Checks for proper text formatting

```bash
pytest app/test/test_extraction.py -v
```

**Chunking Tests** (`app/test/test_chunking.py`)
- Tests text splitting with overlap
- Validates chunk metadata preservation
- Checks chunk size and overlap ratios

```bash
pytest app/test/test_chunking.py -v
```

**Embedding Tests** (`app/test/test_embeddings.py`)
- Tests OpenAI embedding API integration
- Validates embedding dimensions
- Checks batch processing

```bash
pytest app/test/test_embeddings.py -v
```

**Retrieval and Answer Tests** (`app/test/test_retrieval_and_answer.py`)
- Tests semantic similarity search
- Validates LLM-based answer generation
- Checks source attribution

```bash
pytest app/test/test_retrieval_and_answer.py -v
```

**API Endpoint Tests** (`app/test/test_api_endpoints.py`)
- Tests all REST API endpoints
- Validates request/response formats
- Checks error handling

```bash
pytest app/test/test_api_endpoints.py -v
```

---

## API Endpoints

The system provides both main endpoints (recommended) and legacy endpoints for specific testing purposes.

### Main Endpoints (Recommended)

These are the primary endpoints for production use:

#### POST /api/crawl
Crawl and index a website's content.

**Request:**
```json
{
  "base_url": "https://example.com",
  "max_pages": 20,
  "max_depth": 3,
  "max_chars_per_chunk": 800
}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_url` | string | required | The starting URL to crawl |
| `max_pages` | integer | 50 | Maximum number of pages to crawl |
| `max_depth` | integer | 3 | Maximum depth for recursive crawling |
| `max_chars_per_chunk` | integer | 800 | Size of text chunks in characters |

**Response:**
```json
{
  "success": true,
  "message": "Successfully crawled and indexed 3 pages with 45 chunks",
  "pages_crawled": 3,
  "chunks_created": 45,
  "embeddings_created": 45,
  "crawled_urls": ["https://example.com", "https://example.com/about", "https://example.com/docs"]
}
```

#### POST /api/ask
Ask a question about indexed content.

**Request:**
```json
{
  "question": "Your question here?",
  "top_k": 5
}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `question` | string | required | The question to ask about indexed content |
| `top_k` | integer | 5 | Number of chunks to retrieve for context |

**Response:**
```json
{
  "question": "Your question here?",
  "answer": "Generated answer based on retrieved context...",
  "sources": ["https://example.com", "https://example.com/docs"],
  "num_sources": 2,
  "num_chunks_used": 5
}
```

#### GET /api/kb/stats
Get vector database statistics.

**Response:**
```json
{
  "collection_name": "documents",
  "total_documents": 110,
  "metadata": {
    "metric": "cosine"
  }
}
```

### Testing & Debugging Endpoints

These endpoints are useful for testing individual components:

#### POST /api/crawl/test
Test crawling without indexing. Useful for validating that a URL is crawlable before running the full pipeline.

**Request:**
```json
{
  "base_url": "https://example.com",
  "max_pages": 5,
  "max_depth": 2
}
```

**Response:**
```json
{
  "total_pages_crawled": 3,
  "crawled_urls": ["https://example.com", "https://example.com/page1", "https://example.com/page2"]
}
```

#### POST /api/retrieval/test
Test retrieval without LLM answer generation. Useful for debugging which chunks are retrieved for a query.

**Request:**
```json
{
  "query": "Test question?",
  "top_k": 3
}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | The query to test retrieval for |
| `top_k` | integer | 5 | Number of chunks to retrieve |

**Response:**
```json
{
  "query": "Test question?",
  "total_results": 3,
  "results": [
    {
      "rank": 1,
      "id": "chunk_id_123",
      "distance": 0.28,
      "source_url": "https://example.com",
      "title": "Page Title",
      "text_preview": "Retrieved chunk text preview..."
    }
  ]
}
```

### Legacy Endpoints (Alternative)

These endpoints provide alternative ways to achieve the same functionality:

#### POST /api/ingest
Legacy crawl and index endpoint. Same functionality as `/api/crawl` but with slightly different response format.

**Request:**
```json
{
  "base_url": "https://example.com",
  "max_pages": 20,
  "max_depth": 3,
  "max_chars_per_chunk": 800
}
```

**Response:**
```json
{
  "pages_crawled": 3,
  "chunks_created": 45,
  "crawled_urls": ["https://example.com", "https://example.com/about", "https://example.com/docs"]
}
```

#### POST /api/query
Legacy question answering endpoint. Same functionality as `/api/ask` but returns additional debug information.

**Request:**
```json
{
  "question": "Your question?",
  "top_k": 5,
  "use_llm": true
}
```

**Response:**
```json
{
  "question": "Your question?",
  "answer": "Generated answer...",
  "sources": ["url1", "url2"],
  "retrieved_chunks": [{"text": "chunk content", "metadata": {...}}],
  "num_chunks": 5
}
```

---

## System Architecture

### Pipeline Flow

```
Website URL
    ↓
[Web Crawler] → Extract HTML pages
    ↓
[Text Extractor] → Clean HTML, remove noise
    ↓
[Chunker] → Split into overlapping chunks
    ↓
[Embedder] → Generate vector embeddings (OpenAI)
    ↓
[Vector Store] → Store in Chroma database
    ↓
[Retriever] → Semantic search on query
    ↓
[LLM] → Generate answer from context
    ↓
Answer with sources
```

### Key Technologies

- **FastAPI** - Modern Python web framework for building REST APIs
- **Chroma** - Open-source vector database for storing and searching embeddings
- **OpenAI API** - For generating embeddings and answering questions
- **BeautifulSoup4** - HTML parsing and text extraction
- **Requests** - HTTP library for web crawling

### Configuration

Key settings in `.env`:

| Variable | Purpose | Example |
|----------|---------|---------|
| `OPENAI_API_KEY` | OpenAI API authentication | `sk-...` |
| `LLM_MODEL` | Language model for answers | `gpt-4o-mini` |
| `EMBEDDING_MODEL` | Model for embeddings | `text-embedding-3-small` |
| `TEST_URL` | Website to crawl | `https://docs.python.org/3/` |
| `TEST_MAX_PAGES` | Max pages to crawl | `20` |
| `TEST_MAX_DEPTH` | Max crawl depth | `3` |

---

## Limitations and Considerations

### Current Limitations

1. **Crawling Scope** - Limited by `TEST_MAX_PAGES` and `TEST_MAX_DEPTH` to avoid excessive API calls and crawling time. Single-domain crawling only.

2. **Chunk Size** - Fixed at 800 characters with 100-character overlap. May not be optimal for all content types. Token-based chunking would be more sophisticated.

3. **LLM Temperature** - Set to 0.3 for factuality. Lower temperatures reduce creativity and hallucination but may miss nuanced interpretations.

4. **Context Window** - Limited to top-5 retrieved chunks (configurable). Very complex questions requiring many sources may not get complete answers.

5. **Similarity Metric** - Uses cosine similarity. Other metrics (Euclidean, dot product) might work better for specific domains.

6. **Language Support** - Only tested with English content. Performance with other languages unknown.

7. **Rate Limiting** - No built-in rate limiting for OpenAI API calls. Could lead to quota exhaustion with large crawls.

### Assumptions

- All crawled websites are publicly accessible
- Content is primarily text-based (tables, code blocks may lose formatting)
- Questions are related to crawled content (out-of-domain questions will return "no information" responses)
- Single Chroma collection per project (no multi-project support)

---

## Future Improvements

### Short Term

1. **Advanced Chunking**
   - Token-based chunking using tiktoken
   - Semantic-aware chunking (chunk at paragraph/section boundaries)
   - Adaptive chunk sizes based on content density

2. **Improved Text Extraction**
   - Better handling of tables and structured data
   - Code block preservation with syntax highlighting
   - Image alt-text extraction

3. **Enhanced Retrieval**
   - Hybrid search (keyword + semantic)
   - Multi-query expansion for better recall
   - Reranking of retrieved chunks using cross-encoders

4. **Better Answer Generation**
   - Multi-step reasoning for complex questions
   - Confidence scoring
   - Answer validation against retrieved context

### Medium Term

1. **Performance Optimization**
   - Caching of frequently asked questions
   - Batch embedding generation for faster indexing
   - Database indexing for faster retrieval

2. **User Experience**
   - Web UI for asking questions and managing knowledge base
   - Citation formatting and citation lookup
   - Feedback mechanism for answer quality

3. **Robustness**
   - Error recovery and partial crawl completion
   - Rate limiting and backoff strategies
   - Monitoring and logging

### Long Term

1. **Multi-Source Support**
   - Crawl multiple websites/domains
   - Index documents (PDFs, Word docs)
   - Support structured data (databases, APIs)

2. **Advanced RAG**
   - Query decomposition for complex questions
   - Iterative refinement with feedback loops
   - Multi-hop reasoning across documents

3. **Enterprise Features**
   - User authentication and access control
   - Multiple knowledge bases per user
   - Analytics and usage tracking

---

## Troubleshooting

### API Key Issues

**Error:** `AuthenticationError: Invalid API key provided`

**Solution:** 
1. Check that `OPENAI_API_KEY` is set correctly in `.env`
2. Verify your OpenAI account has API credits
3. Ensure no extra whitespace in the key

### Crawling Failures

**Error:** `Connection timeout` or `Failed to fetch URL`

**Solution:**
1. Check internet connection
2. Verify `TEST_URL` is accessible (not behind authentication)
3. Reduce `TEST_MAX_PAGES` and `TEST_MAX_DEPTH`
4. Check server logs for detailed error messages

### Empty Answers

**Error:** `"answer": "I don't have enough information to answer that."`

**Solution:**
1. Crawl more pages using the `/api/crawl` endpoint
2. Try rephrasing the question
3. Check that retrieved chunks in `/api/retrieval/test` are relevant
4. Increase chunk overlap for better context preservation

### Database Issues

**Error:** Vector store operations fail or return stale data

**Solution:**
1. Delete the `data/` directory to reset the database
2. Re-run the `/api/crawl` endpoint to rebuild
3. Check available disk space

---
