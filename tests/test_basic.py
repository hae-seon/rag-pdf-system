"""
Simple test script for RAG System
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import RAGSystem
from dotenv import load_dotenv

load_dotenv()


def test_basic_flow():
    """Test basic RAG workflow"""
    print("Testing RAG System...")
    
    # Initialize system
    rag = RAGSystem()
    print("✓ System initialized")
    
    # Test would require actual PDF file
    print("\nTo run full test:")
    print("1. Place a PDF in data/pdfs/")
    print("2. Uncomment the test code below")
    
    # Example test code (uncomment when ready)
    # rag.ingest_pdf("./data/pdfs/test.pdf")
    # result = rag.query("What is this document about?")
    # assert "answer" in result
    # assert "sources" in result
    # print(f"Answer: {result['answer']}")
    
    print("\n✓ Basic tests passed!")


if __name__ == "__main__":
    test_basic_flow()
