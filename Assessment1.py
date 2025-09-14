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
    # 임시 메시지 표시

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

# 챕터 본문을 일정 길이로 나누기
def split_into_sections(text_lines, max_len=600):  # 글자 수 단위
    sections, buffer, size = [], [], 0
    for line in text_lines:
        if size + len(line) > max_len and buffer:
            sections.append("\n".join(buffer))
            buffer, size = [line], len(line)
        else:
            buffer.append(line)
            size += len(line)
    if buffer:
        sections.append("\n".join(buffer))
    return sections

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
        **환영합니다.**  
        이 AI앱은 아이컨/인사이트베이의 게스트메이션 가이드북을 기준으로 공부하기 위해서 만들어졌습니다.  


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
            placeholder = st.empty()
            placeholder.write("⏳ 잠시만 기다려 주세요...")
            solution_prompt = f"""
            Below is a Guesstimation question. 
            Please provide the following in Korean:

            1. A model answer with reasonable assumptions.
            2. Step-by-step reasoning / how to approach.
            3. Useful tips for solving similar problems.

            QUESTION: {st.session_state.daily_question}
            """
            st.session_state.daily_solution = ask_gpt(solution_prompt)
            placeholder.empty()

        # 모범 답안 출력
        if "daily_solution" in st.session_state and st.session_state.daily_solution:
            st.markdown("### ✅ 모범 답안 & 풀이 가이드")
            st.markdown(st.session_state.daily_solution)

        # 새 문제 받기 버튼
        if st.button("🔄 새 문제 받기", key="reset_daily"):
            placeholder = st.empty()
            placeholder.write("⏳ 잠시만 기다려 주세요...")

            # 먼저 기존 문제/답안 초기화
            st.session_state.daily_question = None
            if "daily_solution" in st.session_state:
                del st.session_state.daily_solution

            # 그 다음 rerun 실행
            st.rerun()
            placeholder.empty()
  
            if st.button("🔙 처음으로 가기", key="exit_daily_bottom", use_container_width=True):
                st.session_state.mode = None
                for k in ["daily_question", "daily_solution", "daily_feedback"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()
       
            st.markdown("### 🌟 오늘의 격려")
            if st.button("격려 한마디 듣기", use_container_width=True, key="study_encourage"):
                encouragement_prompt = """
                Please write a short but sincere encouragement message in Korean 
                for people studying with this app.
                """
                st.success(ask_gpt(encouragement_prompt))


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
        st.write("챕터를 순서대로 보거나, 아래 버튼을 눌러 이동하세요.")
        st.write("")

        # 챕터/파트 인덱스 초기화
        if "chapter_idx" not in st.session_state:
            st.session_state.chapter_idx = 0
        if "chapter_part" not in st.session_state:
            st.session_state.chapter_part = 0

        # 로딩 표시
        if "study_placeholder" not in st.session_state:
            st.session_state.study_placeholder = st.empty()
        st.session_state.study_placeholder.write("⏳ 잠시만 기다려 주세요...")

        # 책 → 챕터 → 세부 섹션
        full_text = load_docx("guesstimation.docx")
        chapters = split_chapters(full_text)
        chapter_list = list(chapters.keys())

        current_chapter = chapter_list[st.session_state.chapter_idx]
        chapter_text = chapters[current_chapter]
        sections = split_into_sections(chapter_text, max_len=600)   # ← 추가

        # 현재 part에 맞는 키 생성
        key_summary = f"summary_{current_chapter}_{st.session_state.chapter_part}"

        if key_summary not in st.session_state:
            st.session_state[key_summary] = summarize_with_gpt(
                current_chapter,
                sections[st.session_state.chapter_part],
                step=st.session_state.chapter_part + 1,
            )

        st.session_state.study_placeholder.empty()

        # 표시
        st.markdown(f"### {current_chapter}")
        st.write(st.session_state[key_summary])

        st.write("---")
        col1, col2, col3, col4 = st.columns([1,1,1,1])

        # ◀️ 이전 part
        with col1:
            if st.button("◀️ 이전", use_container_width=True):
                if st.session_state.chapter_part > 0:
                    st.session_state.chapter_part -= 1
                    st.rerun()
                elif st.session_state.chapter_idx > 0:  # 이전 챕터로
                    st.session_state.chapter_idx -= 1
                    prev_chap = chapter_list[st.session_state.chapter_idx]
                    prev_sections = split_into_sections(chapters[prev_chap], max_len=600)
                    st.session_state.chapter_part = len(prev_sections) - 1
                    st.rerun()

        # ▶️ 다음 part
        with col2:
            if st.button("다음 ▶️", use_container_width=True):
                if st.session_state.chapter_part < len(sections) - 1:
                    st.session_state.chapter_part += 1
                    st.rerun()
                elif st.session_state.chapter_idx < len(chapter_list) - 1:
                    st.session_state.chapter_idx += 1
                    st.session_state.chapter_part = 0
                    st.rerun()

        # 🔙 처음으로
        with col3:
            if st.button("🔙 처음으로", use_container_width=True):
                st.session_state.mode = None
                for k in list(st.session_state.keys()):
                    if k.startswith("summary_") or k in ["chapter_idx", "chapter_part", "study_placeholder"]:
                        del st.session_state[k]
                st.rerun()

        # (옵션) 챕터 위치 안내
        with col4:
            st.caption(f"{st.session_state.chapter_part+1} / {len(sections)}")
        
        st.caption(f"{st.session_state.chapter_part+1} / {len(sections)}")

        # 📌 여기에 챕터 바로가기 버튼 추가
        st.write("### 🔎 원하는 챕터로 바로 가기")

        st.write("")  # 간격 주기
        st.markdown("### 🌟 오늘의 격려")
        if st.button("격려 한마디 듣기", use_container_width=True, key="study_encourage"):
            encouragement_prompt = """
            Please write a short but sincere encouragement message in Korean 
            for people studying with this app.
            """
            st.success(ask_gpt(encouragement_prompt))

        chapter_cols = st.columns(2)  # 3개씩 나란히
        for i, chap in enumerate(chapter_list):
            col = chapter_cols[i % 2]
            with col:
                if st.button(chap, key=f"jump_{i}", use_container_width=True):
                    st.session_state.chapter_idx = i
                    st.session_state.chapter_part = 0
                    st.rerun()


        #     st.session_state.step = 1
        #     st.session_state.chapter_summary = summarize_with_gpt(
        #         current_chapter, chapter_text, st.session_state.step
        #     )   

        # st.write("")
        # st.write("")

        # # 👉 여기에 격려 버튼 추가
        # if st.button("🌟 오늘의 격려 한마디", key="encouragement", use_container_width=True):
        #     encouragement_prompt = """
        #     Please write a short but sincere encouragement message in Korean for people using this service to study.
        #     The message should be simple, providing positive energy without being overwhelming.
        #     """
        #     encouragement = ask_gpt(encouragement_prompt)
        #     st.success(encouragement)

    st.write("")
    
    st.markdown("---")
    st.markdown("### 📢 추가 학습 & 자료 안내")

    st.markdown(
        """
        **Guesstimation 충분히 익혔나요?**  
        Guesstimation은 **PDF**로 한 번에 정리해 보는 것도 좋습니다.  
        """
    )
    st.link_button("📘 Guesstimation PDF 바로가기", "https://www.insightbay.co.kr/books/view/5")

    st.write("")
    st.markdown(
        """
        이제 다음 루틴으로 넘어가 봅시다.  
        아이컨 회원 <b>67%</b>가 아래 루틴을 따릅니다.  
        순차적으로 익혀 보세요:
        """, unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns(3)

    button_style = """
    <style>
    a.custom-button {
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: #2C7BE5;
        color: white !important;
        padding: 12px 0;
        text-decoration: none;
        border-radius: 10px;
        font-weight: bold;
        font-size: 16px;
        width: 100%;
        height: 50px;
    }
    a.custom-button:hover {
        background-color: #1A5BB8;
        text-decoration: none;
    }
    </style>
    """

    st.markdown(button_style, unsafe_allow_html=True)

    with col1:
        st.markdown('<a class="custom-button" href="https://www.insightbay.co.kr/classes/view/21" target="_blank">① 컨설팅 리서치 강의</a>', unsafe_allow_html=True)

    with col2:
        st.markdown('<a class="custom-button" href="https://www.insightbay.co.kr/classes/view/1" target="_blank">② 전략 Excel</a>', unsafe_allow_html=True)

    with col3:
        st.markdown('<a class="custom-button" href="https://www.insightbay.co.kr/classes/view/4" target="_blank">③ 전략 PPT</a>', unsafe_allow_html=True)


if __name__ == "__main__":
  main()
















