import os 
from openai import OpenAI
from PIL import Image
import json
import streamlit as st 

st.set_page_config(page_title="챌린지 생성기", page_icon="🚀")

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css('style.css')

os.environ["OPENAI_API_KEY"] = 'YOUR_API_KEY'

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

st.title("challenge generator for saving money")

challenge_image = Image.open('challenge_image.jpeg')
st.image(challenge_image)

st.markdown("### 😊 기본 정보 😊")
monthly_income = st.text_input("월 소득 (ex. 200만원)")
fixed_expense = st.text_input('고정 비용 (ex. 60만원)')
expense_habit = st.text_area("소비 습관을 적어주세요. ex. 택시를 자주 탄다. 가까운 거리지만 걷지 않는다. 배달음식을 자주 먹는다 등등..!!")
expense_status = st.text_area("소비 실태에 대해 적어주세요. 최대한 구체적으로 적어주세요..!! ex. 택시비에 30만원, 식비 100만원, 월세 80만원 등등 고정 지출과 추가 지출을 나눠서 적어주세요!")
my_problem = st.text_area("본인의 소비에서의 가장 큰 문제가 무엇이라고 생각하시나요? 최대한 구체적으로 적어주세요! (ex. 택시를 너무 많이 탄다. 늦잠 자고 택시를 탄다 등)")
difficulty = st.selectbox(
    "챌린지의 난이도를 어떻게 할까요?",
    ['hard', 'medium', 'easy']
)

chain_of_thought_assistant = """
Develop a personalized money-saving challenge to motivate the user based on their monthly income, fixed expenses, spending habits, expense status and identified problems of user's spending habit. Provide a step-by-step plan with precise reasoning for each recommendation, tailored to improve the user's saving habit. Your response should consider the user's financial situation and behavioral tendencies, offering practical and realistic strategies to encourage better saving habits. Additionally, ensure that the challenge is motivating and achievable for the user. Your answer should be in Korean. Think step by step.

Your response should be in the form of a json object that has the following format: {'개선점1': 'reason for the recommendation', '개선점2': 'reason for the recommendation', ...}
""".strip()

if 'start_button_cliked' not in st.session_state:
    st.session_state.start_button_cliked = False

def on_start_button():
    st.session_state.start_button_cliked = True

start_button = st.button("🏃 소비 분석 🏃", on_click=on_start_button)

if st.session_state.start_button_cliked:
    chain_of_thought_prompt = f"""
    monthly income: {monthly_income},
    fixed expense: {fixed_expense},
    expense habit: {expense_habit},
    expense_status: {expense_status},
    user's problem in spending habit: {my_problem}
    """.strip()
    # 여기서 고정지출 요소들도 적어달라고 하자!
    
    problem_resp = client.chat.completions.create(
        model='gpt-3.5-turbo-0125',
        messages=[
            {'role': 'system', 'content': chain_of_thought_assistant},
            {'role': 'user', 'content': chain_of_thought_prompt}
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )
    
    prob_dict = json.loads(problem_resp.choices[0].message.content)
    
    recommendation_placeholder = st.container()
    recommendation_list = []
    
    for key, value in prob_dict.items():
        recommendation_list.append(f"{key}: {value}")
    
    for i in range(len(recommendation_list)):
        recommendation_placeholder.text(recommendation_list[i])
    
    if recommendation_list:
        desire_change = st.text_input("위의 개선점 중 어떤 부분에 집중을 하고 싶으신가요?")
        long_term_goal = st.text_area("챌린지의 장기적 목표는 무엇인가요? (ex. 바람직하지 못한 내 소비 습관 개선하기!)")
        short_term_goal = st.text_area("챌린지의 단기적인 목표는 무엇인가요?(ex. 300만원 모아서 명품백 사기!)")

        determine_if_more = st.button("🏃 챌린지를 만들어 볼까요? 🏃")

        if determine_if_more:
            information_enough_system_prompt = """
            You are an assistant who helps create hyper-personalized saving challenges for people. As input, you will be presented with the user's personal consumption habits that the user most wants to improve, the user's average monthly income, the user's spending structure (fixed spending, additional spending), and the long-term and short-term goals that people want to achieve through the challenge. You need to determine whether you can create a sufficiently personalized challenge with the information you entered. Here, hyper-personalized challenges refer to challenges just for users that can be created based on personal information. I hope you make your judgment as picky as possible.
            
            Your answer should be in the form of json object that has the following json format: {'is_enough': '[Y] if the information is enough, [N] if more information is needed'.}
            """
            
            information_enought_user = f"""
            가장 개선하고 싶은 부분 : {desire_change},
            챌린지의 장기적 목표 : {long_term_goal},
            챌린지의 단기적 목표 : {short_term_goal},
            한달 평균 수익 : {monthly_income},
            소비 구조 : {expense_status}
            """.strip()
            
            enough_resp = client.chat.completions.create(
                model='gpt-3.5-turbo-0125',
                messages={
                    'role': 'system', 'content': information_enough_system_prompt,
                    'role': 'user', 'content': information_enought_user
                },
                response_format={'type': 'json_object'}
            )
            
            enought_response = json.loads(enough_resp.choices[0].message.content)
            st.markdown(enough_response)
            
            if enough_response['is_enough'] == 'Y':
                pass
            if enough_response['is_enough'] == 'N':
                pass
