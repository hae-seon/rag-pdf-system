"""
Example: Simple usage of RAG System
간단한 사용 예제
"""
import sys
import os
from pathlib import Path

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from main import RAGSystem
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    print("=" * 50)
    print("RAG PDF System - Simple Example")
    print("=" * 50)
    print()
    
    # Initialize system
    print("📚 Initializing RAG system...")
    rag = RAGSystem()
    
    # Check if PDF exists
    pdf_path = "./data/pdfs/sample.pdf"
    if not Path(pdf_path).exists():
        print(f"⚠️  PDF file not found: {pdf_path}")
        print("Please place a PDF file in data/pdfs/ directory")
        print()
        print("Example usage:")
        print("  1. Place your PDF in: data/pdfs/")
        print("  2. Update pdf_path variable in this script")
        print("  3. Run this script again")
        return
    
    # Process PDF
    print(f"📄 Processing PDF: {pdf_path}")
    rag.ingest_pdf(pdf_path)
    print("✅ PDF processed successfully!")
    print()
    
    # Example questions
    questions = [
        "이 문서의 주요 내용은 무엇인가요?",
        "핵심 포인트를 3가지만 알려주세요.",
    ]    
    # Ask questions
    for i, question in enumerate(questions, 1):
        print(f"\n❓ Question {i}: {question}")
        print("-" * 50)
        
        result = rag.query(question)
        
        print(f"💬 Answer:")
        print(result['answer'])
        print()
        
        print(f"📎 Sources: {len(result['sources'])} documents found")
        for j, source in enumerate(result['sources'][:2], 1):  # Show first 2 sources
            print(f"  Source {j}: Page {source['metadata'].get('page', 'N/A')}")
        print()
    
    print("=" * 50)
    print("✅ Example completed!")
    print("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check if .env file exists with valid OPENAI_API_KEY")
        print("2. Make sure PDF file exists in data/pdfs/")
        print("3. Check if all dependencies are installed")
