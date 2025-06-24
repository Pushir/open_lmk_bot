import sqlite3 as sq
import traceback
from datetime import datetime
from zoneinfo import ZoneInfo
from telebot import TeleBot
from SQL import sql_create_errors_table
import os
from dotenv import load_dotenv

load_dotenv()
bot = TeleBot(os.getenv('BOT_TOKEN'))

groups_list = ('ИСИП', 'МТОР', 'МЧМ', 'ВЕБ', 'МТЭ', 'ТАК', 'КСК',
               'ОДЛ', 'ТЭГ', 'БУХ', 'ЭС', 'ТМ', 'П', 'Э', 'А')

day_of_wek = ('понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота')


def error_logging(funct):
    def start_funct(*args, **kwargs):
        try:
            return funct(*args, **kwargs)
        except:
            sql_create_errors_table()
            with sq.connect('bd/LMK.db') as con:
                cur = con.cursor()
                cur.execute('''INSERT INTO errors (error) VALUES (?)''',
                            (f'{datetime.now(ZoneInfo("Europe/Moscow"))}, {str(args)}, {str(kwargs)}\n{str(traceback.format_exc())}', ))
            return {'text': 'Возникла ошибка при обработке запроса.'}
    return start_funct
