# import libraries
import streamlit as st
import openai
from docx import Document
import random
import textwrap
from openai import OpenAI
from PIL import Image

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

# ======== 메인 UI ========

# 페이지 기본 설정
st.set_page_config(
    page_title="Guesstimation AI Trainer",
    page_icon="🎯",
    layout="centered"
)

def main():

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
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 공부 모드", use_container_width=True):
            st.session_state.mode = "study"
        
    with col2:
        if st.button("📅 데일리 액세사이즈", use_container_width=True):
            st.session_state.mode = "daily"

# daily_mode 유지
    if "mode" in st.session_state and st.session_state.mode == "daily":
        st.subheader("📅 오늘의 문제")

        # 책 내용 기반으로 GPT가 문제 생성
        if "daily_question" not in st.session_state:
            question_prompt = f"""
            In the below BOOK:, I've provided you with the Guesstimation book that you are going to use. 
            You are supposed to create a Guesstimation problem based on the book content for a student who does not have a time to read the book.
            Greet the student and create a random problem based on the book content, and just a single question.
            Provide the question in Korean. The problem must be randomly chosen as the user will use this service multiple times so it does not overlap with the previous studies.
            ###
            BOOK:
            {book_content}  # token 제한 있으면 앞부분 일부만 전달 [:4000]
            ###
            """
            
            question = ask_gpt(question_prompt)

            st.markdown(f"{question}")

            user_answer = st.text_area("✏️ 당신의 답변을 입력하세요", height=150)
            
            # 문제와 답변 유지 (필요하면 제거 가능)
            st.session_state.daily_answer = user_answer


            button1 = st.button("제출")

            if button1:
                
                eval_prompt = f"""
                The ANSWER below provides the user's answer to the question.
                Please do the following:

                Please provide a feedback or a comment to the user based on their answer for them to get better understanding of the question and Guesstimation concept.
                While providing the feedback, make sure that you do not evalute them, or mention that it is correct or not, but rather provide a feedback that helps them to understand the concept better.
                Also provide a short positive feedback to encourage them to keep going. 


                ###
                QUESTION: {question}
                ANSWER: {user_answer}
                """
   

                st.markdown("#### 📊 평가 결과")
                st.write("평가가 나올 때까지 잠시 기다려 주세요....")
                feedback = ask_gpt(eval_prompt)
                st.markdown(feedback)


            # 이전 답변 표시
            if "daily_answer" in st.session_state:
                st.markdown(f"**이전 답변:** {st.session_state.daily_answer}")

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

    if "mode" in st.session_state and st.session_state.mode == "study":
        st.subheader("📚 공부 모드 시작")

        # 1️⃣ 대화 상태 초기화
        if "study_turn" not in st.session_state:
            st.session_state.study_turn = 0
            st.session_state.study_history = []  # (질문, 답변, 피드백) 기록

            # 개념 설명 생성
            intro_prompt = f"""
            The 'BOOK CONTENT' below is a Guesstimation book that you are going to use.
            You are supposed to create a brief explanation of the key concepts of Guesstimation for beginners.
            The explanation should be concise, within 5 sentences, and in Korean.

            BOOK CONTENT:
            {book_content}
            """
            st.session_state.study_intro = ask_gpt(intro_prompt)

        # 2️⃣ 개념 설명 출력 (첫 턴에만)
        if st.session_state.study_turn == 0:
            st.markdown(f"**개념 설명:**\n{st.session_state.study_intro}")
            st.markdown("---")

        # 3️⃣ 이전 대화 기록 출력
        if st.session_state.study_history:
            for idx, (q, a, fb) in enumerate(st.session_state.study_history, 1):
                st.markdown(f"**Turn {idx}:** {q}")
                st.markdown(f"**My answer:** {a}")
                st.markdown(f"**Feedback:** {fb}")
                st.markdown("---")

        # 4️⃣ 현재 턴 처리 (10턴 이하)
        if st.session_state.study_turn < 10:
            if "current_question" not in st.session_state:
                # 새로운 문제 생성
                turn = st.session_state.study_turn + 1
                q_prompt = f"""
        
        The BOOK CONTENT below is a Guesstimation book that you are going to use.
            As a professional teacher, are supposed to create a Guesstimation problem based on the book content for a student who does not have a time to read the book.

            You should create a problem that is suitable for a student who has just learned the key concepts of Guesstimation.
            Please create a Guesstimation problem based on the book content randomly, considering that the student will use this service multiple times so it does not overlap with the previous studies.

            The question must be in Korean and should be of medium difficulty.
            Question should not overlap with previous questions.

            You are going to talk with the student multiple times, so as you talk with them, you must provide a feedback to the student based on their answer, or give them an another chance to answer, or provide hint, if they did not answer correctly at all or was very close. Do not follow a strict format, but rather be flexible and adaptive to the student's needs. 
            Try not to move on to the next question until the student has answered the current question correctly or has been given a chance to answer again when it is not correct. When they ask a question, give them a hint rather than giving them the answer directly or moving on to the next question.
            If the student tries to abuse the system such as asking for random stuff that is out of the context, you should politely refuse and remind them that this is a Guesstimation training tool. Do not let them know that you are an AI, but rather act as a professional teacher who is here to help them learn Guesstimation, and do not provide any information about yourself or the system.

            This is {st.session_state.study_turn+1}th conversation with the student. If this is 10th conversation, you should provide a final feedback and summary of the student's performance and end the conversation.
        
            Please print everything in KOrean.
            BOOK CONTENT:
            {book_content}
                """
                st.session_state.current_question = ask_gpt(q_prompt)

            st.markdown(f"**문제 {st.session_state.study_turn + 1}:** {st.session_state.current_question}")

            user_ans = st.text_input("✏️ 답변 입력", key=f"answer_{st.session_state.study_turn}")
            button2 = st.button("제출", key=f"submit_{st.session_state.study_turn}")

            if button2:
                if user_ans.strip():
                    eval_prompt = f"""
                    문제: {st.session_state.current_question}
                    답변: {user_ans}
                    You are going to talk with the student multiple times, so as you talk with them, you must provide a feedback to the student based on their answer, or give them an another chance to answer, or provide hint, if they did not answer correctly at all or was very close. Do not follow a strict format, but rather be flexible and adaptive to the student's needs. 
                    """
                    feedback = ask_gpt(eval_prompt)

                    # 피드백을 상태에 저장해서 항상 같은 위치에 업데이트
                    st.session_state.current_feedback = feedback
                    st.session_state.study_history.append(
                        (st.session_state.current_question, user_ans, feedback)
                    )

                # 만약 정답이라면 다음 턴으로 넘어가도록 처리 (간단히 점수 포함 여부로 판단)
                if "정답" in feedback or "잘했습니다" in feedback or "100" in feedback:
                    st.session_state.study_turn += 1
                    if "current_question" in st.session_state:
                        del st.session_state.current_question
                    if st.session_state.study_turn == 10:
                        st.success("🎉 10턴 학습이 완료되었습니다! GPT가 종합 피드백을 제공했습니다.")
                        st.stop()

        # --- 피드백 출력 (매번 업데이트) ---
        if "current_feedback" in st.session_state:
            st.markdown("#### 📊 피드백")
            st.markdown(st.session_state.current_feedback)





if __name__ == "__main__":
  main()
















