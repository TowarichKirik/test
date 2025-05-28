import telebot
from dotenv import load_dotenv
from telebot import types
import os

load_dotenv()
bot = telebot.TeleBot(os.getenv('BOT_TOKEN')) # токен



#start

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🔐 Зарегистрироваться", callback_data='register')
    btn2 = types.InlineKeyboardButton("📝 Войти", callback_data='login')
    markup.add(btn2, btn1)

    bot.send_message(message.chat.id, '🏦 Приветствуем вас в <b>Fake Bank</b>!\n\n📝 Для <b>Входа</b> в систему введите ваш <b>Логин</b> и <b>Пароль</b>\n\n🔐 Если у вас нету аккаунта в <b>Fake Bank</b>, <b>зарегистрируйтесь</b>!', parse_mode='html', reply_markup=markup)
@bot.callback_query_handler(func= lambda call: True)
def callback_register(call):
    if call.data == 'register':
        bot.send_message(call.message.chat.id, '<b>Fake Bank</b>\n\n🔐 Регистрация:', parse_mode='html')
    elif call.data == 'login':
        bot.send_message(call.message.chat.id, '<b>Fake Bank</b>\n\n📝 Вход:', parse_mode='html')





bot.infinity_polling()