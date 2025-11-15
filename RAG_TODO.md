# RAG System Implementation TODO

**Goal:** Add Retrieval-Augmented Generation to LifeSim backend for contextual, personalized financial education

**Stack:** Google Gemini Embeddings + ChromaDB + PyMuPDF

**Knowledge Sources:**

- Helsinki Education Hub: https://www.helsinki.fi/en/networks/helsinki-education-hub
- DigiConsumers Finland: https://digiconsumers.fi/en/home/
- Manual PDF uploads (financial literacy, Finnish banking/tax guides)

---

## 📋 PHASE 1: Infrastructure Setup

### ✅ Docker & Dependencies

- [ ] Add ChromaDB service to `docker-compose.yml`

  - Image: `chromadb/chroma:latest`
  - Port: 8001:8000
  - Volume: `chromadb_data`
  - Network: `app-network`

- [ ] Update `backend/requirements.txt`

  - Add `chromadb>=0.4.22`
  - Add `langchain>=0.1.0`
  - Add `langchain-community>=0.0.20`
  - Add `pymupdf>=1.23.0` (better table extraction than pypdf)

- [ ] Rebuild and start containers

  - Run `docker-compose down`
  - Run `docker-compose build`
  - Run `docker-compose up -d`

- [ ] Verify ChromaDB is running
  - Check `docker-compose ps` shows chromadb healthy
  - Test connection to `http://localhost:8001`

---

## 📋 PHASE 2: RAG Service Module

### ✅ Create `backend/rag_service.py`

- [ ] Create file structure with imports

  - chromadb, google.genai, typing, json, os, dotenv

- [ ] Implement `RAGService` class initialization

  - Connect to ChromaDB (host="chromadb", port=8000)
  - Initialize Gemini client with API key
  - Create/get collections: `financial_concepts`, `player_decisions`
  - Add error handling for missing API key
  - Initialize in-memory embedding cache (dict with LRU, max 100 entries)

- [ ] Implement `_embed_text()` method

  - Call Gemini `models/text-embedding-004`
  - Extract embedding vector (768 dims)
  - Return list of floats

- [ ] Implement `_chunk_text()` method

  - Split text into 500 char chunks with 50 char overlap
  - Try to break at sentence boundaries
  - Return list of text chunks

- [ ] Implement `index_financial_concept()` method

  - Accept: concept_id, title, content, category, difficulty, age_relevance
  - Chunk content if > 500 chars
  - Generate embeddings for each chunk
  - Store in ChromaDB `financial_concepts` collection
  - Include metadata (title, category, difficulty, etc.)

- [ ] Implement `retrieve_financial_concepts()` method

  - Accept: query, category_filter, difficulty_filter, top_k
  - Generate query embedding
  - Query ChromaDB with filters
  - Return formatted results with content, title, score, metadata

- [ ] Implement `index_player_decision()` method

  - Accept: session_id, step, event_type, chosen_option, consequence, fi_score, age, education
  - Combine text: "event_type: chosen_option. Result: consequence"
  - Generate embedding
  - Store in ChromaDB `player_decisions` collection

- [ ] Implement `retrieve_similar_decisions()` method

  - Accept: query, age, education, event_type, top_k
  - Generate query embedding
  - Query ChromaDB with filters
  - Filter by age range (±2 years) manually
  - Return formatted decision contexts

- [ ] Add global instance and `get_rag_service()` helper
  - Create module-level `rag_service` variable
  - Implement dependency injection function

---

## 📋 PHASE 3: Knowledge Base Content

### ✅ Create PDF loader (`backend/pdf_loader.py`)

- [ ] Implement PyMuPDF-based `load_pdfs_with_pymupdf()`

  - Use `fitz` (PyMuPDF) to open PDFs
  - Extract text with `page.get_text("text")` to preserve table layout
  - Iterate through all pages in directory
  - Use RecursiveCharacterTextSplitter (500 chars, 50 overlap)
  - Return formatted document chunks with page numbers

- [ ] Implement `load_single_pdf()` helper
  - Load single PDF file with PyMuPDF
  - Preserve table structure and layout
  - Chunk and return formatted

### ✅ Create knowledge base directory structure

- [ ] Create `backend/knowledge/pdfs/` directory
- [ ] Add placeholder `.gitkeep` file
- [ ] User will manually download and add PDFs (financial guides, tax docs, etc.)

### ✅ Create knowledge base JSON

- [ ] Create `backend/knowledge_base.json` with 50-100 concepts
- [ ] Source content from:

  - Helsinki Education Hub: https://www.helsinki.fi/en/networks/helsinki-education-hub
  - DigiConsumers Finland: https://digiconsumers.fi/en/home/
  - Research and curate Finnish-specific financial literacy content

