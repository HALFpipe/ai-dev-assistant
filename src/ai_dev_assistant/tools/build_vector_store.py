# build_vector_store.py

import json
from ai_dev_assistant.infra.vector_store import VectorStore
from ai_dev_assistant.rag.config import VECTOR_DIM


def main():
    records = json.loads(open("../../../data/embeddings.json").read())

    store = VectorStore(dim=VECTOR_DIM)
    store.build(records)
    store.save()

    print("FAISS index built and saved")


if __name__ == "__main__":
    main()
