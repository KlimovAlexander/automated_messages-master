import datetime
import smtplib
from additional_functions.config import email_login, email_password
from email.mime.text import MIMEText
from additional_functions.connect import get_email_data, record_email_result
from telegram.settings import add_value


def get_message():
    message = dict()
    with open("Сообщение.html", "r", encoding="utf-8") as file:
        text = file.read()
    message["content"] = text
    with open("Тема.txt", "r", encoding="utf-8") as file:
        subject = file.read()
    message["subject"] = subject
    return message


def send_mail(message, clients):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email_login, email_password)
    index = 0
    for client in clients:
        try:
            if (client["sent"] == "нет" or client["sent"] == "") and client["email"] != "":
                name = client["project_name"]
                content = message["content"].replace("NAME", name)
                subject = message["subject"].replace("NAME", name)
                client_email = client["email"]
                client_emails = client_email.split(",")
                for client_email in client_emails:
                    client_email = client_email.strip()
                    msg = MIMEText(content, "html")
                    msg["Subject"] = subject
                    msg["To"] = client_email
                    msg["From"] = "From: Flexe.io"
                    index += 1
                    add_value(field="email_messages")
                    server.sendmail(msg=msg.as_string(), from_addr=email_login, to_addrs=client_email)
                    add_value(field="email_sent")
                    print(f"[INFO] Сообщение успешно отправлено на адрес {client_email}")
                    client["sent"] = "Да"
                    client["date"] = str(datetime.date.today())
        except Exception as ex:
            print(f"[ERROR] {ex}")
            continue
    return clients


def main():
    print("=" * 100)
    print("[INFO] email рассылка запущена")
    print("=" * 100)
    clients = get_email_data()
    message = get_message()
    result = send_mail(message=message, clients=clients)
    record_email_result(result=result)
    print("=" * 100)
    print("[INFO] email рассылка завершена")
    print("=" * 100)


if __name__ == "__main__":
    main()
