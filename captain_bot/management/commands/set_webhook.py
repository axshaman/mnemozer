from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.urls import reverse
from captain_bot.bot import bot


class Command(BaseCommand):
    def handle(self, *args, **options):
        url = f'https://{Site.objects.get_current().domain}{reverse("telegram_webhook")}'
        print(f'Set telegram webhook to: {url}')
        bot.set_webhook(url)
