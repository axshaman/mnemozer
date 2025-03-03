import datetime
import os

import pytz
from telebot import types

from . import dbworker
from . import config
from .date_parser import parse_date, sort_reminders_and_create_message
from .tasks import delete_buttons
from .date_parser import parse_period_date, detect_user_timezone
from .flow_statuses import reminder_description_status, reminder_date_status, \
    reminder_delete_status, note_delete_status, choose_language_status, choose_timezone_status, \
    reminder_or_note_period_status, reminder_or_note_edit_status, new_note_or_reminder_text_status, \
    get_editable_object_in_reminder, get_new_date_for_reminder, get_reminder_date_status, other_functions, \
    new_reminder, \
    edit_note_flow, delete_note_flow, delete_reminder_flow, show_reminders_or_notes, user_notes, user_reminders, \
    change_user_timezone, help_message, reminders_or_notes_for_period, available_date_formats, start, \
    cancel_operation, \
    show_more_reminders_or_notes, settings, change_delay, get_new_delay_time, enable_cleaning_mode, \
    disable_cleaning_mode, create_more_reminders_status
from .init import bot

from .jobs import scheduler, create_job
from .utils import set_keyboard, save_bot_message_id, detect_message_type_and_send_message
from .user import UserInBot

scheduler.start()
messages_for_user = {"English": {
    'cleaning enabled': 'Message cleaning enabled',
    'cleaning disabled': 'Message cleaning disabled',
    'Timezone edited': 'Timezone successfully edited',
    'delay time edited': 'Delay time successfully edited',
    'Start message after registration': f'Secretary "Captain Bot" for you',
    'Error in timezone': 'Error in timezone or time',
    'Enter timezone': 'For right setting your time zone, please write your current time in 24 format. '
                      'For example 23:18 or just 23. Or enter it manually in format "Europe/Moscow". '
                      'Later you can change this in settings of bot.',
    'Enter delay time': 'Setting waiting time after writing messages for set up reminders',
    'Wrong delay time': 'Delay time must be a number from 1 to 60',
    'Crontab date for user': 'every {}\'s day of week',
    'First message after registration': 'Congratulation! Your starting settings are finished.'
                                        ' You can enjoy yours personal assistant Mnemozer.',
    'Second message after registration': 'Any writing here text or sending here images/files or video(20MB) I '
                                         'understand as notes for current date and time. '
                                         'I making reminders from your note if you in 10 sec after'
                                         ' writing note also write date or time or dayofweek:'
                                         '1) date in next format DD.MM.YYYY, for example ""11.01.2021"";'
                                         '2) date with time in next format DD.MM.YYYY HH:MM, '
                                         'for example ""11.01.2021 12:35"";'
                                         '3) day of week, for example ""mon"" or ""monday"";'
                                         '4) day of week with time, for example ""mon 12:35"" or ""monday 12:35"";'
                                         '5) time in 24 hours format, for example ""12:35"".'
                                         'I those cases I set up reminders for:'
                                         '1) just for date;'
                                         '2) date and time;'
                                         '3) everyday in this day of week;'
                                         '4) everyday in this day of week in setting time;'
                                         '5) everyday in setting time."',
    'Third message after registration': 'Format of date and time in our system just one: 25.12.1985 21:15.'
                                        ' This made just for comfort and avoid confusion. '
                                        'Format of writing day of week - "mon" or "monday".',
    'Error in date message': 'Please, enter date in correct format',
    'Delete note': 'Enter id of notes that you want to delete',
    'Edit note': 'Enter note id for edit',
    'Enter edited note text': 'Enter new text for note',
    'Enter edited reminder text': 'Enter new text for reminder',
    'Edit reminder': 'Enter reminder id for edit',
    'Choose editable object': 'What you want to edit?',
    'Delete reminder': 'Enter id of reminders that you want to delete',
    'Show notes and reminders buttons': [['/all', '/for_period-date']],
    'Error in note ID': 'no notes with next id: \n{}',
    'Error in reminder ID': 'no reminders with next id: \n{}',
    'Reminder successfully create': 'reminder successfully created',
    'Note successfully create': 'note successfully created',
    'Successfully reminder delete': 'reminder successfully deleted',
    'Successfully note delete': 'note successfully deleted',
    'Create note': 'Print your note description',
    'cancel button': 'cancel',
    'Enter reminder date': 'Enter reminder date',
    'Help message': "Hi!\nIf you want to create new note or reminder"
                    "just enter \"/new_note\" command or "
                    "click to button below. After entering text, "
                    "you can enter date and reminder will be create for this date with note text\n"
                    "\nAvailable date formats:"
                    "\n**YYYY:MM:DD:HH:Min:Min** or \n**HH:Min:Min YYYY:MM:DD - executes one time in select date\n"
                    "**HH:MinMin** - Executes one time in first available time\n"
                    "**HH:MinMin:DayOfWeek** - Will be execute every selected day of week"
                    "**YYYY:MM:DD** - By default will be execute in 12:00 in select day"
    "\n  При вводе даты для получения напоминаний за период:\n"
    "    YYYY:MM:DD [HH:MinMin] - DD.MM.YYYY [HH:MinMin] - all notes for period\n"
    "    YYYY:MM:DD [HH:MinMin] - all notes for day or concrete date and time(if hours and minutes entered)",
    'Available date formats': "\nAvailable date formats:"
                              "\n**YYYY:MM:DD:HH:Min:Min** or \n**HH:Min:Min YYYY:MM:DD - executes one time in select "
                              "date\n "
                              "**HH:MinMin** - Executes one time in first available time\n"
                              "**HH:MinMin:DayOfWeek** - Will be execute every selected day of week"
                              "**YYYY:MM:DD** - By default will be execute in 12:00 in select day"
                              "\n  При вводе даты для получения напоминаний за период:\n"
                              "    YYYY:MM:DD [HH:MinMin] - DD.MM.YYYY [HH:MinMin] - all notes for period\n"
                              "    YYYY:MM:DD [HH:MinMin] - "
                              "all notes for day or concrete date and time(if hours and minutes entered)",
    'Reminders not found': "You haven't reminders yet",
    'Notes not found': "You haven't notes yet",
    'Reminders list': 'reminder text: {}\nreminder date: {}\nreminder ID: {}',
    'Notes list': '{}\n{}\n ID: {}',
    'Reminders period': "Enter period for reminders in format:\n"
                        "DD.MM.YYYY HH:MM",
    'Notes period': "Enter period for notes in format:\n"
                    "DD.MM.YYYY [HH:MM] DD.MM.YYYY",
    'Notes date': 'Enter day for see notes for it in format:\n'
                  'DD.MM.YYYY [HH:MM]',
    'Reminders date': 'Enter day for see reminders for it in format:\n'
                      'DD.MM.YYYY [HH:MM]',
    'Incorrect type of note': "Please, send file, photo or text",
    'Choose actions after description': "You have {} seconds ⏲ for enter continue for note or create reminder from it",
    'other message': "Other functionality",
    'settings message': 'Settings',
    'show notes text': 'Choose, what notes you want to see',
    'show reminders text': 'Choose, what reminders you want to see',
    'Successfully edited': 'Successfully edited',
    'disposable reminders': 'Disposable reminders',
    'period reminders': 'Period reminders',
    'canceled': 'canceled',
    'main menu': 'main menu',
    'more notes or reminders': 'press button to get more',
    'last note or reminder': 'this is last'

}, "Russian": {
    'cleaning enabled': 'Автоочистка сообщений бота включена',
    'cleaning disabled': 'Автоочистка сообщений бота выключена',
    'Start message after registration': 'Секретарь "Captain Bot" для Вас',
    'Error in timezone': 'Часовой пояс или время введены неверно',
    'delay time edited': 'Время задержки изменено',
    'Timezone edited': 'Часовой пояс успешно изменён',
    'Enter timezone': 'Для установки правильного часового пояса укажите Ваше текущее время в формате 24 часов, '
                      'например 23:18 или укажите свой часовой пояс сами в формате "Europe/Moscow". '
                      'Потом его можно будет изменить в настройках.',
    'Enter delay time': 'Задать от 0 до 60 время задержки для ввода даты-времени'
                        ' и определения заметки, как напоминания.',
    'Wrong delay time': 'Время задержки должно быть числом от 1 до 60',
    'Crontab date for user': 'каждый {} день недели в {}:{}',
    'First message after registration': 'Поздравляю, настройка завершена!',
    'Second message after registration': 'Любой вводимый текст 📝 или отправленное фото/файл или видео(до 20 мб)'
                                         ' 🌆 воспринимается мной 🤖,'
                                         ' как заметка за дату 📅 и время 🕛, в которое она введена.'
                                         'Если Вы введете в течение 10 секунд дату или день недели'
                                         ' (можно с указанием времени), то заметка превратится в напоминание'
                                         ' или будет внесена, как старая заметка, если дата уже прошла.'
                                         'Если Вы введете просто время в формате, например 23:15, '
                                         'то напоминание будет установлено на каждый следующий день в заданное время.',
    'Third message after registration': 'Формат ввода даты и времени у нас только один: 25.12.1985 21:15. Это сделано,'
                                        ' чтобы не путаться 🙏. '
                                        'Формат ввода дня недели: ПН (сокращенный) или четверг (полный).',
    'Error in date message': 'Пожалуйста, введите дату в корректной форме',
    'Delete note': 'Введите id заметки, которую вы хотите удалить',

    'Edit note': 'Введите id заметки для редактирования',
    'Enter edited note text': 'Введите новый текст заметки',
    'Enter edited reminder text': 'Введите новый тест напоминания',
    'Edit reminder': 'Введите id напоминания для редактирования',
    'Choose editable object': 'Что вы хотите изменить?',
    'Notes period': "Введите период для заметок в формате:\n"
                    "ДД.ММ.ГГГГ ЧЧ:ММ ДД.ММ.ГГГГ [HH:MM]",
    'Delete reminder': 'Введите id напоминания, которое вы хотите удалить',
    'Error in note ID': 'Заметок с таким id не найдено: \n{}',
    'Error in reminder ID': 'Напоминаний с таким id не найдено: \n{}',
    'Reminder successfully create': 'Напоминание успешно создано',
    'Note successfully create': 'Заметка успешно создана',
    'Successfully reminder delete': 'Напоминание успешно удалено',
    'Successfully note delete': 'Заметка успешно удалена',
    'Create note': 'Введите описание заметки',
    'cancel button': 'отмена',
    'Enter reminder date': 'Введите дату напоминания',
    'Help message': "Привет!\nЕсли Вы хотите создать новую заметку или напоминание"
                    "просто введите команду \"/new_note\" или "
                    "нажмите на кнопку ниже. После ввода текста, Вы можете ввести дату, "
                    "для которой будет создано напоминание с текстом заметки\n"
                    "\nДоступные форматы даты:"
                    "\n  При создании напоминания:"
                    "\n    **ГГГГ:ММ:ДД:ЧЧ:Мин:Мин** или \n**ЧЧ:Мин:Мин ГГГГ:ММ:ДД - "
                    "выполняется один раз в указанное время\n"
                    "    **ЧЧ:МинМин** - Выполняется один раз в первое подходящее время\n"
                    "    **ЧЧ:МинМин:ДеньНедели** - будет исполняться каждый указанный день недели в указанное время"
                    "    **ГГГГ:ММ:ДД** - по-умолчанию будет выполнено в 12:00 в указанный день\n"
                    "\n  При вводе даты для получения напоминаний за период:\n"
                    "    ДД.ММ.ГГГГ [ЧЧ:МинМин] - ДД.ММ.ГГГГ [ЧЧ:МинМин] - "
                    "будут выведены все напоминания в заданном промежутке\n"
                    "    ДД.ММ.ГГГГ [ЧЧ:МинМин] - "
                    "будут выведены напоминания за день или за точное время(при указании часов и минут)",
    'Reminders not found': "У Вас пока нет напоминаний",
    'Available date formats': "\nДоступные форматы даты:"
                              "\n  При создании напоминания:"
                              "\n    **ГГГГ:ММ:ДД:ЧЧ:Мин:Мин** или \n**ЧЧ:Мин:Мин ГГГГ:ММ:ДД - "
                              "выполняется один раз в указанное время\n"
                              "    **ЧЧ:МинМин** - Выполняется один раз в первое подходящее время\n"
                              "**ЧЧ:МинМин:ДеньНедели** - будет исполняться каждый указанный день недели в указанное "
                              "время "
                              "    **ГГГГ:ММ:ДД** - по-умолчанию будет выполнено в 12:00 в указанный день\n"
                              "\n  При вводе даты для получения напоминаний за период:\n"
                              "    ДД.ММ.ГГГГ [ЧЧ:МинМин] - ДД.ММ.ГГГГ [ЧЧ:МинМин] - "
                              "будут выведены все напоминания в заданном промежутке\n"
                              "    ДД.ММ.ГГГГ [ЧЧ:МинМин] - "
                              "будут выведены напоминания за день или за точное время(при указании часов и минут)",
    'Notes not found': "У Вас пока нет заметок",
    'Reminders list': 'Текст напоминания: {}\nДата напоминания: {}\nID напоминания: {}',
    'Notes list': '{}\n{}\nID заметки: {}',
    'Reminders period': "Введите период или дату для поиска заметок",
    'Notes date': 'Введите дату, чтобы посмотреть заметки за эту дату:\n'
                  'DD.MM.YYYY [HH:MM]',
    'Reminders date': 'Введите день, чтобы посмотреть напоминания за эту дату:\n'
                      'DD.MM.YYYY [HH:MM]',
    'Incorrect type of note': "Пожалуйста, отправьте файл, фото или текст",
    'Choose actions after description': "У вас {} сек ⏲ для ввода продолжения заметки или создания из нее напоминания.",
    'other message': "Дополнительные функции",
    'settings message': 'Настройки',
    'show notes text': 'Выберите какие заметки вы хотите видеть',
    'show reminders text': 'Выберите, какие напоминания вы хотите видеть',
    'disposable reminders': 'Одноразовые напоминания',
    'period reminders': 'Периодичные напоминания',
    'Successfully edited': 'Успешно отредактировано',
    'canceled': 'Отмена',
    'main menu': 'главное меню',
    'more notes or reminders': 'нажмите на кнопку, чтобы получить больше записей',
    'last note or reminder': 'записей больше нет'

}}


