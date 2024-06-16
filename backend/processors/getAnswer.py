import os
import threading
import time
import requests


def send_question(messages):
    base_url = os.getenv("API_URL_ML", default="http://127.0.0.1:7000")
    url = base_url + "/ticket/answer"
    payload = {
        "messages": messages
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


def work(messages):
    result = send_question(messages)
    if result:
        return result
    else:
        print("Failed to get the answer.")
