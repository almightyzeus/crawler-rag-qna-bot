from typing import Dict
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)

def extract_text_from_html(html: str) -> str:
    """Extracts and cleans visible text from HTML.

    This implementation:
    - Strips scripts/styles
    - Removes navbars, footers, headers
    - Removes cookie banners and popups
    - Removes noscript tags
    - Extracts visible text only
    - Removes noise and empty lines
    """
    try:
        soup = BeautifulSoup(html, "html.parser")

        # Remove unwanted elements
        for tag in soup(["script", "style", "noscript", "meta", "link"]):
            tag.decompose()

        # Remove navigation elements (nav, header, footer)
        for tag in soup(["nav", "header", "footer"]):
            tag.decompose()

        # Remove cookie banners and popups (common patterns)
        for tag in soup.find_all(class_=re.compile(r"cookie|banner|popup|modal|consent|notification")):
            tag.decompose()

        for tag in soup.find_all(id=re.compile(r"cookie|banner|popup|modal|consent|notification")):
            tag.decompose()

        # Remove common ad/tracking containers
        for tag in soup(["iframe", "embed"]):
            tag.decompose()

        # Extract text with proper spacing
        text = soup.get_text(separator="\n", strip=True)

        # Clean up the text
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        
        # Remove multiple newlines (keep max 2)
        text = re.sub(r'\n\n+', '\n\n', text)
        
        # Remove lines that are just whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)

        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from HTML: {e}")
        return ""


def create_cleaned_page(url: str, title: str, html: str) -> Dict:
    """Create a page object with cleaned text.

    Args:
        url: Page URL
        title: Page title
        html: Raw HTML content

    Returns:
        Dictionary with url, title, raw_html, and cleaned_text
    """
    cleaned_text = extract_text_from_html(html)
    
    return {
        "url": url,
        "title": title,
        "raw_html": html,
        "cleaned_text": cleaned_text,
        "text_length": len(cleaned_text)
    }
