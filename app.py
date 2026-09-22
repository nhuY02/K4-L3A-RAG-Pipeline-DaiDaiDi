import streamlit as st
from dotenv import load_dotenv

# pyrefly: ignore [missing-import]
from src.task10_generation import generate_with_citation

load_dotenv()

st.set_page_config(
    page_title="Hỗ trợ thông tin VinUni",
    page_icon="🎓",
    layout="wide",
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("VinUni Assistant")
    st.caption("Dịch vụ đại học (Học phí, học bổng, ký túc xá, thư viện, đăng ký học phần)")
    top_k = st.slider("Số chunks", 3, 10, 5)

st.title("🎓 Hỗ trợ thông tin Sinh viên VinUni")
st.caption("Hỏi đáp về Học phí, Học bổng, Ký túc xá, Thư viện và Đăng ký học phần tại VinUni.")

def display_sources(sources, retrieval_source):
    if sources:
        with st.expander(f"📚 Nguồn tham khảo ({retrieval_source})"):
            for idx, source in enumerate(sources):
                st.markdown(f"**{idx + 1}. {source['metadata'].get('title', 'N/A')}**")
                st.markdown(f"*Nguồn:* {source['metadata'].get('source', 'N/A')} | *Score:* {source.get('score', 0):.4f}")
                st.text(source.get('content', '')[:300] + "...")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "sources" in message:
            display_sources(message["sources"], message.get("retrieval_source", "none"))

query = st.chat_input("Nhập câu hỏi...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Đang tìm kiếm và xử lý câu trả lời..."):
            result = generate_with_citation(query, top_k=top_k)
            answer = result.get("answer", "")
            sources = result.get("sources", [])
            retrieval_source = result.get("retrieval_source", "none")
            
            st.markdown(answer)
            display_sources(sources, retrieval_source)

    st.session_state.messages.append({
        "role": "assistant", 
        "content": answer,
        "sources": sources,
        "retrieval_source": retrieval_source
    })
