import chromadb
from sentence_transformers import SentenceTransformer

from .config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_DIR,
    EMBEDDING_MODEL,
    TOP_K
)

def get_collection():
    """Open existing local chroma collection"""
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_collection(name=CHROMA_COLLECTION_NAME)

def retrieve_chunks(question: str, top_k: int) -> list[dict]:
    """Retrive the most semantically relevant k chunks"""
    model = SentenceTransformer(EMBEDDING_MODEL)
    collection = get_collection()

    query_embedding = model.encode_query(question).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []

    for document, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append(
            {
                "text": document,
                "video_id": metadata["video_id"],
                "title": metadata["title"],
                "playlist_index": metadata["playlist_index"],
                "start": metadata["start"],
                "duration": metadata["duration"],
                "distance": distance
            }
        )

    return chunks

def format_timestamp(seconds: float) -> str:
    total_seconds = int(seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds_rem = divmod(remainder, 60)

    return f"{hours:02d}:{minutes:02d}:{seconds_rem:02d}"

def print_results(question: str, chunks: list[dict]) -> None:
    """Display retrieved chunks and source details"""
    print(f"\nQuestion: {question}")

    for number, chunk in enumerate(chunks, start=1):
        timestamp = format_timestamp(chunk["start"])

        print(f"\n--- Result {number} ---")
        print(f"Video: {chunk['title']}")
        print(f"Timestamp: {timestamp}")
        print(f"Distance: {chunk['distance']:.3f}")
        print(chunk["text"])

def main() -> None:
    """Prompt for a question and display retrieved transcript chunks"""
    question = input("Ask a question about the playlist: ").strip()

    if not question:
        print("Please enter a question.")
        return

    chunks = retrieve_chunks(question, TOP_K)
    print_results(question, chunks)

if __name__ == "__main__":
    main()