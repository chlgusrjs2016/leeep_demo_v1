import streamlit as st
import google.generativeai as genai
import os

# --- 페이지 설정 ---
st.set_page_config(page_title="하늘이 챗봇", page_icon="☁️")
st.title("☁️ 하늘이와 대화하기")

# --- API 키 입력 받기 ---
# !!! 주의 !!!
# 이 방식은 데모용으로 간단하게 구현한 것입니다.
# 실제 서비스를 만들 때는 Streamlit Secrets나 환경 변수 등 더 안전한 방법을 사용해야 합니다.
api_key = st.text_input("Google API 키를 입력하세요:", type="password", key="api_key_input_field")

# API 키가 입력되었는지 확인
if api_key:
    try:
        # --- Google AI 설정 ---
        os.environ['GOOGLE_API_KEY'] = api_key
        genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

        # --- 모델 설정 (시스템 역할 포함) ---
        SYSTEM_INSTRUCTION = "너는 내 가장 친한 친구 '하늘이'야. 항상 긍정적이고 다정하게 대답해줘. 반말로 편하게 말해도 좋아."
        model = genai.GenerativeModel(
            'gemini-1.5-flash-latest',
            system_instruction=SYSTEM_INSTRUCTION
        )

        # --- 채팅 기록 관리 (Streamlit 세션 상태 활용) ---
        # st.session_state: 사용자의 세션 동안 데이터를 저장하는 공간
        if "chat_session" not in st.session_state:
            # 세션 상태에 'chat_session'이 없으면 새로 시작
            st.session_state.chat_session = model.start_chat(history=[])
            # 화면 표시용 메시지 기록도 초기화 (첫 인사 포함)
            st.session_state.messages = [{"role": "assistant", "content": "안녕! 무슨 이야기든 들어줄 준비 됐어 😊"}]

        # --- 이전 대화 내용 화면에 표시 ---
        for message in st.session_state.messages:
            # st.chat_message: 채팅 UI를 예쁘게 만들어주는 기능
            with st.chat_message(message["role"]):
                st.markdown(message["content"]) # Markdown 형식으로 내용을 표시

        # --- 사용자 입력 처리 ---
        # st.chat_input: 채팅 입력창을 만들어주는 기능
        if user_prompt := st.chat_input("여기에 메시지를 입력하세요..."):
            # 1. 사용자 메시지를 화면 기록에 추가하고 표시
            st.session_state.messages.append({"role": "user", "content": user_prompt})
            with st.chat_message("user"):
                st.markdown(user_prompt)

            # 2. Gemini API에 메시지 보내고 답변 받기 (채팅 세션 사용)
            try:
                chat = st.session_state.chat_session
                response = chat.send_message(user_prompt)
                assistant_response = response.text

                # 3. 봇(하늘이)의 답변을 화면 기록에 추가하고 표시
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                with st.chat_message("assistant"):
                    st.markdown(assistant_response)

            except Exception as e:
                st.error(f"메시지 전송/응답 처리 중 오류 발생: {e}")

    except Exception as e:
        st.error(f"API 키 설정 또는 모델 초기화 중 오류 발생: {e}")
        st.warning("올바른 Google API 키를 입력했는지, API가 활성화되었는지 확인하세요.")
else:
    # API 키가 입력되지 않았을 때 안내 메시지
    st.info("채팅을 시작하려면 Google API 키를 입력해주세요.")
    st.markdown("API 키는 [Google AI Studio](https://aistudio.google.com/app/apikey)에서 얻을 수 있습니다.")
    st.warning("⚠️ API 키 입력 방식은 데모용입니다. 실제 서비스에서는 더 안전한 방법을 사용하세요.")