"""Run the transcript-chunking stage of the project pipeline."""

from pathlib import Path

from .chunking_utils import chunk_all_transcripts
from .config import DATA_DIR


def main() -> None:
    """Chunk every successfully downloaded transcript into a matching JSON file."""
    data_dir = Path(DATA_DIR)
    input_dir = data_dir / Path("transcripts") / Path("successful")
    output_dir = data_dir / Path("chunks")

    if not input_dir.exists():
        print(f"No successful transcript folder found: {input_dir}")
        return

    print(f"Chunking transcripts from: {input_dir}")
    chunk_all_transcripts(input_dir, output_dir)
    print(f"Chunks saved to: {output_dir}")


if __name__ == "__main__":
    main()
