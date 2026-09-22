"""
Task 5 — Semantic search.

Embed query bằng chính hàm của Task 4, query ChromaDB và đổi cosine distance
thành similarity. Output phải theo SearchResult, sort giảm dần và không quá top_k.
"""

from .task4_chunking_indexing import embed_texts, get_collection
from .contracts import validate_search_results


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về dense SearchResult theo score giảm dần."""
    if top_k <= 0 or not query.strip():
        return []

    query_vector = embed_texts([query])[0]
    response = get_collection().query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    ids = response.get("ids", [[]])[0]
    documents = response.get("documents", [[]])[0]
    metadatas = response.get("metadatas", [[]])[0]
    distances = response.get("distances", [[]])[0]
    results: list[dict] = []
    for item_id, content, metadata, distance in zip(ids, documents, metadatas, distances):
        normalized_metadata = dict(metadata)
        # ChromaDB does not accept None metadata values; restore the contract value.
        if normalized_metadata.get("url") == "":
            normalized_metadata["url"] = None
        results.append(
            {
                "id": item_id,
                "content": content,
                "score": max(0.0, 1.0 - float(distance)),
                "metadata": normalized_metadata,
                "retrieval_method": "dense",
            }
        )

    results = sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]
    validate_search_results(results, top_k=top_k, expected_method="dense")
    return results


if __name__ == "__main__":
    for result in semantic_search("test query", top_k=3):
        print(result)
