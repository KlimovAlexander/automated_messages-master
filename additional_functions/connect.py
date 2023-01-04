import time
import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from additional_functions.config import sheet_id, start_index


api_json = {
  "type": "service_account",
  "project_id": "automated-messages-alexander",
  "private_key_id": "56b301ce81d9917a1b98771fafdbf32d97664a6c",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCieZpuWnJfEfJ6\nvKh2d1whTQSsPthvW8D2Jz6QCXHuGvfzCMYpkSdMMrGHx3IYwrUG1EQhGXu2h8Og\nS/MIk11+TevvKpMQdqXrWSvz0ZaUsW67/WwYr4Tu5YVR5bhWT6DmnB3FESFBu97o\nWsTV+gri5gc+Jc0BssvoVGTnXzqN68DFuc5MS2zZBohGoDNQfi/fHzvSX9zjw0HD\n/i4WNdCCInnFGAcnCwMJ+J9Lo5fhm+f9Q1ed9dtAz8n1rDirjHeHYNPGyc7R+JtY\ndpjYMDG44CZpob6vBPVSqiax57MBQqx4+XqGWWUT2ydKgW0rEfGjPFIL9859M2ji\n1ZY/BKpFAgMBAAECggEAHZ7l1LCQoVx4RIAYhmCEX13XOD/M3aBwsW++LCxMpQgt\npBU5a2KXM4EadJKb7n+w2SnhsdcfgsuFkrfF+w5CwUAbf2LXpOy8mweKx8yyEzG1\n6nftOSLmrVcS0zd6P+IMh352vvK8iWti3CGQOSJ40Zz2PRJPKbwbCKQ6MSRfXHgQ\nDQKzns2cj6eV3ir4aSolOfu2+iPXGu1awlBWBQ9OQsn/SO1yDPzJl3/iBTkQO9Zt\nVLcaN3FsFS5nrE8a/EfkAgy06+6KlQbwT31+mTcOw6bQGY4xYYQN9/stsTaNB3kL\nwPF+w8enwROpE+zCOyEcLpzitXDQs79dtIk+QJPQEQKBgQDZa2Zf8fBL5/dUaDgY\nXh81p8E/cB9o4/a+mfuNPNwviR9+udtV6SuLgp810HGSrvXLqW6yW6bofjF9Xpig\ngDvYI1tjVKeNqPQt0g/clhsg+pZIvpwxs1FJb3iZjB4eyDcTp4+EWzAEQbxT+sqO\nTZR/FIPCn0+Ec+wWI6HiEkFcWwKBgQC/TkStJGvaztws+Y6d/IPdaq8grs+5iDse\n+33zRF3tuCCs/WxHxdNTyJ/qGa7cYhKAiN9hq03uE45W/Ot/7YvAsDKKvlY5Mu0s\nVl40s28kOddItJJM99B6sTQAPZutziCGhTIWn5UeeDqML3M0Dt68srGs8VanA4jx\nIZ0PlTFV3wKBgEQ3yZhjHiWC8/yc8rTam2pHZ4ATGxfbJylowR/wr5mOqb4mbKaJ\nEaulYXUOIQSINwEe+WenEDi0l6yhiLwbYCuR9HO3NRdiorLZzTZGNt7jIVJT1EhX\n3jJvcmSjLTQ1V+qn0YUS438CbSfgcbuypdw1wJ3JRLbndHUB2yJG3hEvAoGAD1bw\nTM3Z1B64KucL14Ey9aMjTcSWpXLWAsL5s3Ls8S3NePGNKCglrNcuc3ABxGwcva+7\n8bHxusBYroLzQzvB8/5s3xEqCsYZnG+EeEdXBxmYOJ06Ce/pCJ2C5O4LuKEJnJ+7\nh3LeWyYa07jOTQNQOuM9OffUEepHpcYjOOemoBMCgYEAtZd9tLn06K+IBI4emVpr\niNJiFIg4pgWBbzDViodO9IodmF5gqHb4AD0V465V27PrWsDZYsvsGxmN3xTek0jn\n6NH99Mqz0/oFM3D2HJjCf5+CzfKOsPZi7MS+nLsaaMULfuhVNxo97nQdI+ubOlp+\nkXZ244279yJUO2dWJOWEODQ=\n-----END PRIVATE KEY-----\n",
  "client_email": "automated-messages-for-alexand@automated-messages-alexander.iam.gserviceaccount.com",
  "client_id": "110056773054897173680",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/automated-messages-for-alexand%40automated-messages-alexander.iam.gserviceaccount.com"
}


