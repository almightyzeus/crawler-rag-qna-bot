from typing import List, Dict, Tuple
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging
from app.text_extraction.extractor import extract_text_from_html

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pages to skip (login, signup, cart, unrelated sections, etc.)
EXCLUDED_PATHS = {
    '/login', '/signin', '/sign-in', '/auth',
    '/signup', '/sign-up', '/register', '/registration',
    '/cart', '/checkout', '/shop', '/store',
    '/admin', '/dashboard',
    '/privacy', '/terms', '/legal',
    '/contact', '/support/contact',
    '/search', '/search?',
    '.pdf', '.jpg', '.png', '.gif', '.zip',
}

def should_skip_page(url: str) -> bool:
    """Check if a URL should be skipped based on path patterns."""
    parsed = urlparse(url)
    path_lower = parsed.path.lower()
    
    for excluded in EXCLUDED_PATHS:
        if excluded in path_lower:
            return True
    
    # Skip URLs with query parameters (often duplicates or dynamic pages)
    if parsed.query and 'page' in parsed.query.lower():
        return True
    
    return False

def extract_title(html: str) -> str:
    """Extract page title from HTML."""
    try:
        soup = BeautifulSoup(html, "html.parser")
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text(strip=True)
        
        # Fallback to h1 if no title tag
        h1_tag = soup.find("h1")
        if h1_tag:
            return h1_tag.get_text(strip=True)
        
        return "No title found"
    except Exception as e:
        logger.warning(f"Error extracting title: {e}")
        return "Unknown title"

def crawl_website(
    base_url: str,
    max_pages: int = 50,
    max_depth: int = 3
) -> Tuple[List[Dict], List[str]]:
    """
    Crawl a website with controlled depth and page limits.
    
    Args:
        base_url: Starting URL to crawl
        max_pages: Maximum number of pages to crawl
        max_depth: Maximum depth of links to follow (0 = base_url only)
    
    Returns:
        Tuple of (pages_data, crawled_urls)
        pages_data: List of dicts with url, title, html
        crawled_urls: List of all crawled URLs (for testing/debugging)
    """
    pages: List[Dict] = []
    crawled_urls: List[str] = []
    visited = set()
    to_visit: List[Tuple[str, int]] = [(base_url, 0)]  # (url, depth)
    
    base_netloc = urlparse(base_url).netloc
    
    def is_same_domain(url: str) -> bool:
        """Check if URL belongs to the same domain."""
        try:
            return urlparse(url).netloc == base_netloc
        except Exception:
            return False
    
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid and should be visited."""
        return url.startswith('http') and is_same_domain(url) and not should_skip_page(url)
    
    logger.info(f"Starting crawl of {base_url} (max_pages={max_pages}, max_depth={max_depth})")
    
    while to_visit and len(pages) < max_pages:
        current_url, depth = to_visit.pop(0)
        
        # Skip if already visited
        if current_url in visited:
            continue
        
        visited.add(current_url)
        
        # Skip if exceeds max depth
        if depth > max_depth:
            logger.debug(f"Skipping {current_url} (exceeds max_depth={max_depth})")
            continue
        
        try:
            logger.info(f"Crawling [{len(pages) + 1}/{max_pages}]: {current_url}")
            resp = requests.get(current_url, timeout=10)
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to fetch {current_url}: {e}")
            continue
        
        html = resp.text
        title = extract_title(html)
        cleaned_text = extract_text_from_html(html)
        
        # Store page data
        page_data = {
            "url": current_url,
            "title": title,
            "html": html,
            "cleaned_text": cleaned_text,
            "text_length": len(cleaned_text)
        }
        pages.append(page_data)
        crawled_urls.append(current_url)
        
        logger.info(f"  ✓ Stored: {title}")
        
        # Extract and queue new links
        try:
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                full_url = urljoin(current_url, href)
                
                # Normalize URL (remove fragments)
                full_url = full_url.split('#')[0]
                
                if (is_valid_url(full_url) and 
                    full_url not in visited and 
                    not any(url == full_url for url, _ in to_visit)):
                    to_visit.append((full_url, depth + 1))
        except Exception as e:
            logger.warning(f"Error extracting links from {current_url}: {e}")
    
    logger.info(f"Crawl complete. Total pages crawled: {len(pages)}")
    return pages, crawled_urls
