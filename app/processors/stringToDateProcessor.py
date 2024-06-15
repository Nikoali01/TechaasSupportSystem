from datetime import datetime


def convert_to_datetime(ticket):
    ticket['started_at'] = datetime.fromisoformat(ticket['started_at'].replace("Z", "+00:00"))
    if ticket['closed_at']:
        ticket['closed_at'] = datetime.fromisoformat(ticket['closed_at'].replace("Z", "+00:00"))
    for message in ticket['messages']:
        message['timestamp'] = datetime.fromisoformat(message['timestamp'].replace("Z", "+00:00"))
    return ticket
