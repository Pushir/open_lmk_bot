import sqlite3 as sq
from telebot import types


def start_button(chat_type):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    text_my_zam = types.KeyboardButton("Мои замены")
    text_my_zam_last = types.KeyboardButton("Мои замены↩️")
    text_zam = types.KeyboardButton("Замены")
    text_calls = types.KeyboardButton("Звонки")
    text_commands = types.KeyboardButton("Команды")
    markup.row(text_my_zam_last, text_my_zam)
    markup.row(text_zam, text_calls)
    if chat_type == 'private':
        text_settings = types.KeyboardButton("Настройки")
        markup.row(text_commands, text_settings)
    else:
        markup.row(text_commands)
    return markup


def settings_button(chat_id, from_user, replace_spam_type=False):
    markup_inline = types.InlineKeyboardMarkup()
    item_edit_spam = types.InlineKeyboardButton("Изменить статус уведомлений", callback_data='edit_spam')
    item_add_spam_request = types.InlineKeyboardButton("Добавить запрос уведомлений", callback_data='add_spam_request')
    item_del_spam_request = types.InlineKeyboardButton("Удалить запрос уведомлений", callback_data='del_spam_request')
    item_edit_spam_request = types.InlineKeyboardButton("Изменить вашу группу/фамилию", callback_data='edit_my_request')
    markup_inline.add(item_edit_spam, item_add_spam_request, item_del_spam_request, item_edit_spam_request, row_width=1)
    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()
        cur.execute("""SELECT spam, spam_request from all_users WHERE chat_id = ?""", [chat_id, ])
        data = cur.fetchall()
        if data:
            data = data[0]
            spam_type, my_request = data[0], data[1]
            if replace_spam_type:
                spam_type = int(not spam_type)
                cur.execute("""UPDATE all_users SET spam = ? WHERE chat_id = ?""", [spam_type, chat_id])
            if not my_request:
                my_request = ''
            spam_type = 'Вкл' if spam_type else 'Выкл'
        else:
            cur.execute("""INSERT INTO all_users (Name, chat_id, FIO) VALUES (?, ?, ?)""",
                        (from_user.username, str(chat_id), from_user.first_name))
            spam_type = 'Выкл'
            my_request = ''
        cur.execute("""CREATE TABLE IF NOT EXISTS "spam_requests" (
                                "id" INTEGER,
                                "user_id"	TEXT,
                                "request"	TEXT,
                                PRIMARY KEY("id"),
                                FOREIGN KEY("user_id") REFERENCES "all_users"("chat_id"),
                                UNIQUE(user_id, request))""")
        cur.execute("""SELECT request from spam_requests WHERE user_id = ?""", [chat_id, ])
        data = cur.fetchall()
    spam_request = ', '.join(str(i[0]) for i in data)

    return markup_inline, spam_type, my_request, spam_request


def del_spam_request_button(requests):
    markup_inline = types.InlineKeyboardMarkup()
    for request in requests:
        markup_inline.add(types.InlineKeyboardButton(request[0], callback_data=f'del_spam_request_finaly {request[0]}'), row_width=1)
    return markup_inline
