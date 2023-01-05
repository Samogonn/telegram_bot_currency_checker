import telebot
from telebot import types

from config import *
from extensions import Converter, APIException

base_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
buttons = [types.KeyboardButton(val.capitalize()) for val in exchanges.keys()]
base_markup.add(*buttons)

def create_markup(base=None):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    buttons = [types.KeyboardButton(val.capitalize()) for val in exchanges.keys() if val != base]
    return markup.add(*buttons)

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def start(message: telebot.types.Message):
    text = '''Привет. Я бот. Я помогу с конвертацией валют.
Чтобы вывести информацию о доступных валютах, введите /values.
Чтобы начать конвертацию, введите /convert.
Команды /start и /help, чтобы вывести эту инструкцию.'''
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['values'])
def get_values(message: telebot.types.Message):
    text = 'Доступные валюты: \n'
    for cur in exchanges.keys():
        text += cur + '\n'
    bot.reply_to(message, text)

@bot.message_handler(commands=['convert'])
def values(message: telebot.types.Message):
    text = 'Выберите валюту из которой конвертировать:'
    bot.send_message(message.chat.id, text, reply_markup=create_markup())
    bot.register_next_step_handler(message, base_handler)

def base_handler(message: telebot.types.Message):
    base = message.text.strip().lower()
    text = 'Выберите валюту в которую конвертировать:'
    bot.send_message(message.chat.id, text, reply_markup=create_markup(base))
    bot.register_next_step_handler(message, sym_handler, base)

def sym_handler(message: telebot.types.Message, base):
    sym = message.text.strip()
    text = 'Выберите количество конвертируемой валюты'
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, amount_handler, base, sym)

def amount_handler(message: telebot.types.Message, base, sym):
    amount = message.text.strip()
    try:
        new_price = Converter.get_price(base, sym, amount)

    except APIException as e:
        bot.send_message(message.chat.id, f'Ошибка конвертации: \n{e}')
    else:
        text = f'Результат конвертации: {new_price}'
        bot.send_message(message.chat.id, text)

bot.polling()
