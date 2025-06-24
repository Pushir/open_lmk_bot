def bot_start(rep):
    from threading import Thread
    from time import sleep

    from config import bot, error_logging
    from spam import spam as spaming
    import callbacks

    print("Bot is start")

    @error_logging
    def spam(i):
        while True:
            if not i.value:
                sleep(10)
                try:
                    users, lists = spaming()
                except:
                    pass
                else:
                    for user in users:
                        if not user[1] or not user[1] in lists:
                            continue
                        try:
                            bot.send_message(user[0], lists[user[1]], parse_mode='HTML')
                            sleep(0.1)
                        except:
                            pass
                    del users, lists
            sleep(1)
    Thread(target=spam, args=(rep,)).start()
    while True:
        try:
            bot.polling(non_stop=True, timeout=10, long_polling_timeout=5)
        except Exception:
            sleep(3)
