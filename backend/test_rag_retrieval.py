"""
Test RAG retrieval to verify PDF indexing and knowledge retrieval
"""
import asyncio
from rag_service import RAGService
import os

async def test_retrieval():
    print("🧪 Testing RAG Retrieval")
    print("=" * 60)
    
    # Initialize RAG
    rag = RAGService(
        chroma_host=os.getenv("CHROMADB_HOST", "chromadb"),
        chroma_port=int(os.getenv("CHROMADB_PORT", "8000"))
    )
    
    # Check collection stats
    count = rag.financial_concepts.count()
    print(f"📊 Total documents in knowledge base: {count}")
    
    # Test queries
    test_queries = [
        "financial education games and learning",
        "student debt and loan management",
        "saving money and budgeting tips",
        "investing basics for beginners",
        "digital financial literacy"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        results = rag.retrieve_financial_concepts(query, top_k=3)
        
        if results:
            print(f"   Found {len(results)} relevant results:")
            for i, result in enumerate(results, 1):
                score = result['score']
                content_preview = result['content'][:100].replace('\n', ' ')
                source = result.get('source', 'knowledge_base')
                
                # Truncate source if it's a long filename
                if len(source) > 50:
                    source = "..." + source[-47:]
                
                print(f"   {i}. Score: {score:.3f} | Source: {source}")
                print(f"      Preview: {content_preview}...")
        else:
            print("   ⚠️  No results found")
    
    print("\n" + "=" * 60)
    print("✅ RAG retrieval test complete!")

if __name__ == "__main__":
    asyncio.run(test_retrieval())
