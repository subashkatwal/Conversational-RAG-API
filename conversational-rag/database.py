from sqlalchemy import create_engine 
from sqlalchemy.orm import declarative_base, sessionmaker

Database_url = "sqlite:///./bookings.db"

engine = create_engine(Database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind= engine, autocommit= False, autoflush=False)
Base = declarative_base()