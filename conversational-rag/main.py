from fastapi import FastAPI
from typing import Dict
from schemas import BookingRequest,ChatRequest
from database import Base, engine, SessionLocal
from models import Booking
from redis_client import add_message, get_history

Base.metadata.create_all(bind= engine)
app = FastAPI(title="Conversational RAG API")

@app.get("/")
def root() -> Dict[str, str]:
    return {"message":"API is running"}

@app.post("/chat/")
def chat(request: ChatRequest) -> Dict[str, list | str]:
    session_id = request.session_id
    query = request.query
    history = get_history(session_id)
    response = generate_response(query, history)
    add_message(session_id, query)
    add_message(session_id, response)
    return {"response": response, "history": history}

@app.post("/book/")
def book_interview(request: BookingRequest) -> Dict[str, str | int]:
    db = SessionLocal()
    booking = Booking(
        name= request.name,
        email = request.email,
        date = request.date,
        time= request.time
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)
    db.close()
    return {"message":"Booking Confirmed","booking_id":booking.id}
