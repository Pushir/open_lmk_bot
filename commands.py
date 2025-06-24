import text
from telebot import types
from os import listdir

from config import bot, error_logging
from button import start_button, settings_button
from SQL import sql_create_all_users_table, sql_add_user


@bot.message_handler(commands=['start'])
@error_logging
def start(message):
    bot.send_message(message.chat.id, text.start_text, reply_markup=start_button(message.chat.type))

    if message.chat.type == 'private':
        sql_create_all_users_table()
        sql_add_user(message.from_user.username, str(message.chat.id), message.from_user.first_name)


@bot.message_handler(commands=['settings'], chat_types='private')
@error_logging
def settings(message):
    markup_inline, spam_tipe, my_request, spam_request = settings_button(message.chat.id, message.from_user)
    bot.send_message(message.chat.id, f'Уведомления: {spam_tipe}\nЗапрос для уведомлений: {spam_request}\n'
                                      f'Ваша группа/фамилия: {my_request}',
                     reply_markup=markup_inline)


@bot.message_handler(commands=['commands'])
def commands(message):
    bot.send_message(message.chat.id, text.commands_text)


@bot.message_handler(commands=['replacements'])
def png_replacements(message):
    photos = []
    files = listdir('png_zam')
    files.sort()
    for photo in files:
        photos.append(types.InputMediaPhoto(open('png_zam/' + photo, 'rb')))
    bot.send_media_group(message.chat.id, photos)


@bot.message_handler(commands=['calls'])
def calls(message):
    bot.send_photo(message.chat.id, open('calls.png', 'rb'))
