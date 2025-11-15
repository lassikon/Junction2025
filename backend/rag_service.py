"""
RAG Service for LifeSim - Handles embedding generation and retrieval
Uses Google Gemini embeddings + ChromaDB for semantic search
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from google import genai
import os
from dotenv import load_dotenv
import json
from functools import lru_cache

load_dotenv()


class RAGService:
    """
    Retrieval-Augmented Generation service using ChromaDB + Google Gemini embeddings
    """
    
    def __init__(self, chroma_host: str = "chromadb", chroma_port: int = 8000):
        """Initialize ChromaDB client and Gemini API"""
        # Connect to ChromaDB
        self.chroma_client = chromadb.HttpClient(
            host=chroma_host,
            port=chroma_port,
            settings=Settings(allow_reset=True)
        )
        
        # Initialize Gemini client for embeddings
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_api_key:
            self.genai_client = genai.Client(api_key=self.gemini_api_key)
        else:
            self.genai_client = None
            print("⚠️ GEMINI_API_KEY not found - RAG disabled")
        
        # Create/get collections
        self.financial_concepts = self._get_or_create_collection("financial_concepts")
        self.player_decisions = self._get_or_create_collection("player_decisions")
        
        # In-memory embedding cache (LRU cache with max 100 entries)
        self._embedding_cache = {}
        self._cache_max_size = 100
        
        print("✅ RAG Service initialized")
    
    def _get_or_create_collection(self, name: str):
        """Get existing collection or create new one"""
        try:
            return self.chroma_client.get_collection(name=name)
        except:
            return self.chroma_client.create_collection(
                name=name,
                metadata={"description": f"LifeSim {name}"}
            )
    
    def _embed_text(self, text: str, use_cache: bool = True) -> List[float]:
        """
        Generate embedding vector for text using Gemini
        
        Args:
            text: Input text to embed
            use_cache: Whether to use in-memory cache
            
        Returns:
            768-dimensional embedding vector
        """
        if not self.genai_client:
            raise Exception("Gemini API not configured")
        
        # Check cache first
        if use_cache and text in self._embedding_cache:
            return self._embedding_cache[text]
        
        try:
            # Use Gemini embedding model
            response = self.genai_client.models.embed_content(
                model="models/text-embedding-004",
                contents=text  # Note: 'contents' not 'content'
            )
            
            # Extract embedding vector
            embedding = response.embeddings[0].values
            
            # Cache the result (with size limit)
            if use_cache:
                if len(self._embedding_cache) >= self._cache_max_size:
                    # Remove oldest entry (simple FIFO for now)
                    self._embedding_cache.pop(next(iter(self._embedding_cache)))
                self._embedding_cache[text] = embedding
            
            return embedding
            
        except Exception as e:
            print(f"❌ Embedding generation failed: {e}")
            raise
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Input text to chunk
            chunk_size: Target characters per chunk
            overlap: Characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings within last 100 chars
                last_period = text.rfind('.', end - 100, end)
                if last_period > start:
                    end = last_period + 1
            
            chunks.append(text[start:end].strip())
            start = end - overlap
        
        return chunks
    
    # ==========================================
    # Financial Concepts Index
    # ==========================================
    
    def index_financial_concept(
        self,
        concept_id: str,
        title: str,
        content: str,
        category: str,
        difficulty: str = "beginner",
        age_relevance: Optional[List[int]] = None
    ):
        """
        Index a financial education concept
        
        Args:
            concept_id: Unique identifier (e.g., "emergency_fund_101")
            title: Concept title
            content: Full text explanation
            category: Category (e.g., "saving", "investing", "debt")
            difficulty: "beginner", "intermediate", "advanced"
            age_relevance: Ages this is most relevant for (e.g., [18, 25])
        """
        # Chunk long content
        chunks = self._chunk_text(content)
        
        for i, chunk in enumerate(chunks):
            # Generate embedding
            embedding = self._embed_text(chunk, use_cache=False)
            
            # Store in ChromaDB
            self.financial_concepts.add(
                ids=[f"{concept_id}_chunk_{i}"],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{
                    "concept_id": concept_id,
                    "title": title,
                    "category": category,
                    "difficulty": difficulty,
                    "age_relevance": json.dumps(age_relevance or []),
                    "chunk_index": i
                }]
            )
        
        print(f"✅ Indexed concept: {title} ({len(chunks)} chunks)")
    
    def retrieve_financial_concepts(
        self,
        query: str,
        category_filter: Optional[str] = None,
        difficulty_filter: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict]:
        """
        Retrieve relevant financial concepts
        
        Args:
            query: Search query (e.g., "How do I save for emergencies?")
            category_filter: Filter by category
            difficulty_filter: Filter by difficulty level
            top_k: Number of results to return
            
        Returns:
            List of relevant concept chunks with metadata
        """
        # Generate query embedding
        query_embedding = self._embed_text(query)
        
        # Build metadata filter
        where_filter = {}
        if category_filter:
            where_filter["category"] = category_filter
        if difficulty_filter:
            where_filter["difficulty"] = difficulty_filter
        
        # Query ChromaDB
        results = self.financial_concepts.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter if where_filter else None
        )
        
        # Format results
        concepts = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                metadata = results['metadatas'][0][i]
                concepts.append({
                    'content': results['documents'][0][i],
                    'title': metadata.get('title', 'Unknown'),
                    'category': metadata.get('category', 'general'),
                    'source': metadata.get('source', 'knowledge_base'),
                    'type': metadata.get('type', 'concept'),
                    'score': 1 - results['distances'][0][i],  # Convert distance to similarity
                    'metadata': metadata
                })
        
        return concepts
    
    # ==========================================
    # Player Decision History Index
    # ==========================================
    
    def index_player_decision(
        self,
        session_id: str,
        step: int,
        event_type: str,
        chosen_option: str,
        consequence: str,
        fi_score: float,
        age: int,
        education: str
    ):
        """
        Index a player's decision for future retrieval
        
        Args:
            session_id: Player session identifier
            step: Game step number
            event_type: Type of event (e.g., "budget_decision")
            chosen_option: Text of chosen option
            consequence: Outcome narrative
            fi_score: FI score after decision
            age: Player age
            education: Education path
        """
        # Combine for embedding
        decision_text = f"{event_type}: {chosen_option}. Result: {consequence}"
        
        # Generate embedding
        embedding = self._embed_text(decision_text, use_cache=False)
        
        # Store in ChromaDB
        doc_id = f"{session_id}_step_{step}"
        
        self.player_decisions.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[decision_text],
            metadatas=[{
                "session_id": session_id,
                "step": step,
                "event_type": event_type,
                "chosen_option": chosen_option,
                "fi_score": fi_score,
                "age": age,
                "education": education
            }]
        )
    
    def retrieve_similar_decisions(
        self,
        query: str,
        age: Optional[int] = None,
        education: Optional[str] = None,
        event_type: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Retrieve similar past player decisions
        
        Args:
            query: Current decision context
            age: Filter by similar age (±2 years)
            education: Filter by education path
            event_type: Filter by event type
            top_k: Number of results
            
        Returns:
            List of similar decision contexts
        """
        # Generate query embedding
        query_embedding = self._embed_text(query)
        
        # Build filter (ChromaDB doesn't support range queries easily)
        where_filter = {}
        if education:
            where_filter["education"] = education
        if event_type:
            where_filter["event_type"] = event_type
        
        # Query
        results = self.player_decisions.query(
            query_embeddings=[query_embedding],
            n_results=top_k * 2,  # Get more, filter by age manually
            where=where_filter if where_filter else None
        )
        
        # Format and filter results
        decisions = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                metadata = results['metadatas'][0][i]
                
                # Age filter (±2 years)
                if age and abs(metadata['age'] - age) > 2:
                    continue
                
                decisions.append({
                    'content': results['documents'][0][i],
                    'chosen_option': metadata['chosen_option'],
                    'fi_score': metadata['fi_score'],
                    'event_type': metadata['event_type'],
                    'score': 1 - results['distances'][0][i]
                })
                
                if len(decisions) >= top_k:
                    break
        
        return decisions
    
    def index_pdf_documents(self, pdf_directory: str):
        """
        Load PDFs and index them into RAG knowledge base (atomic operation)
        
        Args:
            pdf_directory: Path to folder containing PDF files
        """
        from pdf_loader import load_pdfs_with_pymupdf
        
        print(f"📚 Loading PDFs from {pdf_directory}...")
        
        # Load and chunk PDFs
        document_chunks = load_pdfs_with_pymupdf(pdf_directory)
        
        if not document_chunks:
            print("⚠️  No document chunks extracted from PDFs")
            return
        
        # Prepare batch data (atomic operation - all or nothing)
        print(f"🔄 Generating embeddings for {len(document_chunks)} chunks...")
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        for i, chunk in enumerate(document_chunks):
            # Generate embedding
            embedding = self._embed_text(chunk['content'], use_cache=False)
            
            # Collect for batch insert
            ids.append(chunk['id'])
            embeddings.append(embedding)
            documents.append(chunk['content'])
            metadatas.append({
                'title': chunk.get('title', 'Unknown'),
                'page': chunk.get('page', 0),
                'source': chunk['source'],
                'category': chunk.get('category', 'pdf_document'),
                'type': 'pdf',
                'difficulty': 'beginner'
            })
            
            # Progress indicator
            if (i + 1) % 50 == 0:
                print(f"   Processed {i + 1}/{len(document_chunks)} chunks...")
        
        # Single atomic batch insert
        print(f"💾 Inserting {len(ids)} chunks into ChromaDB (atomic)...")
        self.financial_concepts.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        print(f"✅ Indexed {len(document_chunks)} PDF chunks")
    
    def verify_pdf_indexing(self, expected_sources: list[str]) -> dict:
        """
        Verify PDFs were successfully indexed
        
        Args:
            expected_sources: List of expected PDF filenames
            
        Returns:
            dict with verification results
        """
        # Get all PDF documents
        pdf_docs = self.financial_concepts.get(
            where={'type': 'pdf'},
            include=['metadatas']
        )
        
        total_chunks = len(pdf_docs['ids'])
        
        # Count by source
        from collections import Counter
        sources = [m.get('source', 'unknown') for m in pdf_docs['metadatas']]
        source_counts = Counter(sources)
        
        # Check if expected sources are present
        missing = []
        found = {}
        for expected in expected_sources:
            matches = [src for src in source_counts.keys() if expected in src]
            if matches:
                found[expected] = sum(source_counts[m] for m in matches)
            else:
                missing.append(expected)
        
        return {
            'total_chunks': total_chunks,
            'sources': dict(source_counts),
            'found': found,
            'missing': missing,
            'success': len(missing) == 0
        }
    
    def clear_pdf_documents(self):
        """Remove all PDF documents from the knowledge base (keeps base concepts)"""
        pdf_docs = self.financial_concepts.get(
            where={'type': 'pdf'},
            include=['metadatas']
        )
        
        if pdf_docs['ids']:
            print(f"🗑️  Removing {len(pdf_docs['ids'])} existing PDF chunks...")
            self.financial_concepts.delete(ids=pdf_docs['ids'])
            print(f"✅ Cleared PDF documents")
        else:
            print(f"ℹ️  No PDF documents to clear")


# Global instance (initialized on app startup)
rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Dependency injection for FastAPI"""
    if not rag_service:
        raise Exception("RAG service not initialized")
    return rag_service
