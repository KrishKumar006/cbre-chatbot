# main.py - Free Local Backend with ChromaDB (no API costs!)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Check if packages are installed
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain_community.llms import HuggingFaceHub
    from langchain.schema import SystemMessage, HumanMessage, AIMessage
except ImportError:
    print("⚠️ Please install requirements first:")
    print("   pip install -r requirements.txt sentence-transformers")
    exit(1)

app = FastAPI(title="CBRE Chatbot API")

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("🔧 Initializing AI components...")

# Initialize FREE local embeddings (no API key needed!)
print("📦 Loading local embedding model...")
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)
print("✅ Embeddings ready!")

# For the LLM, we'll use a simple rule-based response for now
# (You can add Ollama or HuggingFace API later if you want)
def generate_response(query: str, context: str) -> str:
    """Simple response generator using context"""
    if context and context != "No documents in database yet. Using general knowledge.":
        return f"Based on CBRE's information: {context[:500]}\n\nIs there anything specific you'd like to know more about?"
    else:
        return "I don't have specific information about that in my database yet. Please make sure you've run 'python ingest_data.py' to load the CBRE documents first."

# Initialize ChromaDB (runs locally, no Docker!)
vectorstore = None
try:
    print("📚 Setting up local vector database...")
    vectorstore = Chroma(
        collection_name="cbre_docs",
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )
    print("✅ Vector database ready!")
except Exception as e:
    print(f"⚠️ Database setup failed: {e}")

# Data models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    conversation_history: Optional[List[Message]] = []

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = []
    timestamp: str

# Routes
@app.get("/")
async def root():
    return {
        "message": "CBRE Chatbot API is running! 🚀",
        "status": "healthy",
        "mode": "FREE LOCAL (No API costs!)",
        "endpoints": {
            "chat": "/chat",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database_ready": vectorstore is not None,
        "documents_count": vectorstore._collection.count() if vectorstore else 0
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint"""
    try:
        # Search for relevant documents
        sources = []
        context = ""
        
        if vectorstore and vectorstore._collection.count() > 0:
            try:
                # Search database for relevant info
                print(f"🔍 Searching for: {request.query[:50]}...")
                results = vectorstore.similarity_search(request.query, k=3)
                context = "\n\n".join([doc.page_content for doc in results])
                sources = [doc.page_content[:150] + "..." for doc in results]
                print(f"✅ Found {len(results)} relevant documents")
            except Exception as e:
                print(f"Search error: {e}")
                context = "No relevant documents found."
        else:
            context = "No documents in database yet. Using general knowledge."
        
        # Generate response
        print(f"💬 Generating response...")
        response_text = generate_response(request.query, context)
        print(f"✅ Response generated!")
        
        return ChatResponse(
            response=response_text,
            sources=sources,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 CBRE Chatbot API Starting (FREE LOCAL MODE)")
    print("="*60)
    print(f"📍 API: http://localhost:8000")
    print(f"📖 Docs: http://localhost:8000/docs")
    print(f"💾 Database: {'✅ Ready' if vectorstore else '⚠️ Not initialized'}")
    print(f"💰 Cost: $0.00 (Running locally!)")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)