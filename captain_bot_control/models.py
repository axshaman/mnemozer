from django.db import models


class Reminder(models.Model):
    user_id = models.CharField(max_length=20)
    text = models.TextField(null=True)
    date = models.DateTimeField(null=True)
    date_for_user = models.CharField(max_length=30, null=True)
    job_id = models.CharField(max_length=50, null=True)
    file_path = models.CharField(max_length=100, null=True)
    body_type = models.CharField(max_length=20, null=True)
    type = models.CharField(max_length=20)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    preserve_after_trigger = models.BooleanField(default=False)


class Note(models.Model):
    user_id = models.CharField(max_length=20)
    text = models.TextField(null=True)
    date = models.DateTimeField(null=True)
    date_for_user = models.CharField(max_length=30, null=True)
    file_path = models.CharField(max_length=100, null=True)
    body_type = models.CharField(max_length=20, null=True)


class User(models.Model):
    user_id = models.CharField(max_length=20)
    language = models.CharField(max_length=30)
    timezone = models.CharField(max_length=40)
    note_or_reminder_for_edit = models.IntegerField(null=True)
    celery_task_id = models.CharField(max_length=100, default='void')
    start_note_to_show = models.IntegerField(default=0)
    start_reminder_to_show = models.IntegerField(default=0)
    registered = models.BooleanField(default=False)
    delay_time = models.IntegerField(default=10)
    created = models.DateTimeField(null=True)
    enable_message_cleaning = models.BooleanField(default=False)


class MessagesFromBot(models.Model):
    user_id = models.CharField(max_length=20)
    message_id = models.CharField(max_length=50)
