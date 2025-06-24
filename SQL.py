import sqlite3 as sq


def sql_create_days_table():
    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS days ("type"	TEXT, "text"	TEXT)''')


def sql_create_spam_requests_table():
    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS "spam_requests" 
        ("id" INTEGER,
        "user_id"	TEXT,
        "request"	TEXT,
        PRIMARY KEY("id"),
        FOREIGN KEY("user_id") REFERENCES "all_users"("chat_id"),
        UNIQUE(user_id, request))''')


def sql_create_all_users_table():
    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS all_users 
        ("Name" TEXT,
        "chat_id" TEXT UNIQUE,
        "FIO" TEXT,
        "spam" INTEGER DEFAULT 0,
        "spam_request" TEXT,
        PRIMARY KEY("chat_id"))""")


def sql_create_errors_table():
    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS errors
        ("number" INTEGER, 
        "error"	TEXT, 
        PRIMARY KEY("number" AUTOINCREMENT))''')


def sql_create_last_replacements_table():
    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS last_replacements
        (groupa TEXT,
        number_para TEXT,
        replacements1 TEXT,
        replacements2 TEXT,
        day TEXT)''')


def sql_create_prepods_table():
    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS "prepods"
        ("id"	INTEGER UNIQUE,
        "prepod"	TEXT UNIQUE,
        PRIMARY KEY("id" AUTOINCREMENT))''')


def sql_create_prepods_cabinet_table():
    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS "prepods_cabinet"
        ("prepod"	INTEGER,
        "cabinet"	INTEGER,
        "para"	INTEGER,
        "day"	TEXT,
        "week_tipe"	TEXT,
        FOREIGN KEY("prepod") REFERENCES "prepods"("id"))''')


def sql_create_replacements_table():
    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS replacements
        ("groupa" TEXT,
        "number_para" TEXT,
        "replacements1" TEXT,
        "replacements2" TEXT,
        "day" TEXT)''')


def sql_create_spam_table():
    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS "spam"
        ("request"	TEXT UNIQUE,
        "replacements"	TEXT)''')


def sql_add_user(username, user_id, name):
    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()
        cur.execute("""INSERT INTO all_users (Name, chat_id, FIO) VALUES (?, ?, ?) 
        ON CONFLICT(chat_id) DO UPDATE SET Name = excluded.Name, FIO = excluded.FIO""", (username, user_id, name))


def sql_update_spam_request(request, chat_id):
    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()
        cur.execute("""UPDATE all_users SET spam_request = ? WHERE chat_id = ?""", (request, str(chat_id)))


def sql_add_spam_request(request, chat_id):
    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()
        cur.execute("""INSERT OR IGNORE INTO spam_requests (user_id, request) VALUES (?, ?)""",
                    (str(chat_id), request))


def sql_del_spam_request(request, chat_id):
    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()
        cur.execute("""DELETE FROM spam_requests WHERE user_id=? AND request=?""",
                    (str(chat_id), request))


def sql_take_request_from_spam_requests(user_id):
    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()
        cur.execute("""SELECT request from spam_requests WHERE user_id = ?""", (user_id,))
        return cur.fetchall()


def sql_take_cabinet_day(prepod):
    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()
        cur.execute("""SELECT DISTINCT cabinet, day, prepods.prepod from prepods_cabinet 
        INNER JOIN prepods ON prepods_cabinet.prepod = prepods.id 
        WHERE prepods.prepod LIKE ?""", (f'%{prepod} %', ))
        return cur.fetchall()


def sql_take_spam_request(user_id):
    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()
        cur.execute("""SELECT spam_request from all_users WHERE chat_id = ?""", (user_id,))
        return cur.fetchone()


