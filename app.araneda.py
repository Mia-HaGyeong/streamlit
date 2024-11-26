import os
import json
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

from main import DocumentTalker

# 페이지 설정
st.set_page_config(page_title="문서와 대화하기", layout="wide")

# Custom CSS
st.markdown(
    """
  <style>
      /* Noto Sans KR 폰트 및 기본 스타일 */
      @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
      
      /* 전체 페이지 스타일 */
      .stApp {
          background-color: #111827;
      }
      
      /* 컨테이너 스타일 */
      [data-testid="stVerticalBlock"] > [style*="flex-direction: column"] > [data-testid="stVerticalBlock"] {
          background-color: #1f2937;
          padding: 1.5rem;
          border-radius: 16px;
          border: 1px solid #374151;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
      }
      
      /* textarea 기본 스타일 */
      .stTextArea textarea {
          background-color: #374151 !important;
          color: #f3f4f6 !important;
          border: 1px solid #4b5563 !important;
          border-radius: 12px !important;
          font-family: 'Noto Sans KR', sans-serif !important;
          font-size: 1rem !important;
          line-height: 1.6 !important;
          resize: none !important;
          padding: 1rem !important;
      }
      
      /* input과 output textarea 높이 */
      [data-testid="stTextArea"] textarea[aria-label="AI-text"],
      [data-testid="stTextArea"] textarea[aria-label="Proof-read-text"] {
          height: 500px !important;
      }
      
      /* Revision textarea 높이 */
      [data-testid="stTextArea"] textarea[aria-label="Revision"] {
          height: 100px !important;
      }

      /* 키워드 입력 textarea 높이 */
      [data-testid="stTextArea"] textarea[aria-label="키워드 입력"] {
          height: 100px !important;
      }
      
      /* 버튼 중앙 정렬 */
      div[data-testid="column"]:nth-child(1) .stButton {
          display: flex;
          justify-content: center;
          margin-top: 1rem;
      }
      
      .stTextArea textarea:focus {
          border-color: #6366f1 !important;
          box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
      }
      
      /* 제목 스타일 */
      .title {
          font-family: 'Noto Sans KR', sans-serif;
          font-weight: 600;
          text-align: center;
          color: #f3f4f6;
          margin-bottom: 0.5rem;
          font-size: 2rem;
      }
      
      .subtitle {
          font-family: 'Noto Sans KR', sans-serif;
          font-weight: 400;
          text-align: center;
          color: #9ca3af;
          font-size: 1.1rem;
          margin-bottom: 2rem;
      }
      
      /* 라벨 스타일 */
      .label {
          font-family: 'Noto Sans KR', sans-serif;
          color: #e5e7eb;
          font-size: 1.1rem;
          font-weight: 500;
          margin-bottom: 0.75rem;
      }
      
      /* 라디오 버튼 스타일 */
      .stRadio > div {
          background-color: transparent !important;
          gap: 2rem !important;
      }
      
      .stRadio label {
          color: #e5e7eb !important;
          font-family: 'Noto Sans KR', sans-serif !important;
          font-size: 0.95rem !important;
      }
      
      /* 버튼 스타일 */
      .stButton > button {
          background-color: #4f46e5 !important;
          color: white !important;
          border: none !important;
          padding: 0.75rem 2.5rem !important;
          font-family: 'Noto Sans KR', sans-serif !important;
          font-size: 1.1rem !important;
          font-weight: 500 !important;
          border-radius: 12px !important;
          transition: all 0.2s ease-in-out !important;
          box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2) !important;
      }
      
      .stButton > button:hover {
          background-color: #4338ca !important;
          transform: translateY(-1px);
          box-shadow: 0 6px 8px -1px rgba(79, 70, 229, 0.3) !important;
      }
      
      .stButton > button:active {
          transform: translateY(0);
      }

      /* 스크롤바 스타일링 */
      .stTextArea textarea::-webkit-scrollbar {
          width: 8px;
      }
      
      .stTextArea textarea::-webkit-scrollbar-track {
          background: #374151;
          border-radius: 4px;
      }
      
      .stTextArea textarea::-webkit-scrollbar-thumb {
          background: #4b5563;
          border-radius: 4px;
      }
      
      .stTextArea textarea::-webkit-scrollbar-thumb:hover {
          background: #6b7280;
      }

      /* 마크다운 텍스트 스타일 */
      .markdown-text {
          background-color: #374151;
          color: #f3f4f6;
          padding: 1rem;
          border-radius: 12px;
          border: 1px solid #4b5563;
          font-family: 'Noto Sans KR', sans-serif;
          font-size: 1rem;
          line-height: 1.6;
          height: 500px;
          overflow-y: auto;
          margin-bottom: 0.75rem;
      }
  </style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "saved_file_path" not in st.session_state:
    # 업로드된 PDF 파일 경로 및 이름 저장
    st.session_state['saved_file_path'] = None
if "saved_file_viewed" not in st.session_state:
    # 업로드가 되었다면 True로 설정
    st.session_state['saved_file_viewed'] = False
if "summary" not in st.session_state:
    st.session_state['summary'] = None
if "summary_display" not in st.session_state:
    st.session_state['summary_display'] = False
if "messages" not in st.session_state:
    st.session_state['messages'] = []

# RAG 기반 질의 응답...
doc_talker = DocumentTalker()

# 제목 섹션
st.markdown('<h1 class="title">문서와 즐거운 대화하기</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">다양한 문서를 로딩해서 그 문서의 내용에 대해서 아주 자세히 질문해 보세요. 요약을 참고하시면 첫 질문을 쉽게 하실 수 있을거에요.</p>',
    unsafe_allow_html=True,
)

# Define the upload directory
UPLOAD_DIR = "uploaded_files"
# Ensure the directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def save_uploaded_file(uploaded_file):
    """
    Save the uploaded file to the server's upload directory.
    """
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# 스타일 옵션 섹션
style_container = st.container(border=True)
with style_container:
    col1, col2 = st.columns(2)
    with st.container(border=True):
        with col1:
            st.markdown('<p class="label">문서 파일 업로드</p>', unsafe_allow_html=True)
            # File uploader with multiple allowed file types
            uploaded_file = st.file_uploader(
                "대화를 나눌 파일을 업로드해 보세요.", 
                #type=["pdf", "doc", "docx", "hwp", "hwpx", "ppt", "pptx", "txt"]
                type=["pdf"]
            )
            
            options = [
                "예시문서1.pdf",
                "예시문서2.pdf",
                "예시문서3.pdf",
                "예시문서4.pdf",
            ]
            demo_file = st.pills(
                "예시문서", 
                options, 
                selection_mode='single', 
                label_visibility="collapsed"
            )
            # 데모 파일은 이미 서버에 업로드되어 있음.
            if demo_file is not None:
                saved_file_path = os.path.join(UPLOAD_DIR, demo_file)
                if saved_file_path != st.session_state['saved_file_path']:
                    st.session_state['saved_file_viewed'] = False
                    st.session_state['summary'] = None
                    st.session_state['summary_display'] = False
                    st.session_state['messages'] = []
                # st.success(f"File saved successfully at: {saved_file_path}")
                # 업로드된 파일 패스 저장.
                st.session_state['saved_file_path'] = saved_file_path
            
            if uploaded_file is not None:
                # Display uploaded file details
                # file_details = {
                #     "Filename": uploaded_file.name,
                #     "FileType": uploaded_file.type,
                #     "FileSize": uploaded_file.size
                # }

                # Save the uploaded file to the server
                saved_file_path = save_uploaded_file(uploaded_file)
                if saved_file_path != st.session_state['saved_file_path']:
                    st.session_state['saved_file_viewed'] = False
                    st.session_state['summary'] = None
                    st.session_state['summary_display'] = False
                    st.session_state['messages'] = []
                # st.success(f"File saved successfully at: {saved_file_path}")
                # 업로드된 파일 패스 저장.
                st.session_state['saved_file_path'] = saved_file_path
            
            
    with st.container(border=True):
        with col2:
            st.markdown('<p class="label">답변 스타일 선택</p>', unsafe_allow_html=True)
            options = [
                "격식 있고 정중한",
                "일상적이고 친근한",
                "감정에 호소하는",
                "스토리텔링",
                "간결하고 목적 지향적인",
                "상상력과 감정을 담아 표현하는",
                "질문을 자주하는",
                "친절하고 상세하게 설명하는",
                "창의적이고 아이디어가 넘치는",
            ]
            style = st.pills(
                "스타일",
                options,
                selection_mode="single",
                default="격식 있고 정중한",
                label_visibility="collapsed",
            )
            
def stream_to_string(stream):
    str = ""
    for token in stream:
        str += token
    return str

# 메인 컨텐츠 컨테이너
col1, col2 = st.columns(2)

with col1:
    input_container = st.container(border=True)
    with input_container:
        st.markdown(
            '<p class="label">업로드된 문서</p>', unsafe_allow_html=True
        )
        if st.session_state['saved_file_path']:
            with st.spinner('업로드하신 문서를 열심히 공부하고 있어요...'):
                pdf_viewer(st.session_state['saved_file_path'])
                st.session_state['saved_file_viewed'] = True
                            
                summary = doc_talker.load_documnet(st.session_state['saved_file_path'])
                doc_talker.build_retriever()
                st.session_state['summary'] = summary
    
with col2:
    output_container = st.container(border=True)
    with output_container:
        st.markdown(
            '<p class="label">문서와 대화 나누기</p>', unsafe_allow_html=True
        )
        if st.session_state.summary:
            summary_container = st.container(border=True)
            summary_container.empty()
            with summary_container:
                st.markdown('업로드한 문서에 대해서 간략하게 소개드리겠습니다.')
                st.markdown(stream_to_string(st.session_state.summary))
                
            chat_container = st.container(border=False)
            with chat_container.chat_message("assistant"):
                st.markdown('업로드하신 문서에 대해서 질문이나 의견 있으신가요?')
                
            for message in st.session_state.messages:
                with chat_container.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            if prompt := st.chat_input('이제 이 문서에 대해서 자유롭게 대화해 보세요.'):
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": prompt})
                # Display user message in chat message container
                with chat_container.chat_message("user"):
                    st.markdown(prompt)
                
                # Display assistant response in chat message container
                with chat_container.chat_message("assistant"):
                    response = doc_talker.ask_document(prompt)
                    response_str = st.write_stream(response)
                    st.session_state.messages.append({"role": "assistant", "content": response_str})