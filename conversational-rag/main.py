from fastapi import FastAPI, UploadFile, File, Form
from typing import Dict
from schemas import BookingRequest, ChatRequest
from database import Base, engine, SessionLocal
from models import Booking, Document
from redis_client import add_message, get_history
from ingestion import extract_text_from_pdf, chunk_text, add_to_vector_db, qdrant, embed_text
import shutil
from pathlib import Path

# Create uploads folder
UPLOAD_FOLDER = Path("./uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Initialize DB
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(title="Conversational RAG API")


@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "API is running"}


@app.post("/upload-document/")
def upload_document(file: UploadFile = File(...), strategy: str = Form("fixed")) -> Dict[str, str]:
    """Upload a PDF or TXT and add chunks to Qdrant & SQL DB."""
    file_path = UPLOAD_FOLDER / file.filename
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Extract text
    if file.filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file.filename.endswith(".txt"):
        text = file_path.read_text(encoding="utf-8")
    else:
        return {"error": "Only PDF or TXT files are supported."}

    # Chunk text using chosen strategy
    chunks = chunk_text(text, strategy=strategy)

    # Add chunks to Qdrant & SQL DB
    add_to_vector_db(chunks, file.filename)

    return {"message": f"{file.filename} uploaded and processed successfully. {len(chunks)} chunks added."}


@app.post("/chat/")
def chat(request: ChatRequest) -> Dict[str, list | str]:
    """Multi-turn conversational RAG."""
    session_id = request.session_id
    query = request.query
    history = get_history(session_id)

 
    query_vector = embed_text(query)
    results = qdrant.search(
        collection_name="documents",
        query_vector=query_vector,
        limit=3 
    )
    chunks = [res.payload["text"] for res in results]

   
    response = " ".join(chunks) if chunks else "Sorry. I don't have that information"

  
    add_message(session_id, query)
    add_message(session_id, response)

    return {"response": response, "history": history}


@app.post("/book/")
def book_interview(request: BookingRequest) -> Dict[str, str | int]:
    """Store booking info in SQL DB."""
    db = SessionLocal()
    booking = Booking(
        name=request.name,
        email=request.email,
        date=request.date,
        time=request.time
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    db.close()
    return {"message": "Booking Confirmed", "booking_id": booking.id}