@bot.message_handler(func=cancel_operation)
def cancel_operation(message):
    try:
        save_bot_message_id(message.chat.id, message.id)
        user = UserInBot(message.chat.id)
        if not user.check_registration():
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            markup.add(types.KeyboardButton('start'))
            message_info = bot.send_message(message.chat.id,
                                            "Please, complete registration\nПожалуйста пройдите регистрацию",
                                            reply_markup=markup)
            save_bot_message_id(message.chat.id, message_info.message_id)
            return
        user.delete_celery_task()
        user.language = user.get_user_language()
        markup = set_keyboard(user.language, 'default keyboard')
        if message.text in ['/cancel', '/отмена', 'cancel', 'отмена']:
            message_info = bot.send_message(message.chat.id,
                                            messages_for_user[user.language]['canceled'],
                                            reply_markup=markup)
            save_bot_message_id(message.chat.id, message_info.message_id)
            dbworker.set_state(message.chat.id, config.States.S_REMINDER_DESC.value)
        else:
            message_info = bot.send_message(message.chat.id,
                                            messages_for_user[user.language]['main menu'],
                                            reply_markup=markup)
            save_bot_message_id(message.chat.id, message_info.message_id)
            dbworker.set_state(message.chat.id, config.States.S_REMINDER_DESC.value)
    except Exception as e:
        print("ERROR IN cancel_operation: ", e)


