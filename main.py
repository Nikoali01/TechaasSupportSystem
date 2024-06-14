import streamlit as st
from datetime import datetime

# Инициализация списка сообщений
if 'messages' not in st.session_state:
    st.session_state['messages'] = []


# Функция для добавления сообщения
def add_message(sender, text):
    st.session_state['messages'].append({
        'sender': sender,
        'text': text,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })


# Интерфейс приложения
st.title("Чат с Поддержкой")

# Поле для ввода сообщения и кнопка отправки
with st.form(key='chat_form', clear_on_submit=True):
    user_input = st.text_input("Ваш вопрос:", "")
    submit_button = st.form_submit_button(label="Отправить")

    if submit_button and user_input:
        add_message("Вы", user_input)
        # Здесь можно добавить логику ответа поддержки
        support_reply = "Спасибо за ваш вопрос! Мы ответим вам в ближайшее время."
        add_message("Поддержка", support_reply)

# CSS для настройки высоты контейнера и включения прокрутки
st.markdown(
    """
    <style>
    .chat-container {
        height: 400px;
        overflow-y: auto;
        border: 1px solid #ddd;
        padding: 10px;
    }
    .chat-message {
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Контейнер для отображения сообщений
st.subheader("История сообщений")
with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    for msg in st.session_state['messages']:
        st.markdown(
            f'<div class="chat-message"><strong>{msg["sender"]}:</strong> {msg["text"]} <span style="float:right;">[{msg["timestamp"]}]</span></div>',
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)
