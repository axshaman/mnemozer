from datetime import datetime

import pytz as pytz
from dateutil.parser import *
from pydantic.datetime_parse import timedelta
from pydantic.main import BaseModel

dates_for_user = {
    'English': {
        'everyday': 'everyday at {}:{}',
        'every day of week': 'every {} day of week at {}:{}'
    },
    'Russian': {
        'everyday': 'Каждый день в {}:{}',
        'every day of week': 'каждый {} день недели в {}:{}'
    }
}

months = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
    "январь": 1, "февраль": 2, "март": 3, "апрель": 4, "май": 5, "июнь": 6, "июль": 7, "август": 8,
    "сентябрь": 9, "октябрь": 10, "ноябрь": 11, "декабрь": 12,
}
days_of_the_week = {"mon": 0, "tue": 1, "wed": 2,
                    "thu": 3, "fri": 4, "sat": 5,
                    "sun": 6,
                    "Mon": 0, "Tue": 1, "Wed": 2,
                    "Thu": 3, "Fri": 4, "Sat": 5,
                    "Sun": 6,
                    "monday": 0, "tuesday": 1,
                    "wednesday": 2, "thursday": 3,
                    "friday": 4, "saturday": 5,
                    "sunday": 6,
                    "понедельник": 0, "вторник": 1,
                    "среда": 2, "четверг": 3,
                    "пятница": 4, "суббота": 5,
                    "воскресенье": 6,
                    "пн": 0, "вт": 1, "ср": 2,
                    "чт": 3, "пт": 4, "сб": 5,
                    "вс": 6,
                    "ПН": 0, "ВТ": 1, "СР": 2,
                    "ЧТ": 3, "ПТ": 4, "СБ": 5,
                    "ВС": 6,
                    }


class Date(BaseModel):
    minute: int = 0
    hour: int = 12
    day_of_month: int = 1
    day_of_week: int = 1
    month: int = 1
    year: int = datetime.now().year
    everyday: bool = False
    date_for_user: str = ''
    trigger: str = 'date'


def find_separator_and_split_date(date):
    available_separators = ['-', '_', '/', '\\', '|', ';', ':', ',', '.', '*', '~', ' ']
    for char in date:
        if char in available_separators:
            date = date.replace(char, ',')
    separated_dates = date.split(',')
    return True, separated_dates


def parse_date(user_entered_date, user_timezone, user_language):
    correct, sep_date = find_separator_and_split_date(user_entered_date)
    for i in range(len(sep_date)):
        if sep_date[i].isdigit():
            sep_date[i] = int(sep_date[i])
    if sep_date[0] in ['everyday', 'ежедневно']:
        date = Date(everyday=True)
        if len(sep_date) == 3:
            date.hour, date.minute = sep_date[1], sep_date[2]
        date.date_for_user = dates_for_user[user_language]['everyday'].format(date.hour, date.minute)
        if date.minute < 10:
            date.date_for_user = dates_for_user[user_language]['everyday'].format(date.hour, f'0{date.minute}')
        date.trigger = 'cron'
        convert_date_to_timezone(date, user_timezone, 'UTC')
        return correct, date
    if sep_date[0] in days_of_the_week:
        date = Date(day_of_week=days_of_the_week[sep_date[0]])
        if len(sep_date) == 3:
            date.hour, date.minute = sep_date[1], sep_date[2]
        date.date_for_user = dates_for_user[user_language]['every day of week'].format(date.day_of_week + 1, date.hour,
                                                                                       date.minute)
        if date.minute < 10:
            date.date_for_user = dates_for_user[user_language]['every day of week'].format(date.day_of_week + 1,
                                                                                           date.hour, f'0{date.minute}')

        hour_before_convert = date.hour
        convert_date_to_timezone(date, user_timezone, 'UTC')
        if hour_before_convert < date.hour:
            if date.day_of_week > 0:
                date.day_of_week -= 1
            else:
                date.day_of_week = 6

        date.trigger = 'cron'
        return correct, date
    elif len(sep_date) == 3 and sep_date[2] in days_of_the_week:
        date = Date(day_of_week=days_of_the_week[sep_date[2]])
        if len(sep_date) == 3:
            date.hour, date.minute = sep_date[0], sep_date[1]
        date.date_for_user = dates_for_user[user_language]['every day of week'].format(date.day_of_week + 1, date.hour,
                                                                                       date.minute)
        if date.minute < 10:
            date.date_for_user = dates_for_user[user_language]['every day of week'].format(date.day_of_week + 1,
                                                                                           date.hour,
                                                                                           f'0{date.minute}')
        hour_before_convert = date.hour
        convert_date_to_timezone(date, user_timezone, 'UTC')

        if hour_before_convert < date.hour:
            if date.day_of_week > 0:
                date.day_of_week -= 1
            else:
                date.day_of_week = 6
        date.trigger = 'cron'
        return correct, date
    parsed_date = parse(user_entered_date)
    date = Date(minute=parsed_date.minute,
                hour=parsed_date.hour,
                day_of_month=parsed_date.day,
                month=parsed_date.month,
                year=parsed_date.year,
                everyday=False,
                )
    if len(sep_date) == 3:
        date.hour = 12
        date.minute = 0
    date.date_for_user = f'{date.day_of_month}.{date.month}.{date.year} {date.hour}:{date.minute}'
    if date.month < 10:
        date.date_for_user = f'{date.day_of_month}.0{date.month}.{date.year} {date.hour}:{date.minute}'
    if date.minute < 10:
        date.date_for_user = f'{date.day_of_month}.0{date.month}.{date.year} {date.hour}:0{date.minute}'
    convert_date_to_timezone(date, user_timezone, 'UTC')
    if len(sep_date) == 2:
        check_for_past_and_edit(date, user_timezone)
    return correct, date


