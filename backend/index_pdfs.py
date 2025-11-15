"""
Script to index PDF documents into RAG knowledge base
Run: python backend/index_pdfs.py
"""
from rag_service import RAGService
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def index_all_pdfs():
    """Index all PDFs from knowledge/pdfs directory"""
    print("🚀 Starting PDF indexing...")
    print("=" * 60)
    
    # Initialize RAG
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
    
    # Path to PDFs
    pdf_dir = os.path.join(os.path.dirname(__file__), 'knowledge', 'pdfs')
    
    if not os.path.exists(pdf_dir):
        print(f"❌ PDF directory not found: {pdf_dir}")
        print("Creating directory...")
        os.makedirs(pdf_dir, exist_ok=True)
        print(f"✅ Created {pdf_dir}")
        print("📄 Add your PDF files there and run this script again")
        return
    
    # Check if PDFs exist
    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"⚠️  No PDF files found in {pdf_dir}")
        print(f"📄 Add PDF files to: {pdf_dir}")
        print("   Then run this script again to index them")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF files:")
    for pdf in pdf_files:
        print(f"   - {pdf}")
    print()
    
    # Index PDFs
    try:
        rag.index_pdf_documents(pdf_dir)
        
        # Verify indexing
        print("\n🔍 Verifying indexing...")
        verification = rag.verify_pdf_indexing(pdf_files)
        
        print(f"📊 Total PDF chunks: {verification['total_chunks']}")
        print(f"\n📄 Indexed sources:")
        for source, count in verification['found'].items():
            print(f"   ✅ {source}: {count} chunks")
        
        if verification['missing']:
            print(f"\n⚠️  Missing sources:")
            for source in verification['missing']:
                print(f"   ❌ {source}")
        
        print("\n" + "=" * 60)
        if verification['success']:
            print("✅ PDF indexing complete and verified!")
        else:
            print("⚠️  PDF indexing incomplete - some files missing")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ PDF indexing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    index_all_pdfs()
