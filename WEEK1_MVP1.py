from openai import OpenAI
import streamlit as st 
import json
import os

st.title("Challenge Generator")

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

if "initialized" not in st.session_state:
    st.session_state.initialized = False

if "messages" not in st.session_state:
    st.session_state.messages = []
    
if not st.session_state.initialized:
    st.session_state.messages.append({'role': 'assistant', 'content': '본인이 몇살이며,(학생이라면 몇학년인지도 함께 말해주세요!) 어떤 분야에서 챌린지를 만들고 싶은지 알려주세요! [최대한 구체적으로 말해주세요! 운동이라고 하지 말고 농구, 공부라고 하지 말고 수학 공부, 중간고사 시험 잘치기라고 하지 말고 수학 시험 잘치기 등]'})
    st.session_state.initialized = True

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

information = st.chat_input("응답을 입력해주세요!")
determination_prompt = """
In your role as an assistant for designing hyper-personalized challenges, your task is to assess whether the user has provided sufficient information to create a personalized challenge in their desired field. Consider the necessary elements for creating a challenge in the user's specified field and determine if all the required information has been provided. Your assessment should focus on ensuring that the user's input contains all the essential elements needed to design a personalized challenge effectively.

To design personalized challenges, identify:
Field: Specify the domain (health, education, personal development, finance, art, technology).
Experience Level: Ascertain current proficiency in the challenge domain.
Goals: Define what the participant aims to achieve.
Preferences/Constraints: Note any likes, dislikes, and limitations (time, resources).
Adaptability: Plan for feedback-based adjustments.
Timeline: Establish the challenge duration or deadline.
Use this information to tailor challenges to individual needs, ensuring a rewarding experience.

Be aware not to ask user to provide information that is not required nor already provided. For example when user asks to create challenge in saving money, you don't need information about which types of food they prefer.

When asking user to provide additional information, you have to take into consideration if that information is already given. If that information is already given you should not ask for more. Your answer should be in Korean. Think step by step.

Your answer should be in the form of json object that has the following format: {'is_enough': '[Y] if the given informations are enough, [N] if more information is requried', 'required_information': '[Additional information required to provide user with a personalized challenge.  Ask for one question at a time and provide example answer.] if is_enough is [N], [] otherwise'}
"""

convolution_prompt = """ 
You are an assistant who compiles and organizes the information provided so far by users. You have to make summarization as short as possible while including every information given in the prompt. Your answer should be in Korean.
"""

if information:
    st.session_state.messages.append({'role': 'user', 'content': information})
    with st.chat_message('user'):
        st.markdown(information)
    total_info = ""
    
    for message in st.session_state.messages:
        if message['role'] == 'user':
            total_info += message['content']
    
    total_info_summary = client.chat.completions.create(
        model='gpt-4-turbo-preview',
        messages=[
            {'role': 'system', 'content': convolution_prompt},
            {'role': 'user', 'content': total_info}
        ],
        max_tokens=1024
    ).choices[0].message.content
    
    determine_response = client.chat.completions.create(
        model='gpt-4-turbo-preview',
        messages=[
            {'role': 'system', 'content': determination_prompt},
            {'role': 'user', 'content': total_info_summary}
        ],
        response_format={'type': 'json_object'}
    )
    
    determination_json = json.loads(determine_response.choices[0].message.content)
    
    if determination_json['is_enough'] == "Y":
        with st.spinner('챌린지가 만들어지고 있어요!!'):
            st.markdown(total_info_summary)
            st.markdown(total_info)
            challenge_generator_prompt = """ 
            As a personalized challenge provider, your task is to create tailored challenges for users based on the information they provide. You will be presented with a summary of the user's information, and your goal is to propose a challenge that is perfectly suited to the user. The challenge should be personalized to align with the user's goals and the specified challenge period, incorporating relevant details to make it as specific and meaningful as possible to the individual user.

            Your response should offer a challenge that is well-aligned with the user's stated goals and is suitable for the specified challenge period. Please ensure that the challenge is personalized and takes into account the user's unique circumstances, preferences, and aspirations. Your proposed challenge should be engaging, motivating, and tailored to inspire the user to achieve their objectives within the given timeframe.

            Please note that your challenge should be flexible enough to accommodate a variety of user goals and challenge periods, while also being creative and original in its design. Answer in Korean.
            """
            
            st.markdown("챌린지가 완성됐어요!!!")
            
            challenge_response = client.chat.completions.create(
                model='gpt-4-turbo-preview',
                messages=[
                    {'role': 'system', 'content': challenge_generator_prompt},
                    {'role': 'user', 'content': total_info_summary}
                ]
            ).choices[0].message.content
            
            st.markdown(challenge_response)
    else:
        more_info = determination_json['required_information']
        st.session_state.messages.append({'role': 'assistant', 'content': more_info})
        with st.chat_message('assistant'):
            st.markdown(more_info)
            
    
