from telebot import TeleBot
import time
import pymysql
from pymysql import cursors
from additional_functions.config import port, host, db_username, password, db_name
import asyncio
from telegram import send_message as profile_send_message
from telegram import send_file as profile_send_file


def database(query):
    try:
        connection = pymysql.connect(port=port, host=host, user=db_username, password=password,
                                     database=db_name, cursorclass=cursors.DictCursor)
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
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


def add_profile(profile_id):
    query = f"INSERT INTO workers (worker_id, status, active) VALUES ('{profile_id}', 'profile', 1);"
    result = database(query=query)
    if result != "Error":
        return "Successful"
    else:
        return "Error"


def add_manager(manager_id):
    query = f"INSERT INTO workers (worker_id, status, active) VALUES ('{manager_id}', 'manager', 1);"
    result = database(query=query)
    if result != "Error":
        return "Successful"
    else:
        return "Error"


def is_profile(sender_id):
    result = database(query="SELECT worker_id from workers WHERE active = 1 AND status = 'profile';")
    for element in result:
        if sender_id == int(element["worker_id"]):
            return True
    return False


def get_manager_ids():
    result_query = database(query="SELECT worker_id FROM workers WHERE active = 1 AND status = 'manager';")
    result = list()
    for element in result_query:
        result.append(element["worker_id"])
    return result


def get_profile_via_user_username(user_username):
    query = f"SELECT profile FROM users WHERE user = '{user_username}';"
    result_query = database(query=query)
    result = result_query[0]["profile"]
    return result


def run_bot():
    token = "5826160626:AAGFMAaPMBizBn61yK7K4Uba8sl26DfYcos"
    bot = TeleBot(token=token)

    @bot.message_handler(commands=["start"])
    def start(message):
        bot.send_message(chat_id=message.chat.id, text="Введите команду /registration для регистрации в системе")

    @bot.message_handler(commands=["profile"])
    def profile(message):
        result = add_profile(profile_id=message.from_user.id)
        if result == "Successful":
            bot.send_message(chat_id=message.chat.id, text="Вы зарегистрированы как профиль")
        else:
            bot.send_message(chat_id=message.chat.id, text="Извините, возникла какая-то ошибка. Попробуйте позже")

    @bot.message_handler(commands=["registration"])
    def manager(message):
        manager_id = message.chat.id
        result = add_manager(manager_id=manager_id)
        if result == "Successful":
            text = "Поздравляю, вы зарегистрированы в системе автоматической рассылки"
            bot.send_message(chat_id=message.chat.id, text=text)
            time.sleep(1)
            with open("Правила.txt", "r", encoding="utf-8") as file:
                text = file.read()
                bot.send_message(chat_id=message.chat.id, text=text)
        else:
            text = "Извините, произошла какая-то ошибка. Попробуйте позже"
            bot.send_message(chat_id=message.chat.id, text=text)

    @bot.message_handler(content_types=["text", "photo", "video", "document", "audio"])
    def send_message(message):
        sender_id = message.from_user.id
        if is_profile(sender_id=sender_id):
            manager_ids = get_manager_ids()
            for manager_id in manager_ids:
                bot.forward_message(chat_id=manager_id, from_chat_id=message.chat.id, message_id=message.id)
        else:
            reply_message = message.reply_to_message
            if reply_message is None:
                text = "Прости, но ты отправил некорректное сообщение. Попробуй еще раз с учетом всех правил"
                bot.send_message(chat_id=message.chat.id, text=text)
            else:
                user_username = f"@{reply_message.forward_from.username}"
                profile_name = get_profile_via_user_username(user_username=user_username)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                if message.content_type == "text":
                    profile_send_message(sender=profile_name, recipients=[user_username], message=message.text)
                elif message.content_type == "photo":
                    photo = "photo.jpg"
                    with open(photo, "wb") as save_file:
                        save_file.write(bot.download_file(bot.get_file(message.photo[-1].file_id).file_path))
                    profile_send_file(sender=profile_name, recipients=[user_username],
                                      file=photo, caption=message.caption)
                elif message.content_type == "document":
                    document = f"document.{message.document.file_name.split('.')[-1]}"
                    with open(document, "wb") as save_file:
                        save_file.write(bot.download_file(bot.get_file(message.document.file_id).file_path))
                    profile_send_file(sender=profile_name, recipients=[user_username],
                                      file=document, caption=message.caption)
                elif message.content_type == "video":
                    video = f"video.{message.video.file_name.split('.')[-1]}"
                    with open(video, "wb") as save_file:
                        save_file.write(bot.download_file(bot.get_file(message.video.file_id).file_path))
                    profile_send_file(sender=profile_name, recipients=[user_username],
                                      file=video, caption=message.caption)

    bot.infinity_polling()


if __name__ == "__main__":
    print("[INFO] Бот запущен")
    run_bot()
