import vigener as cifer

import sqlite3
conn = sqlite3.connect("database.db")
cursor = conn.cursor()


cursor.execute("""CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
login TEXT,
password TEXT,
Account REAL
)
""")


cursor.execute("""CREATE TABLE IF NOT EXISTS credit(
id INTEGER PRIMARY KEY AUTOINCREMENT,
userId INT,
Amount REAL,
PPY REAL,
AdInfo TEXT
)
""")


# Операции
def Operations(num):
    def checkPassword(password):
        if len(password) < 8:
            print("Ваш пароль меньше 8 символов!")
            return True
        return False
    def checkLogin(login):
        cursor.execute("SELECT * FROM users")
        for logins in cursor.fetchall():
            if login == logins[2]:
                return True
        return False
    #Создание аккаунта
    def createAccount():
        name = input("Ваше ФИО: ")
        login = input("Ваш логин: ")
        while checkLogin(login):
            print(f"Ваш логин {login} совпадает с логином другого пользователя!")
            login = input("Ваш логин: ")

        password = input("Ваш пароль: ")
        while checkPassword(password):
            password = input("Введите пароль повторно: ")
        if len(password) < 8:
            print("Ваш пароль меньше 8 символов!")
            password = input("Ваш пароль: ")
            if '0123456789' not in password:
                print("Ваш пароль должен содержать не менее 1 цифры")
                password = input("Ваш пароль: ")
        cursor.execute(f"""INSERT INTO users (name, login, password, Account) VALUES ('{name}', '{login}', '{password}', 1000);""")
        conn.commit()#

    if num == 1:
        createAccount()
Operations(1)