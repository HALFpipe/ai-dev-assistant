# tools/rebuild_embeddings.py
import json
from pathlib import Path

from ai_dev_assistant.rag.schema import CodeChunk
from ai_dev_assistant.rag.embedding_pipeline import embed_chunks
from ai_dev_assistant.infra.config import DRY_RUN

DATA_DIR = Path("../../../data")
CHUNKS_FILE = DATA_DIR / "chunks.json"
EMBEDDINGS_FILE = DATA_DIR / "embeddings.json"


def load_chunks(path: Path) -> list[CodeChunk]:
    raw = json.loads(path.read_text())
    return [CodeChunk(**item) for item in raw]


def main() -> None:
    chunks = load_chunks(CHUNKS_FILE)

    print(f"Loaded {len(chunks)} chunks")

    records = embed_chunks(chunks, dry_run=DRY_RUN)

    if records:
        print(f"Embedded {len(records)} chunks")

        EMBEDDINGS_FILE.write_text(
            json.dumps(records, indent=2)
        )

        print(f"Wrote embeddings to {EMBEDDINGS_FILE}")


if __name__ == "__main__":
    main()
