"""mnemozer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.http.response import HttpResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from captain_bot.bot import bot
from captain_bot_control import api as control_api
from telebot.types import Update


@csrf_exempt
def webhook_receiver(request):
    print(request)
    if request.method == "GET":
        return HttpResponse('ok')
    update = Update.de_json(request.body.decode())
    bot.process_new_messages([update.message])
    return HttpResponse('ok')


@csrf_exempt
def home_page(request):
    if request.method == "GET":
        return HttpResponse('Home page')
    return HttpResponse('ok')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('telegram/', webhook_receiver, name='telegram_webhook'),
    path('', home_page, name='home_page'),
    path('api/v1/users/<str:user_id>/reminders/', control_api.reminders_collection, name='reminders_collection'),
    path('api/v1/users/<str:user_id>/reminders/<int:reminder_id>/', control_api.reminder_detail,
         name='reminder_detail'),
    path('api/v1/users/<str:user_id>/notes/', control_api.notes_collection, name='notes_collection'),
]
