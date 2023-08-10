from datetime import datetime
import requests

from config import URL, API_KEY, currency_types


class APIException(Exception):
    ...


class CurrencyExchange:
    @staticmethod
    def validate_number(number):
        try:
            number = float(number)
        except ValueError:
            raise APIException("нужно ввести число!")
        if number <= 0:
            raise APIException("число должно быть больше нуля!")
        return number

    @staticmethod
    def validate_text(text):
        try:
            quote, base = text.upper().split()
        except ValueError:
            raise APIException("Неверное количество валют")
        reversed_dict = dict((a, b) for (b, a) in currency_types.items())
        try:
            search_quote = reversed_dict[quote]
        except KeyError:
            raise APIException(f"К сожалению, бот не работает с валютой {quote}")
        try:
            search_base = reversed_dict[base]
        except KeyError:
            raise APIException(f"К сожалению, бот не работает с валютой {base}")
        return quote, base

    @staticmethod
    def get_price(quote, base, amount):
        response = requests.get(URL.format(API_KEY, quote, base)).json()
        if response['success']:
            rates = response["rates"]
            exchange_rate = 1 / rates[quote] * rates[base]
            last_updated_datetime = datetime.fromtimestamp(response["timestamp"])
            return last_updated_datetime, exchange_rate * amount
