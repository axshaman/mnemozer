import configparser
import telebot

config = configparser.ConfigParser()
config.read('captain_bot/app.ini')
bot_token = config['api']['bot_token']
bot = telebot.TeleBot(bot_token)
