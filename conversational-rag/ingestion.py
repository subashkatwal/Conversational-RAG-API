from typing import List
from PyPDF2 import PdfReader
import re
from pathlib import Path
import uuid
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams
from models import Document
from database import SessionLocal

model = SentenceTransformer("all-MiniLM-L6-v2")

qdrant = QdrantClient(url="http://localhost:6333")

if not qdrant.get_collections().collections:
    qdrant.recreate_collection(
        collection_name="documents",
        vectors_config=VectorParams(size=384, distance="Cosine")
    )



def extract_text_from_pdf(file_path: str)-> str:
    reader = PdfReader(file_path)
    return " ".join(page.extract_text() for page in reader.pages)

def extract_text_from_txt(file_path: str) -> str:
    path = Path(file_path)
    return path.read_text(encoding="utf-8")

def chunk_text_fixed(text: str, chunk_size: int = 500) -> List[str]:
    """ Split text into fixed-size character chunks."""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def chunk_text_semantic(text: str, max_words: int = 50) -> List[str]:
    """Split text into chunks by sentences, max_words per chunk."""
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks, current_chunk, current_words = [], [], 0

    for sentence in sentences:
        words = sentence.split()
        if current_words + len(words) > max_words:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            current_chunk = words
            current_words = len(words)
        else:
            current_chunk.extend(words)
            current_words += len(words)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def chunk_text(text: str, strategy: str = "fixed") -> List[str]:
    """Choose chunking strategy: 'fixed' or 'semantic'."""
    if strategy == "fixed":
        return chunk_text_fixed(text)
    elif strategy == "semantic":
        return chunk_text_semantic(text)
    else:
        raise ValueError("Invalid strategy. Use 'fixed' or 'semantic'.")


def embed_text(text: str) -> List[float]:
    return model.encode(text).tolist()


def retrieve_chunks(query: str, top_k: int = 2) -> list[str]:
    query_vector = embed_text(query)

    results = qdrant.search(
        collection_name="documents",
        query_vector=query_vector,
        limit=top_k
    )

    return [res.payload["text"] for res in results]

def add_to_vector_db(chunks: List[str], filename: str) -> None:
    db = SessionLocal()
    for chunk in chunks:
        vector = embed_text(chunk)
        chunk_id = str(uuid.uuid4())

        # Store in Qdrant
        qdrant.upsert(
            collection_name="documents",
            points=[{
                "id": chunk_id,
                "vector": vector,
                "payload": {"text": chunk, "filename": filename}
            }]
        )

        # Store metadata in SQL DB
        doc = Document(filename=filename, content=chunk)
        db.add(doc)
    db.commit()
    db.close()