def check_for_past_and_edit(date, user_timezone):
    date_for_check = datetime(year=date.year, month=date.month, day=date.day_of_month,
                              hour=date.hour, minute=date.minute,
                              tzinfo=pytz.timezone('UTC'))
    while date_for_check < datetime.now(tz=pytz.timezone('UTC')):
        final_date = datetime(year=date.year, month=date.month, day=date.day_of_month,
                              hour=date.hour, minute=date.minute,
                              tzinfo=pytz.timezone('UTC')) + timedelta(days=1)
        date_for_check += timedelta(days=1)
        date.year, date.month, date.day_of_month = final_date.year, final_date.month, final_date.day
        date.date_for_user = f'{date.day_of_month}.{date.month}.{date.year} {date.hour}:{date.minute}'
        if date.month < 10:
            date.date_for_user = f'{date.day_of_month}.0{date.month}.{date.year} {date.hour}:{date.minute}'
        if date.minute < 10:
            date.date_for_user = f'{date.day_of_month}.0{date.month}.{date.year} {date.hour}:0{date.minute}'

        convert_date_to_timezone(date, 'UTC', user_timezone)
        date.date_for_user = f'{date.day_of_month}.{date.month}.{date.year} {date.hour}:{date.minute}'
        if date.month < 10:
            date.date_for_user = f'{date.day_of_month}.0{date.month}.{date.year} {date.hour}:{date.minute}'
        if date.minute < 10:
            date.date_for_user = f'{date.day_of_month}.0{date.month}.{date.year} {date.hour}:0{date.minute}'

        convert_date_to_timezone(date, user_timezone, 'UTC')


def convert_date_to_timezone(date, from_timezone, to_timezone):
    tz = pytz.timezone(from_timezone)
    conv_date = tz.localize(datetime(year=date.year, month=date.month, day=date.day_of_month,
                                     hour=date.hour, minute=date.minute))
    converted_date = conv_date.astimezone(pytz.timezone(to_timezone))
    date.year, date.month, date.day_of_month, date.hour, date.minute = converted_date.year, converted_date.month, \
                                                                       converted_date.day, converted_date.hour, \
                                                                       converted_date.minute
    return date


def date_from_sep_date(sep_date):
    date_for_parse = ''
    for element in sep_date:
        date_for_parse += element + '.'
    date_for_parse = date_for_parse.rstrip()
    parsed_date = parse(date_for_parse)
    date = Date(year=parsed_date.year, month=parsed_date.month, day=parsed_date.day,
                hour=parsed_date.hour, minute=parsed_date.minute)
    return date


