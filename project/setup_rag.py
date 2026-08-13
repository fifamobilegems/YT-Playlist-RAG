from pathlib import Path
from sentence_transformers import SentenceTransformer
import json
import chromadb

from .config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_DIR,
    DATA_DIR,
    EMBEDDING_MODEL,
)

def load_all_chunks(chunk_dir = Path) -> list[dict]:
    all_chunks = []
    for chunk_path in chunk_dir.glob("*.json"):
        with open(chunk_path, "r", encoding="utf-8") as file:
            vid_chunks = json.load(file)

        all_chunks.extend(vid_chunks)

    return all_chunks

def prepare_chroma_data(chunks: list[dict]):
    """Turn chunk dicts into chroma ready IDs, text and metadata"""
    ids = []
    docs = []
    metadatas = []

    for chunk in chunks:
        ids.append(chunk["chunk_id"])
        docs.append(chunk["text"])
        metadatas.append(
            {
                "video_id": chunk["video_id"],
                "title": chunk["title"],
                "playlist_index": chunk["playlist_index"],
                "start": chunk["start"],
                "duration": chunk["duration"],
            }
        )

    return ids, docs, metadatas

def setup_rag() -> None:
    """Embed chunks and store in local Chroma collection"""
    chunk_dir = Path(DATA_DIR) / "chunks"
    chunks = load_all_chunks(chunk_dir)

    if not chunks:
        print("No chunks found. Run project.main first")
        return

    model = SentenceTransformer(EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    ids, docs, metadatas = prepare_chroma_data(chunks)

    embeddings = model.encode_document(
        docs,
        batch_size=32,
        show_progress_bar=True,
    ).tolist()

    collection.upsert(
        ids=ids,
        documents=docs,
        metadatas=metadatas,
        embeddings=embeddings
    )

    print(f"Stored {len(chunks)} chunks.")

if __name__ == "__main__":
    setup_rag()