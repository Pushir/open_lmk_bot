if __name__ == '__main__':
    import os
    os.system('pip install -r req')
    import multiprocessing as mp
    import time
    from download import download_replacements
    from download import download_schedule

    if not os.path.isfile('.env'):
        with open('.env', 'w') as file:
            file.write('BOT_TOKEN=' + input('Введите токен бота: '))
        print('Вы ысегда можете заменить токен в файле .env\n\n')

    for name in ('png_zam', 'arhiv', 'bd', 'schedule', 'zam'):
        if not os.path.isdir(name):
            os.mkdir(name)

    from SQL import sql_create_days_table, sql_create_spam_requests_table, sql_create_all_users_table, \
        sql_create_errors_table, sql_create_last_replacements_table, sql_create_prepods_table, \
        sql_create_prepods_cabinet_table, sql_create_replacements_table, sql_create_spam_table

    sql_create_all_users_table()
    sql_create_days_table()
    sql_create_errors_table()
    sql_create_replacements_table()
    sql_create_last_replacements_table()
    sql_create_prepods_table()
    sql_create_prepods_cabinet_table()
    sql_create_spam_table()
    sql_create_spam_requests_table()

    from bot import bot_start

    rep = mp.Value('i', True)

    mp.Process(target=download_schedule, name='test').start()
    time.sleep(5)
    mp.Process(target=bot_start, args=(rep,)).start()
    while True:
        mp.Process(target=download_replacements, args=(rep,)).start()
        time.sleep(30)