def parse_period_date(period):
    available_separators = ['_', '/', '\\', '|', ';', ',', '.', '*', '-', '`', '~', ' ', ':']
    for char in period:
        if char in available_separators:
            period = period.replace(char, ',')

    split_date = period.split(',')
    if len(split_date) == 10:
        from_date = datetime(int(split_date[2]), int(split_date[1]), int(split_date[0]), int(split_date[3]),
                             int(split_date[4]))
        to_date = datetime(int(split_date[7]), int(split_date[6]), int(split_date[5]), int(split_date[8]),
                           int(split_date[9]))
        return True, from_date, to_date
    elif len(split_date) == 6:
        from_date = datetime(int(split_date[2]), int(split_date[1]), int(split_date[0]))
        to_date = datetime(int(split_date[5]), int(split_date[4]), int(split_date[3]), hour=23, minute=59)
        return True, from_date, to_date
    elif len(split_date) == 5:
        from_date = datetime(int(split_date[2]), int(split_date[1]), int(split_date[0]), int(split_date[3]),
                             int(split_date[4]))
        to_date = datetime(int(split_date[2]), int(split_date[1]), int(split_date[0]), int(split_date[3]),
                           int(split_date[4]))
        return True, from_date, to_date
    elif len(split_date) == 3:
        from_date = datetime(int(split_date[2]), int(split_date[1]), int(split_date[0]))
        to_date = datetime(int(split_date[2]), int(split_date[1]), int(split_date[0]), hour=23, minute=59)
        return True, from_date, to_date
    else:
        return False, "", ""


def detect_user_timezone(date_or_timezone):
    if date_or_timezone in pytz.all_timezones:
        timezone_detected = True
        return timezone_detected, date_or_timezone
    try:
        timezone_detected, timezone = parse_date_for_detect_timezone(date_or_timezone)
    except Exception as e:
        print("ERROR IN parse_date_for_detect_timezone: ", e)
        return False, ""
    if timezone_detected:
        return timezone_detected, timezone

    return False, ""


def parse_date_for_detect_timezone(date):
    available_separators = ['-', '_', '/', '\\', '|', ';', ':', ',', '.', '*', '~', ' ']
    for char in date:
        if char in available_separators:
            date = date.replace(char, ',')

    split_date = date.split(',')
    hour = split_date[0]
    for timezone in pytz.all_timezones:
        if datetime.now(pytz.timezone(timezone)).hour == int(hour):
            user_timezone = timezone
            timezone_detected = True
            return timezone_detected, user_timezone
    return False, ""


def sort_reminders_and_create_message(reminders_or_notes_queryset, user_timezone):
    dates = {}
    reminders_or_notes = list(reminders_or_notes_queryset)
    # create dict that use date as key
    for reminder_or_note in reminders_or_notes:
        tz = pytz.timezone('UTC')
        reminder_or_note_date = tz.localize(reminder_or_note.date)
        converted_reminder_or_note = reminder_or_note_date.astimezone(pytz.timezone(user_timezone))
        year_month_day_string = f'{converted_reminder_or_note.day}.{converted_reminder_or_note.month}' \
                                f'.{converted_reminder_or_note.year} '
        if converted_reminder_or_note.month < 10:
            year_month_day_string = f'{converted_reminder_or_note.day}.0{converted_reminder_or_note.month}' \
                                    f'.{converted_reminder_or_note.year} '
        if year_month_day_string in dates:
            dates[year_month_day_string].append(reminder_or_note)
        else:
            dates[year_month_day_string] = [reminder_or_note]
    all_notes_or_reminders = ''
    all_messages = [all_notes_or_reminders]
    i = 0
    for date_string, date in dates.items():
        all_messages.append('')
        i += 1
        all_messages[i] += f'\n=========\n{date_string}\n—————\n\n'
        for reminder_or_note in dates[date_string]:
            if type(all_messages[i]) == dict and reminder_or_note.body_type not in ['document', 'video', 'photo']:
                all_messages.append('')
                i += 1
            note_or_reminder = f'{reminder_or_note.date_for_user} ID: {reminder_or_note.id}\n{reminder_or_note.text}\n\n\n'
            if reminder_or_note.body_type in ['document', 'video', 'photo']:
                reminder_or_note_with_specific_type = {"type": reminder_or_note.body_type, "id": reminder_or_note.id}
                all_messages.append({})
                i += 1
                all_messages[i] = reminder_or_note_with_specific_type
                continue
            if len(all_messages[i] + note_or_reminder) < 4096:
                all_messages[i] += note_or_reminder
            else:
                all_messages.append('')
                i += 1
                all_messages[i] += note_or_reminder

    return all_messages
