import sys
import json

from pathlib import Path
from .config import TRANSCRIPT_LANGUAGES, DATA_DIR, VIDEO_LIMIT

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
except ImportError:
    print("Error: youtube-transcript-api is not installed.")
    print("Install it with: pip install youtube-transcript-api")
    sys.exit(1)

try:
    from yt_dlp import YoutubeDL
except ImportError:
    print("Error: cannot install ytdlp")
    sys.exit(1)

ytt_api = YouTubeTranscriptApi()
ydl_opts = {
    'extract_flat': True,
    'skip_download': True,
}

def get_transcript(video_id: str) -> list[dict]:
    """Download transcript for a single video"""
    transcript = ytt_api.fetch(video_id, languages=TRANSCRIPT_LANGUAGES)
    return transcript.to_raw_data()

def get_playlist_info(playlist_url: str) -> tuple[str, list[dict]]:
    """Get name, ids for a whole ass playlist"""
    with YoutubeDL(ydl_opts) as ydl:
        playlist_dict = ydl.extract_info(playlist_url, download=False)

    playlist_name = playlist_dict.get("title", "Unknown playlist")
    videos = []

    for index, video in enumerate(
        (playlist_dict.get("entries") or [])[:VIDEO_LIMIT],
        start=1,
    ):
        video_id = video.get("id")
        if not video_id:
            print(f"Skipping playlist item {index}: no video ID")
            continue

        videos.append(
            {
                "video_id": video_id,
                "playlist_index": index,
                "title": video.get("title", "Unknown Title"),
            }
        )

    return playlist_name, videos

def get_transcript_from_playlist(playlist_url: str):
    playlist_name, videos = get_playlist_info(playlist_url=playlist_url)

    target_dir = Path(DATA_DIR) / Path("transcripts")
    target_dir.mkdir(parents=True, exist_ok=True)

    success_dir = target_dir / Path("successful")
    success_dir.mkdir(parents=True, exist_ok=True)
    failed_dir = target_dir / Path("failed")
    failed_dir.mkdir(parents=True, exist_ok=True)

    for index, vid in enumerate(videos, start=1):
        file_name = f"{vid["playlist_index"]}_{vid["video_id"]}.json"

        try:
            full_path = success_dir / Path(file_name)
            raw_transcript = get_transcript(vid["video_id"])
            output = {
                **vid,
                "transcript": raw_transcript
            }
            with open(full_path, "w", encoding="utf-8") as json_file:
                json.dump(output, json_file, indent=2, ensure_ascii=False)

        except(NoTranscriptFound, TranscriptsDisabled) as error:
            print(f"Skipping {vid['video_id']}: {error}")
            full_path = failed_dir / Path(file_name)
            output = {
                **vid,
                "error_type": type(error).__name__,
                "error": str(error)
            }
            with open(full_path, "w", encoding="utf-8") as json_file:
                json.dump(output, json_file, indent=2, ensure_ascii=False)

        except Exception as error:

            print(f"Unexpected failure for {vid['video_id']}: {error}")
            full_path = failed_dir / Path(file_name)
            output = {
                **vid,
                "error_type": type(error).__name__,
                "error": str(error)
            }
            with open(full_path, "w", encoding="utf-8") as json_file:
                json.dump(output, json_file, indent=2, ensure_ascii=False)

get_transcript_from_playlist("https://www.youtube.com/playlist?list=PLA1G2nVay86RW7LqJERpgTAWbWmNdXcAI")