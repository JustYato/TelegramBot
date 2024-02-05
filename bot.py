import telebot
from telebot import types
import datetime
import time
import asyncio
import threading

bot = telebot.TeleBot('Токен_бота')
with open("date.txt", "r") as file:
    last_sent_time_str = file.readline().strip()
last_sent_time = datetime.datetime.strptime(last_sent_time_str, "%Y-%m-%d %H:%M:%S")


@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button = types.KeyboardButton('Оформить заявку')
    markup.add(button)

    bot.send_message(message.chat.id, 'Текст предложения оформления заявки', reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def process_message(message):
    if message.text == 'Оформить заявку':
        markup = types.ReplyKeyboardRemove()

        bot.send_message(message.chat.id, 'Текст подтверждения и указания типа заявки', reply_markup=markup)

        bot.register_next_step_handler(message, process_service_type)


def process_service_type(message):
    service_type = message.text

    bot.send_message(message.chat.id, 'ФИО:')
    bot.register_next_step_handler(message, process_full_name, service_type)


def process_full_name(message, service_type):
    full_name = message.text

    bot.send_message(message.chat.id, 'Номер телефона:')
    bot.register_next_step_handler(message, process_phone_number, service_type, full_name)


def process_phone_number(message, service_type, full_name):
    phone_number = message.text

    bot.send_message(message.chat.id, 'Адрес:')
    bot.register_next_step_handler(message, process_address, service_type, full_name, phone_number)


def process_address(message, service_type, full_name, phone_number):
    address = message.text

    bot.send_message(message.chat.id, 'Дата и время')
    bot.register_next_step_handler(message, process_connection_date, service_type, full_name, phone_number, address)


def process_connection_date(message, service_type, full_name, phone_number, address):
    connection_date = message.text

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    yes_button = types.KeyboardButton('Да')
    no_button = types.KeyboardButton('Нет')
    markup.add(yes_button, no_button)

    bot.send_message(message.chat.id, 'Дополнительная консультация', reply_markup=markup)
    bot.register_next_step_handler(message, process_specialist_help, service_type, full_name, phone_number, address, connection_date)


def process_specialist_help(message, service_type, full_name, phone_number, address, connection_date):
    specialist_help = message.text

    bot.send_message('ID_Пользователя', 'Новая заявка:\n'
                                      f'Тип: {service_type}\n'
                                      f'ФИО: {full_name}\n'
                                      f'Номер: {phone_number}\n'
                                      f'Адрес: {address}\n'
                                      f'Дата: {connection_date}\n'
                                      f'Консультация: {specialist_help}')

    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button = types.KeyboardButton('Оформить заявку')
    markup.add(button)

    bot.send_message(message.chat.id, 'Сообщение об успехе', reply_markup=markup)


def run_bot_polling():
    bot.polling()


def send_message_to_group(group_id, message):
    bot.send_message(group_id, message)

    
def should_send_message():
    now = datetime.datetime.now()

    if (now - last_sent_time).days >= 0:
        return True

    return False

async def send_messages():
    while True:
        with open("chats_ids.txt", "r") as file:
            group_ids = file.readlines()

        group_ids = [int(group_id.strip()) for group_id in group_ids]

        if should_send_message():
            for group_id in group_ids:
                send_message_to_group(group_id, "Текст рассылки")

            current_datetime = datetime.datetime.now()
            current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

            with open("date.txt", "w") as file:
                file.write(current_datetime_str)

        await asyncio.sleep(3600)


if __name__ == '__main__':
    threading.Thread(target=run_bot_polling).start()
    asyncio.run(send_messages())
