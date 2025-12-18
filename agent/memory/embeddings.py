"""Text embedding system for creating vector representations"""
from sentence_transformers import SentenceTransformer
import numpy as np
from pathlib import Path
import pickle


class EmbeddingSystem:
    """Creates and manages text embeddings for semantic search"""
    
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize with a sentence transformer model
        all-MiniLM-L6-v2: 384 dimensions, ~80MB, fast and efficient
        """
        self.model_name = model_name
        self.model = None
        self.dimension = 384  # MiniLM-L6-v2 output dimension
        
    def load_model(self):
        """Lazy load the model when needed"""
        if self.model is None:
            print(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            print("Model loaded successfully")
    
    def embed_text(self, text):
        """
        Convert text to vector embedding
        
        Args:
            text: String to embed
            
        Returns:
            numpy array of shape (384,)
        """
        self.load_model()
        
        if isinstance(text, str):
            text = [text]
        
        embeddings = self.model.encode(text, show_progress_bar=False)
        
        if len(embeddings) == 1:
            return embeddings[0]
        return embeddings
    
    def embed_batch(self, texts):
        """
        Embed multiple texts efficiently
        
        Args:
            texts: List of strings
            
        Returns:
            numpy array of shape (n, 384)
        """
        self.load_model()
        return self.model.encode(texts, show_progress_bar=True)
    
    def similarity(self, embedding1, embedding2):
        """
        Compute cosine similarity between two embeddings
        
        Returns:
            float between -1 and 1 (higher = more similar)
        """
        return np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )


if __name__ == "__main__":
    # Test the embedding system
    embedder = EmbeddingSystem()
    
    test_texts = [
        "Disk usage is at 95% on /home partition",
        "High disk space consumption detected",
        "CPU usage spiked to 100%"
    ]
    
    print("Testing embedding system...")
    embeddings = embedder.embed_batch(test_texts)
    
    print(f"\nEmbedding shape: {embeddings.shape}")
    print(f"Dimension: {embeddings.shape[1]}")
    
    # Test similarity
    sim_1_2 = embedder.similarity(embeddings[0], embeddings[1])
    sim_1_3 = embedder.similarity(embeddings[0], embeddings[2])
    
    print(f"\nSimilarity between disk texts: {sim_1_2:.3f}")
    print(f"Similarity between disk and CPU: {sim_1_3:.3f}")
    print("\nEmbedding system working correctly!")
