"""
Task 7 — Reciprocal Rank Fusion (RRF).

Gộp kết quả từ dense và lexical search. Công thức RRF = sum(1 / (k + rank)).
Rank bắt đầu từ 1. ID nào không xuất hiện trong một list thì không cộng điểm cho list đó.
"""

from .contracts import validate_search_results


def rerank_rrf(ranked_lists: list[list[dict]], top_k: int = 5, k: int = 60) -> list[dict]:
    """Kết hợp nhiều danh sách kết quả bằng thuật toán RRF."""
    if not ranked_lists:
        return []

    # Map ID to its corresponding document to reconstruct the result later
    documents = {}
    rrf_scores = {}

    for search_results in ranked_lists:
        for rank, item in enumerate(search_results, 1):
            doc_id = item["id"]
            if doc_id not in documents:
                # Keep the original document structure
                documents[doc_id] = {
                    "id": doc_id,
                    "content": item["content"],
                    "metadata": dict(item["metadata"]),
                    "retrieval_method": "hybrid"
                }
                rrf_scores[doc_id] = 0.0
            
            # Add RRF score for this rank
            rrf_scores[doc_id] += 1.0 / (k + rank)

    # Sort documents by their RRF score
    sorted_docs = sorted(
        rrf_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # Reconstruct the results
    results = []
    for doc_id, score in sorted_docs[:top_k]:
        doc = documents[doc_id]
        doc["score"] = score
        results.append(doc)

    validate_search_results(results, top_k=top_k, expected_method="hybrid")
    return results


if __name__ == "__main__":
    fake_dense = [
        {"id": "doc1", "content": "A", "score": 0.9, "metadata": {}, "retrieval_method": "dense"},
        {"id": "doc2", "content": "B", "score": 0.8, "metadata": {}, "retrieval_method": "dense"},
    ]
    fake_lexical = [
        {"id": "doc2", "content": "B", "score": 5.0, "metadata": {}, "retrieval_method": "bm25"},
        {"id": "doc3", "content": "C", "score": 4.0, "metadata": {}, "retrieval_method": "bm25"},
    ]
    for result in rerank_rrf([fake_dense, fake_lexical]):
        print(result["id"], result["score"])
