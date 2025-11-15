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

# Create a temporary Python script to check indexing
python3 << 'PYTHON_SCRIPT' > /tmp/check_index.txt 2>&1
import sys
try:
    from rag_service import RAGService
    import os
    # Suppress RAG initialization messages
    import io
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    rag = RAGService(chroma_host='chromadb', chroma_port=8000)
    result = rag.financial_concepts.get(where={'type': 'pdf'}, limit=1)
    
    sys.stdout = old_stdout
    count = len(result['ids']) if result and result.get('ids') else 0
    print(count)
    sys.exit(0)
except Exception as e:
    sys.stdout = old_stdout
    print(0)
    sys.exit(0)
PYTHON_SCRIPT

INDEXED_COUNT=$(cat /tmp/check_index.txt | tail -1)

# Check if we got a valid number
if [[ "$INDEXED_COUNT" =~ ^[0-9]+$ ]] && [ "$INDEXED_COUNT" -gt 0 ]; then
    echo "✅ Found PDF chunks already indexed - skipping re-indexing"
else
    echo "📚 No PDFs indexed yet - running indexing..."
    python3 /app/index_pdfs.py
fi

echo ""
echo "📦 Installing MCP Python SDK..."
pip3 install mcp --break-system-packages

echo ""
echo "🎮 Starting LifeSim backend server..."
echo "================================"
exec python3 /app/start_server.py
