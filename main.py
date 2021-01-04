import os
import time
import requests
from dotenv import load_dotenv
from telegram import Bot


def main():
    load_dotenv()
    api_url = 'https://dvmn.org/api/long_polling/'
    dvmn_url = 'https://dvmn.org'
    dvmn_api_token = os.getenv("DVMN_API_TOKEN")
    bot_token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    bot = Bot(token=bot_token)
    timestamp = time.time()
    headers = {
        'Authorization': f'Token {dvmn_api_token}'
    }
    params = {
        'timestamp': timestamp
    }
    while True:
        try:
            response = requests.get(api_url, headers=headers, params=params, timeout=190)
            response.raise_for_status()
            response_json = response.json()
            if response_json['status'] == 'found':
                params['timestamp'] = response_json['last_attempt_timestamp']
                for attempt in response_json['new_attempts']:
                    attempt_result = attempt['is_negative']
                    lesson_title = attempt['lesson_title']
                    lesson_url = dvmn_url + attempt['lesson_url']
                    message_header = f'У вас проверили работу ["{lesson_title}"]({lesson_url})'
                    if attempt_result:
                        message = message_header + '\n\nК сожалению, в работе нашлись ошибки.'
                    else:
                        message = message_header + '\n\nПреподавателю всё понравилось, \
                        можно приступать к следующему уроку!'
                    bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
            else:
                params['timestamp'] = response_json['timestamp_to_request']
        except requests.exceptions.ReadTimeout as error:
            print('Истёк таймаут: ')
            print(error)
        except requests.exceptions.ConnectionError as error:
            print('Ошибка соединения:')
            print(error)
            time.sleep(30)
        except requests.exceptions.HTTPError as error:
            print(error)
            break


if __name__ == '__main__':
    main()
