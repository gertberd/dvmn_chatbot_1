import os
import time
from logging import Handler, LogRecord, getLogger

import requests
from dotenv import load_dotenv
from telegram import Bot

logger = getLogger(__name__)


class TelegramLogsHandler(Handler):
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
    log_level = os.getenv('LOG_LEVEL', default='INFO')
    max_connection_errors = int(os.getenv("MAX_CONNECTION_ERRORS", default=5))
    connection_delay = int(os.getenv("CONNECTION_DELAY", default=300))
    bot = Bot(token=bot_token)
    logger.addHandler(TelegramLogsHandler(chat_id, logging_bot_token))
    logger.setLevel(log_level)
    logger.info("Бот запущен...")

    headers = {
        'Authorization': f'Token {dvmn_api_token}'
    }
    timestamp = time.time()
    params = {
        'timestamp': timestamp
    }

    connection_error_counter = 0

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
        except requests.exceptions.ReadTimeout as error:
            logger.debug(error)
        except requests.exceptions.ConnectionError as error:
            logger.info(error)
            connection_error_counter += 1
            if connection_error_counter >= max_connection_errors:
                connection_error_counter = 0
                time.sleep(connection_delay)


if __name__ == '__main__':
    main()
