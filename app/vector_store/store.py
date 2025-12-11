from typing import List, Dict, Any
import chromadb
import logging

logger = logging.getLogger(__name__)

# For simplicity, use a persistent local Chroma DB under ./data
_client = chromadb.PersistentClient(path="data")
_collection = None

def get_collection(collection_name: str = "documents"):
    """Get or create a Chroma collection."""
    global _collection
    if _collection is None:
        _collection = _client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        logger.info(f"✓ Initialized Chroma collection: {collection_name}")
    return _collection

def add_embeddings(
    embeddings: List[list],
    texts: List[str],
    metadatas: List[Dict[str, Any]],
    collection_name: str = "documents",
) -> None:
    """Add embeddings + texts + metadata to the Chroma collection.
    
    Args:
        embeddings: List of embedding vectors
        texts: List of text chunks
        metadatas: List of metadata dicts for each chunk
        collection_name: Name of the collection to add to
    """
    if not embeddings or not texts:
        logger.warning("No embeddings or texts to add")
        return

    collection = get_collection(collection_name)
    
    try:
        # Generate IDs based on current collection size
        start_id = collection.count()
        ids = [f"doc-{start_id + i}" for i in range(len(texts))]
        
        logger.info(f"Adding {len(texts)} documents to collection '{collection_name}'")
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )
        logger.info(f"✓ Successfully added {len(texts)} documents")
        logger.info(f"  Total documents in collection: {collection.count()}")
    except Exception as e:
        logger.error(f"Error adding embeddings: {e}")
        raise

def query_embeddings(
    query_embedding: list,
    n_results: int = 5,
    collection_name: str = "documents",
) -> Dict[str, Any]:
    """Query the Chroma collection with a single embedding.
    
    Args:
        query_embedding: The query embedding vector
        n_results: Number of results to return
        collection_name: Name of the collection to query
    
    Returns:
        Dictionary with ids, documents, metadatas, distances
    """
    collection = get_collection(collection_name)
    
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
        )
        return results
    except Exception as e:
        logger.error(f"Error querying embeddings: {e}")
        raise

def get_collection_stats(collection_name: str = "documents") -> Dict[str, Any]:
    """Get statistics about the collection.
    
    Args:
        collection_name: Name of the collection
    
    Returns:
        Dictionary with collection stats
    """
    collection = get_collection(collection_name)
    
    try:
        count = collection.count()
        metadata = collection.metadata
        
        stats = {
            "collection_name": collection_name,
            "total_documents": count,
            "metadata": metadata,
        }
        return stats
    except Exception as e:
        logger.error(f"Error getting collection stats: {e}")
        return {}

def delete_collection(collection_name: str = "documents") -> bool:
    """Delete a collection from Chroma.
    
    Args:
        collection_name: Name of the collection to delete
    
    Returns:
        True if successful
    """
    global _collection
    try:
        _client.delete_collection(name=collection_name)
        if _collection is not None:
            _collection = None
        logger.info(f"✓ Deleted collection: {collection_name}")
        return True
    except Exception as e:
        logger.error(f"Error deleting collection: {e}")
        return False

def reset_collection(collection_name: str = "documents") -> None:
    """Reset (delete and recreate) a collection.
    
    Args:
        collection_name: Name of the collection to reset
    """
    global _collection
    delete_collection(collection_name)
    _collection = None
    get_collection(collection_name)
    logger.info(f"✓ Reset collection: {collection_name}")
