from telebot import types

from captain_bot_control.models import MessagesFromBot

from captain_bot.init import bot
from captain_bot.user import UserInBot

messages_for_user = {
    "English": {
        'default keyboard': ["New note", "Notes", "Reminders", 'Other', 'Help', 'Settings'],
        'other keyboard': ['delete note', 'edit note', 'delete reminder', 'edit reminder', 'cancel', 'main menu'],
        'settings keyboard': ['change timezone', 'change delay', 'enable message cleaning',
                              'disable message cleaning', 'cancel'],
        'show reminders button': ['all reminders', 'reminders for period', 'reminders for period', 'cancel'],
        'show notes button': ['all notes', 'notes for period', 'notes for date', 'cancel'],
        'reminder buttons': ['Reminders', 'cancel'],
        'note buttons': ['Notes', 'cancel'],
        'Edit reminder button': ['text', 'date', 'cancel'],
        'keyboard after create note': ["New note", "create reminder from note", "main menu"],
        'Available formats button': ['date formats', 'cancel'],
        'show more reminders': ['show more reminders', 'cancel'],
        'show more notes': ['show more notes', 'cancel']
    },
    "Russian": {
        'default keyboard': ["Новая заметка", "Заметки", "Напоминания", 'Дополнительно', 'Помощь', 'Настройки'],
        'other keyboard': ['удалить напоминание', 'редактировать напоминание',
                           'удалить заметку', 'редактировать заметку', 'главное меню'],
        'settings keyboard': ['сменить часовой пояс', 'изменить время задержки',
                              'включить удаление сообщений', 'выключить удаление сообщений', 'отмена'],
        'show reminders button': ['все напоминания', 'напоминания на период', 'напоминания на дату', 'отмена'],
        'show notes button': ['все заметки', 'заметки на период', 'заметки на дату', 'отмена'],
        'reminder buttons': ['Напоминания', 'отмена'],
        'note buttons': ['Заметки', 'отмена'],
        'Edit reminder button': ['текст', 'дату', 'отмена'],
        'keyboard after create note': ["Новая заметка", "создать напоминание из заметки", "главное меню"],
        'Available formats button': ['форматы даты', 'главное меню'],
        'show more reminders': ['показать больше напоминаний', 'отмена'],
        'show more notes': ['показать больше заметок', 'отмена']
    },
}


def set_keyboard(language, keyboard):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_buttons = messages_for_user[language][keyboard]
    i = 0
    while i < len(keyboard_buttons):
        button1 = types.KeyboardButton(keyboard_buttons[i])
        if i < len(keyboard_buttons)-1:
            button2 = types.KeyboardButton(keyboard_buttons[i+1])
            markup.row(button1, button2)
        else:
            markup.row(button1)
        i += 2

    return markup


def delete_messages_from_db(user_id, message_id):
    return MessagesFromBot.objects.filter(user_id=user_id, message_id=message_id).delete()


def save_bot_message_id(user_id, message_id):
    return MessagesFromBot.objects.create(user_id=user_id, message_id=message_id)


def detect_message_type_and_send_message(user_id, all_messages, send_note=False, send_reminder=False):
    user = UserInBot(user_id)
    for message_with_notes in all_messages:
        if message_with_notes == '':
            continue
        if type(message_with_notes) == dict:
            note_or_reminder = None
            if send_note is True:
                note_or_reminder = user.get_note(message_with_notes['id'])
            elif send_reminder is True:
                note_or_reminder = user.get_reminder(message_with_notes['id'])
            caption = f'DATE: {note_or_reminder.date_for_user}\nID: {note_or_reminder.id}\nTEXT: {note_or_reminder.text}'
            if note_or_reminder.body_type == "document":
                try:
                    document = open(note_or_reminder.file_path, 'rb')
                    message_info = bot.send_document(user_id, document, caption=caption)
                    save_bot_message_id(user.user_id, message_info.message_id)
                except Exception as e:
                    print("ERROR IN send_document: ", e)
            elif note_or_reminder.body_type == "photo":
                try:
                    photo = open(note_or_reminder.file_path, 'rb')
                    message_info = bot.send_photo(user_id, photo, caption=caption)
                    save_bot_message_id(user.user_id, message_info.message_id)
                except Exception as e:
                    print("ERROR IN send_photo: ", e)
            elif note_or_reminder.body_type == "video":
                try:
                    video = open(note_or_reminder.file_path, 'rb')
                    message_info = bot.send_video(user_id, video, caption=caption)
                    save_bot_message_id(user.user_id, message_info.message_id)
                except Exception as e:
                    print("ERROR IN send_video: ", e)
        else:
            message_info = bot.send_message(user_id, message_with_notes)
            save_bot_message_id(user_id, message_info.message_id)
