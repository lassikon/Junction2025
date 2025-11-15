"""
Script to populate RAG knowledge base with financial concepts
Run: python backend/index_knowledge.py
"""
import json
from rag_service import RAGService
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def index_knowledge_base():
    """Load and index all financial concepts from JSON"""
    print("🚀 Starting knowledge base indexing...")
    print("=" * 60)
    
    # Initialize RAG service (use localhost for testing outside Docker)
    try:
        # Try Docker network name first
        rag = RAGService(chroma_host="chromadb", chroma_port=8000)
    except Exception as e:
        print(f"Failed to connect to Docker chromadb, trying localhost...")
        try:
            rag = RAGService(chroma_host="localhost", chroma_port=8001)
        except Exception as e2:
            print(f"❌ Failed to connect to ChromaDB: {e2}")
            print("Make sure ChromaDB is running: docker-compose ps")
            return
    
    # Load concepts from JSON
    json_path = os.path.join(os.path.dirname(__file__), 'knowledge_base.json')
    
    if not os.path.exists(json_path):
        print(f"❌ knowledge_base.json not found at {json_path}")
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    concepts = data.get('concepts', [])
    print(f"📚 Found {len(concepts)} concepts to index\n")
    
    # Index each concept
    success_count = 0
    for i, concept in enumerate(concepts, 1):
        try:
            rag.index_financial_concept(
                concept_id=concept['id'],
                title=concept['title'],
                content=concept['content'],
                category=concept['category'],
                difficulty=concept.get('difficulty', 'beginner'),
                age_relevance=concept.get('age_relevance')
            )
            success_count += 1
            print(f"  [{i}/{len(concepts)}] ✅ {concept['title']}")
        except Exception as e:
            print(f"  [{i}/{len(concepts)}] ❌ Failed to index {concept.get('title', 'Unknown')}: {e}")
    
    print("\n" + "=" * 60)
    print(f"✅ Indexing complete!")
    print(f"   Successful: {success_count}/{len(concepts)}")
    print(f"   Failed: {len(concepts) - success_count}/{len(concepts)}")
    print("=" * 60)

if __name__ == "__main__":
    index_knowledge_base()
