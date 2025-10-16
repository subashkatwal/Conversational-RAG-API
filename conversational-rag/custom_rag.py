from typing import List 
from ingestion import embed_text
from qdrant_client import QdrantClient
knowledge_base = []

qdrant = QdrantClient(url="http://localhost:6333")
def add_to_Kb(chunks:List[str])->None:
    knowledge_base.extend(chunks)

def retrieve_chunks(query: str, top_k: int = 2) -> list[str]:
    query_vector = embed_text(query)
    
    # Search in Qdrant
    results = qdrant.search(
        collection_name="documents",
        query_vector=query_vector,
        limit=top_k
    )
    return [res.payload["text"] for res in results]

def generate_response(query: str, history: list[str]) -> str:
    chunks = retrieve_chunks(query)
    if not chunks:
        return "Sorry. I don't have that information"
    return " ".join(chunks)
