"""
Test the new min_concepts logic in RAG retrieval
"""
from rag_service import RAGService
import os

def test_min_concepts():
    print("🧪 Testing min_concepts logic")
    print("=" * 80)
    
    # Initialize RAG
    rag = RAGService(
        chroma_host=os.getenv("CHROMADB_HOST", "chromadb"),
        chroma_port=int(os.getenv("CHROMADB_PORT", "8000"))
    )
    
    # Test queries with varying relevance
    test_cases = [
        ("financial education games and learning", "High relevance expected"),
        ("buying a car at age 25", "Medium relevance expected"),
        ("saving money and budgeting tips", "Low relevance expected"),
    ]
    
    for query, description in test_cases:
        print(f"\n{'='*80}")
        print(f"Query: '{query}'")
        print(f"Expected: {description}")
        print("-" * 80)
        
        # Retrieve top 5 concepts
        all_concepts = rag.retrieve_financial_concepts(query, top_k=5)
        
        if not all_concepts:
            print("❌ No concepts retrieved")
            continue
        
        print(f"📊 Retrieved {len(all_concepts)} concepts:")
        for i, c in enumerate(all_concepts, 1):
            print(f"  {i}. Score: {c['score']:.3f} - {c['title'][:60]}")
        
        # Apply filtering logic (same as in retrieve_rag_context)
        min_score = 0.4
        min_concepts = 3
        
        above_threshold = [c for c in all_concepts if c['score'] >= min_score]
        
        if len(above_threshold) >= min_concepts:
            filtered = above_threshold
            print(f"\n✅ Using {len(filtered)} concepts (all above threshold {min_score})")
        else:
            filtered = all_concepts[:min_concepts]
            above_count = len(above_threshold)
            below_count = len(filtered) - above_count
            print(f"\n✅ Using {len(filtered)} concepts: {above_count} above, {below_count} below threshold")
            print(f"   (Guaranteed minimum of {min_concepts} concepts)")
        
        for i, c in enumerate(filtered, 1):
            marker = "⭐" if c['score'] >= min_score else "📌"
            print(f"  {marker} {i}. Score: {c['score']:.3f}")

    print(f"\n{'='*80}")
    print("✅ Test complete!")

if __name__ == "__main__":
    test_min_concepts()
