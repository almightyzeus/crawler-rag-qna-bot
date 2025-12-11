from typing import List
import os
import logging
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# The OpenAI Python client uses the OPENAI_API_KEY env var.
client = OpenAI()

def embed_texts(texts: List[str], model: str | None = None) -> List[list]:
    """Create embeddings for a list of texts.

    Requires:
    - OPENAI_API_KEY in the environment
    - (Optional) EMBEDDING_MODEL env var, otherwise a default is used.

    Returns a list of embedding vectors (list[float]).
    """
    if not texts:
        return []

    model = model or os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    try:
        logger.info(f"Generating embeddings for {len(texts)} texts using model: {model}")
        response = client.embeddings.create(
            model=model,
            input=texts,
        )
        embeddings = [item.embedding for item in response.data]
        logger.info(f"✓ Generated {len(embeddings)} embeddings successfully")
        return embeddings
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise

def get_embedding_dimension(model: str | None = None) -> int:
    """Get the dimension of embeddings for a given model.
    
    Args:
        model: Model name (defaults to text-embedding-3-small)
    
    Returns:
        Embedding dimension
    """
    model = model or os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Common embedding dimensions for OpenAI models
    dimensions = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
    }
    
    return dimensions.get(model, 1536)  # Default to 1536
