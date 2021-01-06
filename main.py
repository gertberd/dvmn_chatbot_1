import os
import time
from logging import Handler, LogRecord, getLogger

import requests
from dotenv import load_dotenv
from telegram import Bot


class TelegramBotHandler(Handler):
    def __init__(self, chat_id: str, bot: Bot):
        super().__init__()
        self.chat_id = chat_id
        self.bot = bot

    def emit(self, record: LogRecord):
        self.bot.send_message(
            self.chat_id,
            self.format(record)
        )
        print(record.message)


def main():
    load_dotenv()
    api_url = 'https://dvmn.org/api/long_polling/'
    dvmn_url = 'https://dvmn.org'
    dvmn_api_token = os.getenv('DVMN_API_TOKEN')
    bot_token = os.getenv('TG_BOT_TOKEN')
    chat_id = os.getenv('TG_CHAT_ID')
    log_level = os.getenv('LOG_LEVEL')
    bot = Bot(token=bot_token)
    logger = getLogger(__name__)
    logger.addHandler(TelegramBotHandler(chat_id, bot))
    logger.setLevel(log_level)
    logger.info("Starting bot...")
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
                    attempt_result = attempt['is_negative']
                    lesson_title = attempt['lesson_title']
                    lesson_url = f'{dvmn_url}{attempt["lesson_url"]}'
                    message_header = f'У вас проверили работу ["{lesson_title}"]({lesson_url})'
                    if attempt_result:
                        message = f'{message_header}\n\nК сожалению, в работе нашлись ошибки.'
                    else:
                        message = f'{message_header}\n\nПреподавателю всё понравилось, ' \
                                  'можно приступать к следующему уроку!'
                    bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode="Markdown",
                        disable_web_page_preview=True
                    )
            else:
                params['timestamp'] = response_data['timestamp_to_request']
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError as error:
            logger.debug("Connection error, sleep 30 seconds...")
            time.sleep(30)
        except Exception:
            logger.critical(f'Bot failed! Sleep 30 minutes...', exc_info=True)
            time.sleep(1800)


if __name__ == '__main__':
    main()