@bot.message_handler(func=available_date_formats)
def available_date_formats(message):
    save_bot_message_id(message.chat.id, message.id)
    try:
        user = UserInBot(user_id=message.chat.id)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('start'))
        if not user.check_registration():
            message_info = bot.send_message(message.chat.id,
                                            "Please, complete registration\nПожалуйста пройдите регистрацию",
                                            reply_markup=markup)
            save_bot_message_id(message.chat.id, message_info.message_id)
            return
        user.language = user.get_user_language()
        message_info = bot.send_message(user.user_id, messages_for_user[user.language]['Available date formats'])
        save_bot_message_id(message.chat.id, message_info.message_id)
    except Exception as e:
        print("ERROR: ", e)


@bot.message_handler(func=start)
def start(message):
    try:
        save_bot_message_id(message.chat.id, message.id)
        user = UserInBot(user_id=message.chat.id)
        user_registered = user.check_registration()
        try:
            user.language = user.get_user_language()
        except Exception as e:
            print("ERROR IN get_user_language: ", e)
            user.language = None
        if user_registered:
            user.language = user.get_user_language()
            markup = set_keyboard(user.language, 'default keyboard')
            message_info = bot.send_message(chat_id=message.chat.id,
                                            text=messages_for_user[user.language]["Start message after registration"],
                                            reply_markup=markup,
                                            )
            save_bot_message_id(message.chat.id, message_info.message_id)

            dbworker.set_state(message.chat.id, config.States.S_START.value)
            return
        elif not user_registered and user.language is None:
            message_english = 'Hello! You starting to use bot who will be your personal assistant 🙍‍♂️.' \
                              ' Name this bot - Mnemozer.' \
                              ' We hope that u will be great experience and good impressions from our service.' \
                              ' More information and web-service of our system you can see here - www.mnemozer.com.' \
                              ' There are also u can using more additional function of Mnemozer.' \
                              ' Also very soon you will be able to download our mobile applications.'
            message_russian = "Здравствуйте! Вы начали использование бота" \
                              " - личного помощника 🙍‍♂️: Mnemozer." \
                              " Надеемся, Вам понравится наш сервис." \
                              " Подробности на сайте www.mnemozer.com, там же Вы " \
                              "найдете веб-сервис с расширенными функциями. Совсем скоро Вы можете скачать " \
                              "наши мобильные приложения в Google Playmarket и Apple AppStore.																						"
            message_info = bot.send_message(chat_id=message.chat.id, text=message_english)
            save_bot_message_id(message.chat.id, message_info.message_id)
            message_info = bot.send_message(chat_id=message.chat.id, text=message_russian)
            save_bot_message_id(message.chat.id, message_info.message_id)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add(types.KeyboardButton('English 🇺🇸 🇬🇧 🇪🇺 🇺🇳 🌎'))
            markup.add(types.KeyboardButton('Русский 🇷🇺 🇺🇦 🇰🇿'))
            message_info = bot.send_message(chat_id=message.chat.id,
                                            text="Please, choose language. Пожалуйста, выберите Ваш язык.",
                                            reply_markup=markup)
            save_bot_message_id(message.chat.id, message_info.message_id)
            dbworker.set_state(message.chat.id, config.States.S_CHOOSE_LANGUAGE.value)
            dbworker.set_state(message.chat.id, config.States.S_CHOOSE_LANGUAGE.value)
        elif not user_registered and user.language is not None:
            message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['Enter timezone'])
            save_bot_message_id(message.chat.id, message_info.message_id)
            dbworker.set_state(message.chat.id, config.States.S_GET_TIMEZONE.value)
    except Exception as e:
        print("ERROR: ", e)


@bot.message_handler(func=choose_language_status)
def get_language_for_register_user(message):
    available_russian_languages = ['Русский', 'Russian', 'Русский 🇷🇺 🇺🇦 🇰🇿']
    available_english_languages = ['Английский', 'English', 'English 🇺🇸 🇬🇧 🇪🇺 🇺🇳 🌎']
    if message.text not in available_russian_languages and message.text not in available_english_languages:
        message_info = bot.send_message(message.chat.id,
                                        'Please, choose the correct language\nПожалуйста, выберите один из'
                                        'доступных языков')
        save_bot_message_id(message.chat.id, message_info.message_id)

        return

    user = UserInBot(message.chat.id)
    language = message.text
    if message.text in available_russian_languages:
        language = "Russian"
    elif message.text in available_english_languages:
        language = "English"
    try:
        user.register_user(language)
    except Exception as e:
        print("ERROR: ", e)
    user.language = user.get_user_language()
    message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['Enter timezone'])
    save_bot_message_id(message.chat.id, message_info.message_id)
    dbworker.set_state(message.chat.id, config.States.S_GET_TIMEZONE.value)


@bot.message_handler(func=choose_timezone_status)
def get_user_timezone(message):
    try:
        user = UserInBot(message.chat.id)
        user.language = user.get_user_language()
        registered = user.check_registration()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('start'))
        if not registered and user.language is None:
            message_info = bot.send_message(message.chat.id,
                                            "Please, complete registration\nПожалуйста пройдите регистрацию",
                                            reply_markup=markup)
            save_bot_message_id(message.chat.id, message_info.message_id)
            return
        user.language = user.get_user_language()

        timezone_detected, timezone = detect_user_timezone(message.text)
        if not timezone_detected:
            message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['Error in timezone'])
            save_bot_message_id(message.chat.id, message_info.message_id)
            return
        else:
            user.save_user_timezone(timezone)
            user.update_registered_status()
            markup = set_keyboard(user.language, 'default keyboard')
            if registered:
                message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['Timezone edited'],
                                                reply_markup=markup)
                save_bot_message_id(message.chat.id, message_info.message_id)
                dbworker.set_state(message.chat.id, config.States.S_START.value)
                return

            message_info = bot.send_message(chat_id=message.chat.id,
                                            text=messages_for_user[user.language]["First message after registration"],
                                            reply_markup=markup)
            save_bot_message_id(message.chat.id, message_info.message_id)
            message_info = bot.send_message(chat_id=message.chat.id,
                                            text=messages_for_user[user.language]["Second message after registration"])
            save_bot_message_id(message.chat.id, message_info.message_id)

            message_info = bot.send_message(chat_id=message.chat.id,
                                            text=messages_for_user[user.language]["Third message after registration"])
            save_bot_message_id(message.chat.id, message_info.message_id)

            dbworker.set_state(message.chat.id, config.States.S_START.value)
    except Exception as e:
        print("ERROR: ", e)


