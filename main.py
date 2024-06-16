import streamlit as st
import random
import uuid
import httpx
import time
from streamlit_star_rating import st_star_rating
from streamlit_cookies_manager import EncryptedCookieManager
from streamlit import session_state as ss


class API:
    def __init__(self, url):
        self.base_url = url
        self.client = httpx.Client(base_url=url)

    def close(self):
        self.client.close()

    def _request(self, method, endpoint, **kwargs):
        url = self.base_url + endpoint
        resp = self.client.request(method, url, **kwargs)
        resp.raise_for_status()
        return resp

    def get_tickets(self, user_id):
        endpoint = f"/{user_id}/tickets"
        return self._request("GET", endpoint)

    def start_ticket(self, user_id, access_token):
        endpoint = f"/start_ticket"
        return self._request("POST", endpoint, json={"user_id": user_id, "access_token": access_token})

    def get_ticket(self, ticket_id):
        endpoint = f"/ticket/{ticket_id}"
        return self._request("GET", endpoint, params={'ticket_id': ticket_id})

    def close_ticket(self, ticket_id, user_rating, access_token):
        endpoint = f"/ticket/close"
        return self._request("PATCH", endpoint,
                             json={"ticket_id": ticket_id, "user_rating": user_rating, "access_token": access_token})

    def add_message(self, user_id, ticket_id, message, access_token):
        endpoint = f"/ticket/add_message"
        return self._request("POST", endpoint,
                             json={"user_id": user_id, "ticket_id": ticket_id, "message": message,
                                   "access_token": access_token})

    def get_updates(self, user_id, ticket_id, access_token):
        endpoint = f"/ticket/get_updates"
        return self._request("POST", endpoint,
                             json={"user_id": user_id, "ticket_id": ticket_id, "access_token": access_token})


# api = API("http://localhost:8000")

@st.cache_data()
def get_session_id():
    return str(uuid.uuid4())


if 'session_id' not in st.session_state:
    st.session_state.session_id = get_session_id()

user_id = get_session_id()
access_token = "1234"


def response_generator(response):
    response_text = ""
    for word in response.split():
        response_text += word + " "
        yield word + " "
        time.sleep(0.05)
    return response_text


def create_ticket():
    resp = api.start_ticket(user_id, access_token)
    if resp.status_code == 200:
        resp = resp.json()
        print(resp)
        print(user_id)
        ss.chats[resp['ticket_id']] = {'rated': False, 'messages': []}
        ss.current_chat = resp['ticket_id']
    else:
        print(resp.status_code)


st.title("Чат техподдержки")

if "chats" not in ss:
    ss.chats = {}
    print("I'm here!")
    all_tickets = api.get_tickets(user_id)
    if all_tickets.status_code == 200:
        for ticket_id in all_tickets.json()['tickets']:
            ticket = api.get_ticket(ticket_id)
            if ticket.status_code == 200:
                ticket = ticket.json()
                print(ticket)
                pre_messages = ticket['messages']
                messages = []
                for i in pre_messages:
                    messages.append({"role": "user" if i['from_'] == "user" else "support", "content": i['content']})
                ss.chats[ticket_id] = {'rated': True if ticket['status'].lower() == "closed" else False,
                                       'messages': messages}
if "current_chat" not in ss:
    if ss.chats:
        print(ss.chats)
        ss.current_chat = list(ss.chats.keys())[0]
    else:
        create_ticket()
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
        create_ticket()
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
            print(prompt, user_id, ss.current_chat)
            resp = api.add_message(user_id, ss.current_chat, prompt, access_token)
            if resp.status_code == 200:
                ss.chats[ss.current_chat]['messages'].append(
                    {"role": "user", "content": prompt})
                with st.chat_message("user", avatar=ss.avatar):
                    ss.chat_disabled = True
                    st.markdown(prompt)
                    st.rerun()

        with st.chat_message(name="support", avatar=ss.support_avatar):
            with st.spinner("Печатает..."):
                count = 0
                resp = api.get_updates(user_id, ss.current_chat, access_token)
                while resp.status_code != 200:
                    count += 1
                    time.sleep(1)
                    resp = api.get_updates(user_id, ss.current_chat, access_token)
                    if count == 30:
                        st.empty()
                        st.write("Проблемы с соединением. Вы можете попробовать еще раз, нажав на кнопку.")
                        if st.button("Попробовать еще раз"):
                            st.rerun()
            response_container = st.empty()
            response = ""
            for chunk in response_generator(resp.json()['answer']):
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
                prompt = f"Ваша оценка диалогу: {stars}"
                resp = api.add_message(user_id, ss.current_chat, prompt, access_token)
                if resp.status_code == 200:
                    resp = api.close_ticket(ss.current_chat, stars, access_token)
                    if resp.status_code == 200:
                        ss.chats[ss.current_chat]['messages'].append(
                            {"role": "user", "content": prompt}
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
