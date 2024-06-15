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
if "avatar" not in ss:
    ss.avatar = "user.png"
if "support_avatar" not in ss:
    ss.support_avatar = "support.png"

with st.sidebar:
    st.header("Ваши чаты")
    chat_names = list(ss.chats.keys())
    col1, col2 = st.columns([4, 1])
    with col1:
        selected_chat = st.radio("chats", label_visibility="hidden", options=chat_names,
                                index=chat_names.index(ss.current_chat), disabled=ss.chat_disabled)
    if selected_chat != ss.current_chat:
        ss.current_chat = selected_chat
        st.rerun()

    if st.button("Создать новый чат", disabled=ss.chat_disabled):
        new_chat_name = f"{uuid.uuid4()}"
        ss.chats[new_chat_name] = {'rated': False, 'messages': []}
        ss.current_chat = new_chat_name
        st.rerun()

col1, col2 = st.columns([4, 1])
with col1:
    st.subheader(f"Текущий чат: {st.session_state['current_chat']}")
with col2:
    if st.button("Удалить текущий чат", disabled=(len(ss.chats) <= 1 or ss.chat_disabled)):
        all_chats = list(ss.chats)
        index_to_delete = all_chats.index(ss.current_chat)
        if index_to_delete > 0:
            prev_key = all_chats[index_to_delete - 1]
        else:
            prev_key = all_chats[1]
        del ss.chats[ss.current_chat]
        ss.current_chat = prev_key
        st.rerun()

for message in ss.chats[ss.current_chat]['messages']:
    with st.chat_message(message["role"], avatar=ss.avatar if message["role"] == "user" else ss.support_avatar):
        st.markdown(message["content"])

if not ss.chats[ss.current_chat]['rated']:
    if prompt := st.chat_input("Ваше сообщение", disabled=ss.chat_disabled) or ss.chat_disabled:
        if not ss.chat_disabled:
            ss.chats[ss.current_chat]['messages'].append(
                {"role": "user", "content": prompt})
            with st.chat_message("user", avatar=ss.avatar):
                ss.chat_disabled = True
                st.markdown(prompt)
                st.rerun()

        with st.chat_message(name="support", avatar=ss.support_avatar):
            with st.spinner("Печатает..."):
                time.sleep(2)
            a = random.random()
            if a > 0.5:
                st.empty()
                st.write("Проблемы с соединением. Вы можете попробовать еще раз, нажав на кнопку.")
                if st.button("Попробовать еще раз"):
                    st.rerun()
            else:
                response_container = st.empty()
                response = ""
                for chunk in response_generator():
                    response_container.markdown(response + chunk)
                    response += chunk
                ss.chat_disabled = False
                ss.chats[ss.current_chat]['messages'].append(
                    {"role": "support", "content": response})
                st.rerun()


else:
    st.chat_input("Ваше сообщение", disabled=True)
    st.info("Вы уже оценили этот чат, поэтому больше не можете отправлять сообщения.")

if not ss.chats[ss.current_chat]['rated'] and not ss.chat_disabled:
    assistant_responses = [msg for msg in ss.chats[ss.current_chat]['messages'] if
                           msg["role"] == "support"]
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