@bot.message_handler(func=reminders_or_notes_for_period)
def reminders_or_notes_for_period(message):
    save_bot_message_id(message.chat.id, message.id)
    try:
        user = UserInBot(user_id=message.chat.id)
        if not user.check_registration():
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton('register'))
            markup.add(types.KeyboardButton('зарегистрироваться'))
            message_info = bot.send_message(message.chat.id,
                                            "Please, complete registration\nПожалуйста, пройдите регистрацию",
                                            reply_markup=markup)
            save_bot_message_id(message.chat.id, message_info.message_id)
            return
        user.language = user.get_user_language()
        markup = set_keyboard(user.language, 'Available formats button')
        if message.text in ['/reminders_for_period', '/напоминания_за_период', 'reminders for period',
                            'напоминания на период']:
            reminders = user.all_reminders(check_availability=True)
            if not reminders:
                message_info = bot.send_message(message.chat.id,
                                                messages_for_user[user.language]['Reminders not found'])
                save_bot_message_id(message.chat.id, message_info.message_id)
                dbworker.set_state(message.chat.id, config.States.S_REMINDER_DESC.value)
                return
            message_info = bot.send_message(message.chat.id, messages_for_user[user.language]["Reminders period"],
                                            reply_markup=markup
                                            )
            save_bot_message_id(message.chat.id, message_info.message_id)

            dbworker.set_state(message.chat.id, config.States.S_REMINDER_PERIOD.value)
            return
        elif message.text in ['/notes_for_period', '/заметки_на_период',
                              'notes for period', 'заметки на период']:

            notes = user.all_notes(check_availability=True)
            if not notes:
                message_info = bot.send_message(message.chat.id,
                                                messages_for_user[user.language]['Notes not found'])
                save_bot_message_id(message.chat.id, message_info.message_id)
                dbworker.set_state(message.chat.id, config.States.S_REMINDER_DESC.value)
                return
            message_info = bot.send_message(message.chat.id, messages_for_user[user.language]["Notes period"],
                                            reply_markup=markup)
            save_bot_message_id(message.chat.id, message_info.message_id)
            dbworker.set_state(message.chat.id, config.States.S_NOTE_PERIOD.value)
            return

        elif message.text in ['/reminders_for_date', 'reminders for date', '/напоминания_на_дату',
                              'напоминания на дату']:
            reminders = user.all_reminders(check_availability=True)
            if not reminders:
                message_info = bot.send_message(message.chat.id,
                                                messages_for_user[user.language]['Reminders not found'])
                save_bot_message_id(message.chat.id, message_info.message_id)
                dbworker.set_state(message.chat.id, config.States.S_REMINDER_DESC.value)
                return
            message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['Reminders date'])
            save_bot_message_id(message.chat.id, message_info.message_id)

            dbworker.set_state(message.chat.id, config.States.S_REMINDER_PERIOD.value)
            return

        elif message.text in ['/notes_for_date', 'notes for date', '/заметки_на_дату', 'заметки на дату']:
            notes = user.all_notes(check_availability=True)
            if not notes:
                message_info = bot.send_message(message.chat.id,
                                                messages_for_user[user.language]['Notes not found'])
                save_bot_message_id(message.chat.id, message_info.message_id)
                dbworker.set_state(message.chat.id, config.States.S_REMINDER_DESC.value)
                return
            message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['Notes date'])
            save_bot_message_id(message.chat.id, message_info.message_id)

            dbworker.set_state(message.chat.id, config.States.S_NOTE_PERIOD.value)
            return
    except Exception as e:
        print("ERROR: ", e)


@bot.message_handler(func=reminder_or_note_period_status)
def reminders_or_notes_for_period_list(message):
    user = UserInBot(message.chat.id)
    date = message.text
    user.language = user.get_user_language()
    user.timezone = user.get_user_timezone()
    correct, from_date, to_date = parse_period_date(date)
    if not correct:
        message_info = bot.send_message(message.chat.id, messages_for_user[user.language]["Error in date message"])
        save_bot_message_id(message.chat.id, message_info.message_id)

        return
    tz = pytz.timezone(user.timezone)
    from_date_in_utc = tz.localize(from_date).astimezone(pytz.timezone('UTC'))
    to_date_in_utc = tz.localize(to_date).astimezone(pytz.timezone('UTC'))
    to_date_in_utc = datetime.datetime(to_date_in_utc.year, to_date_in_utc.month, to_date_in_utc.day, to_date.hour,
                                       to_date.minute)

    try:
        if dbworker.get_current_state(message.chat.id) == "4":
            reminders = user.reminders_for_period(from_date_in_utc, to_date_in_utc)
            if len(reminders) == 0:
                message_info = bot.send_message(message.chat.id,
                                                messages_for_user[user.language]["Reminders not found"])
                save_bot_message_id(message.chat.id, message_info.message_id)

                return
            all_messages = sort_reminders_and_create_message(reminders, user.timezone)
            detect_message_type_and_send_message(user.user_id, all_messages, send_reminder=True)

            dbworker.set_state(message.chat.id, config.States.S_REMINDER_DESC.value)

        elif dbworker.get_current_state(message.chat.id) == "10":
            notes = user.notes_for_period(from_date_in_utc, to_date_in_utc)
            if len(notes) == 0:
                message_info = bot.send_message(message.chat.id, messages_for_user[user.language]["Notes not found"])
                save_bot_message_id(message.chat.id, message_info.message_id)

            all_messages = sort_reminders_and_create_message(notes, user.timezone)
            detect_message_type_and_send_message(user.user_id, all_messages, send_note=True)

            dbworker.set_state(message.chat.id, config.States.S_REMINDER_DESC.value)

    except Exception as e:
        print("ERROR IN reminders_for_period_list: ", e)
        message_info = bot.send_message(message.chat.id, messages_for_user[user.language]["Error in date message"])
        save_bot_message_id(message.chat.id, message_info.message_id)


@bot.message_handler(func=help_message)
def help_message(message):
    save_bot_message_id(message.chat.id, message.id)
    user = UserInBot(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('start'))
    if not user.check_registration():
        message_info = bot.send_message(message.chat.id,
                                        "Please, complete registration\nПожалуйста пройдите регистрацию",
                                        reply_markup=markup)
        save_bot_message_id(message.chat.id, message_info.message_id)
        return
    user.language = user.get_user_language()

    message_info = bot.send_message(message.chat.id, messages_for_user[user.language]["Help message"])
    save_bot_message_id(message.chat.id, message_info.message_id)


@bot.message_handler(func=other_functions)
def other_functions(message):
    save_bot_message_id(message.chat.id, message.id)
    user = UserInBot(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('start'))
    if not user.check_registration():
        message_info = bot.send_message(message.chat.id,
                                        "Please, complete registration\nПожалуйста пройдите регистрацию",
                                        reply_markup=markup)
        save_bot_message_id(message.chat.id, message_info.message_id)
        return
    user.language = user.get_user_language()
    markup = set_keyboard(user.language, 'other keyboard')
    message_info = bot.send_message(user.user_id, text=messages_for_user[user.language]['other message'],
                                    reply_markup=markup)
    save_bot_message_id(message.chat.id, message_info.message_id)


@bot.message_handler(func=settings)
def settings(message):
    save_bot_message_id(message.chat.id, message.id)
    user = UserInBot(message.chat.id)
    user.language = user.get_user_language()
    markup = set_keyboard(user.language, 'settings keyboard')
    message_info = bot.send_message(user.user_id, text=messages_for_user[user.language]['settings message'],
                                    reply_markup=markup)
    save_bot_message_id(message.chat.id, message_info.message_id)


@bot.message_handler(func=enable_cleaning_mode)
def enable_cleaning_mode(message):
    save_bot_message_id(message.chat.id, message.id)
    user = UserInBot(message.chat.id)
    user.update_cleaning_mode_status(enable=True)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('start'))
    if not user.check_registration():
        message_info = bot.send_message(message.chat.id,
                                        "Please, complete registration\nПожалуйста пройдите регистрацию",
                                        reply_markup=markup)
        save_bot_message_id(message.chat.id, message_info.message_id)
        return
    user.language = user.get_user_language()
    message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['cleaning enabled'])
    save_bot_message_id(message.chat.id, message_info.message_id)


@bot.message_handler(func=disable_cleaning_mode)
def disable_cleaning_mode(message):
    save_bot_message_id(message.chat.id, message.id)
    user = UserInBot(message.chat.id)
    user.update_cleaning_mode_status(disable=True)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('start'))
    if not user.check_registration():
        message_info = bot.send_message(message.chat.id,
                                        "Please, complete registration\nПожалуйста пройдите регистрацию",
                                        reply_markup=markup)
        save_bot_message_id(message.chat.id, message_info.message_id)
        return
    user.language = user.get_user_language()
    message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['cleaning disabled'])
    save_bot_message_id(message.chat.id, message_info.message_id)


@bot.message_handler(func=change_delay)
def change_delay(message):
    save_bot_message_id(message.chat.id, message.id)
    user = UserInBot(message.chat.id)
    user.language = user.get_user_language()
    message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['Enter delay time'])
    save_bot_message_id(message.chat.id, message_info.message_id)

    dbworker.set_state(message.chat.id, config.States.S_GET_NEW_DELAY_TIME.value)


