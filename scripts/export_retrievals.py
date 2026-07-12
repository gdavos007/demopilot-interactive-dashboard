#!/usr/bin/env python3
"""
Export retrieval results for the DemoPilot RAG pipeline.

Runs in the APP's venv (langchain 0.3.x). It imports the real
ProductKnowledgeAgent, builds the FAISS index exactly as production does,
and dumps what the retriever returns for each golden question to
eval_results/retrievals.json.

This file deliberately has NO ragas / mlflow imports. Scoring is a
separate step (score_retrievals.py) so the scoring dependencies -- which
require langchain 1.x and conflict with this repo's <1.0 pin -- never
have to share this environment.

Golden set: each entry in CROWDSTRIKE_KNOWLEDGE_DOCS pairs a question
with the one source doc that should answer it (1:1). That mapping is the
retrieval ground truth; a hand-labeled set is a natural v2 improvement.

Usage:
    python scripts/export_retrievals.py
"""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.knowledge.agent import ProductKnowledgeAgent
from app.config.knowledge_docs import CROWDSTRIKE_KNOWLEDGE_DOCS

TOP_K = 4
OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "eval_results",
    "retrievals.json",
)


async def main() -> None:
    agent = ProductKnowledgeAgent()
    await agent.initialize_agent()

    if agent.vector_store is None:
        raise SystemExit(
            "Vector store was not initialized -- doc scrape/embedding failed. "
            "Check network access, Dropbox URLs, and OPENAI_API_KEY."
        )

    chunk_size = agent.text_splitter._chunk_size
    chunk_overlap = agent.text_splitter._chunk_overlap

    records = []
    for doc in CROWDSTRIKE_KNOWLEDGE_DOCS:
        question = doc["question"]
        retrieved_docs = agent.vector_store.similarity_search(question, k=TOP_K)
        retrieved_contexts = [d.page_content for d in retrieved_docs]
        records.append(
            {
                "question": question,
                "source_url": doc["url"],
                "retrieved_contexts": retrieved_contexts,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
            }
        )

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(records)} retrieval records to {OUTPUT_PATH}")
    print(f"chunk_size={chunk_size}  chunk_overlap={chunk_overlap}  top_k={TOP_K}")
    empty = [r["question"] for r in records if not r["retrieved_contexts"]]
    if empty:
        print(f"WARNING: {len(empty)} question(s) returned no contexts:")
        for q in empty:
            print(f"  - {q}")


if __name__ == "__main__":
    asyncio.run(main())
