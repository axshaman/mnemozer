import datetime

from captain_bot_control.models import Reminder, Note, User

from .celery import app


class UserInBot:

    def __init__(self, user_id):
        self.user_id = user_id

    def delete_celery_task(self):
        try:
            user = User.objects.get(user_id=self.user_id)
            if user.celery_task_id != 'void':
                app.control.revoke(user.celery_task_id)
                user.celery_task_id = 'void'
                user.save()
            return user
        except Exception as e:
            print("ERROR: ", e)

    def save_celery_task_id(self, celery_task_id):
        user = User.objects.get(user_id=self.user_id)
        user.celery_task_id = celery_task_id
        user.save()
        return user

    def create_note(self, body_type, user_tz, note_text='', note_body=''):
        if body_type == "text":
            date_for_user = f'{datetime.datetime.now(tz=user_tz).day}.{datetime.datetime.now(tz=user_tz).month}.'
            f'{datetime.datetime.now(tz=user_tz).year} '
            f'{datetime.datetime.now(tz=user_tz).hour}:{datetime.datetime.now(tz=user_tz).minute}'
            if datetime.datetime.now(tz=user_tz).month < 10:
                date_for_user = f'{datetime.datetime.now(tz=user_tz).day}.{datetime.datetime.now(tz=user_tz).month}.' \
                                f'{datetime.datetime.now(tz=user_tz).year}' \
                                f' {datetime.datetime.now(tz=user_tz).hour}:{datetime.datetime.now(tz=user_tz).minute}'
            return Note.objects.create(
                date=datetime.datetime.now(),
                user_id=self.user_id,
                text=note_text,
                file_path=note_body,
                body_type=body_type,
                date_for_user=date_for_user,)
        elif body_type in ["photo", "document", "video"]:
            date_for_user = f'{datetime.datetime.now(tz=user_tz).day}.{datetime.datetime.now(tz=user_tz).month}.'
            f'{datetime.datetime.now(tz=user_tz).year} '
            f'{datetime.datetime.now(tz=user_tz).hour}:{datetime.datetime.now(tz=user_tz).minute}'
            if datetime.datetime.now(tz=user_tz).month < 10:
                date_for_user = f'{datetime.datetime.now(tz=user_tz).day}.{datetime.datetime.now(tz=user_tz).month}.' \
                                f'{datetime.datetime.now(tz=user_tz).year} {datetime.datetime.now(tz=user_tz).hour}:' \
                                f'{datetime.datetime.now(tz=user_tz).minute} '
            return Note.objects.create(
                date=datetime.datetime.now(),
                user_id=self.user_id,
                text=note_text,
                file_path=note_body,
                body_type=body_type,
                date_for_user=date_for_user)

    def get_note(self, note_id=0):
        if note_id != 0:
            notes = Note.objects.get(user_id=self.user_id, id=note_id)
            return notes
        else:
            notes = Note.objects.filter(user_id=self.user_id).last()
            return notes

    def save_editable_note_or_reminder(self, note_or_reminder_id):
        user = User.objects.get(user_id=self.user_id)
        user.note_or_reminder_for_edit = int(note_or_reminder_id)
        user.save()

    def editable_object_id(self):
        user = User.objects.get(user_id=self.user_id)
        return user.note_or_reminder_for_edit

    def update_reminder(self, reminder_id=0, **kwargs):
        if reminder_id != 0:
            reminder = Reminder.objects.get(user_id=self.user_id, id=reminder_id)
        else:
            reminder = Reminder.objects.filter(user_id=self.user_id).last()
        for field, value in kwargs.items():
            setattr(reminder, field, value)
        reminder.save()
        return reminder

    def update_note(self, note_id, **kwargs):
        note = Note.objects.get(user_id=self.user_id, id=note_id)
        for field, value in kwargs.items():
            setattr(note, field, value)
        note.save()
        return note

    def create_reminder(self, text, file_path, body_type, date, date_for_user, type):
        date_for_rem = datetime.datetime(year=date.year, month=date.month, day=date.day,
                                         hour=date.hour, minute=date.minute)
        return Reminder.objects.create(user_id=self.user_id, text=text, date=date_for_rem, date_for_user=date_for_user,
                                       file_path=file_path, body_type=body_type, type=type)

    def delete_reminder(self, reminder_id):
        return Reminder.objects.filter(user_id=self.user_id, id=reminder_id).delete()

    def all_reminders(self, check_availability=False, reminder_type=''):
        user = User.objects.get(user_id=self.user_id)
        if check_availability:
            return Reminder.objects.all().filter(user_id=self.user_id)
        from_reminder = user.start_reminder_to_show
        to_reminder = from_reminder + 4
        if reminder_type in ['cron', 'date']:
            reminders = Reminder.objects.filter(user_id=self.user_id,
                                                type=reminder_type).order_by('date')[from_reminder:to_reminder]
            return reminders
        return Reminder.objects.all().filter(user_id=self.user_id)

    def get_reminder(self, reminder_id=0):
        if reminder_id != 0:
            return Reminder.objects.get(user_id=self.user_id, id=reminder_id)
        else:
            return Reminder.objects.filter(user_id=self.user_id).last()

    def update_from_and_to_notes_or_reminders(self, note=False, reminder=False, increase_for=0):
        user = User.objects.get(user_id=self.user_id)
        if note is True:
            user.start_note_to_show = 0
        elif reminder is True:
            if increase_for > 0:
                user.start_reminder_to_show += increase_for
            else:
                user.start_reminder_to_show = 0
        else:
            user.start_reminder_to_show = 0
            user.start_note_to_show = 0
        user.save()

    def all_notes(self, check_availability=False):
        user = User.objects.get(user_id=self.user_id)
        if check_availability:
            return Note.objects.all().filter(user_id=self.user_id)
        from_note = user.start_note_to_show
        to_note = from_note + 10
        notes = Note.objects.all().filter(user_id=self.user_id).order_by('date')[from_note:to_note]
        user.start_note_to_show += 10
        user.save()
        return notes

    def delete_note(self, reminder_created=False, note_id=0):
        if reminder_created:
            note = Note.objects.filter(user_id=self.user_id).last()
        else:
            note = Note.objects.filter(user_id=self.user_id, id=note_id)
        note.delete()

    def get_user_language(self):
        user = User.objects.get(user_id=self.user_id)
        return user.language

    def get_user_delay(self):
        user = User.objects.get(user_id=self.user_id)
        return user.delay_time

    def reminders_for_period(self, from_date, to_date):
        return Reminder.objects.all().filter(user_id=self.user_id, date__range=(from_date, to_date), type='date')

    def notes_for_period(self, from_date, to_date):
        return Note.objects.all().filter(user_id=self.user_id, date__range=(from_date, to_date))

    def check_registration(self):
        user = User.objects.filter(user_id=self.user_id).last()
        if user is not None:
            return user.registered
        else:
            return False

    def update_registered_status(self):
        user = User.objects.filter(user_id=self.user_id).last()
        user.registered = True
        user.save()
        return user

    def register_user(self, language):
        try:
            already_registered_user = User.objects.get(user_id=self.user_id)
            return
        except Exception as e:
            print("USER DOES NOT EXISTS: ", e)
            User.objects.create(user_id=self.user_id, language=language, created=datetime.datetime.now())

    def save_user_timezone(self, timezone):
        user = User.objects.get(user_id=self.user_id)
        user.timezone = timezone
        user.save()

    def update_delay_time(self, new_delay_time):
        user = User.objects.filter(user_id=self.user_id).last()
        user.delay_time = new_delay_time
        user.save()

    def get_user_timezone(self):
        user = User.objects.get(user_id=self.user_id)
        return user.timezone

    def get_user_lifetime(self):
        user = User.objects.get(user_id=self.user_id)
        return (datetime.datetime.now() - user.created) / 60

    def update_cleaning_mode_status(self, enable=False, disable=False):
        user = User.objects.get(user_id=self.user_id)
        if enable:
            user.enable_message_cleaning = True
        else:
            user.enable_message_cleaning = False
        user.save()
        return user
