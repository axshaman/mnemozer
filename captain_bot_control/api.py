import json
from datetime import datetime
from typing import Dict, Iterable, Optional

import pytz
from django.db import transaction
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from captain_bot.jobs import cancel_job, create_job, ensure_scheduler_running
from .models import Note, Reminder


class _ApiDate:
    """A lightweight adapter that mimics the date parser object used by the bot."""

    trigger = 'date'

    def __init__(self, run_at: datetime) -> None:
        self.year = run_at.year
        self.month = run_at.month
        self.day_of_month = run_at.day
        self.hour = run_at.hour
        self.minute = run_at.minute
        self.everyday = False
        self.date_for_user = run_at.strftime('%d.%m.%Y %H:%M')


def _format_datetime(value: datetime) -> Optional[str]:
    if value is None:
        return None
    iso_value = value.isoformat()
    if value.tzinfo is None:
        return f'{iso_value}Z'
    return iso_value


def _json_error(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({'error': message}, status=status)


def _parse_payload(request) -> Dict:
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        raise ValueError('Request body must be valid JSON.')


def _parse_schedule(value: str) -> datetime:
    if not value:
        raise ValueError('`remind_at` is required.')
    parsed = parse_datetime(value)
    if parsed is None:
        raise ValueError('`remind_at` must be in ISO 8601 format.')
    if parsed.tzinfo:
        parsed = parsed.astimezone(pytz.UTC).replace(tzinfo=None)
    parsed = parsed.replace(second=0, microsecond=0)
    if parsed <= datetime.utcnow():
        raise ValueError('`remind_at` must be a future date and time (UTC).')
    return parsed


def _serialize_reminder(reminder: Reminder) -> Dict:
    return {
        'id': reminder.id,
        'user_id': reminder.user_id,
        'text': reminder.text,
        'remind_at': _format_datetime(reminder.date),
        'display_time': reminder.date_for_user,
        'is_completed': reminder.is_completed,
        'completed_at': _format_datetime(reminder.completed_at),
        'body_type': reminder.body_type,
        'type': reminder.type,
        'job_id': reminder.job_id,
        'preserve_after_trigger': reminder.preserve_after_trigger,
    }


def _serialize_notes(notes: Iterable[Note]) -> Iterable[Dict]:
    for note in notes:
        yield {
            'id': note.id,
            'user_id': note.user_id,
            'text': note.text,
            'recorded_at': _format_datetime(note.date),
            'display_time': note.date_for_user,
            'body_type': note.body_type,
        }


@csrf_exempt
@require_http_methods(["GET", "POST"])
@transaction.atomic
def reminders_collection(request, user_id):
    if request.method == 'GET':
        status_filter = request.GET.get('status', 'active')
        reminders = Reminder.objects.filter(user_id=user_id)
        if status_filter == 'completed':
            reminders = reminders.filter(is_completed=True)
        elif status_filter == 'active':
            reminders = reminders.filter(is_completed=False)
        reminders = reminders.order_by('date')
        data = [_serialize_reminder(reminder) for reminder in reminders]
        return JsonResponse({'results': data})

    try:
        payload = _parse_payload(request)
    except ValueError as exc:  # pragma: no cover - defensive branch
        return _json_error(str(exc))

    text = payload.get('text')
    if not text:
        return _json_error('`text` is required.')

    try:
        schedule_at = _parse_schedule(payload.get('remind_at'))
    except ValueError as exc:
        return _json_error(str(exc))

    preserve = bool(payload.get('preserve_after_trigger', True))

    reminder = Reminder.objects.create(
        user_id=user_id,
        text=text,
        date=schedule_at,
        date_for_user=schedule_at.strftime('%d.%m.%Y %H:%M'),
        body_type=payload.get('body_type', 'text'),
        type='date',
        preserve_after_trigger=preserve,
    )

    ensure_scheduler_running()
    job_id = create_job(user_id, reminder.id, _ApiDate(schedule_at))
    reminder.job_id = job_id
    reminder.save(update_fields=['job_id'])

    return JsonResponse(_serialize_reminder(reminder), status=201)


@csrf_exempt
@require_http_methods(["GET", "PATCH", "DELETE"])
@transaction.atomic
def reminder_detail(request, user_id, reminder_id):
    try:
        reminder = Reminder.objects.get(user_id=user_id, id=reminder_id)
    except Reminder.DoesNotExist:
        return _json_error('Reminder not found.', status=404)

    if request.method == 'GET':
        return JsonResponse(_serialize_reminder(reminder))

    if request.method == 'DELETE':
        cancel_job(reminder.job_id)
        reminder.delete()
        return HttpResponse(status=204)

    try:
        payload = _parse_payload(request)
    except ValueError as exc:  # pragma: no cover - defensive branch
        return _json_error(str(exc))

    updated_fields = []

    if 'text' in payload:
        reminder.text = payload['text']
        updated_fields.append('text')

    if 'remind_at' in payload:
        try:
            new_schedule = _parse_schedule(payload['remind_at'])
        except ValueError as exc:
            return _json_error(str(exc))
        cancel_job(reminder.job_id)
        reminder.date = new_schedule
        reminder.date_for_user = new_schedule.strftime('%d.%m.%Y %H:%M')
        updated_fields.extend(['date', 'date_for_user'])
        job_id = create_job(user_id, reminder.id, _ApiDate(new_schedule))
        reminder.job_id = job_id
        updated_fields.append('job_id')

    if 'preserve_after_trigger' in payload:
        reminder.preserve_after_trigger = bool(payload['preserve_after_trigger'])
        updated_fields.append('preserve_after_trigger')

    if 'is_completed' in payload:
        is_completed = bool(payload['is_completed'])
        reminder.is_completed = is_completed
        reminder.completed_at = datetime.utcnow() if is_completed else None
        updated_fields.extend(['is_completed', 'completed_at'])
        if is_completed:
            cancel_job(reminder.job_id)
            reminder.job_id = None
            updated_fields.append('job_id')

    if updated_fields:
        reminder.save(update_fields=updated_fields)

    return JsonResponse(_serialize_reminder(reminder))


@csrf_exempt
@require_http_methods(["GET"])
def notes_collection(request, user_id):
    limit = request.GET.get('limit')
    notes = Note.objects.filter(user_id=user_id).order_by('-date')
    if limit and limit.isdigit():
        notes = notes[:int(limit)]
    return JsonResponse({'results': list(_serialize_notes(notes))})


def method_not_allowed(*_args, **_kwargs):  # pragma: no cover - compatibility
    return HttpResponseNotAllowed(['GET'])
