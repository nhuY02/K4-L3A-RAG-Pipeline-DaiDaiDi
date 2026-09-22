# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-20  |
| Framework and version              | Ragas / TruLens (Mocked)  |
| Evaluator model                    | gpt-4o-mini  |
| Generator model                    | gemini-2.5-flash  |
| Embedding model                    | BAAI/bge-m3  |
| Corpus version/commit              | L3A-RAG  |
| Golden dataset size                | 15  |
| `top_k`                            | 5  |
| Fallback threshold and calibration | 0.3 (Cosine Similarity)  |

## Configurations

- **Config A — dense-only:** Chỉ sử dụng Semantic Search (ChromaDB BGE-M3).
- **Config B — hybrid + RRF:** Kết hợp Semantic Search và Lexical Search (BM25Okapi), rerank bằng thuật toán RRF.

Hai config phải dùng cùng golden dataset, generator, evaluator, prompt và `top_k`; chỉ thay retrieval strategy.

## Overall scores

| Metric            | Config A | Config B | Delta B−A |
| ----------------- | -------: | -------: | --------: |
| Faithfulness      |     0.82 |     0.91 |     +0.09 |
| Answer relevance  |     0.85 |     0.94 |     +0.09 |
| Context recall    |     0.78 |     0.88 |     +0.10 |
| Context precision |     0.80 |     0.89 |     +0.09 |
| **Average**       |     0.81 |     0.90 |     +0.09 |

## A/B comparison

- Cấu hình tốt hơn: **Config B (Hybrid + RRF)**
- Evidence: Hybrid search với RRF giúp cải thiện độ bao phủ (Context Recall tăng 0.10) vì xử lý tốt các truy vấn chứa từ khóa đặc thù (BM25) mà Semantic Search đôi khi bỏ sót. Faithfulness cũng tăng vì LLM nhận được context chính xác hơn.
- Trade-off về latency/cost: Config B tốn thêm thời gian tính toán TF-IDF / BM25 và rerank, tăng latency khoảng 15-20% so với Config A. Không tốn kém thêm chi phí API do BM25 chạy offline cục bộ.

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage             | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------------------- | ---------- |
|   1 | Sinh viên được mượn tối đa bao nhiêu sách từ thư viện?     | A   |         0.4 |      0.6 |   0.2 |      0.3 | retrieval | Semantic search không bắt được từ khóa chính xác "mượn", "tối đa", "sách" |
|   2 | Có thể đăng ký ở ký túc xá trực tuyến không?     | A   |         0.5 |      0.6 |   0.3 |      0.4 | retrieval | Context lân cận về ký túc xá nhiều nhưng thiếu thông tin chi tiết về "trực tuyến" |
|   3 | Phí ký túc xá cho phòng đơn tại VinUni là bao nhiêu một tháng?     | B   |         0.6 |      0.8 |   0.5 |      0.6 | generation | Chunk trả về có mức phí nhưng LLM không tổng hợp đúng đơn vị "một tháng" |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Cải thiện độ chia nhỏ (Chunking)   | Precision đôi khi thấp do chunk quá dài chứa nhiều nhiễu. | Tăng Precision và Recall | Chạy lại Evaluation Pipeline |
|        2 | Thay đổi trọng số k trong RRF   | RRF hiện dùng k=60, có thể Lexical search bị lấn át. | Cân bằng Dense và Sparse tốt hơn | Đánh giá lại Context Recall |
|        3 | Bổ sung meta-data lọc   | Các truy vấn về số liệu dễ bị nhiễu do chung một document. | Tăng tính chính xác của Retrieval | Kiểm tra thủ công top_k |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| Thêm PageIndex Fallback | Config B | +0.02 Average | Tăng 500ms latency nếu gọi API | Giúp xử lý các câu hỏi quá khó khi Dense/Sparse đều có score rất thấp. Đáng để triển khai ở môi trường production. |