@bot.message_handler(func=get_new_delay_time)
def set_new_delay_time(message):
    save_bot_message_id(message.chat.id, message.id)
    user = UserInBot(message.chat.id)
    user.language = user.get_user_language()
    new_delay_time = message.text
    if not new_delay_time.isdigit():
        message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['Wrong delay time'])
        save_bot_message_id(message.chat.id, message_info.message_id)

        return
    if int(new_delay_time) <= 0 or int(new_delay_time) > 60:
        message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['Wrong delay time'])
        save_bot_message_id(message.chat.id, message_info.message_id)

        return
    markup = set_keyboard(user.language, 'default keyboard')
    user.update_delay_time(new_delay_time)
    message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['delay time edited'],
                                    reply_markup=markup)
    save_bot_message_id(message.chat.id, message_info.message_id)
    dbworker.set_state(message.chat.id, config.States.S_REMINDER_DESC.value)


@bot.message_handler(func=change_user_timezone)
def change_user_timezone(message):
    save_bot_message_id(message.chat.id, message.id)
    user = UserInBot(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('start'))
    if not user.check_registration():
        message_info = bot.send_message(message.chat.id,
                                        "Please, complete registration\nПожалуйста пройдите регистрацию",
                                        reply_markup=markup)
        save_bot_message_id(message.chat.id, message_info.message_id)
        return
    user.delete_celery_task()
    user.language = user.get_user_language()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(messages_for_user[user.language]['cancel button']))
    message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['Enter timezone'],
                                    reply_markup=markup)
    save_bot_message_id(message.chat.id, message_info.message_id)
    dbworker.set_state(message.chat.id, config.States.S_GET_TIMEZONE.value)


@bot.message_handler(func=user_reminders)
def user_reminders(message):
    save_bot_message_id(message.chat.id, message.id)
    try:
        user = UserInBot(message.chat.id)
        user.update_from_and_to_notes_or_reminders(reminder=True)
        user.language = user.get_user_language()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('start'))
        if not user.check_registration():
            message_info = bot.send_message(message.chat.id,
                                            "Please, complete registration\nПожалуйста пройдите регистрацию",
                                            reply_markup=markup)
            save_bot_message_id(message.chat.id, message_info.message_id)
            return
        try:
            date_reminders = user.all_reminders(check_availability=True, reminder_type='date')
            cron_reminders = user.all_reminders(check_availability=True, reminder_type='cron')
            markup = set_keyboard(user.language, 'show reminders button')
            if len(date_reminders) == 0 and len(cron_reminders) == 0:
                message_info = bot.send_message(message.chat.id,
                                                messages_for_user[user.language]['Reminders not found'])
                save_bot_message_id(message.chat.id, message_info.message_id)

                return
        except Exception as e:
            print("Error in user_reminders:", e)

        message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['show reminders text'],
                                        reply_markup=markup)
        save_bot_message_id(message.chat.id, message_info.message_id)
    except Exception as e:
        print("ERROR: ", e)


@bot.message_handler(func=user_notes)
def user_notes(message):
    save_bot_message_id(message.chat.id, message.id)
    user = UserInBot(message.chat.id)
    try:
        user.update_from_and_to_notes_or_reminders(note=True)
    except Exception as e:
        print("ERROR: ", e)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('start'))
    if not user.check_registration():
        message_info = bot.send_message(message.chat.id,
                                        "Please, complete registration\nПожалуйста пройдите регистрацию",
                                        reply_markup=markup)
        save_bot_message_id(message.chat.id, message_info.message_id)
        return
    notes = user.all_notes(check_availability=True)
    user.language = user.get_user_language()
    markup = set_keyboard(user.language, 'show notes button')
    if len(notes) == 0:
        message_info = bot.send_message(message.chat.id, messages_for_user[user.language]["Notes not found"])
        save_bot_message_id(message.chat.id, message_info.message_id)
        return
    message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['show notes text'],
                                    reply_markup=markup)

    save_bot_message_id(message.chat.id, message_info.message_id)


@bot.message_handler(func=show_reminders_or_notes)
def show_reminders_or_notes(message):
    save_bot_message_id(message.chat.id, message.id)
    user = UserInBot(message.chat.id)
    user.language = user.get_user_language()
    user.timezone = user.get_user_timezone()
    if message.text in ['/all_notes', '/все_заметки', 'all notes', 'все заметки']:
        try:
            notes = user.all_notes()
            if not notes:
                message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['Notes not found'])
                save_bot_message_id(message.chat.id, message_info.message_id)
                return
            try:
                all_messages = sort_reminders_and_create_message(notes, user.timezone)
                detect_message_type_and_send_message(user.user_id, all_messages, send_note=True)

            except Exception as e:
                print("ERROR IN create message: ", e)
            show_more_keyboard = set_keyboard(user.language, 'show more notes')
            message_info = bot.send_message(message.chat.id,
                                            messages_for_user[user.language]['more notes or reminders'],
                                            reply_markup=show_more_keyboard)
            save_bot_message_id(message.chat.id, message_info.message_id)

        except Exception as e:
            print("ERROR: ", e)

    elif message.text in ['/all_reminders', '/все_напоминания', 'all reminders', 'все напоминания']:
        date_reminders = user.all_reminders(reminder_type='date')
        cron_reminders = user.all_reminders(reminder_type='cron')
        user.update_from_and_to_notes_or_reminders(reminder=True, increase_for=4)
        if not date_reminders and not cron_reminders:
            bot.send_message(message.chat.id, messages_for_user[user.language]['Reminders not found'])
            return
        try:
            all_messages = sort_reminders_and_create_message(date_reminders, user.timezone)
            detect_message_type_and_send_message(user.user_id, all_messages, send_reminder=True)

        except Exception as e:
            print("ERROR IN create message: ", e)
        reminders_message = ''
        if len(cron_reminders) > 0:
            for reminder in cron_reminders:
                reminders_message += messages_for_user[user.language]["Reminders list"].format(
                    reminder.date_for_user, reminder.text, reminder.id) + '\n\n'
            message_info = bot.send_message(message.chat.id,
                                            f'{messages_for_user[user.language]["period reminders"]}'
                                            f'\n\n{reminders_message}')
            save_bot_message_id(message.chat.id, message_info.message_id)

        show_more_keyboard = set_keyboard(user.language, 'show more reminders')
        message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['more notes or reminders'],
                                        reply_markup=show_more_keyboard)
        save_bot_message_id(message.chat.id, message_info.message_id)


@bot.message_handler(func=show_more_reminders_or_notes)
def show_more_reminders_or_notes(message):
    save_bot_message_id(message.chat.id, message.id)
    user = UserInBot(message.chat.id)
    user.language = user.get_user_language()
    user.timezone = user.get_user_timezone()
    if message.text in ['/show_more_notes', '/показать_больше_заметок',
                        'show more notes', 'показать больше заметок']:
        notes = user.all_notes()
        if len(notes) == 0:
            message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['last note or reminder'])
            save_bot_message_id(message.chat.id, message_info.message_id)

            return
        try:
            all_messages = sort_reminders_and_create_message(notes, user.timezone)
            detect_message_type_and_send_message(user.user_id, all_messages, send_note=True)
        except Exception as e:
            print("ERROR IN show more reminders: ", e)

    if message.text in ['/show_more_reminders', '/показать_больше_напоминаний',
                        'show more reminders', 'показать больше напоминаний']:
        date_reminders = user.all_reminders(reminder_type='date')
        cron_reminders = user.all_reminders(reminder_type='cron')
        user.update_from_and_to_notes_or_reminders(reminder=True, increase_for=4)
        if len(date_reminders) + len(cron_reminders) == 0:
            message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['last note or reminder'])
            save_bot_message_id(message.chat.id, message_info.message_id)

            return
        try:
            all_messages = sort_reminders_and_create_message(date_reminders, user.timezone)
            detect_message_type_and_send_message(user.user_id, all_messages, send_reminder=True)

        except Exception as e:
            print("ERROR IN create message: ", e)
        reminders_message = ''
        if len(cron_reminders) > 0:
            for reminder in cron_reminders:
                reminders_message += messages_for_user[user.language]["Reminders list"].format(
                    reminder.date_for_user, reminder.text, reminder.id) + '\n\n'
            message_info = bot.send_message(message.chat.id,
                                            f'{messages_for_user[user.language]["period reminders"]}'
                                            f'\n\n{reminders_message}')
            save_bot_message_id(message.chat.id, message_info.message_id)


