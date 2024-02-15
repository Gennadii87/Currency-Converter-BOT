import json
import datetime
import requests
from config import exchanges, KEY


class APIException(Exception):
    pass


class Convertor:
    @staticmethod
    def get_price(base: str, sym: str, amount: float):
        try:
            base_key = exchanges[base.lower()]
        except KeyError:
            raise APIException(f"Валюта {base} не найдена!")

        try:
            sym_key = exchanges[sym.lower()]
        except KeyError:
            raise APIException(f"Валюта {sym} не найдена!")

        if base_key == sym_key:
            raise APIException(f'Невозможно перевести одинаковые валюты {base}!')

        try:
            amount = float(amount)
        except ValueError:
            raise APIException(f'Не удалось обработать количество {amount}!')

        url = f"https://api.apilayer.com/exchangerates_data/latest?base={base_key}&symbols={sym_key}"

        r = requests.get(url, headers=KEY)

        resp = json.loads(r.content)
        new_price = resp['rates'][sym_key] * amount
        new_price = round(new_price, 3)
        day = datetime.date.today()

        message = f"Цена: {amount} {base} = {new_price} {sym}! Текущее дата: {day}."
        return message
