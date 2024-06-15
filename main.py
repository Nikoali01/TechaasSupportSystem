import streamlit as st
import random
import uuid
import time
from streamlit_star_rating import st_star_rating
from streamlit import session_state as ss


def response_generator():
    response = random.choice([
        "Hello there! How can I assist you today?",
        "Hi, human! Is there anything I can help you with?",
        "Do you need help?",
    ])
    response_text = ""
    for word in response.split():
        response_text += word + " "
        yield word + " "
        time.sleep(0.05)
    return response_text


st.title("Чат техподдержки")

first_chat = str(uuid.uuid4())
if "chats" not in ss:
    ss.chats = {first_chat: {'rated': False, 'messages': []}}
if "current_chat" not in ss:
    ss.current_chat = first_chat
if "chat_disabled" not in ss:
    ss.chat_disabled = False
if "rated" not in ss:
    ss.rated = False

with st.sidebar:
    st.header("Ваши чаты")
    chat_names = list(ss.chats.keys())

    for chat_name in chat_names:
        cols = st.columns([4, 1])
        if cols[0].button(chat_name):
            ss.current_chat = chat_name
            st.rerun()
        if len(ss.chats) > 1:
            if cols[1].button("❌", key=f"del_{chat_name}"):
                if len(ss.chats) > 1:
                    all_chats = list(ss.chats)
                    index_to_delete = all_chats.index(chat_name)
                    if index_to_delete > 0:
                        prev_key = all_chats[index_to_delete - 1]
                    else:
                        prev_key = all_chats[1]
                    if ss.current_chat == chat_name:
                        ss.current_chat = prev_key
                    del ss.chats[chat_name]
                    st.rerun()

    if st.button("Создать новый чат"):
        new_chat_name = f"{uuid.uuid4()}"
        ss.chats[new_chat_name] = {'rated': False, 'messages': []}
        ss.current_chat = new_chat_name
        st.rerun()

st.subheader(f"Текущий чат: {ss.current_chat}")

for message in ss.chats[ss.current_chat]['messages']:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if not ss.chats[ss.current_chat]['rated']:
    if prompt := st.chat_input("Ваше сообщение", disabled=ss.chat_disabled) or ss.chat_disabled:
        if not ss.chat_disabled:
            ss.chats[ss.current_chat]['messages'].append(
                {"role": "user", "content": prompt})
            with st.chat_message("user"):
                ss.chat_disabled = True
                st.markdown(prompt)
                st.rerun()

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                time.sleep(2)
            response_container = st.empty()
            response = ""
            for chunk in response_generator():
                response_container.markdown(response + chunk)
                response += chunk
            ss.chat_disabled = False
            print("Acaseacr", ss.chat_disabled)
            ss.chats[ss.current_chat]['messages'].append(
                {"role": "assistant", "content": response})
            st.rerun()


else:
    st.chat_input("Ваше сообщение", disabled=True)
    st.info("Вы уже оценили этот чат, поэтому больше не можете отправлять сообщения.")

if not ss.chats[ss.current_chat]['rated']:
    assistant_responses = [msg for msg in ss.chats[ss.current_chat]['messages'] if
                           msg["role"] == "assistant"]
    if assistant_responses:

        def end_dialog(stars):
            if stars:
                ss.chats[ss.current_chat]['messages'].append(
                    {"role": "user", "content": f"Ваша оценка диалогу: {stars}"}
                )
                ss.chats[ss.current_chat]['rated'] = True
                st.rerun()


        st_star_rating(
            "Оцените ответ системы:",
            maxValue=5,
            defaultValue=0,
            key="rating",
            emoticons=True,
            on_click=end_dialog
        )
