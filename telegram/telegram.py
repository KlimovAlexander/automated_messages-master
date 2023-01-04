import os
from telethon.sync import TelegramClient
import pymysql
from pymysql import cursors
from additional_functions.config import port, host, db_username, password, db_name, api_id, api_hash
from settings import add_value


def database(query):
    try:
        connection = pymysql.connect(port=port, host=host, user=db_username, password=password,
                                     database=db_name, cursorclass=cursors.DictCursor)
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            connection.commit()
            return result
        except Exception as ex:
            print(f"Something Wrong: {ex}")
            return "Error"
        finally:
            connection.close()
    except Exception as ex:
        print(f"Connection was not completed because {ex}")
        return "Error"


def send_file(sender, recipients, file, caption):
    with TelegramClient(f"sessions/{sender}", api_id=api_id, api_hash=api_hash) as client:
        for recipient in recipients:
            client.send_file(entity=recipient, file=file, caption=caption)


def send_message(sender, recipients, message):
    with TelegramClient(f"sessions/{sender}", api_id=api_id, api_hash=api_hash) as client:
        for recipient in recipients:
            client.send_message(entity=recipient, message=message)


def get_last_message(user_username):
    query = f"SELECT last_message FROM users WHERE user = '{user_username}';"
    result = database(query=query)
    if result == "Error" or result is None or result["last_message"] is None:
        return 0
    return result["last_message"]


def add_message(message_id, user_username, profile):
    query = f"SELECT last_message FROM users WHERE user = '{user_username}';"
    check = database(query=query) is None
    if check:
        query = f"""INSERT INTO users (user, profile, last_message) 
                    VALUES ('{user_username}', '{profile}', '{message_id}');"""
        text = f"[INFO] Пользователь {user_username} добавлен в базу данных"
    else:
        query = f"UPDATE users SET last_message = '{message_id}' WHERE user = '{user_username}';"
        text = f"[INFO] Последнее сообщение пользователя {user_username} было обновлено"
    result = database(query=query)
    if result != "Error":
        print(text)


def get_all_profiles():
    result = list()
    users = os.listdir("sessions")
    for user in users:
        result.append(user.replace(".session", ""))
    return result


def check_message(profile):
    with TelegramClient(f"sessions/{profile}", api_id=api_id, api_hash=api_hash) as client:
        chats = client.get_dialogs()
        for chat in chats:
            if (chat.is_user and not chat.is_channel and not chat.is_group and
               chat.entity.id != 777000 and chat.entity.id != 5826160626):
                user_username = f"@{chat.entity.username}"
                user_id = chat.entity.id
                message_objects = list(client.iter_messages(chat, from_user=user_id, limit=20))
                message_objects.reverse()
                last_message = get_last_message(user_username=user_username)
                for message_object in message_objects:
                    message_id = int(message_object.id)
                    if message_id > int(last_message):
                        add_message(message_id=message_id, user_username=user_username, profile=profile)
                        add_value(field="telegram_answers")
                        message_object.forward_to(entity="@automated_messages_buldog_bot")


def main():
    while True:
        profiles = get_all_profiles()
        for profile in profiles:
            check_message(profile=profile)


if __name__ == "__main__":
    main()
