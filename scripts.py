from config import groups_list
from message_handlers import my_replacements
from commands import start, settings, commands, png_replacements, calls


def take_group_or_prepod(req):
    for group in groups_list:
        req = req.replace(f'{group}2', f'{group} 2')
        if req.split(' ')[0] == group:
            req = req.replace('ИСИП', 'ИСиП')
            break
    else:
        req = req.capitalize()
    return req


def check_in_commands(message):
    commands_list = {'/start': start,
                     '/settings': settings,
                     '/commands': commands,
                     '/replacements': png_replacements,
                     '/calls': calls,
                     'Мои замены': [my_replacements, 'now'],
                     'Мои замены↩️': [my_replacements, 'last'],
                     'Замены': png_replacements,
                     'Звонки': calls,
                     'Команды': commands,
                     'Настройки': settings}
    if message.text in commands_list:
        funkciya = commands_list[message.text]
        if type(funkciya) == list:
            funkciya[0](message, funkciya[1])
        else:
            funkciya(message)
        return True


