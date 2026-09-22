"""
Task 4 — Chunking, embedding và indexing.

Hướng dẫn:
    1. Đọc toàn bộ Markdown trong data/standardized/.
    2. Chia văn bản bằng strategy đã chọn.
    3. Embed chunks bằng một provider duy nhất.
    4. Upsert vào ChromaDB với cosine distance.

Mỗi document/chunk phải theo docs/MODULE_CONTRACTS.md. ID cần ổn định để
chạy lại pipeline không tạo dữ liệu trùng. Task 5 phải dùng chung embed_texts().
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv() -> bool:
        """Allow contract-level chunking checks without optional runtime packages."""
        return False

from .contracts import validate_document


STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

# Giải thích lựa chọn tham số trong báo cáo nhóm.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024

COLLECTION_NAME = "rag_documents"

load_dotenv()

_embedding_model = None


def _metadata_from_markdown(path: Path, content: str, doc_type: str) -> dict:
    """Derive stable document metadata from the standardized Markdown file."""
    title = path.stem
    url = None
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# ") and title == path.stem:
            title = stripped[2:].strip() or title
        if stripped.startswith("**Source:**"):
            candidate = stripped.removeprefix("**Source:**").strip()
            url = candidate or None
    return {"source": path.name, "title": title, "doc_type": doc_type, "url": url}


def _split_text(text: str) -> list[str]:
    """Use LangChain's recursive splitter, with a deterministic local fallback."""
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        return splitter.split_text(text)
    except ModuleNotFoundError:
        step = CHUNK_SIZE - CHUNK_OVERLAP
        return [text[start : start + CHUNK_SIZE] for start in range(0, len(text), step)]


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed texts with the provider configured in ``.env``."""
    if not texts:
        return []

    provider = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers").lower()
    model_name = os.getenv("EMBEDDING_MODEL", EMBEDDING_MODEL)

    if provider == "sentence_transformers":
        global _embedding_model
        if _embedding_model is None:
            from sentence_transformers import SentenceTransformer

            _embedding_model = SentenceTransformer(model_name, local_files_only=True)
        return _embedding_model.encode(texts, normalize_embeddings=True).tolist()

    if provider == "openai":
        from openai import OpenAI

        response = OpenAI().embeddings.create(model=model_name, input=texts)
        return [item.embedding for item in response.data]

    if provider == "gemini":
        from google import genai

        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client.models.embed_content(model=model_name, contents=texts)
        return [embedding.values for embedding in response.embeddings]

    raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {provider}")


def get_collection():
    """Mở Chroma collection dùng cosine distance."""
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def load_documents() -> list[dict]:
    """Đọc Markdown và trả về danh sách Document."""
    documents: list[dict] = []
    for doc_type in ("legal", "news"):
        source_dir = STANDARDIZED_DIR / doc_type
        for path in sorted(source_dir.glob("*.md")):
            content = path.read_text(encoding="utf-8").strip()
            if not content:
                continue
            document = {
                "id": path.relative_to(STANDARDIZED_DIR).as_posix(),
                "content": content,
                "metadata": _metadata_from_markdown(path, content, doc_type),
            }
            validate_document(document)
            documents.append(document)
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành chunks có id và chunk_index."""
    chunks: list[dict] = []
    for document in documents:
        validate_document(document)
        for index, content in enumerate(_split_text(document["content"])):
            content = content.strip()
            if not content:
                continue
            chunk = {
                "id": f"{document['id']}::chunk-{index}",
                "content": content,
                "metadata": {**document["metadata"], "chunk_index": index},
            }
            validate_document(chunk, require_chunk=True)
            chunks.append(chunk)
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Thêm embedding vào từng chunk."""
    if not chunks:
        return []
    vectors = embed_texts([chunk["content"] for chunk in chunks])
    if len(vectors) != len(chunks):
        raise ValueError("Embedding provider returned an unexpected vector count")
    return [{**chunk, "embedding": vector} for chunk, vector in zip(chunks, vectors)]


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks vào ChromaDB."""
    if not chunks:
        return
    if len({chunk["id"] for chunk in chunks}) != len(chunks):
        raise ValueError("Chunk IDs must be unique before indexing")

    collection = get_collection()
    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["content"] for chunk in chunks],
        embeddings=[chunk["embedding"] for chunk in chunks],
        metadatas=[{**chunk["metadata"], "url": chunk["metadata"]["url"] or ""} for chunk in chunks],
    )


def run_pipeline() -> None:
    """Chạy load, chunk, embed và index."""
    documents = load_documents()
    chunks = chunk_documents(documents)
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)
    print(f"Indexed {len(embedded_chunks)} chunks")


if __name__ == "__main__":
    run_pipeline()
