# import libraries
import streamlit as st
import openai
from docx import Document
import random
import textwrap
from openai import OpenAI
from PIL import Image
from docx import Document
import time

# General Setting
st.set_page_config(page_title="Guesstimation Trainer", layout="centered")

# Call OpenAI API
openai.api_key = st.secrets["OPENAI_API_KEY"]
# OpenAI 클라이언트 생성
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# GPT 답변을 저장할 공간 생성
if "gpt_responses" not in st.session_state:
    st.session_state.gpt_responses = []

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
        model="gpt-4o-mini", 
        messages=[
            {"role": "system", "content": prompt}
        ],
        temperature=1.0
    )
    return response.choices[0].message.content

# 챕터로 나누기
def split_chapters(full_text):
    chapters = {}
    current_chapter = None
    buffer = []

    for line in full_text.split("\n"):
        if line.startswith("Chapter"):
            if current_chapter:
                chapters[current_chapter] = buffer
            current_chapter = line.strip()
            buffer = []
        else:
            buffer.append(line.strip())
    if current_chapter:
        chapters[current_chapter] = buffer
    return chapters


def summarize_with_gpt(chapter_title, chapter_text, step):
    st.write("잠시만 기다려 주세요...")
    prompt = f"""
    You are a professional tutor helping a student study "Guesstimation".
    The BOOK CHAPTER below is from a Guesstimation book.
    
    Please display this chapter step by step, in Korean.
    For each step, do the following:
    1. Summarize the key concepts in easy-to-understand Korean.
    2. Comments (Why is it important? How can it be applied?)
    3. If there is a problem (example), present the problem + model answer + explanation.
    
    Output should be structured and easy to follow. It should be in Korean.
    Make it like a summary that helps the student grasp the key points quickly, but be detailed in necessary parts..
    Make sure it is easy to read and understand - it should be readable in terms of formatting.
    The student is currently viewing the {step}th part of this chapter.
    If it is 1st part, provide a Chatper 1 summary.
    If it is 2nd part, provide a Chatper 2 summary, and so on.
    Don't miss a single concept and summzarize everything in the chapter.
    At the end, provide a brief conclusion and key takeaways for each chapter.
    Do not use more than two enter spaces between paragraphs, because the output will be split based on double enter spaces. 


    CHAPTER TITLE: {chapter_title}
    BOOK CHAPTER CONTENT:
    {chapter_text}
    """
    return ask_gpt(prompt)  # ✅ 기존 코드의 ask_gpt 함수 활용

# ======== 메인 UI ========

# 페이지 기본 설정
st.set_page_config(
    page_title="Guesstimation AI Trainer",
    page_icon="🎯",
    layout="centered"
)
def reset_study():
    st.session_state.study_index = 0
    st.session_state.mode = "study"

def reset_daily():
    st.session_state.daily_question = None
    st.session_state.daily_answer = None
    st.session_state.mode = "daily"

def main():

    if "daily_question" not in st.session_state:
        st.session_state.daily_question = None
    if "daily_question_prompt" not in st.session_state:
        st.session_state.daily_question_prompt = None
    if "daily_feedback" not in st.session_state:
        st.session_state.daily_feedback = None
    if "mode" not in st.session_state:
        st.session_state.mode = None

    # 이미지 표시
    image_path = 'iconlogowhite.png'
    image = Image.open(image_path)


    st.image(image , width=100)
    st.title("Guesstimation Trainer")
    
    
    st.write("")
    st.write("")
    st.write("")


    st.markdown(
        """
        **환영합니다!**  
        이 앱은 게스티메이션 책을 기준으로 공부를 하기 위한 AI 기반 학습 도구입니다.  


        아래에서 모드를 선택하세요.
        """
    )
    st.write("")
    st.write("")

    
   
    


    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 공부모드")
        st.write("책의 챕터를 선택하여 해당 내용의 요점과 설명을 들으며 공부합니다.")
        
    with col2:
        st.markdown("### 데일리 액서사이즈")
        st.write("GPT가 랜덤으로 내 주는 문제를 풀고 피드백을 받아봅니다.")
        
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 공부 모드", key="study", use_container_width=True):
            reset_study()
        
    with col2:
        if st.button("📅 데일리 액세사이즈", key="daily", use_container_width=True):
            reset_daily()

    st.write("")
    st.write("")

