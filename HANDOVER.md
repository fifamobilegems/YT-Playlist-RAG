# RAG Project Handover

## 1. Project Goal

Build a local RAG (Retrieval-Augmented Generation) system from a YouTube playlist containing approximately:

- 15 long streams/videos
- 140+ hours of content

The finished system should allow the user to ask questions about the content of the playlist and receive answers grounded in the transcripts, ideally with references to the relevant video/stream and timestamp.

High-level pipeline:

```text
YouTube Playlist
    ↓
Download transcripts
    ↓
Inspect raw transcript structure
    ↓
Design chunking strategy based on actual transcript data
    ↓
Chunk transcripts while preserving source/timestamps
    ↓
Create embeddings
    ↓
Store in Chroma
    ↓
Retrieve relevant chunks for a question
    ↓
Send retrieved context to Claude
    ↓
Return grounded answer + timestamps
```

---

## 2. Important Current Decision

DO NOT design or implement the final chunking strategy yet.

The current plan is to:

1. Export transcripts first.
2. Inspect what the actual transcript data looks like.
3. Only then decide how chunks should be formed.

This is important because YouTube transcript/caption data may:

- split sentences across multiple segments
- contain very short caption fragments
- have inconsistent punctuation/capitalization
- represent spoken code poorly
- contain filler/repetition
- provide timestamps at caption-segment level rather than semantic-section level

Therefore, earlier ideas such as detecting code from indentation or triple backticks should NOT be assumed to work.

The chunker should eventually be designed from the real exported data.

---

## 3. Current Intended Architecture

```text
project/
├── config.py
├── download_transcripts.py       ← NEXT FILE TO WORK ON
├── chunking_utils.py             ← AFTER transcript inspection
├── setup_rag.py
├── query_rag.py
├── requirements.txt
├── .env
├── .gitignore
│
├── data/
│   └── transcripts/
│
└── knowledge_base/
    └── chroma_db/
```

This structure may evolve if there is a good reason, but avoid unnecessary abstraction for the first version.

---

## 4. File Responsibilities

### `config.py`

Purpose:

A central control panel for values/settings used by the rest of the project.

It should contain or expose things such as:

- project paths
- transcript/output paths
- transcript languages
- chunking settings later
- embedding model name
- Chroma collection/path
- retrieval `TOP_K`
- Claude model/settings

Secrets should NOT be hardcoded in `config.py`.

Example:

```text
.env
    ↓
ANTHROPIC_API_KEY
    ↓
config.py reads environment variable
```

The actual API key must remain in `.env`, and `.env` should be ignored by Git.

General rule:

> `config.py` stores settings. Other files contain behaviour.

---

### `download_transcripts.py`

THIS IS THE NEXT COMPONENT TO BUILD.

Its first version should stay simple.

Responsibility:

```text
YouTube URL / playlist
    ↓
Get video information
    ↓
Retrieve transcript/caption segments
    ↓
Preserve raw data
    ↓
Save structured JSON for inspection
```

Do NOT perform semantic chunking here.

Do NOT aggressively clean or modify the transcript.

Preserve enough raw information so the chunking strategy can be designed later.

---

### `chunking_utils.py`

Do not implement the final version yet.

Eventually responsible for turning the raw transcript into useful retrieval units while preserving source metadata and timestamps.

Potential concerns later:

- combining tiny transcript segments
- semantic/topic boundaries
- sentence boundaries
- maximum/minimum chunk length
- overlap
- start/end timestamps
- code-related sections
- explanations
- decisions
- preserving sufficient surrounding context

Do not assume the final chunk types must be:

- `code_block`
- `decision`
- `explanation`

Those were initial ideas only.

---

### `setup_rag.py`

Eventually orchestrates:

```text
load transcripts
    ↓
chunk
    ↓
embed
    ↓
store in Chroma
```

This should be built only after transcript export and chunking are understood.

---

### `query_rag.py`

Eventually:

