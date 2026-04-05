# app_chatbot.py
# 실행: streamlit run app_chatbot.py
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# .env 파일에서 OPENAI_API_KEY를 자동으로 읽어옴
load_dotenv()

# 참고: 한글 변수명은 학습 이해를 위한 것입니다. 실무에서는 영문 변수명을 사용하세요.

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("API 키가 설정되지 않았습니다. .env 파일에 OPENAI_API_KEY를 추가하세요.")
    st.stop()

client = OpenAI(api_key=api_key)

# ===== 역할 정의 (CRAFT 프레임워크 적용) =====
ROLES = {
    "파이썬 튜터": """[Context] 파이썬을 처음 배우는 비전공자 학생이 프로그래밍 기초를 질문합니다.
[Role] 당신은 3년차 백엔드 개발자이고 신입 교육을 담당합니다.
[Action] 질문에 항상 실행 가능한 코드 예시를 포함해 답변합니다. 잘못된 코드를 보여주면 어디가 잘못인지 짚고 수정된 코드를 제시합니다.
[Format] 답변 구조: ① 핵심 설명 (2-3문장) → ② 코드 예시 (```python 블록) → ③ 한 줄 팁. 마지막에 항상 '더 궁금한 점이 있나요?'라고 묻습니다.
[Tone] 친절하고 격려하는 선배 개발자 말투. 전문 용어는 쉬운 비유와 함께 설명합니다.""",

    "딥러닝 멘토": """[Context] 딥러닝을 처음 접하는 학생이 개념을 질문합니다. 수학적 배경이 약합니다.
[Role] 당신은 5년차 ML 엔지니어입니다.
[Action] CNN, RNN, YOLO 등 딥러닝 개념을 실생활 비유로 설명합니다. 수학 공식은 필요할 때만 직관적 수준으로 사용합니다. 학습 로드맵과 추천 자료를 함께 제공합니다.
[Format] 답변 구조: ① 한 줄 요약 → ② 실생활 비유 → ③ 핵심 원리 → ④ 추천 자료
[Tone] 열정적이고 친근한 멘토. 학생의 궁금증을 환영하는 태도.""",

    "코드 리뷰어": """[Context] 프로그래밍을 배우는 학생이 작성한 파이썬 코드를 리뷰합니다.
[Role] 당신은 시니어 개발자이며 코드 리뷰 전문가입니다.
[Action] 코드의 문제점을 찾고 개선된 버전을 제시합니다. 버그보다 설계 문제를 먼저 지적하고, 개선 이유를 반드시 설명합니다.
[Format] 답변 구조: ① 전체 평가 (한 줄) → ② 개선 포인트 (번호 리스트) → ③ 수정된 코드
[Tone] 격려하되 핵심은 날카롭게. "잘 작성했네요! 여기만 더 좋아지면..." 패턴 사용.""",
}

# ===== Streamlit UI =====
st.set_page_config(page_title="역할 전환 AI 챗봇", page_icon="💬", layout="centered")
st.title("💬 프로그래밍 학습 AI 챗봇")
st.caption("역할을 선택하면 해당 전문가로 대화합니다.")

# 사이드바: 역할 선택
with st.sidebar:
    st.header("설정")
    선택_역할 = st.radio("대화 상대 선택", list(ROLES.keys()))

    # 역할 변경 시 대화 초기화
    if "현재_역할" not in st.session_state:
        st.session_state["현재_역할"] = 선택_역할
    if st.session_state["현재_역할"] != 선택_역할:
        st.session_state["현재_역할"] = 선택_역할
        st.session_state["messages"] = []
        st.rerun()

    st.divider()
    st.markdown(f"**현재 역할**: {선택_역할}")
    st.markdown(f"**대화 수**: {len(st.session_state.get('messages', []))} 턴")

    if st.button("대화 초기화", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

# 대화 히스토리 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 이전 대화 표시
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 사용자 입력 처리
if user_input := st.chat_input(f"{선택_역할}에게 말을 걸어보세요..."):
    # 사용자 메시지 표시 & 저장
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state["messages"].append({"role": "user", "content": user_input})

    # API 호출 (system + 전체 히스토리)
    api_messages = [
        {"role": "system", "content": ROLES[선택_역할]},
    ] + st.session_state["messages"]

    with st.chat_message("assistant"):
        with st.spinner("생각 중..."):
            response = client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=api_messages,
                temperature=0.7,
                stream=True,   # 실시간 스트리밍
            )
            전체_답변 = st.write_stream(response)

    # AI 응답 저장
    st.session_state["messages"].append({"role": "assistant", "content": 전체_답변})
