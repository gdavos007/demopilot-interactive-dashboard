#!/usr/bin/env python3
"""
Export retrieval results for the DemoPilot RAG pipeline.

Runs in the APP's venv (langchain 0.3.x). It imports the real
ProductKnowledgeAgent, builds the FAISS index exactly as production does,
and dumps what the retriever returns for each golden question to
eval_results/retrievals.json.

This file deliberately has NO ragas / mlflow imports. Scoring is a
separate step (a Databricks notebook) so the scoring dependencies -- which
require langchain 1.x and conflict with this repo's <1.0 pin -- never
have to share this environment.

Ground truth (reference_contexts): each entry in CROWDSTRIKE_KNOWLEDGE_DOCS
pairs a question with the one source doc that should answer it (1:1). For
each question we emit the chunks of THAT question's own source doc as
`reference_contexts`. Because production ingests those same chunks into the
shared FAISS store, a retrieved chunk that came from the correct doc is
byte-identical to one of these reference chunks. That lets the Databricks
notebook score with `NonLLMContextPrecisionWithReference` (default
NonLLMStringSimilarity, threshold 0.5): a retrieved chunk from the right
doc matches at similarity 1.0, a chunk from any other doc (or the fallback
text) matches nothing -- i.e. rank-weighted precision on "did retrieval
return chunks from the correct source doc?". No LLM judge, no reference
answers needed. Per-question answer labels (which specific chunk answers
the question) are a natural v2 refinement.

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


def _labeled_source_text(question: str, text: str) -> str:
    """Reproduce the exact labeling the agent applies before chunking.

    Must match ProductKnowledgeAgent._initialize_crowdstrike_docs so the
    reference chunks are byte-identical to the chunks in the FAISS store.
    (If the agent's label ever drifts, the label is tiny relative to a
    chunk, so similarity stays well above the 0.5 threshold anyway.)
    """
    return f"Demo question: {question}\nProduct: CrowdStrike Falcon\n\n{text}"


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
        url = doc["url"]

        # What the shared retriever actually returns for this question.
        retrieved_docs = agent.vector_store.similarity_search(question, k=TOP_K)
        retrieved_contexts = [d.page_content for d in retrieved_docs]

        # Ground truth: the chunks of THIS question's own source doc, built
        # with the same splitter + labeling the agent used at ingestion.
        source_text = await agent.scrape_documentation(url)
        reference_contexts = agent.text_splitter.split_text(
            _labeled_source_text(question, source_text)
        )

        records.append(
            {
                "question": question,
                "source_url": url,
                "retrieved_contexts": retrieved_contexts,
                "reference_contexts": reference_contexts,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
            }
        )

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(records)} retrieval records to {OUTPUT_PATH}")
    print(f"chunk_size={chunk_size}  chunk_overlap={chunk_overlap}  top_k={TOP_K}")

    # Sanity signal: how many top-k chunks per question are byte-identical to a
    # reference chunk (i.e. came from the correct source doc). This previews
    # what NonLLMContextPrecisionWithReference will score, so a broken export
    # is obvious here rather than only after Databricks scoring.
    for r in records:
        ref_set = set(r["reference_contexts"])
        hits = sum(1 for c in r["retrieved_contexts"] if c in ref_set)
        empty = " [NO CONTEXTS]" if not r["retrieved_contexts"] else ""
        print(f"  correct-doc hits: {hits}/{len(r['retrieved_contexts'])}  | {r['question'][:50]}{empty}")


if __name__ == "__main__":
    asyncio.run(main())
