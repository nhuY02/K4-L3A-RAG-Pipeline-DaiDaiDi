# Individual contribution report

Mỗi thành viên copy template này thành:

```text
reports/<student-id>-<short-name>.md
```

Giới hạn khuyến nghị: 1 trang, không chép lại README hoặc mô tả lý thuyết chung. Báo cáo không phải một bài pipeline cá nhân; mục đích là ghi nhận ownership và bằng chứng đóng góp trong sản phẩm nhóm.

---

## Thông tin

- Họ và tên: Trần Thị Như Ý
- Mã học viên: 2A202602372
- Nhóm: Nhóm 1 - DaiDaiDi
- Repository/branch: main

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 1-3 | Cài đặt dữ liệu pháp lý (fpdf2) và tin tức (json), convert Markdown | `task1_collect_legal_docs.py`, `task2_crawl_news.py`, `task3_convert_markdown.py` | Done |
| Task 4 | Indexing vào ChromaDB (BAAI/bge-m3) | `task4_chunking_indexing.py` | Done |
| Task 5-8 | Thiết lập Semantic, Lexical (BM25), Reranking (RRF), và PageIndex Fallback | `task6_lexical_search.py`, `task7_reranking.py`, `task8_pageindex_vectorless.py` | Done |
| Task 9-10 | Viết Retrieval Pipeline kết hợp (Hybrid + Fallback) và Generation (Gọi LLM API) | `task9_retrieval_pipeline.py`, `task10_generation.py` | Done |
| Application UI | Cập nhật Streamlit app tích hợp pipeline RAG và show sources | `app.py` | Done |
| Evaluation | Tạo 15 Golden Q&A pairs và đánh giá mô phỏng, viết báo cáo | `group_project/evaluation/golden_dataset.json`, `RESULT.md`, báo cáo này | Done |

*Lưu ý: Mặc dù đây là bài tập nhóm, tôi đã thực hiện toàn bộ khối lượng công việc của dự án này một cách độc lập từ đầu đến cuối.*

Chỉ kê khai công việc có thể đối chiếu bằng file, commit, pull request, test hoặc kết quả evaluation.

## Quyết định kỹ thuật quan trọng

Mô tả tối đa hai quyết định mà bạn trực tiếp tham gia:

1. **Quyết định:** Sử dụng BM25Okapi làm Lexical Search engine nội bộ kết hợp với ChromaDB.
   **Lý do/evidence:** Thư viện `rank_bm25` nhẹ, không yêu cầu Elasticsearch server, rất phù hợp cho dataset nhỏ đến vừa.
   **Trade-off:** Dữ liệu index BM25 được giữ trong bộ nhớ (in-memory), có thể gây tràn RAM nếu dataset quá lớn. Tuy nhiên với phạm vi lab, tốc độ query và độ chính xác lai (hybrid) được ưu tiên hơn.

2. **Quyết định:** Tự động tạo mock dữ liệu (tạo file JSON trực tiếp thay vì crawl real-time) trong Task 2.
   **Lý do/evidence:** Hạn chế về thời gian thực hiện lab, mục tiêu chính là thử nghiệm và hoàn thiện đường ống RAG thay vì xây dựng bot crawl phức tạp.
   **Trade-off:** Dữ liệu không phong phú bằng crawl thật, nhưng đảm bảo pipeline chạy được mượt mà, độc lập môi trường mạng và kết quả đầu ra có thể kiểm soát (đánh giá dễ dàng hơn).

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: "Phí ký túc xá cho phòng đơn tại VinUni là bao nhiêu một tháng?", "Mức học phí của chương trình Cử nhân Kỹ thuật phần mềm là bao nhiêu?"
- Kết quả trước/sau nếu có: Dense search đôi khi trả về đoạn text nói về phí Ký túc xá chung chung nhưng thiếu phòng đơn. Sau khi bật Hybrid + RRF, kết quả trả về chính xác đoạn text có đề cập "phòng đơn".
- Lỗi đã phát hiện và cách xử lý: Không import được thư viện trong background task do thiếu cài đặt (`pypdf`, v.v.). Cách xử lý: Đã thêm các thư viện vào file `pyproject.toml` và chạy lại `pip install -e .`

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Tốc độ load index của BM25 bị lặp lại mỗi lần khởi chạy. PageIndex fallback mới chỉ ở dạng mock (safe try-catch).
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Serialize (Pickle) BM25 index ra disk để tiết kiệm thời gian khởi tạo; Gọi API thật của PageIndex.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-20
- Tên thành viên: Trần Thị Như Ý
