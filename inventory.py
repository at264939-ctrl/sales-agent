"""Inventory module: Load CSV products into ChromaDB for semantic search."""

import csv
import os
from typing import Optional

import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

load_dotenv()


class InventoryStore:
    """ChromaDB-based inventory storage with semantic search."""

    def __init__(self, persist_dir: str = None):
        persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name="products",
            metadata={"hnsw:space": "cosine"}
        )

    def load_csv(self, csv_path: str) -> int:
        """Load products from CSV file. Returns count of loaded products."""
        loaded = 0
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                doc = f"{row['name']}: {row['description']}"
                self.collection.upsert(
                    ids=[row["product_id"]],
                    documents=[doc],
                    metadatas=[{
                        "product_id": row["product_id"],
                        "name": row["name"],
                        "price": row["price"],
                        "stock": row["stock"]
                    }]
                )
                loaded += 1
        return loaded

    def search(self, query: str, n_results: int = 3) -> list[dict]:
        """Semantic search for products."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        if not results["ids"] or not results["ids"][0]:
            return []
        return [
            {
                "product_id": m["product_id"],
                "name": m["name"],
                "price": m["price"],
                "stock": m["stock"]
            }
            for m in results["metadatas"][0]
        ]

    def get_product(self, product_id: str) -> Optional[dict]:
        """Get product by ID."""
        results = self.collection.get(ids=[product_id])
        if not results["metadatas"]:
            return None
        m = results["metadatas"][0]
        return {
            "product_id": m["product_id"],
            "name": m["name"],
            "price": m["price"],
            "stock": m["stock"]
        }
