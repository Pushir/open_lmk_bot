import sqlite3 as sq
from config import error_logging
from telebot import types


@error_logging
def take_replacements(user_group, status='now'):
    if 'ИСИП' in user_group:
        user_group = user_group.replace('ИСИП', 'ИСиП')
    user_group = user_group[:-1] + user_group[-1].lower()  # Для групп с постфиксом "с"

    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()

        markup_inline = types.InlineKeyboardMarkup()
        if status == 'now':
            read_last = types.InlineKeyboardButton("Прошлые замены", callback_data='last_replacements')
            markup_inline.add(read_last, row_width=1)
            cur.execute("""SELECT * from replacements WHERE groupa = ?""", [user_group])
        else:
            cur.execute("""SELECT * from last_replacements WHERE groupa = ?""", [user_group])
        replacements = cur.fetchall()
    end = False
    if len(replacements) == 1:
        if replacements[0][1] == 'практика':
            return {'text': f'{replacements[0][4]}\n\n{replacements[0][0]}\n{replacements[0][1]}'}
    if not len(replacements):
        with sq.connect('bd/LMK.db') as con:
            cur = con.cursor()
            if status == 'now':
                cur.execute("""SELECT text from days WHERE type = 'replacements_day'""")
            else:
                cur.execute("""SELECT text from days WHERE type = 'last_replacements_day'""")
            day = cur.fetchall()[0][0]
        replacements = ([None, None, None, None, day],)
        end = True

    if replacements[0][4].split(' ')[0].lower() == 'расписание':
        if replacements[0][0] is None:
            return {'text': f'{day}\n\n{user_group} отдыхает', 'reply_markup': markup_inline}
        return {'text': take_replacements_2(replacements), 'reply_markup': markup_inline}

    day_week = replacements[0][4].split(' ')
    if 'за' in day_week:
        day = day_week[-5].lower()
        week = f'{day_week[-2]} {day_week[-1]}'.lower()
    else:
        day = day_week[-3].replace('(', '').replace(')', '').lower()
        week = f'{day_week[-2]} {day_week[-1]}'.lower()
    reqrst = [user_group, week, day]

    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()
        cur.execute("""SELECT number, para from schedule WHERE (groupa = ?) and (week_tipe = ?) and (day = ?)""",
                    reqrst)
        schedule = cur.fetchall()

    if not schedule:
        return {'text': 'Группа не найдена'}

    result = f'{replacements[0][4]}\n\n{user_group}\n'

    if not end:
        numbers_replacements = []
        numbers_in_replacements = []
        for i in replacements:
            if len(i[1]) == 1:
                numbers_replacements.append(i[1])
                numbers_in_replacements.append([i[1], i[3]])
            else:
                numbers_replacements.append(i[1][2])
                numbers_replacements.append(i[1][-1])
                numbers_in_replacements.append([i[1][-1], i[3]])

        kostil = []
        for i in numbers_in_replacements:
            if i not in kostil:
                kostil.append(i)
        numbers_in_replacements = kostil
        del kostil

        for i in enumerate(numbers_in_replacements):
            if 'Иностранный язык' in i[1][1]:
                break
            with sq.connect('bd/LMK.db') as con:
                cur = con.cursor()
                cur.execute("""SELECT DISTINCT cabinet from prepods_cabinet 
                        INNER JOIN prepods ON prepods_cabinet.prepod = prepods.id 
                        WHERE prepods.prepod LIKE ? AND day = ?  AND week_tipe = ? AND para = ?""",
                            (f'%{i[1][1].split(" ")[0]} %', day, week, i[1][0]))
                cabinet = cur.fetchall()
                if cabinet:
                    numbers_in_replacements[i[0]][1] += f'  ({cabinet[0][0]})'
                else:
                    cur.execute("""SELECT DISTINCT cabinet from prepods_cabinet 
                                INNER JOIN prepods ON prepods_cabinet.prepod = prepods.id 
                                WHERE prepods.prepod LIKE ? AND day = ?  AND week_tipe = ?""",
                                (f'%{i[1][1].split(" ")[0]} %', day, week))
                    cabinet = cur.fetchall()
                    if cabinet:
                        if len(cabinet) == 1:
                            numbers_in_replacements[i[0]][1] += f'  возможно в {cabinet[0][0]}'
                        else:
                            cabinet = ''.join(str(lists[0]) + ' ' for lists in cabinet)
                            numbers_in_replacements[i[0]][1] += f'  возможно в {cabinet}'

        schedule_list = []
        for i in schedule:
            i = list(i)
            if i[0] in numbers_replacements:
                numbers_replacements.remove(i[0])
                i[1] = f'<strike>{i[1]}</strike>'
            schedule_list.append(i)
        schedule = schedule_list
        del schedule_list
        for_del = []
        for i in numbers_in_replacements:
            for n in schedule:
                if i[0] == n[0]:
                    n[1] = f'{n[1]}    <b>{i[1]}</b>'
                    for_del.append(i)
                elif '<strike>' not in n[1]:
                    n[1] = f'<b>{n[1]}</b>'
        for i in for_del:
            numbers_in_replacements.remove(i)

        if len(numbers_in_replacements):
            for i in numbers_in_replacements:
                schedule.append(i)
            schedule.sort()

    if schedule[0][0] == ' ':  # У разговоров и класного часа в начале пробел
        rep = schedule.pop(0)
        if ' о ' in rep[1]:
            schedule.insert(2-int(schedule[0][0]), rep)
        else:
            index = [[index, item] for index, item in enumerate(schedule) if item[0] in ('3', '4')]
            if len(index) == 2:
                schedule.insert(index[1][0], rep)
            else:
                index = index[0]
                schedule.insert(index[0], rep) if index[1][0] == '4' else schedule.insert(index[0]+1, rep)

    for i in schedule:
        result += f'{i[0]}  {i[1]}\n'

    if status == 'now':
        result += 'Для проверки: /replacements'

    return {'text': result, 'reply_markup': markup_inline}