@bot.message_handler(func=delete_reminder_flow)
def delete_reminder_flow(message):
    save_bot_message_id(message.chat.id, message.id)
    user = UserInBot(message.chat.id)
    user.update_from_and_to_notes_or_reminders(reminder=True)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('start'))
    if not user.check_registration():
        message_info = bot.send_message(message.chat.id,
                                        "Please, complete registration\nПожалуйста пройдите регистрацию",
                                        reply_markup=markup)
        save_bot_message_id(message.chat.id, message_info.message_id)
        return
    user.language = user.get_user_language()
    reminders_exists = user.all_reminders(check_availability=True)
    if not reminders_exists:
        message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['Reminders not found'])
        save_bot_message_id(message.chat.id, message_info.message_id)
        return
    user.delete_celery_task()
    markup = set_keyboard(user.language, 'show reminders button')
    message_info = bot.send_message(message.chat.id, messages_for_user[user.language]["Delete reminder"],
                                    reply_markup=markup)
    save_bot_message_id(message.chat.id, message_info.message_id)
    dbworker.set_state(message.chat.id, config.States.S_REMINDER_DELETE.value)


@bot.message_handler(func=reminder_delete_status)
def get_reminder_id_for_delete(message):
    user = UserInBot(message.chat.id)
    user.language = user.get_user_language()
    markup = set_keyboard(user.language, 'default keyboard')
    reminder_ids_from_user = message.text.strip()
    reminder_ids = reminder_ids_from_user.split(",")
    reminders_not_found = []
    for reminder_id in reminder_ids:
        try:
            reminder = user.get_reminder(reminder_id)
            scheduler.remove_job(reminder.job_id)
            message_info = bot.send_message(message.chat.id,
                                            messages_for_user[user.language]["Successfully reminder delete"],
                                            reply_markup=markup)
            save_bot_message_id(message.chat.id, message_info.message_id)
            user.delete_reminder(reminder_id)
            dbworker.set_state(message.chat.id, config.States.S_REMINDER_DESC.value)
        except Exception as e:
            print("ERROR IN DELETE REMINDER:", e)
            reminders_not_found.append(reminder_id)

    reminders_not_found_string = ""
    if len(reminders_not_found) > 0:
        for not_found_job in reminders_not_found:
            reminders_not_found_string += (not_found_job + "\n")

        message_info = bot.send_message(
            message.chat.id,
            messages_for_user[user.language]['Error in reminder ID'].format(reminders_not_found_string))
        save_bot_message_id(message.chat.id, message_info.message_id)

    dbworker.set_state(message.chat.id, config.States.S_REMINDER_DESC.value)


@bot.message_handler(func=delete_note_flow)
def delete_note_flow(message):
    save_bot_message_id(message.chat.id, message.id)
    user = UserInBot(message.chat.id)
    user.update_from_and_to_notes_or_reminders(note=True)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('start'))
    if not user.check_registration():
        message_info = bot.send_message(message.chat.id,
                                        "Please, complete registration\nПожалуйста пройдите регистрацию",
                                        reply_markup=markup)
        save_bot_message_id(message.chat.id, message_info.message_id)
        return
    user.language = user.get_user_language()
    user.delete_celery_task()
    notes_exists = user.all_notes(check_availability=True)
    if not notes_exists:
        message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['Reminders not found'])
        save_bot_message_id(message.chat.id, message_info.message_id)
        return
    markup = set_keyboard(user.language, 'note buttons')
    message_info = bot.send_message(message.chat.id, messages_for_user[user.language]["Delete note"],
                                    reply_markup=markup)
    save_bot_message_id(message.chat.id, message_info.message_id)
    dbworker.set_state(message.chat.id, config.States.S_NOTE_DELETE.value)


@bot.message_handler(func=note_delete_status)
def get_note_id_for_delete(message):
    user = UserInBot(message.chat.id)
    note_ids = message.text.strip()
    user.language = user.get_user_language()
    markup = set_keyboard(user.language, 'default keyboard')
    notes = note_ids.split(",")
    notes_not_found = []
    for note in notes:
        try:
            user.delete_note(note_id=note)
            dbworker.set_state(message.chat.id, config.States.S_REMINDER_DESC.value)
        except Exception as e:
            print("get_note_id_for_delete ERROR:", e)
            notes_not_found.append(note)
    message_info = bot.send_message(message.chat.id, messages_for_user[user.language]["Successfully note delete"],
                                    reply_markup=markup)
    save_bot_message_id(message.chat.id, message_info.message_id)

    jobs_not_found_string = ""
    if len(notes_not_found) > 0:
        for not_found_job in notes_not_found:
            jobs_not_found_string += (not_found_job + "\n")

        message_info = bot.send_message(message.chat.id,
                                        messages_for_user[user.language]['Error in note ID'].format(
                                            jobs_not_found_string))
        save_bot_message_id(message.chat.id, message_info.message_id)

    dbworker.set_state(message.chat.id, config.States.S_REMINDER_DESC.value)


@bot.message_handler(func=edit_note_flow)
def edit_note_flow(message):
    save_bot_message_id(message.chat.id, message.id)
    user = UserInBot(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('start'))
    if not user.check_registration():
        message_info = bot.send_message(message.chat.id,
                                        "Please, complete registration\nПожалуйста пройдите регистрацию",
                                        reply_markup=markup)
        save_bot_message_id(message.chat.id, message_info.message_id)
        return
    user.delete_celery_task()
    user.language = user.get_user_language()
    if message.text in ['/edit_note', '/редактировать_заметку', 'edit note', 'редактировать заметку']:
        markup = set_keyboard(user.language, 'note buttons')
        message_info = bot.send_message(message.chat.id, messages_for_user[user.language]["Edit note"],
                                        reply_markup=markup)
        save_bot_message_id(message.chat.id, message_info.message_id)
        dbworker.set_state(message.chat.id, config.States.S_NOTE_EDIT.value)
        return
    elif message.text in ['/edit_reminder', '/редактировать_напоминание', 'edit reminder', 'редактировать напоминание']:
        markup = set_keyboard(user.language, 'reminder buttons')
        message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['Edit reminder'],
                                        reply_markup=markup)
        save_bot_message_id(message.chat.id, message_info.message_id)
        dbworker.set_state(message.chat.id, config.States.S_GET_REMINDER_ID.value)


@bot.message_handler(func=reminder_or_note_edit_status)
def get_note_id_for_edit(message):
    user = UserInBot(message.chat.id)
    user.language = user.get_user_language()
    if dbworker.get_current_state(message.chat.id) == "11":
        try:
            note = user.get_note(note_id=int(message.text))
            message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['Enter edited note text'])
            save_bot_message_id(message.chat.id, message_info.message_id)
            user.save_editable_note_or_reminder(note_or_reminder_id=note.id)
            dbworker.set_state(message.chat.id, config.States.S_GET_NEW_NOTE_TEXT.value)
        except Exception as e:
            print("ERROR IN ID FOR EDIT NOTE: ", e)
            message_info = bot.send_message(message.chat.id,
                                            messages_for_user[user.language]['Error in note ID'].format(message.text))
            save_bot_message_id(message.chat.id, message_info.message_id)

    elif dbworker.get_current_state(message.chat.id) == "13":
        try:
            reminder = user.get_reminder(reminder_id=message.text)
            user.save_editable_note_or_reminder(note_or_reminder_id=reminder.id)
            markup = set_keyboard(user.language, 'Edit reminder button')
            message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['Choose editable object'],
                                            reply_markup=markup)
            save_bot_message_id(message.chat.id, message_info.message_id)
            dbworker.set_state(message.chat.id, config.States.S_GET_EDITABLE_REMINDER_OBJECT.value)

        except Exception as e:
            print("ERROR IN ID FOR EDIT REMINDER: ", e)
            message_info = bot.send_message(message.chat.id,
                                            messages_for_user[user.language]['Error in reminder ID'].format(
                                                message.text))
            save_bot_message_id(message.chat.id, message_info.message_id)


