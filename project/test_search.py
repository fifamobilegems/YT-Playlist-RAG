import chromadb
from sentence_transformers import SentenceTransformer

from .config import CHROMA_COLLECTION_NAME, CHROMA_DIR, EMBEDDING_MODEL

def test_search(question: str) -> None:
    """Print most relevant stored k chunks for 1 qn"""
    model = SentenceTransformer(EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_collection(name=CHROMA_COLLECTION_NAME)

    query_embedding = model.encode_query(question).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        include=["documents", "metadatas", "distances"],
    )

    for document, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        print("\n---")
        print(f"Video: {metadata['title']}")
        print(f"Start: {metadata['start']:.1f}s")
        print(f"Distance: {distance:.3f}")
        print(document)

if __name__ == "__main__":
    test_search("Why does the speaker use a VLM instead of standard OCR for scanned PDFs?")