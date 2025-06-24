from read import take_replacements, prepod_r
import sqlite3 as sq
import traceback
from config import error_logging


@error_logging
def spam():
    lists = {}
    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()

        cur.execute("""SELECT user_id, request from spam_requests 
        INNER JOIN all_users ON spam_requests.user_id = all_users.chat_id 
        WHERE all_users.spam=1""")
        users = cur.fetchall()

        cur.execute("""SELECT DISTINCT request from spam_requests 
                INNER JOIN all_users ON spam_requests.user_id = all_users.chat_id 
                WHERE all_users.spam=1""")
        requests = cur.fetchall()

        cur.execute("""CREATE TABLE IF NOT EXISTS "spam" ("request"	TEXT UNIQUE, "replacements"	TEXT);""")

    for i in requests:
        i = i[0]
        try:
            if not i:
                continue
            if '-' in i:
                new_replacements = take_replacements(i)['text']
            else:
                new_replacements = prepod_r(i)['text']
        except Exception:
            with sq.connect('bd/LMK.db') as con:
                cur = con.cursor()
                cur.execute(
                    '''CREATE TABLE IF NOT EXISTS errors ("number"	INTEGER, "error" TEXT, PRIMARY KEY("number" AUTOINCREMENT))''')
                cur.execute('''INSERT INTO errors (error) VALUES (?)''', (str(i) + '\n' + str(traceback.format_exc()),))
                continue

        try:
            old_replacements = cur.execute("""SELECT replacements from spam WHERE request = ?""", [i]).fetchall()[0][0]
        except:
            old_replacements = []

        if ('практика' in new_replacements and 'практика' in old_replacements) \
                or ('отдыхает' in new_replacements and 'отдыхает' in old_replacements):
            continue

        if not old_replacements:
            with sq.connect('bd/LMK.db') as con:
                cur = con.cursor()
                try:
                    cur.execute("""INSERT INTO spam VALUES (?, ?)""", [i, new_replacements])
                except:
                    cur.execute("""UPDATE spam SET replacements = ? WHERE request = ?""", [new_replacements, i])
            lists[i] = new_replacements

        elif old_replacements != new_replacements:
            with sq.connect('bd/LMK.db') as con:
                cur = con.cursor()
                cur.execute("""UPDATE spam SET replacements = ? WHERE request = ?""", [new_replacements, i])
            lists[i] = new_replacements
    return users, lists