@bot.message_handler(func=new_note_or_reminder_text_status)
def get_new_note_or_reminder_text(message):
    user = UserInBot(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('start'))
    if not user.check_registration():
        message_info = bot.send_message(message.chat.id,
                                        "Please, complete registration\nПожалуйста пройдите регистрацию",
                                        reply_markup=markup)
        save_bot_message_id(message.chat.id, message_info.message_id)
        return
    user.language = user.get_user_language()
    editable_object_id = user.editable_object_id()
    if dbworker.get_current_state(message.chat.id) == "12":
        user.update_note(editable_object_id, text=message.text)
        markup = set_keyboard(user.language, 'default keyboard')
        message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['Successfully edited'],
                                        reply_markup=markup)
        save_bot_message_id(message.chat.id, message_info.message_id)
        dbworker.set_state(message.chat.id, config.States.S_REMINDER_DESC.value)
        return
    elif dbworker.get_current_state(message.chat.id) == "15":
        user.update_reminder(reminder_id=editable_object_id, text=message.text)
        markup = set_keyboard(user.language, 'default keyboard')
        message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['Successfully edited'],
                                        reply_markup=markup)
        save_bot_message_id(message.chat.id, message_info.message_id)
        dbworker.set_state(message.chat.id, config.States.S_REMINDER_DESC.value)
        return


@bot.message_handler(func=get_editable_object_in_reminder)
def get_reminder_attribute_for_edit(message):
    save_bot_message_id(message.chat.id, message.id)
    user = UserInBot(message.chat.id)
    user.language = user.get_user_language()
    if message.text in ['/text', '/текст', 'text', 'текст']:
        dbworker.set_state(message.chat.id, config.States.S_GET_NEW_REMINDER_TEXT.value)
        message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['Enter edited reminder text'])
        save_bot_message_id(message.chat.id, message_info.message_id)

    else:
        message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['Enter reminder date'])
        save_bot_message_id(message.chat.id, message_info.message_id)

        dbworker.set_state(message.chat.id, config.States.S_GET_NEW_REMINDER_DATE.value)


@bot.message_handler(func=get_new_date_for_reminder)
def get_new_reminder_date(message):
    save_bot_message_id(message.chat.id, message.id)
    user_entered_date = message.text
    user = UserInBot(message.chat.id)
    user.language = user.get_user_language()
    user.timezone = user.get_user_timezone()
    note = user.get_note()
    reminder_id = user.editable_object_id()
    markup = set_keyboard(user.language, 'default keyboard')
    try:
        correct, date = parse_date(user_entered_date, user.timezone, user.language)
        date_for_reminder = datetime.datetime(year=date.year, month=date.month,
                                              day=date.day_of_month, hour=date.hour,
                                              minute=date.minute, tzinfo=pytz.utc)
        reminder = user.get_reminder(reminder_id=reminder_id)
        user.update_reminder(
            reminder_id=reminder.id,
            date=date_for_reminder,
            date_for_user=date.date_for_user, type=date.trigger)
        if not correct:
            message_info = bot.send_message(message.chat.id,
                                            messages_for_user[user.language]["Error in date message"])
            save_bot_message_id(message.chat.id, message_info.message_id)

            dbworker.set_state(message.chat.id, config.States.S_REMINDER_DATE_OR_ADDITION.value)
            return
        else:
            if date.trigger == "cron":
                scheduler.remove_job(reminder.job_id)
                job_id = create_job(message.chat.id, reminder.id, date)
                user.update_reminder(job_id=job_id)
                message_info = bot.send_message(message.chat.id,
                                                messages_for_user[user.language]['Successfully edited'],
                                                reply_markup=markup)
                save_bot_message_id(message.chat.id, message_info.message_id)

                dbworker.set_state(message.chat.id, config.States.S_REMINDER_DESC.value)
            else:
                scheduler.remove_job(reminder.job_id)
                job_id = create_job(message.chat.id, reminder.id, date)
                user.update_reminder(job_id=job_id, crontab=False)
                message_info = bot.send_message(message.chat.id,
                                                messages_for_user[user.language]['Successfully edited'],
                                                reply_markup=markup)
                save_bot_message_id(message.chat.id, message_info.message_id)

                dbworker.set_state(message.chat.id, config.States.S_REMINDER_DESC.value)

        user.delete_note(reminder_created=True, note_id=note.id)
    except Exception as e:
        print("ERROR IN update_reminder: ", e)
        message_info = bot.send_message(message.chat.id,
                                        messages_for_user[user.language]["Error in date message"])
        save_bot_message_id(message.chat.id, message_info.message_id)

    dbworker.set_state(message.chat.id, config.States.S_REMINDER_DATE_OR_ADDITION.value)
    return


@bot.message_handler(func=new_reminder)
def new_reminder(message):
    save_bot_message_id(message.chat.id, message.id)
    try:
        user = UserInBot(message.chat.id)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton('start')
        markup.add(button)
        if not user.check_registration():
            message_info = bot.send_message(message.chat.id,
                                            "Please, complete registration\nПожалуйста пройдите регистрацию",
                                            reply_markup=markup)
            save_bot_message_id(message.chat.id, message_info.message_id)
            return
        user.delete_celery_task()
        user.language = user.get_user_language()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton(messages_for_user[user.language]['cancel button']))
        message_info = bot.send_message(message.chat.id, messages_for_user[user.language]["Create note"],
                                        reply_markup=markup)
        save_bot_message_id(message.chat.id, message_info.message_id)
        dbworker.set_state(message.chat.id, config.States.S_REMINDER_DESC.value)
    except Exception as e:
        print("ERROR: ", e)


