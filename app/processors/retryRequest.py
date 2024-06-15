import requests


def check_health():
    url = "http://0.0.0.0:7000/health"

    try:
        response = requests.get(url)
        if response.status_code == 204:
            return True
        else:
            print(f"Unexpected status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return False
