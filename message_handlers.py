from config import bot, day_of_wek, groups_list, error_logging
from commands import settings, commands, png_replacements
from read import take_replacements as tr, prepod_r, take_schedule, take_prepod_schedule
from SQL import sql_take_cabinet_day, sql_take_spam_request


@bot.message_handler(regexp=r'^где ')
def serch_prepod(message):
    text = message.text.lower().replace('где ', '')
    if ' ' not in text:
        text = text.capitalize()
        cabinet_list = sql_take_cabinet_day(text)

        if not cabinet_list:
            bot.send_message(message.chat.id, f'Кабинеты для {text} не найдены')
            return

        result = {}
        for i in cabinet_list:
            result[i[1]] = result.get(i[1], '') + (', ' if result.get(i[1]) else '') + str(i[0])

        resultat = f'{i[2]}\n'

        for i in day_of_wek:
            if i in result:
                n = result.pop(i)
                resultat += f'\n{i} - {n}'

        bot.send_message(message.chat.id, resultat)


@bot.message_handler(regexp=r'^замены ')
def message_replacements(message):
    text = message.text.upper().replace('ЗАМЕНЫ ', '')

    if text == 'ИСИП99-9' or text == 'ИСИП 99-9':
        bot.send_message(message.chat.id, 'ИСиП 99-9 было для примера, а ты пиши свою группу')
        return

    for group in groups_list:
        text = text.replace(f'{group}2', f'{group} 2')
        if text.split(' ')[0] == group:
            bot.send_message(message.chat.id, **tr(text), parse_mode='HTML')
            return

    if ' ' not in text:
        bot.send_message(message.chat.id, **prepod_r(text), parse_mode='HTML')


@bot.message_handler(regexp=r'^звонки$')
def message_calls(message):
    bot.send_photo(message.chat.id, open('calls.png', 'rb'))


@bot.message_handler(regexp=r'^замены$')
def message_replacements_picts(message):
    png_replacements(message)


@bot.message_handler(regexp=r'^расписание ')
@error_logging
def message_schedule_picts(message):
    text = message.text.upper().replace('РАСПИСАНИЕ ', '').split(' ')
    for group in groups_list:
        text[0] = text[0].replace(f'{group}2', f'{group} 2')
        if text[0].split(' ')[0] == group:
            if len(text) == 4:
                text[0] = text[0] + ' ' + text[1]
                text.pop(1)
            elif len(text) != 3:
                return
            group = f"{text[0].replace('ИСИП', 'ИСиП')}"
            day = text[1].lower()
            if day in day_of_wek:
                week_type = text[2].lower()
                if week_type == 'з':
                    week_type = 'зеленая неделя'
                elif week_type == 'б':
                    week_type = 'белая неделя'
                else:
                    return
                bot.send_message(message.chat.id, take_schedule([group, week_type, day]))
            return
    else:
        if len(text) == 3:
            day = text[1].lower()
            if day in day_of_wek:
                week_type = text[2].lower()
                if week_type == 'з':
                    week_type = 'зеленая неделя'
                elif week_type == 'б':
                    week_type = 'белая неделя'
                else:
                    return
                bot.send_message(message.chat.id, take_prepod_schedule(text[0], week_type, day))


@bot.message_handler()
def messages_handler(message):
    text = message.text.upper()
    if text == 'КОМАНДЫ':
        commands(message)
        return
    elif text == 'НАСТРОЙКИ' and message.chat.type == 'private':
        settings(message)
        return
    elif text == 'МОИ ЗАМЕНЫ↩️':
        my_replacements(message, 'last')
        return
    elif text == 'МОИ ЗАМЕНЫ':
        my_replacements(message, 'now')
        return

    elif text == 'ИСИП99-9' or text == 'ИСИП 99-9':
        bot.send_message(message.chat.id, 'ИСиП 99-9 было для примера, а ты пиши свою группу')
        return

    elif message.chat.type == 'private' or (text[0:7] == 'ЗАМЕНЫ '):
        text = text.replace('ЗАМЕНЫ ', '')
        for group in groups_list:
            text = text.replace(f'{group}2', f'{group} 2')
            if text.split(' ')[0] == group:
                bot.send_message(message.chat.id, **tr(text), parse_mode='HTML')
                return
    if ' ' not in text and message.chat.type == 'private':
        bot.send_message(message.chat.id, **prepod_r(text), parse_mode='HTML')


def my_replacements(message, status):
    request = sql_take_spam_request(message.from_user.id)
    if request and request[0]:
        request = request[0]
    else:
        text = 'Для работы данной функции, необходимо настроить запрос в настройках.' \
               '\nВключать уведомления не обязательно.\n /settings'
        if message.chat.type != 'private':
            text += '\n\nНАСТРОЙКИ РАБОТАЮТ ТОЛЬКО В ЛИЧНЫХ СООБЩЕНИЯХ'
        bot.send_message(message.chat.id, text)
        return
    if '-' in request:
        bot.send_message(message.chat.id, **tr(request, status=status), parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, **prepod_r(request, status=status), parse_mode='HTML')