- [ ] Include concept categories:
  - **Saving:** Emergency funds, budgeting (50/30/20 rule), savings accounts
  - **Investing:** Compound interest, index funds, ETFs, risk/return tradeoff
  - **Debt:** Repayment strategies (avalanche/snowball), interest rates, student loans
  - **Finnish Specifics:** Tax system, Kela benefits, banking (Nordea/OP), pension system
  - **Behavioral Finance:** Loss aversion, FOMO, delayed gratification, sunk cost fallacy
  - **Career & Income:** Salary negotiation, side hustles, passive income
  - **Life Planning:** Work-life balance, major purchases (housing/car), insurance
  - **Digital Finance:** Online banking security, investment apps, crypto awareness

### ✅ Create indexing script

- [ ] Create `backend/index_knowledge.py`

  - Load concepts from JSON
  - Initialize RAG service (localhost:8001 for testing)
  - Index each concept into ChromaDB
  - Print progress and summary

- [ ] Create `backend/index_pdfs.py`

  - Check if `knowledge/pdfs/` directory exists
  - List all PDF files
  - Use PyMuPDF loader to extract text with table preservation
  - Call `rag.index_pdf_documents()`
  - Print progress and summary (pages processed, chunks created)

- [ ] Add API endpoint `/api/admin/reindex` (optional for Phase 3)
  - Endpoint to trigger manual re-indexing
  - Clear and rebuild ChromaDB collections
  - Useful after adding new PDFs

---

## 📋 PHASE 4: Backend Integration

### ✅ Update `backend/main.py`

- [ ] Add imports

  - `from rag_service import RAGService, get_rag_service`
  - `import rag_service as rag_module`

- [ ] Modify `lifespan()` function

  - After `await init_db()`, initialize RAG service
  - `rag_module.rag_service = RAGService(chroma_host="chromadb", chroma_port=8000)`
  - Add try/except with warning if RAG fails
  - Print success message

- [ ] Update `/api/step` endpoint - Add decision indexing

  - After `db_session.commit()` (around line 565)
  - Try to get RAG service
  - Call `rag.index_player_decision()` with session data
  - Add try/except (non-fatal error)
  - Print success/failure message

- [ ] Index existing player decisions from database
  - Create `backend/index_existing_decisions.py` script
  - Query all DecisionHistory records from SQLite
  - Loop through and call `rag.index_player_decision()` for each
  - Backfill player decision embeddings for RAG context
  - Run once after RAG service is initialized

### ✅ Update `backend/ai_narrative.py`

- [ ] Add import: `from rag_service import get_rag_service`

- [ ] Modify `generate_learning_moment()` function

  - Replace 30% random logic with RAG-based retrieval
  - Build query from chosen_option + player context
  - Call `rag.retrieve_financial_concepts(query, top_k=2)`
  - Check if score > 0.7 (relevance threshold)
  - If relevant concept found, build enhanced prompt with retrieved context
  - Pass to Gemini for tip generation
  - Keep fallback to None if no relevant concepts
  - Wrap in try/except for RAG failures

- [ ] (Optional) Enhance `generate_consequence_narrative()`

  - Retrieve similar past player decisions
  - Add peer comparison context to prompt
  - "Players similar to you typically..."

- [ ] (Optional) Enhance `generate_event_narrative()`
  - Retrieve player's last 3-5 decisions
  - Add continuity references to prompt
  - "Remember when you..."

---

## 📋 PHASE 5: Testing & Validation

### ✅ Manual Testing

- [ ] Start services: `docker-compose up --build`
- [ ] Verify ChromaDB logs show successful startup
- [ ] Verify backend logs show "✅ RAG Service initialized"

- [ ] Index knowledge base

  - Run: `docker-compose exec backend python index_knowledge.py`
  - Verify: "✅ Indexed X concepts" message
  - Check ChromaDB has documents

- [ ] Test retrieval in Python console

  ```python
  docker-compose exec backend python
  >>> from rag_service import RAGService
  >>> rag = RAGService(chroma_host="chromadb", chroma_port=8000)
  >>> results = rag.retrieve_financial_concepts("emergency fund", top_k=3)
  >>> print(results[0]['title'])
  >>> print(results[0]['score'])
  ```

- [ ] Play through game (frontend)

  - Start new game
  - Make 3-5 decisions
  - Watch backend logs for:
    - "💡 Learning moment (RAG-enhanced): ..."
    - "✅ Indexed decision for RAG (step X)"
  - Verify learning moments are contextually relevant

- [ ] Test with PDFs (if available)
  - Add PDF to `backend/knowledge/pdfs/`
  - Run: `docker-compose exec backend python index_pdfs.py`
  - Verify chunks indexed
  - Play game and check if PDF content appears in tips

### ✅ Performance Testing

- [ ] Measure retrieval latency

  - Add timing logs to RAG service
  - Target: <200ms per retrieval
  - Check Gemini API embedding time
  - Check ChromaDB query time

- [ ] Test with multiple concurrent players
  - Start 3-5 game sessions
  - Make decisions simultaneously
  - Verify no race conditions
  - Check ChromaDB handles concurrent writes

### ✅ Error Handling

- [ ] Test ChromaDB connection failure

  - Stop chromadb: `docker-compose stop chromadb`
  - Restart backend
  - Verify game still works (RAG disabled gracefully)
  - Check logs for warning message