def take_replacements_2(replacements):
    result = f'{replacements[0][4]}\n\n{replacements[0][0]}\n'
    for i in replacements:
        if i[1] == '2':
            if 'понедельник' in i[4]:
                result += '  Разговор о важном\n'
        elif i[1] == '4' and 'час' not in result:
            if 'четверг' in i[4]:
                result += '  Классный час\n'

        result += f'{i[1]}  {i[3]}\n'

        if i[1] == '3':
            if 'четверг' in i[4]:
                result += ' Классный час\n'
    return result


@error_logging
def prepod_r(prepod, status='now'):
    prepod = prepod.capitalize()
    prepod = prepod.replace('ё', 'е')
    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()

        markup_inline = types.InlineKeyboardMarkup()
        if status == 'now':
            read_last = types.InlineKeyboardButton("Прошлые замены", callback_data='last_replacements')
            markup_inline.add(read_last, row_width=1)
            cur.execute("""SELECT * from replacements WHERE (replacements1 LIKE ?) OR (replacements2 LIKE ?)""",
                        [f'%{prepod} %', f'%{prepod} %'])
        else:
            cur.execute("""SELECT * from last_replacements WHERE (replacements1 LIKE ?) OR (replacements2 LIKE ?)""",
                        [f'%{prepod} %', f'%{prepod} %'])
        replacements = cur.fetchall()
        cur.execute("""SELECT groupa from replacements WHERE number_para = 'практика'""")
        practics = cur.fetchall()
    end = False
    if not replacements:
        with sq.connect('bd/LMK.db') as con:
            cur = con.cursor()
            if status == 'now':
                cur.execute("""SELECT text from days WHERE type = 'replacements_day'""")
            else:
                cur.execute("""SELECT text from days WHERE type = 'last_replacements_day'""")
            day = cur.fetchall()[0][0]
        replacements = ([None, None, None, None, day],)
        end = True
    practic = []
    for i in practics:
        practic.append(i[0])
    del practics

    if replacements[0][4].split(' ')[0].lower() == 'расписание':
        if end:
            return {'text': f'{replacements[0][4]}\n\n{prepod} отдыхает', 'reply_markup': markup_inline}
        return {'text': prepod_r_2(replacements, prepod), 'reply_markup': markup_inline}

    day_week = replacements[0][4].split(' ')
    day = day_week[-3].replace('(', '').replace(')', '').lower()
    week = f'{day_week[-2]} {day_week[-1]}'.lower()
    reqest = [f'%{prepod} %', week, day]
    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()
        cur.execute("""SELECT number, groupa from schedule WHERE (para LIKE ?) and (week_tipe = ?) and (day = ?)""",
                    reqest)
        schedule = cur.fetchall()

        cur.execute("""SELECT DISTINCT para, cabinet from prepods_cabinet 
        INNER JOIN prepods ON prepods_cabinet.prepod = prepods.id 
        WHERE prepods.prepod LIKE ? AND day = ?  AND week_tipe = ?""", (f'%{prepod} %', day, week))
        cabinet_list = {str(key): str(value) for key, value in cur.fetchall()}

    for i in range(len(schedule)):
        if schedule[i][1] in practic:
            schedule[i] = (schedule[i][0], f'<strike>{schedule[i][1]}</strike>')

    if not end:
        numbers_replacements = []
        numbers_in_replacements = []
        for i in replacements:
            if len(i[1]) == 1:
                if prepod in i[2]:
                    numbers_replacements.append([i[1], i[0]])
                if prepod in i[3]:
                    numbers_in_replacements.append([i[1], i[0]])
            else:
                if prepod in i[2]:
                    numbers_replacements.append([i[1][2], i[0]])
                if prepod in i[3]:
                    numbers_in_replacements.append([i[1][-1], i[0]])
                    numbers_replacements.append([i[1][-1], i[0]])

        kostil = []
        for i in numbers_replacements:
            if i not in kostil:
                kostil.append(i)
        numbers_replacements = kostil
        kostil = []
        for i in numbers_in_replacements:
            if i not in kostil:
                kostil.append(i)
        numbers_in_replacements = kostil
        del kostil

        if len(schedule) and len(numbers_replacements):
            schedule_list = []
            for i in schedule:
                i = list(i)
                if i in numbers_replacements:
                    numbers_replacements.remove(i)
                    i[1] = f'<strike>{i[1]}</strike>'
                schedule_list.append(i)
            schedule = schedule_list
            del schedule_list

            for_del = []
            for i in numbers_in_replacements:
                for n in schedule:
                    if i[0] == n[0] and '<strike>' in n[1]:
                        n[1] = f'{n[1]}    <b>{i[1]}</b>'
                        for_del.append(i)
                    elif '<strike>' not in n[1]:
                        n[1] = f'<b>{n[1]}</b>'

            for i in for_del:
                try:
                    numbers_in_replacements.remove(i)
                except:
                    pass

        if len(numbers_in_replacements):
            numbers_in_replacements.sort()
            if len(schedule):
                range_list = [int(schedule[0][0]), int(schedule[-1][0])]
            else:
                range_list = [0, 0]
            for i in numbers_in_replacements:
                if int(i[0]) > range_list[1]:
                    schedule.append(i)
                    range_list = [int(schedule[0][0]), int(schedule[-1][0])]
                else:
                    schedule.insert(0, i)
                    range_list = [int(schedule[0][0]), int(schedule[-1][0])]
    bufer = []

    for i in schedule:
        bufer.append(f'{i[0]}  {i[1]}\n')
    bufer.sort()
    result = f'{replacements[0][4]}\n\n{prepod}\n'
    for i in bufer:
        try:
            i = i.replace('\n', f'   {cabinet_list[i[0]]}\n')
        except:
            pass
        result += i
    if status == 'now':
        result += '\nДля проверки: /replacements'

    return {'text': result, 'reply_markup': markup_inline}


