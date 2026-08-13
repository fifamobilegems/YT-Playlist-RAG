import json
from pathlib import Path

from .config import MAX_CHUNK_WORDS, TIMESTAMP_GAP_SECONDS

def load_transcript_file(path: Path) -> dict:
    """Load one saved video transcript JSON file."""
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

def segment_end_time(segment: dict) -> float:
    """Return the timestamp at which a caption segment ends."""
    start = segment["start"]
    dur = segment["duration"]
    return start + dur

def has_large_time_gap(prev_segment: dict, curr_segment: dict) -> bool:
    """Check whether two adjacent segments are separated by a long pause."""
    if not prev_segment:
        return False
    
    curr_start = curr_segment["start"]
    prev_end = segment_end_time(prev_segment)
    return (curr_start - prev_end) > TIMESTAMP_GAP_SECONDS

def count_words(text: str) -> int:
    """Count whitespace-separated words in text."""
    return len(text.split())

def merge_segments(segments: list[dict]) -> dict:
    """Join consecutive caption segments into one timestamped passage."""
    start = segments[0]["start"]
    end = segment_end_time(segments[-1])
    duration = end - start
    text = " ".join(s["text"] for s in segments)

    return {
        "text": text,
        "start": start,
        "duration": duration
    }

def chunk_one_video(video: dict) -> list[dict] :
    """Split one video's transcript into source-aware retrieval chunks."""
    transcript = video["transcript"]
    curr_segments = []
    prev_segment = {}
    chunks = []
    chunk_count = 0
    word_count = 0

    for seg in transcript:
        if has_large_time_gap(prev_segment, seg) or word_count > MAX_CHUNK_WORDS:

            new_chunk = merge_segments(curr_segments)
            output = {
                **new_chunk,
                "video_id": video["video_id"],
                "chunk_id": f"{video["video_id"]}_{chunk_count}",
                "title": video["title"],
                "playlist_index": video["playlist_index"]
            }
            chunks.append(output)
            chunk_count += 1

            curr_segments = []
            word_count = 0

        curr_segments.append(seg)
        word_count += count_words(seg["text"])
        prev_segment = seg

    if not curr_segments:
        return chunks
    
    last_chunk = merge_segments(curr_segments)
    output = {
        **last_chunk,
        "video_id": video["video_id"],
        "chunk_id": f"{video["video_id"]}_{chunk_count}",
        "title": video["title"],
        "playlist_index": video["playlist_index"]
            }
    chunks.append(output)

    return chunks

def save_chunks(chunks: list[dict], output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(chunks, json_file, indent=2, ensure_ascii=False)

def chunk_all_transcripts(input_dir: Path, output_dir: Path):

    for transcript_path in input_dir.glob("*.json"):
        video = load_transcript_file(transcript_path)
        chunks = chunk_one_video(video)
        save_chunks(chunks, output_dir / transcript_path.name)