"""Tests for the transcript chunking helpers."""

import json
from pathlib import Path

from project.chunking_utils import (
    chunk_one_video,
    count_words,
    has_large_time_gap,
    load_transcript_file,
    merge_segments,
    segment_end_time,
)


def segment(text: str, start: float, duration: float = 1.0) -> dict:
    """Build a small transcript segment for a test."""
    return {"text": text, "start": start, "duration": duration}


def video_with(transcript: list[dict]) -> dict:
    """Build a minimal successful-transcript record for a test."""
    return {
        "video_id": "test-video",
        "playlist_index": 1,
        "title": "Test video",
        "transcript": transcript,
    }


def test_load_transcript_file(tmp_path: Path):
    expected = video_with([segment("Hello", 0.0)])
    path = tmp_path / "video.json"
    path.write_text(json.dumps(expected), encoding="utf-8")

    assert load_transcript_file(path) == expected


def test_small_helpers():
    first = segment("one two", 10.0, 2.5)
    later = segment("three", 30.0)

    assert count_words("one  two\nthree") == 3
    assert segment_end_time(first) == 12.5
    assert has_large_time_gap(first, later)
    assert not has_large_time_gap(first, segment("nearby", 15.0))


def test_merge_segments_preserves_text_and_time_range():
    merged = merge_segments([
        segment("Hello", 10.0, 2.0),
        segment("world", 13.0, 3.0),
    ])

    assert merged["text"] == "Hello world"
    assert merged["start"] == 10.0
    assert merged["duration"] == 6.0


def test_chunker_splits_at_a_large_timestamp_gap():
    chunks = chunk_one_video(video_with([
        segment("first chunk", 0.0),
        segment("still first", 2.0),
        segment("second chunk", 30.0),
    ]))

    assert len(chunks) == 2
    assert chunks[0]["text"] == "first chunk still first"
    assert chunks[1]["text"] == "second chunk"
    assert chunks[1]["start"] == 30.0
    assert chunks[0]["video_id"] == "test-video"
    assert chunks[0]["chunk_id"] == "test-video_0"
    assert chunks[1]["chunk_id"] == "test-video_1"


def test_chunker_keeps_the_final_chunk_and_handles_empty_input():
    assert chunk_one_video(video_with([])) == []

    chunks = chunk_one_video(video_with([segment("only chunk", 5.0)]))
    assert len(chunks) == 1
    assert chunks[0]["text"] == "only chunk"
    assert chunks[0]["chunk_id"] == "test-video_0"
