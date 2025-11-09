import json
from datetime import datetime, timedelta

from django.test import Client, TestCase

from captain_bot.jobs import ensure_scheduler_running, scheduler
from captain_bot_control.models import Reminder


class ReminderApiTests(TestCase):
    def setUp(self):
        ensure_scheduler_running()
        scheduler.remove_all_jobs()
        self.client = Client()
        self.user_id = '42'

    def test_create_and_fetch_reminder(self):
        payload = {
            'text': 'Team sync',
            'remind_at': (datetime.utcnow() + timedelta(minutes=10)).isoformat() + 'Z',
        }
        response = self.client.post(
            f'/api/v1/users/{self.user_id}/reminders/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        reminder_id = data['id']
        self.assertEqual(data['text'], payload['text'])
        self.assertFalse(data['is_completed'])
        self.assertTrue(data['job_id'])

        detail = self.client.get(f'/api/v1/users/{self.user_id}/reminders/{reminder_id}/')
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()['id'], reminder_id)

    def test_patch_and_complete_reminder(self):
        reminder = Reminder.objects.create(
            user_id=self.user_id,
            text='Prepare agenda',
            date=datetime.utcnow() + timedelta(minutes=20),
            date_for_user='scheduled',
            type='date',
            preserve_after_trigger=True,
        )
        reminder.job_id = ''
        reminder.save()

        new_time = (datetime.utcnow() + timedelta(minutes=45)).isoformat() + 'Z'
        response = self.client.patch(
            f'/api/v1/users/{self.user_id}/reminders/{reminder.id}/',
            data=json.dumps({'remind_at': new_time}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        updated = response.json()
        self.assertEqual(updated['display_time'], Reminder.objects.get(id=reminder.id).date_for_user)
        self.assertTrue(updated['job_id'])

        complete = self.client.patch(
            f'/api/v1/users/{self.user_id}/reminders/{reminder.id}/',
            data=json.dumps({'is_completed': True}),
            content_type='application/json',
        )
        self.assertEqual(complete.status_code, 200)
        body = complete.json()
        self.assertTrue(body['is_completed'])
        self.assertIsNone(body['job_id'])

        listing = self.client.get(f'/api/v1/users/{self.user_id}/reminders/', {'status': 'completed'})
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(len(listing.json()['results']), 1)

    def test_delete_reminder(self):
        reminder = Reminder.objects.create(
            user_id=self.user_id,
            text='Delete me',
            date=datetime.utcnow() + timedelta(minutes=5),
            date_for_user='soon',
            type='date',
        )
        response = self.client.delete(f'/api/v1/users/{self.user_id}/reminders/{reminder.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Reminder.objects.filter(id=reminder.id).exists())

    def test_list_notes_limit_parameter(self):
        response = self.client.get(f'/api/v1/users/{self.user_id}/notes/', {'limit': '5'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.json())
