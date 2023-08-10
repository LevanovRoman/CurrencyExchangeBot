import telebot
from telebot import types

from config import TOKEN, currency_types
from extensions import CurrencyExchange, APIException


bot = telebot.TeleBot(TOKEN)
amount = 0
TEXT = 'Доступные валюты:'
for key, value in currency_types.items():
    TEXT += '\n' + key + '  -  ' + value


@bot.message_handler(commands=['help'])
def get_help(message: telebot.types.Message):
    text = ('Вам нужно ввести число - количество валюты, которую вы хотите перевести в другую.\n'
            'На следующем шаге выбрать валюты из меню или ввести собственный вариант из предложенных в списке валют.\n'
            'Список возможных валют  - наберите или выберите в меню /values \n'
            'Начало работы - /start')
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['start'])
def get_start(message: telebot.types.Message):
    text = 'Привет! Это конвертер валют. Какую сумму хотите перевести?'
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, get_sum)


@bot.message_handler(commands=['values'])
def get_help(message: telebot.types.Message):
    bot.reply_to(message, TEXT)


def get_sum(message):
    global amount
    amount = message.text.strip().replace(",", ".")

    try:
        amount = CurrencyExchange.validate_number(amount)
    except APIException as e:
        bot.reply_to(message,f"Ошибка:\n{e}")
        bot.register_next_step_handler(message, get_sum)
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('USD ---> EUR', callback_data='usd eur')
    btn2 = types.InlineKeyboardButton('EUR ---> USD', callback_data='eur usd')
    btn3 = types.InlineKeyboardButton('USD ---> RUB', callback_data='usd rub')
    btn4 = types.InlineKeyboardButton('RUB ---> USD', callback_data='rub usd')
    btn5 = types.InlineKeyboardButton('EUR ---> RUB', callback_data='eur rub')
    btn6 = types.InlineKeyboardButton('RUB ---> EUR', callback_data='rub eur')
    btn7 = types.InlineKeyboardButton('Другие валюты', callback_data='else')
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
    bot.send_message(message.chat.id, 'Выберите валюты для перевода', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data != 'else':
        quote, base = call.data.upper().split()
        last_updated_datetime, result = CurrencyExchange.get_price(quote, base, amount)
        text = (f'Получается: <b>{amount}</b> {quote} = <b>{round(result, 2)}</b> {base}\n\nДата: {last_updated_datetime}\n\nМожете заново ввести сумму')
        bot.send_message(call.message.chat.id, text, parse_mode='html')
        bot.register_next_step_handler(call.message, get_sum)

    else:
        bot.send_message(call.message.chat.id, f'Введите код исходной валюты и код валюты, в которую хотите перевести через пробел в любом регистре\n'
                                               f'например RUB JPY\n{TEXT}')
        bot.register_next_step_handler(call.message, another_currency)


def another_currency(message):
    try:
        quote, base = CurrencyExchange.validate_text(message.text)
    except APIException as e:
        bot.reply_to(message, f"Ошибка с валютами:\n{e}")
        bot.register_next_step_handler(message, another_currency)
        return

    last_updated_datetime, result = CurrencyExchange.get_price(quote, base, amount)
    text = f'Получается: {amount} {quote} = {round(result, 2)} {base}\nДата: {last_updated_datetime}\nМожете заново ввести сумму'
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, get_sum)


bot.polling()
