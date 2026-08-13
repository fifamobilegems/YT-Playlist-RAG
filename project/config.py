from pathlib import Path

BASE_DIR = "C:/Users/maxli/OneDrive/Desktop/cs/yt transcript downloader/project"
DATA_DIR = "C:/Users/maxli/OneDrive/Desktop/cs/yt transcript downloader/project/data"

# youtube/transcript
PLAYLIST_URL = "..."
TRANSCRIPT_LANGUAGES = ["en"]
SAVE_RAW_TRANSCRIPTS = True
VIDEO_LIMIT = 20

# chunks
MAX_CHUNK_WORDS = 150
TIMESTAMP_GAP_SECONDS = 12
MIN_CHUNK_SIZE = 300
MAX_CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150

# embeddings
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"

# chroma db
CHROMA_COLLECTION_NAME = "youtube_streams"
CHROMA_DIR = BASE_DIR / Path("knowledge_base") / Path("chroma_db")

# retrieval
TOP_K = 5

# end model (openai?)
OPENAI_MODEL = "..."
MAX_TOKENS = 2000
TEMPERATURE = 0.2