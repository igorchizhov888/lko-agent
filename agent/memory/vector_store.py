"""FAISS-based vector store for semantic search"""
import faiss
import numpy as np
import pickle
from pathlib import Path
from datetime import datetime
from agent.memory.embeddings import EmbeddingSystem


class VectorStore:
    """Manages vector storage and similarity search using FAISS"""
    
    def __init__(self, dimension=384, index_path="agent/memory/faiss.index", 
                 metadata_path="agent/memory/metadata.pkl"):
        self.dimension = dimension
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)
        
        self.embedder = EmbeddingSystem()
        self.index = None
        self.metadata = []  # Stores original data associated with vectors
        
        # Ensure directory exists
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or create index
        if self.index_path.exists():
            self.load()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        # Using IndexFlatL2 for exact search (good for small datasets)
        # For larger datasets, could use IndexIVFFlat
        self.index = faiss.IndexFlatL2(self.dimension)
        print("Created new FAISS index")
    
    def add(self, text, metadata_dict):
        """
        Add a text with associated metadata to the store
        
        Args:
            text: String to embed and store
            metadata_dict: Dictionary with metadata (timestamp, problem, solution, etc.)
        """
        # Create embedding
        embedding = self.embedder.embed_text(text)
        
        # Add to FAISS index
        embedding_2d = embedding.reshape(1, -1).astype('float32')
        self.index.add(embedding_2d)
        
        # Store metadata
        metadata_dict['text'] = text
        metadata_dict['added_at'] = datetime.now().isoformat()
        self.metadata.append(metadata_dict)
        
        return len(self.metadata) - 1  # Return ID
    
    def add_batch(self, texts, metadata_list):
        """
        Add multiple texts efficiently
        
        Args:
            texts: List of strings
            metadata_list: List of metadata dictionaries
        """
        # Create embeddings
        embeddings = self.embedder.embed_batch(texts)
        embeddings = embeddings.astype('float32')
        
        # Add to index
        self.index.add(embeddings)
        
        # Store metadata
        for text, meta in zip(texts, metadata_list):
            meta['text'] = text
            meta['added_at'] = datetime.now().isoformat()
            self.metadata.append(meta)
    
    def search(self, query, k=5):
        """
        Search for similar texts
        
        Args:
            query: Search query string
            k: Number of results to return
            
        Returns:
            List of (metadata, similarity_score) tuples
        """
        if self.index.ntotal == 0:
            return []
        
        # Embed query
        query_embedding = self.embedder.embed_text(query)
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        
        # Search
        k = min(k, self.index.ntotal)  # Don't request more than we have
        distances, indices = self.index.search(query_embedding, k)
        
        # Return results with metadata
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                similarity = 1 / (1 + dist)  # Convert L2 distance to similarity
                results.append((self.metadata[idx], similarity))
        
        return results
    
    def save(self):
        """Save index and metadata to disk"""
        # Save FAISS index
        faiss.write_index(self.index, str(self.index_path))
        
        # Save metadata
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        
        print(f"Saved vector store with {self.index.ntotal} vectors")
    
    def load(self):
        """Load index and metadata from disk"""
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            
            if self.metadata_path.exists():
                with open(self.metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
            
            print(f"Loaded vector store with {self.index.ntotal} vectors")
        else:
            self._create_new_index()
    
    def count(self):
        """Return number of vectors in store"""
        return self.index.ntotal if self.index else 0


if __name__ == "__main__":
    # Test the vector store
    print("Testing Vector Store...")
    
    store = VectorStore()
    
    # Add some test incidents
    incidents = [
        ("Disk usage exceeded 90% on /home partition due to docker logs",
         {"problem": "disk_full", "solution": "docker system prune", "outcome": "success"}),
        
        ("High memory consumption by Chrome process causing system slowdown",
         {"problem": "memory_leak", "solution": "restart chrome", "outcome": "success"}),
        
        ("Disk space critically low, /var/log filled with old logs",
         {"problem": "disk_full", "solution": "log rotation", "outcome": "success"}),
    ]
    
    print(f"\nAdding {len(incidents)} test incidents...")
    for text, meta in incidents:
        store.add(text, meta)
    
    print(f"Store now has {store.count()} vectors")
    
    # Test search
    print("\n" + "="*60)
    query = "Why is my disk filling up?"
    print(f"Query: {query}")
    print("="*60)
    
    results = store.search(query, k=2)
    
    for i, (meta, score) in enumerate(results, 1):
        print(f"\nResult {i} (similarity: {score:.3f}):")
        print(f"  Problem: {meta['problem']}")
        print(f"  Solution: {meta['solution']}")
        print(f"  Text: {meta['text'][:80]}...")
    
    # Save
    store.save()
    print("\nVector store test complete!")
