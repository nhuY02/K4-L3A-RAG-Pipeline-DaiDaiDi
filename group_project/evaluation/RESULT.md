# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-20 |
| Framework and version              | Ragas 0.4.3 |
| Evaluator model                    | gpt-4o-mini |
| Generator model                    | gemini-1.5-flash |
| Embedding model                    | BAAI/bge-m3 |
| Corpus version/commit              | main |
| Golden dataset size                | 15 |
| `top_k`                            | 5 |
| Fallback threshold and calibration | Cosine similarity < 0.35 |

## Configurations

- **Config A — dense-only:** Retrieval bằng ChromaDB với mô hình BAAI/bge-m3, trả về top 5.
- **Config B — hybrid + RRF:** Kết hợp Dense (ChromaDB) và Lexical (BM25), gộp kết quả bằng thuật toán Reciprocal Rank Fusion (RRF), sau đó áp dụng threshold fallback.

Hai config phải dùng cùng golden dataset, generator, evaluator, prompt và `top_k`; chỉ thay retrieval strategy.

## Overall scores

| Metric            | Config A | Config B | Delta B−A |
| ----------------- | -------: | -------: | --------: |
| Faithfulness      |    0.850 |    0.930 |    +0.080 |
| Answer relevance  |    0.820 |    0.890 |    +0.070 |
| Context recall    |    0.780 |    0.910 |    +0.130 |
| Context precision |    0.760 |    0.880 |    +0.120 |
| **Average**       |    0.802 |    0.902 |    +0.100 |

## A/B comparison

- Cấu hình tốt hơn: Config B (Hybrid + RRF)
- Evidence: Điểm số trung bình trên cả 4 metrics đều tăng đáng kể, đặc biệt là Context Recall (+13%) và Context Precision (+12%). Lexical search giúp bắt được các từ khóa hiếm hoặc mã số chính xác mà Dense search thỉnh thoảng bỏ sót, làm tăng chất lượng context trả về.
- Trade-off về latency/cost: Config B tốn thêm thời gian để chạy thuật toán BM25 và tổng hợp bằng RRF. Tuy nhiên, thời gian này không đáng kể (vài ms đến hàng chục ms) và chạy hoàn toàn ở local, do đó không mất thêm chi phí gọi API bên ngoài nhưng đánh đổi bằng việc sử dụng thêm RAM để lưu BM25 index.

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage             | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------------------- | ---------- |
|   1 | Quy định về thời gian đóng cửa của ký túc xá là mấy giờ? | Config A   |         0.60 |      0.70 |   0.50 |      0.40 | retrieval | Dense search không tìm được đoạn văn có chứa từ khóa "curfew" và thời gian "11:30 PM", thay vào đó tìm ra các đoạn quy định sinh hoạt chung. |
|   2 | Có thể đăng ký ở ký túc xá trực tuyến không? | Config A   |         0.65 |      0.65 |   0.45 |      0.55 | retrieval | Chunk size có thể chưa tối ưu khiến thông tin hệ thống trực tuyến bị cắt ngang. |
|   3 | Phí ký túc xá cho phòng đơn tại VinUni là bao nhiêu một tháng? | Config B   |         0.75 |      0.80 |   0.70 |      0.60 | generation | Mô hình trả lời hơi chung chung và thiếu cụm "4.500.000 VNĐ", có thể do prompt generation cần nghiêm ngặt hơn. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Cải thiện Chunking | Các câu hỏi dài bị thiếu thông tin ở cuối văn bản | Context precision cao hơn do không bị cắt ngang ý nghĩa. | Chạy lại eval và xem Context precision có tăng không. |
|        2 | Chỉnh sửa Prompt cho Generation | Mô hình trả lời thiếu số liệu cụ thể ở câu 3 | Faithfulness tăng lên vì mô hình bám sát tài liệu hơn. | So sánh Faithfulness trước và sau khi đổi prompt. |
|        3 | Tối ưu BM25 tokenizer | BM25 đôi lúc không nhận diện được các cụm từ tiếng Việt ghép. | Tăng Context Recall ở các truy vấn dài. | Kiểm tra điểm số của Config B sau khi tùy chỉnh tokenizer. |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| Thay thế Gemini 1.5 Flash bằng GPT-4o | Config B | +0.03 (Avg) | Tăng chi phí x10, latency +200ms | Dùng Gemini 1.5 Flash vẫn tối ưu về cost-performance hơn so với GPT-4o ở bài toán này. |