@bot.message_handler(content_types=['document', 'photo', 'video'])
def create_note_with_document(message):
    save_bot_message_id(message.chat.id, message.id)
    user = UserInBot(message.chat.id)
    user.delay_time = user.get_user_delay()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('start'))
    if not user.check_registration():
        message_info = bot.send_message(message.chat.id,
                                        "Please, complete registration\nПожалуйста пройдите регистрацию",
                                        reply_markup=markup)
        save_bot_message_id(message.chat.id, message_info.message_id)
        return
    user.language = user.get_user_language()
    tz = pytz.timezone(user.get_user_timezone())
    os.makedirs('media', exist_ok=True)
    os.makedirs('media/photos', exist_ok=True)
    os.makedirs('media/videos', exist_ok=True)
    markup = set_keyboard(user.language, 'keyboard after create note')
    note_text = message.text
    if note_text is None:
        note_text = message.caption
    if note_text is None:
        note_text = 'reminder'
    try:
        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = 'media' + '/' + file_info.file_path
            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            body_type = 'photo'
            user.create_note(note_body=file_path, user_tz=tz, note_text=note_text, body_type=body_type)

        elif message.content_type == 'document':
            file_id = message.document.file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = 'media' + '/' + f'{file_info.file_unique_id}{message.document.file_name}'
            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            body_type = 'document'
            user.create_note(note_body=file_path, user_tz=tz, note_text=note_text, body_type=body_type)

        elif message.content_type == 'video':
            try:
                file_id = message.video.file_id
                file_info = bot.get_file(file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                file_path = 'media' + '/videos/' + f'{file_info.file_unique_id}{message.video.file_name}'
                with open(file_path, 'wb') as new_file:
                    new_file.write(downloaded_file)
                body_type = 'video'
                user.create_note(note_body=file_path, user_tz=tz, note_text=note_text, body_type=body_type)
            except Exception as e:
                print("ERROR: ", e)

        message_info = bot.send_message(chat_id=message.chat.id,
                                        text=messages_for_user[user.language][
                                            "Choose actions after description"].format(user.delay_time),
                                        reply_markup=markup)
        save_bot_message_id(message.chat.id, message_info.message_id)

        task_id = delete_buttons.apply_async(countdown=user.delay_time, args=(message.chat.id,))
        user.save_celery_task_id(task_id)
        dbworker.set_state(message.chat.id, config.States.S_REMINDER_DATE_OR_ADDITION.value)
        return

    except Exception as e:
        print("ERROR in save media: ", e)


@bot.message_handler(func=reminder_description_status)
def reminder_date(message):
    try:
        user = UserInBot(message.chat.id)
        user.delay_time = user.get_user_delay()
        user.language = user.get_user_language()
        tz = pytz.timezone(user.get_user_timezone())
        user.delete_celery_task()
        markup = set_keyboard(user.language, 'keyboard after create note')
        user.create_note(note_text=message.text, user_tz=tz, body_type='text')
        message_info = bot.send_message(chat_id=message.chat.id,
                                        text=messages_for_user[user.language][
                                            "Choose actions after description"].format(user.delay_time),
                                        reply_markup=markup
                                        )
        save_bot_message_id(message.chat.id, message_info.message_id)

        dbworker.set_state(message.chat.id, config.States.S_REMINDER_DATE_OR_ADDITION.value)
        user.delete_celery_task()
        task_id = delete_buttons.apply_async(countdown=user.delay_time, args=(message.chat.id,))
        user.save_celery_task_id(task_id)
    except Exception as e:
        print("error: ", e)


@bot.message_handler(func=reminder_date_status)
def create_reminder_from_note(message):
    user = UserInBot(message.chat.id)
    user.language = user.get_user_language()
    user.delete_celery_task()
    message_info = bot.send_message(message.chat.id, messages_for_user[user.language]['Enter reminder date'])
    save_bot_message_id(message.chat.id, message_info.message_id)


@bot.message_handler(func=get_reminder_date_status)
def save_reminder(message):
    user_entered_date = message.text
    user = UserInBot(message.chat.id)
    user.language = user.get_user_language()
    user.timezone = user.get_user_timezone()
    note = user.get_note()
    reminder_text = note.text
    file_path = note.file_path
    body_type = note.body_type
    markup = set_keyboard(user.language, 'default keyboard')
    try:
        correct, date = parse_date(user_entered_date, user.timezone, user.language)
        date_for_reminder = datetime.datetime(year=date.year, month=date.month,
                                              day=date.day_of_month, hour=date.hour,
                                              minute=date.minute, tzinfo=pytz.timezone('UTC'))
        if date_for_reminder < datetime.datetime.now(tz=pytz.timezone('UTC')):
            user.delete_celery_task()
            user.update_note(note_id=note.id, date_for_user=date.date_for_user, date=date_for_reminder)
            markup = set_keyboard(user.language, 'default keyboard')
            message_info = bot.send_message(message.chat.id,
                                            messages_for_user[user.language]['Note successfully create'],
                                            reply_markup=markup)
            save_bot_message_id(message.chat.id, message_info.message_id)
            dbworker.set_state(message.chat.id, config.States.S_REMINDER_DESC.value)
            return
        user.create_reminder(text=reminder_text,
                             date=date_for_reminder,
                             date_for_user=date.date_for_user,
                             body_type=body_type,
                             file_path=file_path,
                             type=date.trigger)

        if date.trigger == "cron":
            reminder = user.get_reminder()
            job_id = create_job(message.chat.id, reminder.id, date)
            user.update_reminder(job_id=job_id)
            message_info = bot.send_message(message.chat.id,
                                            messages_for_user[user.language]['Reminder successfully create'],
                                            reply_markup=markup)
            save_bot_message_id(message.chat.id, message_info.message_id)

            dbworker.set_state(message.chat.id, config.States.S_REMINDER_DESC.value)
        else:
            reminder = user.get_reminder()
            job_id = create_job(message.chat.id, reminder.id, date)
            user.update_reminder(job_id=job_id, crontab=False)
            message_info = bot.send_message(message.chat.id,
                                            messages_for_user[user.language]['Reminder successfully create'],
                                            reply_markup=markup)
            save_bot_message_id(message.chat.id, message_info.message_id)

            dbworker.set_state(message.chat.id, config.States.S_CREATE_MORE_REMINDERS.value)

        user.delete_note(reminder_created=True, note_id=note.id)
        user.delete_celery_task()
    except Exception as e:
        print("ERROR IN save_reminder: ", e)
        new_note_text = note.text + f'\n{message.text}'
        user.update_note(note.id, text=new_note_text)
        dbworker.set_state(message.chat.id, config.States.S_REMINDER_DATE_OR_ADDITION.value)
    return


@bot.message_handler(func=create_more_reminders_status)
def create_more_reminders(message):
    user_entered_date = message.text
    user = UserInBot(message.chat.id)
    user.language = user.get_user_language()
    user.timezone = user.get_user_timezone()
    reminder = user.get_reminder()
    reminder_text = reminder.text
    file_path = reminder.file_path
    body_type = reminder.body_type
    markup = set_keyboard(user.language, 'default keyboard')
    try:
        correct, date = parse_date(user_entered_date, user.timezone, user.language)
        date_for_reminder = datetime.datetime(year=date.year, month=date.month,
                                              day=date.day_of_month, hour=date.hour,
                                              minute=date.minute, tzinfo=pytz.timezone('UTC'))
        if date_for_reminder < datetime.datetime.now(tz=pytz.timezone('UTC')):
            message_info = bot.send_message(message.chat.id,
                                            messages_for_user[user.language]['Error in date message'])
            save_bot_message_id(message.chat.id, message_info.message_id)
            dbworker.set_state(message.chat.id, config.States.S_CREATE_MORE_REMINDERS.value)
            return
        user.create_reminder(text=reminder_text,
                             date=date_for_reminder,
                             date_for_user=date.date_for_user,
                             body_type=body_type,
                             file_path=file_path,
                             type=date.trigger)

        if date.trigger == "cron":
            reminder = user.get_reminder()
            job_id = create_job(message.chat.id, reminder.id, date)
            user.update_reminder(job_id=job_id)
            message_info = bot.send_message(message.chat.id,
                                            messages_for_user[user.language]['Reminder successfully create'],
                                            reply_markup=markup)
            save_bot_message_id(message.chat.id, message_info.message_id)

            dbworker.set_state(message.chat.id, config.States.S_CREATE_MORE_REMINDERS.value)
        else:
            reminder = user.get_reminder()
            job_id = create_job(message.chat.id, reminder.id, date)
            user.update_reminder(job_id=job_id, crontab=False)
            message_info = bot.send_message(message.chat.id,
                                            messages_for_user[user.language]['Reminder successfully create'],
                                            reply_markup=markup)
            save_bot_message_id(message.chat.id, message_info.message_id)

            dbworker.set_state(message.chat.id, config.States.S_CREATE_MORE_REMINDERS.value)

    except Exception as e:
        print("ERROR IN save_reminder: ", e)
        user.delay_time = user.get_user_delay()
        user.create_note(body_type='text', user_tz=pytz.timezone(user.timezone), note_text=message.text)

        message_info = bot.send_message(chat_id=message.chat.id,
                                        text=messages_for_user[user.language][
                                            "Choose actions after description"].format(user.delay_time),
                                        reply_markup=markup)
        save_bot_message_id(message.chat.id, message_info.message_id)
        task_id = delete_buttons.apply_async(countdown=user.delay_time, args=(message.chat.id,))
        user.save_celery_task_id(task_id)
        dbworker.set_state(message.chat.id, config.States.S_REMINDER_DATE_OR_ADDITION.value)
    return
