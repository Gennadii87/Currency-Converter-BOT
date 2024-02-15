import json
import logging
import telebot
from extensions import APIException, Convertor
from config import TOKEN, exchanges, KEY, val1, val2, col
import traceback
import requests
import datetime


logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

bot = telebot.TeleBot(TOKEN)

def log_user_action(user_id, action):
    logger.info(f"User {user_id} performed action: {action}")

@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    text = "Привет, Я бот - конвертер валют! помощь - /help\nсписок валют - /values\nбыстрая команда - /exchange "
    bot.send_message(message.chat.id, text)
    log_user_action(message.from_user.id, "/start")


@bot.message_handler(commands=['help'])
def start(message: telebot.types.Message):
    text = "Пример запроса для получения курса валют: рубль доллар 1"
    bot.send_message(message.chat.id, text)
    log_user_action(message.from_user.id, "/help")


@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты:'
    for i in exchanges.keys():
        text = '\n'.join((text, i))
    bot.reply_to(message, text)
    log_user_action(message.from_user.id, "/values")


@bot.message_handler(commands=['exchange'])
def send_exchange_rate(message):
    result = exchange_rate()
    bot.send_message(chat_id=message.chat.id, text=result)
    log_user_action(message.from_user.id, "/exchange")


def exchange_rate():
    url = f'https://api.apilayer.com/exchangerates_data/latest?base={val2}&symbols={val1}'
    response = requests.get(url, headers=KEY)

    if response.status_code == 200:
        try:
            data = response.json()
            exchange_rate = data['rates'][val1]
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            message = f"{col} {val2} = {exchange_rate} {val1} на {date}"
            logger.info(f"Отправлено пользователю: {message}")
            print(f"Отправлено пользователю: {message}")
        except json.JSONDecodeError as e:
            message = f"Ошибка декодирования JSON: {e}"
            logger.info(f"Отправлено пользователю: {message}")
            print(f"Отправлено пользователю: {message}")
    else:
        message = f"Ошибка получения курса валют. Статус код: {response.status_code}"
        logger.info(f"Отправлено пользователю: {message}")
        print(f"Отправлено пользователю: {message}")

    return message


@bot.message_handler(content_types=['text'])
def converter(message: telebot.types.Message):
    values = message.text.split(' ')
    try:
        if len(values) != 3:
            raise APIException('Неверное количество параметров!')

        answer = Convertor.get_price(*values)
    except APIException as e:
        bot.reply_to(message, f"Ошибка в команде:\n{e}")
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        bot.reply_to(message, f"Неизвестная ошибка:\n{e}")
        print(f"Отправляется пользователю: {message}")
    else:
        bot.reply_to(message, answer)
        log_user_action(message.from_user.id, f"Conversion request: {message.text}")
        logger.info(f"Отправлено пользователю: {message}")


def main():
    try:
        # Вывод в консоль при запуске бота
        print("Бот запущен!")
        # Запуск бота
        bot.polling()
    finally:
        # Вывод в консоль при остановке бота
        print("Бот остановлен!")


if __name__ == "__main__":
    main()