# daily_mode 유지
    if st.session_state.mode == "daily":
        st.subheader("📅 오늘의 문제")

        # 문제를 session_state에 저장 (처음 한 번만)
        if st.session_state.daily_question is None:
            question_prompt = f""" 
                In the below BOOK:, I've provided you with the Guesstimation book that you are going to use. 

            You are supposed to create a Guesstimation problem based on the book content for a student who does not have a time to read the book.

            Make sure that the problem is from the book content, and is suitable for a student who has just learned the key concepts of Guesstimation. 

        

            Greet the student and create a random problem based on the book content, and just a single question.

            Provide the question in Korean. The problem must be randomly chosen as the user will use this service multiple times so it does not overlap with the previous studies.

            ###
            BOOK:

            {book_content}  # token 제한 있으면 앞부분 일부만 전달 [:4000]

            ###


            """
            st.session_state.daily_question = ask_gpt(question_prompt)

        # 항상 문제 출력
        st.markdown("아래 문제를 하나 낼 테니, 차근차근 생각해 보고 후에 모범 답안과 비교해 보세요.")
        st.markdown(f"{st.session_state.daily_question}")

        # 모범 답안 보기 버튼
        if st.button("💡 모범 답안 보기", key="show_solution"):
            solution_prompt = f"""
            Below is a Guesstimation question. 
            Please provide the following in Korean:

            1. A model answer with reasonable assumptions.
            2. Step-by-step reasoning / how to approach.
            3. Useful tips for solving similar problems.

            QUESTION: {st.session_state.daily_question}
            """
            st.session_state.daily_solution = ask_gpt(solution_prompt)

        # 모범 답안 출력
        if "daily_solution" in st.session_state and st.session_state.daily_solution:
            st.markdown("### ✅ 모범 답안 & 풀이 가이드")
            st.markdown(st.session_state.daily_solution)

        # 새 문제 받기 버튼
        if st.button("🔄 새 문제 받기", key="reset_daily"):
            st.session_state.daily_question = None
            if "daily_solution" in st.session_state:
                del st.session_state.daily_solution
            st.rerun()
                # 👉 나가기 버튼 추가
        if st.button("나가기", key="exit_daily"):
            st.session_state.mode = None

    # -------------------------------
    # 7. 공부 모드
    # -------------------------------
    # if study_mode:
    #     st.subheader("📚 공부 모드 시작")
    #     intro_prompt = f"""
    #     The 'BOOK CONTENT' below is a Guesstimation book that you are going to use.
    #     You are supposed to create a brief explanation of the key concepts of Guesstimation for beginners.
    #     The explanation should be concise, within 5 sentences, and in Korean.

    #     BOOK CONTENT:
    #     {book_content[:4000]}
    #     """
    #     intro_text = ask_gpt(intro_prompt)
    #     st.markdown(f"**개념 설명:**\n{intro_text}")

    #     st.markdown("---")
    #     st.markdown("### 문제 풀이")
    #     for i in range(10):
    #         q_prompt = f"""
    #         다음은 게스티메이션 책의 내용입니다.
    #         The BOOK CONTENT below is a Guesstimation book that you are going to use.
    #         As a professional teacher, are supposed to create a Guesstimation problem based on the book content for a student who does not have a time to read the book.

    #         You should create a problem that is suitable for a student who has just learned the key concepts of Guesstimation.
    #         Please create a Guesstimation problem based on the book content randomly, considering that the student will use this service multiple times so it does not overlap with the previous studies.

    #         The question must be in Korean and should be of medium difficulty.
    #         Question should not overlap with previous questions.

    #         You are going to talk with the student multiple times, so as you talk with them, you must provide a feedback to the student based on their answer, or give them an another chance to answer, or provide hint, if they did not answer correctly at all or was very close. Do not follow a strict format, but rather be flexible and adaptive to the student's needs. 

    #         If the student tries to abuse the system such as asking for random stuff that is out of the context, you should politely refuse and remind them that this is a Guesstimation training tool. Do not let them know that you are an AI, but rather act as a professional teacher who is here to help them learn Guesstimation, and do not provide any information about yourself or the system.

    #         This is {i+1}th conversation with the student. If this is 10th conversation, you should provide a final feedback and summary of the student's performance and end the conversation.
    #         이를 바탕으로 학습용 게스티메이션 문제를 {i+1}번째로 출제해주세요.
    #         Please print everything in KOrean.
    #         BOOK CONTENT:
    #         {book_content}
    #         """
    #         q_text = ask_gpt(q_prompt)
    #         st.markdown(f"**Turn {i+1}:** {q_text}")
    #         ans = st.text_input(f"문제 {i+1} 답변")
    #         if ans:
    #             eval_prompt = f"문제: {q_text}\n답변: {ans}\n이 답변을 평가하고 모범 답안을 제시해주세요."
    #             feedback = ask_gpt(eval_prompt)
    #             st.markdown(feedback)

    if st.session_state.mode == "study":
        st.subheader("📚 공부 모드 시작")
        st.write("사이드 바에서 원하는 챕터를 선택하고, 해당되는 챕터를 학습해 보세요.")
        st.write("")

        # 책 불러오기 & 챕터 나누기
        docx_path = "guesstimation.docx"
        full_text = load_docx(docx_path)
        chapters = split_chapters(full_text)

        # 세션 상태 초기화
        if "chapter" not in st.session_state:
            st.session_state.chapter = list(chapters.keys())[0]
        if "chapter_summary" not in st.session_state:
            st.session_state.chapter_summary = ""

        # 사이드바에서 챕터 선택
        selected_chapter = st.sidebar.radio("Chapters", list(chapters.keys()))
        if selected_chapter != st.session_state.chapter:
            st.session_state.chapter = selected_chapter
            st.session_state.chapter_summary = ""

        # 현재 챕터 내용
        current_chapter = st.session_state.chapter
        chapter_text = chapters[current_chapter]

        # GPT 요약 호출 (처음 한 번만)
        if st.session_state.chapter_summary == "":
            raw_summary = summarize_with_gpt(
                current_chapter, chapter_text, step=1  # step은 고정
            )
            st.session_state.chapter_summary = raw_summary

        # 챕터 전체 요약 표시
        st.markdown(f"### {current_chapter}")
        st.write(st.session_state.chapter_summary)

        # 나가기 버튼
        if st.button("나가기", key="exit"):
            st.session_state.mode = None


        #     st.session_state.step = 1
        #     st.session_state.chapter_summary = summarize_with_gpt(
        #         current_chapter, chapter_text, st.session_state.step
        #     )   

    st.write("")
    st.write("")

    # 👉 여기에 격려 버튼 추가
    if st.button("🌟 오늘의 격려 한마디", key="encouragement", use_container_width=True):
        encouragement_prompt = """
        Please write a short but sincere encouragement message in Korean for people using this service to study.
        The message should be simple, providing positive energy without being overwhelming.
        """
        encouragement = ask_gpt(encouragement_prompt)
        st.success(encouragement)





if __name__ == "__main__":
  main()
















