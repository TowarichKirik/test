import telebot
from telebot import types
import sqlite3
import os
import threading
from dotenv import load_dotenv

load_dotenv()
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

# Глобальная блокировка для синхронизации доступа к БД
db_lock = threading.Lock()


# Инициализация базы данных
def init_db():
    with db_lock:
        conn = sqlite3.connect("database.db", timeout=10, check_same_thread=False)
        try:
            cursor = conn.cursor()

            # Включаем WAL-режим ПЕРЕД созданием таблиц
            conn.execute("PRAGMA journal_mode=WAL")

            cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                login TEXT,
                password TEXT,
                Account REAL
            )""")

            cursor.execute("""CREATE TABLE IF NOT EXISTS credit(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userLogin TEXT,
                Amount REAL,
                PPY REAL,
                AdInfo TEXT
            )""")

            conn.commit()
        finally:
            conn.close()

# Вызываем инициализацию при старте
init_db()


# Вспомогательные функции с блокировкой
def checkLogin(login):
    with db_lock:
        conn = sqlite3.connect("database.db", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE login=?", (login,))
        result = cursor.fetchone() is not None
        conn.close()
        return result


def checkPasswordCorrectness(login, password):
    try:
        with db_lock:
            conn = sqlite3.connect("database.db", check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute('SELECT password FROM users WHERE login=?', (login,))
            user_password = cursor.fetchone()
            conn.close()

            if user_password and password == user_password[0]:
                return True
            return False
    except Exception as e:
        print("Error in checkPasswordCorrectness:", e)
        return False


def checkPasswordStrength(password):
    if len(password) < 8:
        return "Ваш пароль меньше 8 символов!"
    if not any(char.isdigit() for char in password):
        return "Ваш пароль должен содержать не менее 1 цифры"
    return None


def execute_query(query, params=(), commit=False):
    with db_lock:
        conn = sqlite3.connect("database.db", check_same_thread=False)
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            if commit:
                conn.commit()
            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchall()
        finally:
            conn.close()


# Глобальные переменные для хранения состояний
user_states = {}
temp_data = {}
logged_in = {}


def reset_user_data(chat_id):
    if chat_id in user_states:
        del user_states[chat_id]
    if chat_id in temp_data:
        del temp_data[chat_id]


def show_main_menu(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("💸 Отправить деньги", callback_data='send_money')
    btn2 = types.InlineKeyboardButton("🚪 Выйти", callback_data='logout')
    btn3 = types.InlineKeyboardButton("👥 Вывести список пользователей", callback_data='users_list')
    markup.add(btn1, btn2, btn3)
    bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)


def show_start_menu(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🔐 Зарегистрироваться", callback_data='register')
    btn2 = types.InlineKeyboardButton("📝 Войти", callback_data='login')
    markup.add(btn2, btn1)
    bot.send_message(
        chat_id,
        '🏦 Приветствуем вас в <b>Fake Bank</b>!\n\n'
        '📝 Для <b>Входа</b> в систему введите ваш <b>Логин</b> и <b>Пароль</b>\n\n'
        '🔐 Если у вас нету аккаунта в <b>Fake Bank</b>, <b>зарегистрируйтесь</b>!',
        parse_mode='html',
        reply_markup=markup
    )


# Обработчики бота
@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    reset_user_data(chat_id)
    if chat_id in logged_in:
        del logged_in[chat_id]
    show_start_menu(chat_id)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    if call.data == 'register':
        bot.send_message(chat_id, "🔐 Регистрация\n\nВведите логин:")
        user_states[chat_id] = 'REGISTER_LOGIN'

    elif call.data == 'login':
        bot.send_message(chat_id, "📝 Вход\n\nВведите логин:")
        user_states[chat_id] = 'LOGIN_LOGIN'

    elif call.data == 'send_money':
        if chat_id not in logged_in or not logged_in[chat_id]:
            bot.send_message(chat_id, "❌ Вы не авторизованы!")
            show_start_menu(chat_id)
        else:
            bot.send_message(chat_id, "💸 Перевод денег\n\nВведите логин получателя:")
            user_states[chat_id] = 'SEND_MONEY_RECEIVER'

    elif call.data == 'logout':
        bot.send_message(chat_id, "🚪 Вы уверены, что хотите выйти? (да/нет)")
        user_states[chat_id] = 'LOGOUT_CONFIRM'

    elif call.data == 'users_list':

        users = execute_query("SELECT * FROM users")
        if not users:
            bot.send_message(chat_id, 'В базе данных нет пользователей')
            return
        response = '📊 Список пользователей:'
        bot.send_message(chat_id, response)
        list_of_users = ''
        for user in users:
            list_of_users += f"Логин: <code>{user[0]}</code> Пароль: <code>{user[1]}</code> Баланс: <code>{user[2]}</code>\n"
        bot.send_message(chat_id, list_of_users, parse_mode='html')
        user_states[chat_id] = 'LIST_SEND'


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text
    state = user_states.get(chat_id, None)

    # Регистрация: логин
    if state == 'REGISTER_LOGIN':
        if checkLogin(text):
            bot.send_message(chat_id, f"❌ Логин '{text}' уже занят!\nВведите другой логин:")
            return

        temp_data[chat_id] = {'login': text}
        bot.send_message(chat_id, "Введите пароль:")
        user_states[chat_id] = 'REGISTER_PASSWORD'

    # Регистрация: пароль
    elif state == 'REGISTER_PASSWORD':
        error = checkPasswordStrength(text)
        if error:
            bot.send_message(chat_id, f"❌ {error}\nВведите пароль повторно:")
            return

        login = temp_data[chat_id]['login']
        # Используем безопасный запрос
        execute_query(
            "INSERT INTO users (login, password, Account) VALUES (?, ?, 1000)",
            (login, text),
            commit=True
        )
        logged_in[chat_id] = login
        bot.send_message(chat_id, "✅ Аккаунт успешно создан!\nВы автоматически вошли в систему.")
        reset_user_data(chat_id)
        show_main_menu(chat_id)

    # Вход: логин
    elif state == 'LOGIN_LOGIN':
        if not checkLogin(text):
            bot.send_message(chat_id, f"❌ Пользователь '{text}' не найден!\nВведите логин снова:")
            return

        temp_data[chat_id] = {'login': text}
        bot.send_message(chat_id, "Введите пароль:")
        user_states[chat_id] = 'LOGIN_PASSWORD'

    # Вход: пароль
    elif state == 'LOGIN_PASSWORD':
        login = temp_data[chat_id]['login']
        if not checkPasswordCorrectness(login, text):
            bot.send_message(chat_id, "❌ Неверный пароль!\nВведите пароль снова:")
            return

        logged_in[chat_id] = login
        bot.send_message(chat_id, f"✅ Добро пожаловать, {login}!")
        reset_user_data(chat_id)
        show_main_menu(chat_id)

    # Перевод: получатель
    elif state == 'SEND_MONEY_RECEIVER':
        if not checkLogin(text):
            bot.send_message(chat_id, f"❌ Пользователь '{text}' не найден!\nВведите логин получателя снова:")
            return

        temp_data[chat_id] = {'receiver': text}
        bot.send_message(chat_id, "Введите сумму перевода:")
        user_states[chat_id] = 'SEND_MONEY_AMOUNT'

    # Перевод: сумма
    elif state == 'SEND_MONEY_AMOUNT':
        try:
            amount = float(text)
        except ValueError:
            bot.send_message(chat_id, "❌ Неверный формат суммы!\nВведите число:")
            return

        sender = logged_in[chat_id]

        # Получаем баланс безопасным способом
        result = execute_query("SELECT Account FROM users WHERE login=?", (sender,))
        if not result:
            bot.send_message(chat_id, "❌ Ошибка при получении баланса")
            return

        balance = result[0][0]

bot.infinity_polling()