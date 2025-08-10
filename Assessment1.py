# import libraries
import streamlit as st
import openai
from docx import Document
import random
import textwrap

# General Setting
st.set_page_config(page_title="Guesstimation Trainer", layout="centered")

# Call OpenAI API
openai.api_key = st.secrets["OPENAI_API_KEY"]
# OpenAI 클라이언트 생성
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# load docx file
@st.cache_data
def load_docx(docx_path):
    doc = Document(docx_path)
    full_text = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            full_text.append(text)
    return "\n".join(full_text)


# get the book information
BOOK_PATH = "guesstimation.docx"  
book_content = load_docx(BOOK_PATH)

# Function to call GPT API
def ask_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=[
            {"role": "system", "content": "You are a helpful assistant that creates and evaluates guesstimation problems for people who does not have an enough time to go through guesstimation book."},
            {"role": "system", "content": prompt}
        ],
        temperature=0.8
    )
    return response.choices[0].message["content"]

# ======== 메인 UI ========

# 페이지 기본 설정
st.set_page_config(
    page_title="Guesstimation AI Trainer",
    page_icon="🎯",
    layout="centered"
)


st.title("🎯 Guesstimation Trainer")
st.markdown(
    """
    **환영합니다!**  
    이 앱은 게스티메이션 책을 기준으로 공부를 하기 위한 AI 기반 학습 도구입니다.  
    아래에서 모드를 선택하세요.
    """
)

col1, col2 = st.columns(2)
with col1:
    daily_mode = st.button("📅 데일리 액세사이즈", use_container_width=True)
with col2:
    study_mode = st.button("📚 공부 모드", use_container_width=True)


if daily_mode:
    st.subheader("📅 오늘의 문제")
    # 책 내용 기반으로 GPT가 문제 생성
    question_prompt = f"""
     In the below BOOK:, I've provided you with the Guesstimation book that you are going to use. 
    You are supposed to create a Guesstimation problem based on the book content for a student who does not have a time to read the book.
    Greet the student and create a random problem based on the book content, and just a single question.
    Provide the question in Korean.
    ###
    BOOK:
    {book_content}  # token 제한 있으면 앞부분 일부만 전달 [:4000]
    ###
    """
    question = ask_gpt(question_prompt)
    st.markdown(f"{question}")

    user_answer = st.text_area("✏️ 당신의 답변을 입력하세요", height=150)
    if st.button("제출"):
        eval_prompt = f"""
        The ANSWER below provides the user's answer to the question.
        Please do the following:
        1. Score the answer from 0 to 100 based on its accuracy.
        2. Provide feedback on the answer if the score is not 100, including:
            1. What is good about the answer
            2. Areas for improvement
        3. Provide a model answer.

        ###
        QUESTION: {question}
        ANSWER: {user_answer}
        """
        feedback = ask_gpt(eval_prompt)
        st.markdown(feedback)

# -------------------------------
# 7. 공부 모드
# -------------------------------
if study_mode:
    st.subheader("📚 공부 모드 시작")
    intro_prompt = f"""
    다음은 게스티메이션 책의 내용입니다.
    이를 바탕으로 게스티메이션 초보자를 위한 핵심 개념 설명을 5문장 이내로 해주세요.
    책 내용:
    {book_content[:4000]}
    """
    intro_text = ask_gpt(intro_prompt)
    st.markdown(f"**개념 설명:**\n{intro_text}")

    st.markdown("---")
    st.markdown("### 문제 풀이")
    for i in range(5):
        q_prompt = f"""
        다음은 게스티메이션 책의 내용입니다.
        이를 바탕으로 학습용 게스티메이션 문제를 {i+1}번째로 출제해주세요.
        난이도는 중간 수준이고, 한국어로 작성해주세요.
        책 내용:
        {book_content}
        """
        q_text = ask_gpt(q_prompt)
        st.markdown(f"**문제 {i+1}:** {q_text}")
        ans = st.text_input(f"문제 {i+1} 답변")
        if ans:
            eval_prompt = f"문제: {q_text}\n답변: {ans}\n이 답변을 평가하고 모범 답안을 제시해주세요."
            feedback = ask_gpt(eval_prompt)
            st.markdown(feedback)