def prepod_r_2(replacements, prepod):
    wr = []
    for i in replacements:
        wr.append(f'{i[1]}  {i[0]}\n')
    wr.sort()
    result = f'{replacements[0][4]}\n\n{prepod}\n'
    for i in wr:
        result += i
    return result


@error_logging
def take_prepod_schedule(prepod, week, day):
    prepod = f"%{prepod.capitalize()} %"
    prepod = prepod.replace('ё', 'е')
    data = []
    result = ''

    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()
        cur.execute(
            """SELECT groupa, number, para from schedule WHERE (para LIKE ?) and (week_tipe = ?) and (day = ?)""",
            [prepod, week, day])
        record = cur.fetchall()

    for i in record:
        data.append(f"{i[1]}  {i[0]}  {i[2]}\n")
    data.sort()
    for i in data:
        result += i
    if result == "":
        return 'Расписание не найдено'
    return result


@error_logging
def take_schedule(reqest):
    result = ''
    with sq.connect('bd/LMK.db') as con:
        cur = con.cursor()
        cur.execute("""SELECT number, para from schedule WHERE (groupa = ?) and (week_tipe = ?) and (day = ?)""",
                    reqest)
        record = cur.fetchall()
    for i in record:
        result += f"{i[0]}  {i[1]}\n"
    if result == "":
        return 'Расписание не найдено'
    return result
