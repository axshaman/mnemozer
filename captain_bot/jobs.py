from datetime import datetime

from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import SchedulerAlreadyRunningError
from .init import bot

from captain_bot_control.models import Reminder

from captain_bot_control.models import Note

from .user import UserInBot
from .utils import save_bot_message_id

scheduler = BackgroundScheduler({
    'apscheduler.jobstores.default': {
        'type': 'sqlalchemy',
        'url': 'sqlite:///users_jobs.sqlite'
    },
    'apscheduler.job_defaults.coalesce': 'false',
    'apscheduler.job_defaults.max_instances': '3',
}, timezone="UTC")


message_for_user = {
    'English': {
        'completed': 'completed on '
    },
    'Russian': {
        'completed': 'выполнена '
    }
}



def ensure_scheduler_running():
    """Start the scheduler if it has not been started yet."""
    try:
        scheduler.start()
    except SchedulerAlreadyRunningError:
        pass


def create_job(user_id, reminder_id, date):
    ensure_scheduler_running()
    print(user_id, reminder_id, date)
    if date.trigger == "cron":
        if date.everyday is True:
            job = scheduler.add_job(func=send_reminder, trigger='cron',
                                    minute=date.minute, hour=date.hour,
                                    day_of_week="*", args=[user_id, reminder_id, False, reminder_id])
            return job.id

        else:
            job = scheduler.add_job(func=send_reminder, trigger='cron',
                                    minute=date.minute, hour=date.hour,
                                    day_of_week=date.day_of_week, args=[user_id, reminder_id, False, reminder_id])
            return job.id

    elif date.trigger == "date":
        job = scheduler.add_job(func=send_reminder, trigger='date', run_date=datetime(
            date.year, date.month, date.day_of_month, date.hour, date.minute),
                                args=[user_id, reminder_id, True, reminder_id])
        return job.id


def cancel_job(job_id):
    if not job_id:
        return False
    ensure_scheduler_running()
    try:
        scheduler.remove_job(job_id)
        return True
    except JobLookupError:
        return False


def send_reminder(chat_id, reminder_id, delete_reminder_after_execute=True, note_id=0):
    user = UserInBot(user_id=chat_id)
    reminder = user.get_reminder(reminder_id=reminder_id)
    if reminder.body_type == "document":
        try:
            document = open(reminder.file_path, 'rb')
            message_info = bot.send_document(chat_id, document, caption=reminder.text)
            save_bot_message_id(user.user_id, message_info.message_id)
        except Exception as e:
            print("ERROR IN send_document: ", e)
    elif reminder.body_type == "photo":
        try:
            photo = open(reminder.file_path, 'rb')
            message_info = bot.send_photo(chat_id, photo, caption=reminder.text)
            save_bot_message_id(user.user_id, message_info.message_id)
        except Exception as e:
            print("ERROR IN send_photo: ", e)
    elif reminder.body_type == "video":
        try:
            video = open(reminder.file_path, 'rb')
            message_info = bot.send_video(chat_id, video, caption=reminder.text)
            save_bot_message_id(user.user_id, message_info.message_id)
        except Exception as e:
            print("ERROR IN send_video: ", e)

    elif reminder.body_type == "text":
        message_info = bot.send_message(chat_id, reminder.text)
        transfer_reminder_to_notes(chat_id, note_id, delete_reminder_after_execute)
        save_bot_message_id(user.user_id, message_info.message_id)


def transfer_reminder_to_notes(user_id, reminder_id, delete_reminder_after_execute=False):
    reminder = Reminder.objects.get(id=reminder_id)
    user = UserInBot(user_id)
    user.language = user.get_user_language()
    Note.objects.create(user_id=user_id, text=reminder.text,
                        date_for_user=f'{message_for_user[user.language]["completed"]}{reminder.date_for_user}',
                        date=datetime.now())
    updated_fields = []
    reminder.completed_at = datetime.now()
    updated_fields.append('completed_at')
    if delete_reminder_after_execute:
        reminder.is_completed = True
        reminder.job_id = None
        updated_fields.extend(['is_completed', 'job_id'])
    reminder.save(update_fields=updated_fields)
    if delete_reminder_after_execute and not reminder.preserve_after_trigger:
        Reminder.objects.filter(user_id=user_id, id=reminder_id).delete()