def get_service_sacc():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds_service = ServiceAccountCredentials.from_json_keyfile_dict(api_json, scopes=scopes).authorize(httplib2.Http())
    return build(serviceName="sheets", version="v4", http=creds_service)


def get_email_data():
    service = get_service_sacc()
    sheet = service.spreadsheets()
    response = sheet.values().get(spreadsheetId=sheet_id, range=f"Рабочая таблица по лидам!A{start_index}:I100000").execute()

    result = list()
    for element in response["values"]:
        sub_result = dict()
        sub_result["project_name"] = element[3]
        if len(element) > 6:
            sub_result["email"] = element[6]
        else:
            sub_result["email"] = ""
        if len(element) > 7:
            sub_result["date"] = element[7]
        else:
            sub_result["date"] = ""
        if len(element) > 8:
            sub_result["sent"] = element[8].lower()
        else:
            sub_result["sent"] = ""
        result.append(sub_result)
    return result


def set_email_data(index, client):
    service = get_service_sacc()
    sheet = service.spreadsheets()
    values = [[client["date"], client["sent"]]]
    body = {"values": values}
    sheet.values().update(spreadsheetId=sheet_id, range=f"Рабочая таблица по лидам!H{index}:I{index}",
                          valueInputOption="RAW", body=body).execute()


def record_email_result(result):
    print("[INFO] Идет запись результатов в Google Таблицу")
    index = start_index - 1
    for element in result:
        index += 1
        if element["sent"] == "Да":
            set_email_data(index=index, client=element)
            time.sleep(1)
    print("[INFO] Результаты записаны в Google Таблицу")


def get_linkedin_data():
    service = get_service_sacc()
    sheet = service.spreadsheets()
    response = sheet.values().get(spreadsheetId=sheet_id, range=f"Рабочая таблица по лидам!Q{start_index}:S100000").execute()

    result = list()
    for element in response["values"]:
        sub_result = dict()
        if len(element) > 0:
            sub_result["linked_urls"] = element[0]
        else:
            sub_result["linked_urls"] = ""
        if len(element) > 1:
            sub_result["date"] = element[1]
        else:
            sub_result["date"] = ""
        if len(element) > 2:
            sub_result["sent"] = element[2].lower()
        else:
            sub_result["sent"] = ""
        result.append(sub_result)
    return result


def set_linkedin_data(index, client):
    service = get_service_sacc()
    sheet = service.spreadsheets()
    values = [[client["date"], client["sent"]]]
    body = {"values": values}
    sheet.values().update(spreadsheetId=sheet_id, range=f"Рабочая таблица по лидам!R{index}:S{index}",
                          valueInputOption="RAW", body=body).execute()


def record_linkedin_result(result):
    print("[INFO] Идет запись результатов в Google Таблицу")
    index = start_index - 1
    for element in result:
        index += 1
        if element["sent"] == "Да":
            set_linkedin_data(index=index, client=element)
            time.sleep(1)
    print("[INFO] Результаты записаны в Google Таблицу")


def get_telegram_data():
    service = get_service_sacc()
    sheet = service.spreadsheets()
    response = sheet.values().get(spreadsheetId=sheet_id, range=f"Рабочая таблица по лидам!Z{start_index}:AB100000").execute()

    result = list()
    for element in response["values"]:
        sub_result = dict()
        sub_result["telegram_links"] = element[0]
        sub_result["date"] = element[1]
        sub_result["sent"] = element[2].lower()
        result.append(sub_result)
    return result


def set_telegram_data(index, client):
    service = get_service_sacc()
    sheet = service.spreadsheets()
    values = [[client["date"], client["sent"]]]
    body = {"values": values}
    sheet.values().update(spreadsheetId=sheet_id, range=f"Рабочая таблица по лидам!AA{index}:AB{index}",
                          valueInputOption="RAW", body=body).execute()


def record_telegram_data(result):
    print("[INFO] Идет запись результатов в Google Таблицу")
    index = start_index - 1
    for element in result:
        index += 1
        if element["sent"] == "Да":
            set_telegram_data(index=index, client=element)
            time.sleep(1)
    print("[INFO] Результаты записаны в Google Таблицу")


if __name__ == "__main__":
    get_telegram_data()
