import datetime
from telethon.sync import TelegramClient
from additional_functions.config import api_id, api_hash, oclock
from telegram.settings import get_statistic, update_amount_profiles, hard_reboot_statistic
import os
import time
import schedule


def get_report():
    amount_profiles = len(os.listdir(path="../sessions"))
    update_amount_profiles(amount_profiles=amount_profiles)
    today = get_statistic(period="день")
    email_messages = today["email_messages"] - today["email_sent"]
    email_sent = today["email_sent"]
    linkedin_messages = today["linkedin_messages"] - today["linkedin_sent"]
    linkedin_sent = today["linkedin_sent"]
    telegram_chats = today["telegram_chats"]
    telegram_admins = today["telegram_admins"] - today["telegram_messages"]
    telegram_messages = today["telegram_messages"]
    telegram_answers = today["telegram_answers"]
    telegram_profiles = today["telegram_profiles"]
    date = str(datetime.date.today())
    text = "\n".join([
        f"ОТЧЕТ ЗА ДЕНЬ\n",
        f"Дата: {date}\n",
        f"email",
        f"-Не отправлено имейлов: {email_messages}",
        f"-Отправлено писем: {email_sent}\n",
        f"linkedin",
        f"-Не отправлено линкединов: {linkedin_messages}",
        f"-Отправлено линкединов: {linkedin_sent}\n",
        f"telegram",
        f"-Найдено телеграм чатов и каналов: {telegram_chats}",
        f"-Не отправлено сообщений: {telegram_admins}",
        f"-Отправлено сообщений: {telegram_messages}",
        f"-Получено ответов: {telegram_answers}",
        f"-Аккаунтов в работе: {telegram_profiles}"
    ])
    with TelegramClient(f"statistic", api_id=api_id, api_hash=api_hash) as telegram_client:
        telegram_client.send_message(entity="@automated_messages_buldog_bot", message=text)
    hard_reboot_statistic(period="день")


def main():
    print("[INFO] Включено оповещение об отчетах")
    schedule.every().days.at(oclock).do(get_report)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
