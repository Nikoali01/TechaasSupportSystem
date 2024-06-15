import requests


def send_question(message_id, ticket_id, message):
    url = "http://0.0.0.0:7000/get_question"
    payload = {
        "message_id": message_id,
        "ticket_id": ticket_id,
        "message": message
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
