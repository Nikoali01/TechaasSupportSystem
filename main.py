import streamlit as st
import random
import uuid
import time


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
if "chats" not in st.session_state:
    st.session_state.chats = {first_chat: {'rated': False, 'messages': []}}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = first_chat
if "rated" not in st.session_state:
    st.session_state.rated = False

with st.sidebar:
    st.header("Ваши чаты")
    chat_names = list(st.session_state.chats.keys())

    for chat_name in chat_names:
        cols = st.columns([4, 1])
        if cols[0].button(chat_name):
            st.session_state.current_chat = chat_name
            st.rerun()

        if cols[1].button("❌", key=f"del_{chat_name}"):
            if len(st.session_state.chats) > 1:
                del st.session_state.chats[chat_name]
                if st.session_state.current_chat == chat_name:
                    if chat_names:
                        st.session_state.current_chat = chat_names[0] if chat_names[0] != chat_name else first_chat
                    else:
                        st.session_state.current_chat = first_chat
                st.rerun()

    if st.button("Создать новый чат"):
        new_chat_name = f"{uuid.uuid4()}"
        st.session_state.chats[new_chat_name] = {'rated': False, 'messages': []}
        st.session_state.current_chat = new_chat_name
        st.rerun()

st.subheader(f"Текущий чат: {st.session_state.current_chat}")

for message in st.session_state.chats[st.session_state.current_chat]['messages']:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if not st.session_state.chats[st.session_state.current_chat]['rated']:
    prompt = st.chat_input("Ваше сообщение")
    if prompt:
        print(prompt)
        st.session_state.chats[st.session_state.current_chat]['messages'].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_container = st.empty()
            response = ""
            for chunk in response_generator():
                response_container.markdown(response + chunk)
                response += chunk
            st.session_state.chats[st.session_state.current_chat]['messages'].append(
                {"role": "assistant", "content": response})

    assistant_responses = [msg for msg in st.session_state.chats[st.session_state.current_chat]['messages'] if
                           msg["role"] == "assistant"]

    if assistant_responses:
        st.markdown("### Оцените наш сервис:")

        rating_options = {}
        for i in range(1, 6):
            rating_options[i] = st.checkbox(f"{i}", key=f"rating_{i}")

        for rating, selected in rating_options.items():
            if selected:
                st.session_state.chats[st.session_state.current_chat]['messages'].append(
                    {"role": "user", "content": f"Ваша оценка диалогу: {rating}"}
                )
                st.session_state.chats[st.session_state.current_chat]['rated'] = True
                st.rerun()
else:
    st.info("Вы уже оценили этот чат, поэтому больше не можете отправлять сообщения.")
