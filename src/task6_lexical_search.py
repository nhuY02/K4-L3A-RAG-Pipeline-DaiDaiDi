"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""

from rank_bm25 import BM25Okapi
import numpy as np

# Giữ nguyên cấu trúc ban đầu, biến này sẽ được gán dữ liệu từ bên ngoài (hoặc qua monkeypatch trong lúc test)
CORPUS: list[dict] = []


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    if not corpus:
        return None
    
    # Tokenize: chuyển thành chữ thường và cắt theo khoảng trắng
    tokenized = [item["content"].lower().split() for item in corpus]
    return BM25Okapi(tokenized)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    bm25 = build_bm25_index(CORPUS)
    
    if bm25 is None or not query.strip():
        return []

    query_tokens = query.lower().split()
    scores = bm25.get_scores(query_tokens)
    
    # Sắp xếp index theo điểm số giảm dần
    indices = np.argsort(scores)[::-1][:top_k]
    
    results = []
    query_tokens_set = set(query_tokens)
    
    for index in indices:
        score = float(scores[index])
        item = CORPUS[index]
        doc_tokens = set(item["content"].lower().split())
        
        # Chỉ skip nếu điểm <= 0 VÀ từ khóa hoàn toàn không xuất hiện trong văn bản
        if score <= 0 and query_tokens_set.isdisjoint(doc_tokens):
            continue
            
        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": score,
            "metadata": dict(item["metadata"]),
            "retrieval_method": "bm25",
        })
        
    return results


if __name__ == "__main__":
    for result in lexical_search("test query", top_k=3):
        print(result)
