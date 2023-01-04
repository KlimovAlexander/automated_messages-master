import datetime
from telethon.sync import TelegramClient
import pymysql
from pymysql import cursors
from additional_functions.config import port, host, db_username, password, db_name, api_id, api_hash
import os
from additional_functions.connect import get_telegram_data, record_telegram_data
from settings import add_value
import time


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


def get_all_profiles():
    result = dict()
    sub_result = list()
    users = os.listdir("sessions")
    for user in users:
        sub_result.append(user.replace(".session", ""))
    for element in sub_result:
        result[element] = 0
    return result


def get_message():
    with open("Сообщение.txt", "r", encoding="utf-8") as file:
        text = file.read()
    return text


def add_user(user_username, profile):
    query = f"SELECT user FROM users WHERE user = '{user_username}';"
    result = database(query=query)
    if result is None:
        query = f"""INSERT INTO users (user, profile) VALUES ('{user_username}', '{profile}');"""
        result = database(query=query)
        if result != "Error":
            print(f"[INFO] Пользователь {user_username} успешно добавлен в базу данных")


def send_auto_message(sender, client, message, profiles):
    with TelegramClient(f"sessions/{sender}", api_id=api_id, api_hash=api_hash) as telegram_client:
        telegram_links = client["telegram_links"].split(",")
        for telegram_link in telegram_links:
            telegram_link = telegram_link.strip()
            user = telegram_client.get_entity(telegram_link)
            first_name = user.first_name
            last_name = user.last_name
            name = f"{first_name} {last_name}"
            name = name.replace("None", "")
            message_text = message.replace("NAME", name)
            add_value(field="telegram_admins")
            telegram_client.send_message(entity=telegram_link, message=message_text)
            add_user(user_username=telegram_link, profile=sender)
            add_value(field="telegram_messages")
            profiles[sender] += 1
            time.sleep(600)
        client["date"] = str(datetime.date.today())
        client["sent"] = "Да"


def main():
    print("=" * 100)
    print("[INFO] telegram рассылка запущена")
    print("=" * 100)
    message = get_message()
    profiles = get_all_profiles()
    clients = get_telegram_data()
    for client in clients:
        if len(client["telegram_links"]) != 0 and (client["sent"] == "нет" or client["sent"] == ""):
            for key in profiles.keys():
                if profiles[key] < 5:
                    current_profile = key
            try:
                send_auto_message(sender=current_profile, client=client, message=message, profiles=profiles)
                add_value(field="telegram_chats")
            except Exception as ex:
                print(f"[ERROR] {ex}")
                continue
    record_telegram_data(result=clients)
    print("=" * 100)
    print("[INFO] telegram рассылка завершена")
    print("=" * 100)


if __name__ == "__main__":
    main()
