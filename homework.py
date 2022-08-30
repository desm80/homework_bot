import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Отправленно сообщение: {message}')
    except Exception as error:
        logger.error(f'При отправке сообщения в чат возникла ошибка: {error}',
                     exc_info=True)


def get_api_answer(current_timestamp):
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT, headers=HEADERS, params=params
        )
    except Exception as error:
        logger.error(f'Недоступен эндпоинт. Ошибка: {error}')
        raise Exception(f'Недоступен эндпоинт. Ошибка: {error}')
    if homework_statuses.status_code != 200:
        logger.error(f'Ошибка доступа к API {homework_statuses.status_code}')
        raise requests.ConnectionError(homework_statuses.status_code)
    return homework_statuses.json()


def check_response(response):
    # homework = response.get('homeworks')[0]
    # return homework
    if type(response) is not dict:
        raise TypeError('Ответ API отличен от словаря')
    try:
        homeworks = response.get('homeworks')
    except KeyError:
        logger.error('Ошибка словаря по ключу homeworks')
        raise KeyError('Ошибка словаря по ключу homeworks')
    try:
        homework = homeworks[0]
    except IndexError:
        logger.error('Список домашних работ пуст')
        raise IndexError('Список домашних работ пуст')
    return homework


def parse_status(homework):
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_STATUSES:
        raise Exception('Некорректный статус домашней работы')

    verdict = HOMEWORK_STATUSES[homework_status]


    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка наличия обязательных переменных окружения"""
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return True


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical(
            'Работа программы принудительно остановлена, отсутствуют '
            'обязательные переменные окружения')
        exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    ...

    while True:
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response.get('current_date')
            homework = check_response(response)
            message = parse_status(homework)
        except requests.ConnectionError as error:
            message = f'Не удалось соединиться с эндпоинтом. Ошибка: {error}'
            logger.error(message, exc_info=True)
            time.sleep(RETRY_TIME)
        try:

            send_message(bot, message)
            time.sleep(RETRY_TIME)
        except:
            ...

        else:
            ...


if __name__ == '__main__':
    main()
