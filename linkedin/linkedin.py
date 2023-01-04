import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from additional_functions.config import linkedin_login, linkedin_password, linkedin_max_messages_count
import time
from bs4 import BeautifulSoup
from additional_functions.connect import get_linkedin_data, record_linkedin_result
from telegram.settings import add_value


ua_chrome = " ".join(["Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                      "AppleWebKit/537.36 (KHTML, like Gecko)",
                      "Chrome/108.0.0.0 Safari/537.36"])
options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={ua_chrome}")
options.add_argument("--headless")
options.add_argument("--no-sandbox")
timeout = 30


def get_message():
    with open("Сообщение.txt", "r", encoding="utf-8") as file:
        text = file.read()
    return text


def authorization(login, password):
    print("[INFO] Авторизуемся в профиле LinkedIn")
    browser = webdriver.Chrome(options=options)
    browser.set_window_size(width=1920, height=1080)
    try:
        browser.get(url="https://www.linkedin.com/home")
        login_input = browser.find_element(By.ID, "session_key")
        login_input.send_keys(login)
        password_user = browser.find_element(By.ID, "session_password")
        password_user.send_keys(password)
        login_button = browser.find_element(By.CLASS_NAME, "sign-in-form__submit-button")
        login_button.click()
        time.sleep(1)
        response = browser.page_source
        bs_object = BeautifulSoup(response, "lxml")
        main_element = bs_object.find(name="main", id="main")
        if main_element is None:
            return authorization(login, password)
        print("[INFO] Авторизация в профиле LinkedIn прошла успешно")
        return browser
    except Exception as ex:
        print("[ERROR] Ошибка при попытке авторизоваться. Пробуем еще раз")
        print(f"[ERROR] {ex}")
        authorization(login, password)


def send_message(browser, user_link, message):
    try:
        browser.get(user_link)
        response = browser.page_source
        bs_object = BeautifulSoup(response, "lxml")
        name = bs_object.h1.text.strip().split(" ")[0]
        message = message.replace("NAME", name)
        time.sleep(2)
        invite_xpath = "/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[3]/div/div[1]/button"
        invite_button = browser.find_element(By.XPATH, invite_xpath)
        invite_button.click()
        send_message_xpath = "/html/body/div[3]/div/div/div[3]/button[1]"
        send_message_button = browser.find_element(By.XPATH, send_message_xpath)
        send_message_button.click()
        message_input_xpath = "/html/body/div[3]/div/div/div[2]/div/textarea"
        message_input_section = browser.find_element(By.XPATH, message_input_xpath)
        message_input_section.send_keys(message)
        send_xpath = "/html/body/div[3]/div/div/div[3]/button[2]"
        send_button = browser.find_element(By.XPATH, send_xpath)
        send_button.click()
        print(f"[INFO] Приглашение с сообщением отправлено пользователю {user_link}")
        add_value(field="linkedin_sent")
    except NoSuchElementException:
        send_message(browser, user_link, message)


def main():
    print("=" * 100)
    print("[INFO] linkedin рассылка запущена")
    print("=" * 100)
    browser = authorization(login=linkedin_login, password=linkedin_password)
    clients = get_linkedin_data()
    message = get_message()
    try:
        for client in clients:
            try:
                if client["linked_urls"] != "" and (client["sent"] == "нет" or client["sent"] == ""):
                    if len(client["linked_urls"].split(",")) <= linkedin_max_messages_count:
                        linkedin_urls = client["linked_urls"]
                        linkedin_urls = linkedin_urls.split(",")
                        for linkedin_url in linkedin_urls:
                            add_value(field="linkedin_messages")
                            linkedin_url = linkedin_url.strip()
                            send_message(browser=browser, user_link=linkedin_url, message=message)
                        client["date"] = str(datetime.date.today())
                        client["sent"] = "Да"
                    else:
                        linkedin_urls = client["linked_urls"]
                        linkedin_urls = linkedin_urls.split(",")
                        for index in range(len(linkedin_urls)):
                            add_value(field="linkedin_messages")
            except Exception as ex:
                print(f"[ERROR] {ex}")
                continue
        record_linkedin_result(result=clients)
        print("=" * 100)
        print("[INFO] linkedin рассылка завершена")
        print("=" * 100)
    finally:
        browser.close()
        browser.quit()


if __name__ == "__main__":
    main()
