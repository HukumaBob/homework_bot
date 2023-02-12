import logging
import os
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv
from requests.exceptions import RequestException

import exceptions

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
OBSERVATION_TIME = 60 * 60 * 24 * 120
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    level=logging.DEBUG,
    filename='program.log',
    filemode='w',
)

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.addHandler(handler)


def check_tokens():
    """Check for tokens existence."""
    return all([TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, PRACTICUM_TOKEN])


def send_message(bot, message):
    """Send messages via telegram bot."""
    try:
        logger.debug('Trying to send a message...')
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.TelegramError as telegram_err:
        msg = ('Error while sending message.')
        logger.error(msg)
        raise telegram_err(msg)
    else:
        logger.debug('All OK, message sent.')


def get_api_answer(timestamp):
    """Send messages via telegram bot."""
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            url=ENDPOINT, headers=HEADERS, params=params)
    except RequestException as error:
        logger.error(error)
        raise exceptions.GetApiAnswerError(error)
    if response.status_code != HTTPStatus.OK:
        error200 = response.raise_for_status()
        logger.error(error200)
        raise exceptions.GetApiAnswerError(error200)
    return response.json()


def check_response(response):
    """
    Check structure of JSON document.
    Return main part of it.
    """
    responce_dict = {'homeworks': list,
                     'current_date': int,
                     }
    homework = False
    for key, value in responce_dict.items():
        try:
            dict_value = response[key]
        except KeyError as keyerror:
            msg = f'{keyerror} is absent.'
            logger.error(msg)
            raise exceptions.CheckResponseError(msg)
        if dict_value is None:
            msg = f'"None" value in {key} dictionary'
            logger.error(msg)
            raise exceptions.ValuesMissingError(msg)
        if not dict_value:
            msg = f'{key} dictionary value/s is empty'
            logger.error(msg)
        if not isinstance(dict_value, value):
            msg = f'{key} dictionary value is not {value} type'
            logger.error(msg)
            raise TypeError(msg)
        if value == list:
            homework = dict_value[0]
    return homework


def parse_status(homework):
    """Parse homework dictionary.
    Return status in string.
    """
    homework_status = homework['status']
    try:
        homework_name = homework['homework_name']
    except KeyError as key_error:
        msg = f'Error or missing key: {key_error}'
        logger.error(msg)
    if homework_status not in HOMEWORK_VERDICTS:
        error_message = (
            f'Unknown homework status: {homework_status}')
        logger.exception(error_message)
        raise exceptions.ValuesMissingError(error_message)
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        msg = 'Environment variable is missing.'
        logger.critical(msg)
        raise exceptions.ValuesMissingError(msg)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time()) - OBSERVATION_TIME
    previous_status = ''
    previous_error = ''

    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            if previous_status != parse_status(homework):
                previous_status = parse_status(homework)
                send_message(bot, previous_status)

        except Exception as error:
            if str(error) != previous_error:
                previous_error = str(error)
                msg = f'Сбой в работе программы: {error}'
                logger.error(msg)
                send_message(bot, msg)
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
