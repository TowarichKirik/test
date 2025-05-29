import vigener as cifer

import sqlite3
conn = sqlite3.connect("database.db")
cursor = conn.cursor()


"""МОЖНО УЛУЧШИТЬ: 
Убрать айди, заменив его логином.
Логин так или иначе все равно уникален, как и айди
Зачем тогда айди, который нигде не нужен, если есть логин?"""


cursor.execute("""CREATE TABLE IF NOT EXISTS users(
login TEXT,
password TEXT,
Account REAL
)
""")


cursor.execute("""CREATE TABLE IF NOT EXISTS credit(
id INTEGER PRIMARY KEY AUTOINCREMENT,
userLogin TEXT,
Amount REAL,
PPY REAL,
AdInfo TEXT
)
""")
#PPY - percent per year, AdInfo - Additional information


# Операции
def Operations(num):
    loggedAs = ""

    def checkPasswordStrength(password):
        if len(password) < 8:
            print("Ваш пароль меньше 8 символов!")
            return True
        return False

    def checkLogin(login):
        cursor.execute("SELECT * FROM users")
        for table in cursor.fetchall():
            if login == table[0]:
                return True
        return False

    def checkPasswordCorrectness(login, password):
        try:
            cursor.execute(f'SELECT password FROM users WHERE login="{login}"')
            user_password = cursor.fetchone()
            if password == user_password[0]:
                return True
            return False
        except Exception as e:
            print("Эксепшн: ", e)
            pass


    #что-то странное творится
    #Создание аккаунта
    def createAccount():
        login = input("Ваш логин: ")
        while checkLogin(login):
            print(f"Ваш логин {login} совпадает с логином другого пользователя!")
            login = input("Ваш логин: ")
        password = input("Ваш пароль: ")
        while checkPasswordStrength(password):
            password = input("Введите пароль повторно: ")
        if len(password) < 8:
            print("Ваш пароль меньше 8 символов!")
            password = input("Ваш пароль: ")
            if '0123456789' not in password:
                print("Ваш пароль должен содержать не менее 1 цифры")
                password = input("Ваш пароль: ")
        cursor.execute(f"""INSERT INTO users (login, password, Account) VALUES ('{login}', '{password}', 1000);""")
        conn.commit()#
        log_in_account(login, password)

    #Перевод средств
    def send_money(loginSender, loginReciever, amount):
        cursor.execute(f"UPDATE users SET Account = Account - {amount} WHERE login = {loginSender}")
        cursor.execute(f"UPDATE users SET Account = Account + {amount} WHERE login = {loginReciever}")
        conn.commit()

    #Логин в аккаунт
    def log_in_account(login="0", password="0"):
        if login == "0":
            login = input("Введите ваш логин: ")
            password = input("Введите ваш пароль: ")
        isRealLogin = False
        isPasswordCorrect = False
        if checkLogin(login):
            isRealLogin = True
        if checkPasswordCorrectness(login, password):
            isPasswordCorrect = True
        if isRealLogin and isPasswordCorrect:
            print("Добро пожаловать!")
            loggedAs = login
        else:
            print("Неверный логин или пароль!")




    if num == 1:
        createAccount()
    if num == 2:
        log_in_account()
Operations(1)