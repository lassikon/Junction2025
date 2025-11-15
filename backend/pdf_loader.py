"""
PDF document loader for RAG knowledge base
Uses PyMuPDF (fitz) for better table extraction and layout preservation
"""
import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict
import os


def load_pdfs_with_pymupdf(pdf_directory: str) -> List[Dict]:
    """
    Load PDFs using PyMuPDF (preserves table structure)
    
    Args:
        pdf_directory: Path to folder with PDFs
        
    Returns:
        List of document chunks ready for embedding
    """
    documents = []
    
    if not os.path.exists(pdf_directory):
        print(f"⚠️ PDF directory not found: {pdf_directory}")
        return documents
    
    pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"⚠️ No PDF files found in {pdf_directory}")
        return documents
    
    print(f"📄 Found {len(pdf_files)} PDF files")
    
    for filename in pdf_files:
        pdf_path = os.path.join(pdf_directory, filename)
        
        try:
            # Open PDF with PyMuPDF
            doc = fitz.open(pdf_path)
            
            full_text = []
            page_count = len(doc)  # Store page count before closing
            for page_num in range(page_count):
                page = doc[page_num]
                
                # Extract text with layout preservation (maintains table structure)
                text = page.get_text("text")
                
                if text.strip():
                    full_text.append(f"--- Page {page_num + 1} ---\n{text}")
            
            doc.close()
            
            # Combine all pages
            combined_text = "\n\n".join(full_text)
            
            # Chunk the text
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            
            chunks = text_splitter.split_text(combined_text)
            
            # Format chunks
            for i, chunk in enumerate(chunks):
                documents.append({
                    'id': f"{filename.replace('.pdf', '')}_{i}",
                    'content': chunk,
                    'source': filename,
                    'title': filename.replace('.pdf', '').replace('_', ' '),
                    'category': 'financial_education',
                    'page': i  # Approximate page (chunk index)
                })
            
            print(f"  ✅ {filename}: {page_count} pages → {len(chunks)} chunks")
            
        except Exception as e:
            print(f"  ❌ Failed to load {filename}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"📚 Total: {len(documents)} chunks from {len(pdf_files)} PDFs")
    return documents


def load_single_pdf(pdf_path: str) -> List[Dict]:
    """
    Load and chunk a single PDF file
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        List of document chunks
    """
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return []
    
    try:
        filename = os.path.basename(pdf_path)
        
        # Open with PyMuPDF
        doc = fitz.open(pdf_path)
        
        full_text = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            
            if text.strip():
                full_text.append(f"--- Page {page_num + 1} ---\n{text}")
        
        doc.close()
        
        # Chunk
        combined_text = "\n\n".join(full_text)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        chunks = text_splitter.split_text(combined_text)
        
        # Format
        documents = []
        for i, chunk in enumerate(chunks):
            documents.append({
                'id': f"{filename.replace('.pdf', '')}_{i}",
                'content': chunk,
                'source': filename,
                'title': filename.replace('.pdf', '').replace('_', ' '),
                'category': 'financial_education',
                'page': i
            })
        
        print(f"✅ Loaded {filename}: {len(doc)} pages → {len(chunks)} chunks")
        return documents
        
    except Exception as e:
        print(f"❌ Error loading {pdf_path}: {e}")
        return []
