from config import bot, error_logging
from button import settings_button, del_spam_request_button
from read import take_replacements as tr, prepod_r
from scripts import check_in_commands, take_group_or_prepod
from commands import settings
from SQL import sql_update_spam_request, sql_add_spam_request, sql_del_spam_request, sql_take_request_from_spam_requests


@bot.callback_query_handler(func=lambda call: call.data == 'last_replacements')
def callback_last_replacements(call):
    bot.answer_callback_query(call.id)
    text = call.message.text.split('\n')[2]
    if '-' in text:
        text = text.split(' ')
        text = f"{text[0]} {text[1]}"
        bot.send_message(call.message.chat.id, **tr(text, status='last'), parse_mode='HTML')
    else:
        text = text.split(' ')[0]
        bot.send_message(call.message.chat.id, **prepod_r(text, status='last'), parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: call.data == 'edit_spam')
def callback_edit_spam(call):
    bot.answer_callback_query(call.id)
    markup_inline, spam_type, my_request, spam_request = settings_button(call.message.chat.id,
                                                                         call.message.from_user, True)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text=f'Уведомления: {spam_type}\n'
                               f'Запрос для уведомлений: {spam_request}\n'
                               f'Ваша группа/фамилия: {my_request}',
                          reply_markup=markup_inline)


@bot.callback_query_handler(func=lambda call: call.data == 'edit_my_request')
def callback_add_my_request(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, 'Введите название группы или фамилию преподавателя:')
    bot.register_next_step_handler(call.message, register_my_request)


@bot.callback_query_handler(func=lambda call: call.data == 'add_spam_request')
def callback_edit_spam_request(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, 'Введите название группы или фамилию преподавателя:')
    bot.register_next_step_handler(call.message, register_spam_request)


@bot.callback_query_handler(func=lambda call: call.data == 'del_spam_request')
def callback_del_spam_request_start(call):
    bot.answer_callback_query(call.id)
    requests = sql_take_request_from_spam_requests(call.message.chat.id)
    if requests:
        bot.send_message(call.message.chat.id, 'Выберите запрос, который вы хотите удалить:',
                         reply_markup=del_spam_request_button(requests))
    else:
        bot.send_message(call.message.chat.id, 'У вас нет заппросов для уведомлений.')


@bot.callback_query_handler(func=lambda call: call.data[0:23] == 'del_spam_request_finaly')
@error_logging
def callback_del_spam_request_finaly(call):
    bot.answer_callback_query(call.id)
    data = call.data.replace('del_spam_request_finaly ', '')
    sql_del_spam_request(data, call.message.chat.id)
    requests = sql_take_request_from_spam_requests(call.message.chat.id)
    if requests:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text='Выберите запрос, который вы хотите удалить:',
                              reply_markup=del_spam_request_button(requests))
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text='У вас больше нет заппросов для уведомлений.',
                              reply_markup=del_spam_request_button(requests))


@error_logging
def register_my_request(message):
    if check_in_commands(message):
        return
    sql_update_spam_request(take_group_or_prepod(message.text.upper()), message.chat.id)
    settings(message)


@error_logging
def register_spam_request(message):
    if check_in_commands(message):
        return
    sql_add_spam_request(take_group_or_prepod(message.text.upper()), message.chat.id)
    settings(message)
