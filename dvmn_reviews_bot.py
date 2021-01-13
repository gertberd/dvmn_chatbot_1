import os
import time
from logging import Handler, LogRecord, getLogger

import requests
from dotenv import load_dotenv
from telegram import Bot, TelegramError


class TelegramLogHandler(Handler):
    def __init__(self, chat_id: str, token: str):
        super().__init__()
        self.chat_id = chat_id
        self.bot = Bot(token=token)

    def emit(self, record: LogRecord):
        self.bot.send_message(
            self.chat_id,
            self.format(record)
        )


def check_attempt(attempt, dvmn_url) -> str:
    lesson_title = attempt['lesson_title']
    lesson_url = f'{dvmn_url}{attempt["lesson_url"]}'
    message_header = f'У вас проверили работу ["{lesson_title}"]({lesson_url})'
    if attempt['is_negative']:
        return f'{message_header}\n\nК сожалению, в работе нашлись ошибки.'
    return f'{message_header}\n\nПреподавателю всё понравилось, можно приступать к следующему уроку!'


def main():
    load_dotenv()
    api_url = 'https://dvmn.org/api/long_polling/'
    dvmn_url = 'https://dvmn.org'
    dvmn_api_token = os.getenv('DVMN_API_TOKEN')
    bot_token = os.getenv('TG_BOT_TOKEN')
    logging_bot_token = os.getenv('TG_LOGGING_BOT_TOKEN')
    chat_id = os.getenv('TG_CHAT_ID')
    log_level = os.getenv('LOG_LEVEL')
    bot = Bot(token=bot_token)
    logger = getLogger(__name__)
    logger.addHandler(TelegramLogHandler(chat_id, logging_bot_token))
    logger.setLevel(log_level)
    logger.info("Бот запущен...")
    timestamp = time.time()
    headers = {
        'Authorization': f'Token {dvmn_api_token}'
    }
    params = {
        'timestamp': timestamp
    }
    while True:
        try:
            response = requests.get(api_url, headers=headers, params=params, timeout=90)
            response.raise_for_status()
            response_data = response.json()
            if response_data['status'] == 'found':
                params['timestamp'] = response_data['last_attempt_timestamp']
                for attempt in response_data['new_attempts']:
                    message = check_attempt(attempt, dvmn_url)
                    bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode="Markdown",
                        disable_web_page_preview=True
                    )
            else:
                params['timestamp'] = response_data['timestamp_to_request']
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            continue
        except TelegramError as error:
            logger.exception(f'Бот упал с ошибкой: ')
            logger.exception(error, exc_info=True)


if __name__ == '__main__':
    main()
