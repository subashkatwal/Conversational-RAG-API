from sqlalchemy import Column, Integer, String,DateTime
from datetime import datetime
from database import Base 

class Booking(Base):
    __tablename__= "bookings"
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String)
    email = Column(String)
    date= Column(DateTime)
    time = Column(String)

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    content = Column(String) 
    uploaded_at = Column(DateTime, default=datetime.now)