"""
QA Chain - Question Answering with RAG (Gemini Version)
"""
from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QAChain:
    def __init__(self, vectorstore, model_name: str = "gemini-pro",
                 temperature: float = 0.2, max_tokens: int = 1000):
        
        # Use Google Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            max_output_tokens=max_tokens,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        self.prompt_template = """당신은 문서를 기반으로 질문에 답변하는 AI 어시스턴트입니다.
제공된 컨텍스트를 사용하여 질문에 정확하게 답변하세요.
컨텍스트에 답이 없으면 "제공된 문서에서 해당 정보를 찾을 수 없습니다"라고 답변하세요.

컨텍스트: {context}

질문: {question}

답변:"""
        
        self.prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context", "question"]
        )        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.prompt}
        )
    
    def ask(self, question: str) -> Dict:
        try:
            logger.info(f"Processing question: {question}")
            result = self.qa_chain({"query": question})
            
            response = {
                "answer": result["result"],
                "sources": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata
                    }
                    for doc in result["source_documents"]
                ]
            }
            
            logger.info("Question answered successfully")
            return response
        except Exception as e:
            logger.error(f"Error during QA: {e}")
            raise