```text
User question
    ↓
Embed question
    ↓
Vector search in Chroma
    ↓
Retrieve top-K chunks + metadata
    ↓
Build grounded context
    ↓
Send to Claude
    ↓
Answer with source video/timestamps
```

---

## 5. Tentative Technology Choices

These are current intended choices, not immutable requirements:

| Purpose | Tool |
|---|---|
| Video metadata | `yt-dlp` |
| YouTube transcripts | `youtube-transcript-api` |
| Embeddings | `sentence-transformers` |
| Tentative embedding model | `all-mpnet-base-v2` |
| Vector database | Chroma |
| Answer generation | Claude API |
| Environment variables | `python-dotenv` |
| Progress display | `tqdm` |

Tentative dependency list:

```text
youtube-transcript-api
yt-dlp
sentence-transformers
chromadb
anthropic
python-dotenv
tqdm
```

Use current library APIs when implementing rather than blindly copying outdated examples.

---

## 6. Transcript Export: What We Need to Preserve

For each video, preserve as much useful source information as practical.

Desired video-level information:

```json
{
  "video_id": "...",
  "title": "...",
  "url": "...",
  "playlist_index": 1,
  "duration": 12345,
  "transcript": []
}
```

Each transcript segment should preserve at minimum:

```json
{
  "text": "example transcript text",
  "start": 125.4,
  "duration": 3.8
}
```

If the transcript API exposes other genuinely useful information, it can be retained, but avoid unnecessary fields.

Do not convert timestamps only into formatted strings. Preserve numeric seconds because later processing will need them.

Formatted timestamps such as `01:23:45` can always be generated later.

---

## 7. First Export Strategy

Do NOT immediately process all 140+ hours unless there is a good reason.

First test the export pipeline on approximately 1–2 representative videos.

We want to inspect:

1. What one raw transcript segment looks like.
2. Average segment length.
3. Whether punctuation exists.
4. How sentences are split.
5. Whether code-heavy sections look different from normal speech.
6. How accurate/useful the timestamps are.
7. Whether there are missing transcript sections.
8. Whether manually-created vs auto-generated captions differ.
9. How much transcript cleanup is actually necessary.
10. Whether topic boundaries are visible enough for semantic chunking.

Save the transcript in human-readable pretty-printed JSON for this inspection stage.

---

## 8. Requirements for `download_transcripts.py`

For the initial implementation, prefer a clear, debuggable program over a highly abstract system.

It should ideally be able to:

- accept a playlist URL or video URL
- retrieve the videos in playlist order
- retrieve useful video metadata
- retrieve available transcript data
- preserve transcript timestamps
- save output to `data/transcripts/`
- create required output directories if missing
- handle a video with no usable transcript without crashing the whole playlist job
- clearly report failures
- avoid silently discarding data
- avoid transcript chunking
- avoid embeddings
- avoid Claude calls

For initial testing, make it easy to limit processing to the first 1–2 videos.

Possible design:

```bash
python download_transcripts.py --url "<playlist-url>" --limit 2
```

Exact CLI design can be adjusted if a simpler clean approach is preferable.

---

## 9. Suggested Output Layout

One reasonable structure is:

```text
data/
└── transcripts/
    ├── playlist_metadata.json
    ├── 001_<video-id>.json
    ├── 002_<video-id>.json
    └── ...
```

or a single JSON file containing all videos.

For 140+ hours of content, separate files per video are probably easier to inspect, retry, update, and process incrementally.

Prefer stable filenames based on playlist index + video ID.

Do not rely solely on video titles for filenames because titles can contain invalid/path-unfriendly characters.

---

## 10. Error Handling Expectations

The downloader should distinguish between situations such as:

- video unavailable
- transcript disabled
- no transcript in preferred language
- automatically generated transcript available
- API/network failure
- metadata retrieval failure

A single failed video should normally be logged/skipped while processing continues.

Do not hide exceptions without reporting enough information to debug them.

---

## 11. Configuration Thinking

Current likely configuration categories:

