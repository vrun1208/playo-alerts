import json
import os

USERS_FILE = "data/users.json"
MESSAGES_FILE = "data/messages.json"


def ensure_data_files():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({"users": []}, f)

    if not os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, "w") as f:
            json.dump({}, f)


# --------------------------------------------------
# Users
# --------------------------------------------------

def load_users():
    ensure_data_files()

    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_user(chat_id, username=None):
    data = load_users()

    exists = any(
        u["chat_id"] == chat_id
        for u in data["users"]
    )

    if exists:
        return False

    data["users"].append({
        "chat_id": chat_id,
        "username": username,
    })

    save_users(data)

    return True


def remove_user(chat_id):
    data = load_users()

    before = len(data["users"])

    data["users"] = [
        u for u in data["users"]
        if u["chat_id"] != chat_id
    ]

    save_users(data)

    return before != len(data["users"])


# --------------------------------------------------
# Messages
# --------------------------------------------------

def load_messages():
    ensure_data_files()

    with open(MESSAGES_FILE, "r") as f:
        return json.load(f)


def save_messages(data):
    with open(MESSAGES_FILE, "w") as f:
        json.dump(data, f, indent=2)