import datetime

from captain_bot import dbworker
from captain_bot.init import bot
from . import config
from captain_bot.utils import set_keyboard
from captain_bot.user import UserInBot
from .celery import app
from captain_bot_control.models import MessagesFromBot, User
from telebot.apihelper import ApiTelegramException, ConnectionError, ApiException

from .utils import delete_messages_from_db, save_bot_message_id

messages_for_user = {
    'English': {
        'Note successfully create': 'note successfully created',
        'Plan messages cleaning': 'Procedure of automatic cleaning systems notifications is finished'
    },
    'Russian': {
        'Note successfully create': 'Заметка успешно создана',
        'Plan messages cleaning': 'Произведена авто-очистка системных уведомлений',
    },
}


@app.task
def delete_buttons(chat_id):
    user = UserInBot(chat_id)
    user.language = user.get_user_language()
    markup = set_keyboard(user.language, 'default keyboard')
    message_info = bot.send_message(chat_id, text=messages_for_user[user.language]['Note successfully create'],
                                    reply_markup=markup)
    save_bot_message_id(user.user_id, message_info.message_id)
    dbworker.set_state(chat_id, config.States.S_REMINDER_DESC.value)


@app.task
def delete_all_bot_messages():
    try:
        users = User.objects.all()
        for user in users:
            user_lifetime = (datetime.datetime.now() - user.created)
            if not user.enable_message_cleaning or (user_lifetime.seconds / 60) <= 1:
                continue

            markup = set_keyboard(user.language, 'default keyboard')

            messages_from_bot = MessagesFromBot.objects.all().filter(user_id=user.user_id)
            try:
                for message in messages_from_bot:
                    not_success = delete_message_from_bot(user.user_id, message.message_id)
                    if not_success == 1:
                        continue
                try:
                    message_info = bot.send_message(user.user_id,
                                                    messages_for_user[user.language]['Plan messages cleaning'],
                                                    disable_notification=True, reply_markup=markup)
                    save_bot_message_id(user.user_id, message_info.message_id)
                except Exception as e:
                    print("ERROR IN SEND MESSAGES: ", e)
                    continue
            except ApiTelegramException as e:
                print("HANDLED ERROR: ", e)
                continue
    except Exception as e:
        print("ERROR IN DELETE ALL MESSAGES: ", e)
        delete_all_bot_messages()


def delete_message_from_bot(user_id, message_id):
    try:
        bot.delete_message(user_id, message_id)
        delete_messages_from_db(user_id, message_id)
    except ApiTelegramException as e:
        print(f"ERROR IN DELETE MESSAGE WITH ID {message_id}: ", e)
        return 1
    except ConnectionResetError as e:
        print(f'CONNECTION RESET ERROR: {e}')
        delete_message_from_bot(user_id, message_id)
    except ApiException as e:
        print("BOT WAS BLOCKED BY THE USER: ", e)
        return 1
    return 0
