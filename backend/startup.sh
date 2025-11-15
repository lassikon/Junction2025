#!/bin/bash
# Startup script for backend container

echo "🚀 Backend startup script"
echo "================================"

# Wait for ChromaDB to be ready
echo "⏳ Waiting for ChromaDB to be ready..."
for i in {1..30}; do
    if curl -s http://chromadb:8000/api/v1/heartbeat > /dev/null 2>&1; then
        echo "✅ ChromaDB is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  ChromaDB not responding after 30 seconds, continuing anyway..."
        break
    fi
    sleep 1
done

# Check if PDFs are already indexed
echo ""
echo "🔍 Checking if PDFs are indexed..."
INDEXED_COUNT=$(python3 -c "from rag_service import RAGService; import os; os.environ.setdefault('GEMINI_API_KEY', 'check'); rag = RAGService(chroma_host='chromadb', chroma_port=8000); result = rag.financial_concepts.get(where={'type': 'pdf'}); print(len(result['ids']) if result['ids'] else 0)" 2>/dev/null)

if [ "$INDEXED_COUNT" -gt 0 ]; then
    echo "✅ Found $INDEXED_COUNT PDF chunks already indexed - skipping indexing"
else
    echo "📚 No PDFs indexed yet - running indexing..."
    python3 /app/index_pdfs.py
fi

echo ""
echo "🎮 Starting LifeSim backend server..."
echo "================================"
exec python3 /app/start_server.py
