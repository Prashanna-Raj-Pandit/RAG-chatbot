from __future__ import annotations

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / "src/rag_bot/.env")

import chromadb

LOCAL_CHROMA_DIR = str(Path(__file__).parent / "data/chroma_db")
LOCAL_COLLECTION_NAME = "chroma_db"                              # name used in local DB
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "knowledge_base")  # target cloud name
API_KEY = os.getenv("CHROMA_API_KEY", "")
TENANT = os.getenv("CHROMA_TENANT", "")
DATABASE = os.getenv("CHROMA_DATABASE", "DocuChat")
BATCH_SIZE = 100


def main() -> None:
    if not API_KEY or not TENANT:
        sys.exit("ERROR: CHROMA_API_KEY and CHROMA_TENANT must be set in .env")

    # --- local client ---
    print(f"Connecting to local ChromaDB at: {LOCAL_CHROMA_DIR}")
    local_client = chromadb.PersistentClient(path=LOCAL_CHROMA_DIR)

    try:
        local_col = local_client.get_collection(name=LOCAL_COLLECTION_NAME)
    except Exception as e:
        sys.exit(f"ERROR: Could not open local collection '{LOCAL_COLLECTION_NAME}': {e}")

    total = local_col.count()
    print(f"Local collection '{LOCAL_COLLECTION_NAME}' has {total} documents.")

    if total == 0:
        print("Nothing to migrate.")
        return

    # --- cloud client ---
    print(f"Connecting to ChromaDB Cloud (tenant={TENANT}, database={DATABASE}) ...")
    cloud_client = chromadb.CloudClient(
        api_key=API_KEY,
        tenant=TENANT,
        database=DATABASE,
    )

    cloud_col = cloud_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "RAG chatbot knowledge base"},
    )
    print(f"Cloud collection '{COLLECTION_NAME}' ready. Current count: {cloud_col.count()}")

    # --- paginate and upsert ---
    migrated = 0
    offset = 0

    while offset < total:
        batch = local_col.get(
            limit=BATCH_SIZE,
            offset=offset,
            include=["documents", "metadatas", "embeddings"],
        )

        ids = batch["ids"]
        if not ids:
            break

        embeddings = batch.get("embeddings")
        if embeddings is not None:
            embeddings = [e.tolist() if hasattr(e, "tolist") else e for e in embeddings]

        cloud_col.upsert(
            ids=ids,
            documents=batch.get("documents") or [],
            metadatas=batch.get("metadatas") or [],
            embeddings=embeddings,
        )

        migrated += len(ids)
        offset += BATCH_SIZE
        print(f"  Migrated {migrated}/{total} ...")

    print(f"\nDone. {migrated} documents migrated to ChromaDB Cloud.")
    print(f"Cloud collection count: {cloud_col.count()}")


if __name__ == "__main__":
    main()
