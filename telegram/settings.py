import pymysql
from pymysql import cursors
from additional_functions.config import port, host, db_username, password, db_name, api_id, api_hash
from telethon.sync import TelegramClient
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.functions import account


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


def create_table_users():
    query = "CREATE TABLE users (user VARCHAR(50) UNIQUE, profile VARCHAR(50), last_message VARCHAR(50));"
    result = database(query=query)
    if result != "Error":
        print("[INFO] Таблица users успешно создана в базе данных")


def create_table_workers():
    query = "CREATE TABLE workers (worker_id VARCHAR(50) UNIQUE, status VARCHAR(50), active INT);"
    result = database(query=query)
    if result != "Error":
        print("[INFO] Таблица workers успешно создана в базе данных")


def create_table_statistic():
    query = """CREATE TABLE statistic 
               (`period` VARCHAR(30), 
                `email_messages` INT, `email_sent` INT, 
                `linkedin_messages` INT, `linkedin_sent` INT, 
                `telegram_chats` INT, `telegram_admins` INT, `telegram_messages` INT, `telegram_answers` INT, 
                `telegram_profiles` INT);"""
    database(query=query)
    query = """INSERT INTO statistic VALUES 
               ('день', 0, 0, 0, 0, 0, 0, 0, 0, 0), 
               ('неделя', 0, 0, 0, 0, 0, 0, 0, 0, 0),
               ('месяца', 0, 0, 0, 0, 0, 0, 0, 0, 0);"""
    database(query=query)
    print("[INFO] Таблица statistic создана в базе данных")


def hard_reboot_statistic(period):
    query = f"DElETE FROM statistic WHERE `period` = '{period}';"
    database(query=query)
    query = f"INSERT INTO statistic VALUES ('{period}', 0, 0, 0, 0, 0, 0, 0, 0, 0);"
    database(query=query)


def add_value(field):
    query = f"""UPDATE statistic SET `{field}` = `{field}` + 1;"""
    database(query=query)


def get_statistic(period):
    query = f"""SELECT * FROM statistic WHERE `period` = '{period}';"""
    result = database(query=query)
    return result


def update_amount_profiles(amount_profiles):
    query = f"UPDATE statistic SET `telegram_profiles` = {amount_profiles};"
    database(query=query)


def user_registration():
    sender = input("[INPUT] Введите номер телефона профиля, который регистрируете: >>> ")
    if sender != "exit":
        with TelegramClient(sender, api_id=api_id, api_hash=api_hash) as client:
            photos = client.get_profile_photos("me")
            client(DeletePhotosRequest(photos))
            client(UploadProfilePhotoRequest(client.upload_file("logo.jpg")))
            client(account.UpdateProfileRequest(first_name="Flexe.io", last_name=" ", about=" "))
            client.send_message("@automated_messages_buldog_bot", "/profile")
        print("[INFO] Регистрация профиля в автоматической рассылке прошла успешно!")
    else:
        return True


def main():
    mode = input("[INPUT] Выберите режим работы (1 - создать таблицы базы данных, 2 - регистрация новой сессии): >>> ")
    if mode == "1":
        create_table_workers()
        create_table_users()
        create_table_statistic()
    else:
        print("[INFO] Чтобы выйти из режима регистрации сессий, введите exit")
        while True:
            result = user_registration()
            if result:
                break


if __name__ == "__main__":
    main()
