#!/usr/bin/env python3
"""
RAG knowledge base indexer with chunking and full-text search.
Chunks documents into ~400-word segments, stores full content,
enables keyword-based retrieval for grounded responses.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict
import requests
import re

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks by words."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks

def load_documents(kb_path: str) -> List[Dict]:
    """Load all knowledge base documents."""
    docs = []
    kb_dir = Path(kb_path)

    # Load posts from metadata
    metadata_file = kb_dir / "POSTS_METADATA.json"
    if metadata_file.exists():
        with open(metadata_file) as f:
            posts = json.load(f).get('posts', [])
            for post in posts[:10]:  # Top 10 posts by impressions
                post_file = kb_dir / post.get('file', '')
                if post_file.exists():
                    with open(post_file) as pf:
                        content = pf.read()
                        docs.append({
                            "id": f"post_{post['rank']}",
                            "title": post.get('title', 'Untitled'),
                            "content": content,
                            "source": "linkedin_post",
                            "impressions": post.get('impressions', 0),
                        })
                        print(f"✓ Loaded post: {post.get('title', 'Untitled')} ({post.get('impressions', 0)} impressions)")

    # Load case studies
    case_studies_dir = kb_dir / "case_studies"
    if case_studies_dir.exists():
        for cs_file in sorted(case_studies_dir.glob("*.md")):
            with open(cs_file) as f:
                content = f.read()
                title = cs_file.stem.replace("_", " ").title()
                docs.append({
                    "id": f"case_{cs_file.stem}",
                    "title": title,
                    "content": content,
                    "source": "case_study",
                })
                print(f"✓ Loaded case study: {title}")

    # Load resume
    resume_file = kb_dir / "RESUME.md"
    if resume_file.exists():
        with open(resume_file) as f:
            docs.append({
                "id": "resume",
                "title": "Resume - Chris Wetzel",
                "content": f.read(),
                "source": "resume",
            })
            print(f"✓ Loaded resume")

    # Load PROFESSIONAL_CONTEXT
    prof_context = kb_dir.parent / "PROFESSIONAL_CONTEXT.md"
    if prof_context.exists():
        with open(prof_context) as f:
            docs.append({
                "id": "professional_context",
                "title": "Professional Context & Positioning",
                "content": f.read(),
                "source": "context",
            })
            print(f"✓ Loaded professional context")

    return docs

def create_collection(qdrant_url: str, collection_name: str) -> bool:
    """Create Qdrant collection with text index."""
    try:
        resp = requests.get(f"{qdrant_url}/collections/{collection_name}")
        if resp.status_code == 200:
            print(f"✓ Collection '{collection_name}' already exists")
            return True
    except:
        pass

    try:
        payload = {
            "vectors": {
                "size": 1,
                "distance": "Cosine",
            }
        }
        resp = requests.put(f"{qdrant_url}/collections/{collection_name}", json=payload)
        if resp.status_code == 200:
            print(f"✓ Created collection '{collection_name}'")
            return True
        else:
            print(f"✗ Failed to create collection: {resp.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error creating collection: {e}")
        return False

def index_documents(qdrant_url: str, docs: List[Dict], collection_name: str = "documents"):
    """Index documents as chunks to Qdrant with full content."""
    print(f"\n=== Indexing Documents with Chunking ===")

    if not create_collection(qdrant_url, collection_name):
        return False

    points = []
    point_id = 0

    for doc in docs:
        # Chunk the content
        chunks = chunk_text(doc['content'], chunk_size=400, overlap=50)

        for chunk_idx, chunk in enumerate(chunks):
            points.append({
                "id": point_id,
                "vector": [0.5],  # Dummy vector; we'll use text search
                "payload": {
                    "doc_id": doc["id"],
                    "title": doc["title"],
                    "content": chunk,  # Full chunk text for text search
                    "source": doc["source"],
                    "chunk_index": chunk_idx,
                    "word_count": len(chunk.split()),
                    "impressions": doc.get("impressions", 0),
                }
            })
            point_id += 1

        print(f"  → {doc['title']}: {len(chunks)} chunks")

    # Upload all points
    try:
        resp = requests.put(
            f"{qdrant_url}/collections/{collection_name}/points",
            json={"points": points}
        )
        if resp.status_code == 200:
            print(f"✓ Indexed {len(points)} chunks across {len(docs)} documents")
            return True
        else:
            print(f"✗ Failed to index: {resp.status_code} {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"✗ Error indexing: {e}")
        return False

def main():
    qdrant_url = "http://ai.cwetzel.com:6333"
    kb_path = "/tmp/knowledge_base"

    print(f"Qdrant URL: {qdrant_url}")
    print(f"KB Path: {kb_path}\n")

    docs = load_documents(kb_path)
    if not docs:
        print("✗ No documents found")
        return 1

    print(f"\n✓ Total: {len(docs)} documents\n")

    if index_documents(qdrant_url, docs, "documents"):
        print("\n✅ Knowledge base indexed with full content for text search!")
        return 0
    else:
        print("\n✗ Indexing failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