```text
PATHS
TRANSCRIPTS
CHUNKING              ← later
EMBEDDINGS             ← later
CHROMA                 ← later
RETRIEVAL              ← later
CLAUDE                 ← later
```

Likely early values:

```python
BASE_DIR
DATA_DIR
TRANSCRIPT_DIR
TRANSCRIPT_LANGUAGES
```

Values such as these may come later:

```python
MIN_CHUNK_SIZE
MAX_CHUNK_SIZE
CHUNK_OVERLAP
EMBEDDING_MODEL
CHROMA_COLLECTION_NAME
TOP_K
CLAUDE_MODEL
MAX_TOKENS
TEMPERATURE
```

Avoid inventing dozens of configuration options before they are needed.

---

## 12. Embedding / Retrieval Notes for Later

Tentative model:

```text
sentence-transformers/all-mpnet-base-v2
```

The exact same embedding model must be used for:

- stored chunks
- user queries against those chunks

Do not build the embedding layer until transcript/chunk structure is settled.

Tentative vector database:

```text
Chroma
```

Each stored chunk will eventually need metadata such as:

```json
{
  "video_id": "...",
  "video_title": "...",
  "playlist_index": 5,
  "start_time": 5025.4,
  "end_time": 5070.2
}
```

Potential extra metadata should be based on actual usefulness after transcript inspection.

---

## 13. Design Philosophy

This project should be built incrementally.

Avoid trying to make the entire RAG system "smart" in one pass.

Preferred progression:

```text
RAW DATA
    ↓
Understand it
    ↓
Reliable preprocessing
    ↓
Good chunks
    ↓
Good retrieval
    ↓
LLM answering
```

Retrieval quality matters more than adding complicated LLM orchestration early.

Avoid premature complexity.

Do not introduce:

- agents
- rerankers
- query rewriting
- hybrid retrieval
- complex classification
- multiple vector databases
- elaborate abstractions

unless actual retrieval tests demonstrate that they are needed.

---

## 14. Current Status

Planning/design has started.

The intended project architecture has been discussed.

`config.py` has been conceptually designed, including:

- why it exists
- what types of settings belong there
- keeping API keys in `.env`
- centralising shared settings

Do NOT assume all files have already been implemented unless they exist in the repository.

The latest decision is:

> Export real transcript data before designing `chunking_utils.py`.

Therefore the immediate implementation target is:

# `download_transcripts.py`

---

## 15. Immediate Task for Codex

1. Inspect the existing repository first.
2. Do not overwrite working code unnecessarily.
3. Determine what already exists, especially `config.py`, `.env.example`, `.gitignore`, and `requirements.txt`.
4. Implement or refine `download_transcripts.py`.
5. Keep the first version focused only on transcript acquisition + preservation.
6. Make it easy to test on 1–2 videos.
7. Save raw transcript output in readable JSON.
8. Preserve numeric timestamps.
9. Handle unavailable transcripts/videos gracefully.
10. Do not implement chunking yet.
11. After implementation, run a small test if possible.
12. Show the resulting transcript JSON structure.
13. Based on the real exported transcript, propose chunking considerations — but do not build the final chunker until the transcript has been inspected.

---

## 16. What Success Looks Like for the Next Step

A successful next milestone is NOT:

> "The whole RAG system works."

It is:

> "I can reliably export one or two representative YouTube videos into clean, inspectable JSON while preserving the raw transcript segments and timestamps."

Once that is working, inspect the output and decide how `chunking_utils.py` should actually work.

---

## 17. Instructions for Working Style

When making changes:

- explain major decisions briefly
- keep implementation straightforward
- avoid unnecessary abstractions
- prefer readable Python
- preserve raw information
- make assumptions explicit
- do not jump ahead into chunking/embedding unless requested
- if library APIs differ from older examples, use the currently installed/current documented API
- test small before scaling to the full playlist

The user wants to understand the reasoning behind the implementation, not just receive unexplained code.