- [ ] Test Gemini API failure

  - Remove GEMINI_API_KEY temporarily
  - Verify RAG service shows warning
  - Verify game falls back to original behavior

- [ ] Test empty knowledge base
  - Clear ChromaDB collections
  - Make game decision
  - Verify no learning moments generated (no crashes)

---

## 📋 PHASE 6: Optimization & Enhancement

### ✅ Performance Improvements

- [ ] Cache frequent embeddings (in-memory)

  - Identify common queries ("emergency fund", "save money", etc.)
  - Store query embeddings in Python dict cache
  - LRU cache with max 100 entries
  - Reduce Gemini API calls by ~40-60%
  - **Note:** Redis upgrade planned if time permits

- [ ] Batch embedding operations

  - Embed multiple chunks in single API call if Gemini supports
  - Use Gemini batch endpoint if available
  - Otherwise, keep sequential for reliability

- [ ] Add embedding queue for decision indexing
  - Index player decisions asynchronously (background task)
  - Don't block game flow (<100ms overhead target)
  - Use asyncio.create_task() for non-blocking indexing

### ✅ Content Expansion

- [ ] Expand financial concepts in JSON (target: 50-100 concepts)

  - Research Helsinki Education Hub content
  - Research DigiConsumers Finland resources
  - Finnish-specific content (Kela, OP bank, Nordea, tax system)
  - Age-specific advice (18-25 vs 25-30 vs 30+)
  - Education path variations (vocational vs university vs high school)
  - City-specific cost of living (Helsinki vs Oulu vs Tampere)

- [ ] Manually add PDF documents to `backend/knowledge/pdfs/`

  - Finnish tax authority (Vero.fi) guides
  - Banking institution guides (Nordea, OP, Danske Bank)
  - FIRE movement resources (Mr. Money Mustache, etc.)
  - Investment primers (Bogleheads, Vanguard guides)
  - Consumer protection guides from DigiConsumers

- [ ] Add behavioral finance concepts
  - Loss aversion
  - Sunk cost fallacy
  - FOMO and peer pressure
  - Delayed gratification

### ✅ Advanced Features

- [ ] Implement player pattern recognition

  - Aggregate decision history across all players
  - Identify successful strategies (high FI score patterns)
  - Surface insights: "Top players at step 5 typically..."

- [ ] Add conversation history context

  - Store last 5 learning moments per player
  - Avoid repeating same tips
  - Progressive difficulty (beginner → advanced concepts)

- [ ] Implement A/B testing

  - Track learning moment effectiveness
  - Measure: decision quality improvement after tips
  - Compare RAG vs non-RAG outcomes

- [ ] Add admin endpoint for content management
  - `/api/admin/index-knowledge` endpoint
  - Upload PDFs via API
  - Trigger re-indexing

---

## 📋 PHASE 7: Documentation & Deployment

### ✅ Documentation

- [ ] Add RAG architecture diagram to `docs/`
- [ ] Document embedding model choice rationale
- [ ] Create knowledge base contribution guide
- [ ] Add troubleshooting section (ChromaDB connection, etc.)

### ✅ Production Readiness

- [ ] Add health check for ChromaDB to `/health` endpoint
- [ ] Implement RAG metrics logging (retrieval latency, hit rate)
- [ ] Add environment variable for ChromaDB host (prod vs dev)
- [ ] Create backup/restore scripts for ChromaDB data
- [ ] Add monitoring alerts for RAG service failures

### ✅ Cleanup

- [ ] Remove debug print statements
- [ ] Add proper logging with levels (INFO, WARNING, ERROR)
- [ ] Update README.md with RAG setup instructions
- [ ] Create demo video showing RAG-enhanced learning moments

---

## 🎯 Success Criteria

- [ ] ChromaDB successfully stores 50+ financial concepts
- [ ] Learning moments appear 60%+ of time (when relevant concepts exist)
- [ ] Learning moment relevance score > 0.75 average
- [ ] RAG retrieval adds < 200ms latency to game flow
- [ ] Player decisions indexed within 100ms (non-blocking)
- [ ] Game works gracefully if RAG service unavailable
- [ ] No crashes or errors during normal gameplay

---

## 📝 Notes

**Decisions Made:**

- ✅ PDF source: Manual download by user (banking guides, tax docs, DigiConsumers, Helsinki Education Hub)
- ✅ Index decision history: YES - create script to backfill existing DecisionHistory table
- ✅ Re-indexing endpoint: YES - add `/api/admin/reindex` endpoint
- ✅ Embedding cache: In-memory (Python dict with LRU, max 100 entries). Redis upgrade if time permits.
- ✅ Knowledge base size: 50-100 concepts in JSON, unlimited PDFs (user-provided)
- ✅ PDF library: PyMuPDF (better table extraction than pypdf)

**Dependencies:**

- GEMINI_API_KEY must be set
- ChromaDB must be accessible on network
- Docker volumes persist between restarts

**Rollback Plan:**

- If RAG causes issues, comment out initialization in `main.py`
- Game falls back to original 30% random learning moments
- No database migrations needed (RAG is additive only)
