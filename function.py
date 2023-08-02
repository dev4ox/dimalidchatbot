import sqlite3
import datetime
import uuid
from yookassa import Configuration, Payment
import setting


key_return_list = [11,12,13,14,15]

# Создание базы данных
def create_db():
    try:
        conn = sqlite3.connect('dima_bot.db')
        cursor = conn.cursor()
        cursor.execute('''
                        CREATE TABLE IF NOT EXISTS users (
                            user_id INTEGER PRIMARY KEY,
                            username TEXT,
                            first_name TEXT,
                            phone TEXT,
                            email TEXT,
                            sub_pub BOOLEAN,
                            sub_priv BOOLEAN,
                            reg_date TEXT
                        )
                        ''')
        cursor.execute('''
                        CREATE TABLE IF NOT EXISTS payments (
                            user_id INTEGER PRIMARY KEY,
                            count TEXT,
                            payment_id TEXT,
                            date TEXT
                        )
                        ''')
    except Exception as e:
        print('Error create db', e)
    finally:
        cursor.close()
        conn.close()


# Запросы к базе данных, таблица users
def users_query(user_id: str, username: str = '', first_name: str = '', phone: str = '', email: str = '',
                sub_pub: bool = '', sub_priv: bool = '', key: int = 0):
    try:
        conn = sqlite3.connect('dima_bot.db')
        cursor = conn.cursor()

        # Проверяем, существует ли пользователь с таким id в базе данных
        cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
        existing_user = cursor.fetchone()

        # Обновление статуса подписки на паблик
        if existing_user and key == 1:
            cursor.execute("UPDATE users SET sub_pub=? WHERE user_id=?", (sub_pub, user_id))
        # Обновление статуса подписки на приват
        elif existing_user and key == 2:
            cursor.execute("UPDATE users SET sub_priv=? WHERE user_id=?", (sub_priv, user_id))
        # Обновление номера телефона
        elif existing_user and key == 3:
            cursor.execute("UPDATE users SET phone=? WHERE user_id=?", (phone, user_id))
        # Извлечение времени регистрации
        elif existing_user and key == 11:
            result = cursor.execute("SELECT reg_date FROM users WHERE user_id=?", (user_id,))
        else:
            # Получаем текущую дату и время
            current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            # Добавляем пользователя в базу данных со статусом подписки
            cursor.execute(
                'INSERT INTO users (user_id, username, first_name, phone, email, sub_pub, sub_priv, reg_date) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (user_id, username, first_name, phone, email, sub_pub, sub_priv, current_date))

        conn.commit()
    except Exception as e:
        print('Error users query', e)
    finally:
        cursor.close()
        conn.close()
        if key == key_return_list and result:
            return result


# Запросы к базе данных, таблица payments
def payments_query(user_id: str, count: str, payment_id: str, key: int):
    try:
        conn = sqlite3.connect('dima_bot.db')
        cursor = conn.cursor()
        if key == 1:
            # Запись в базу данных при успешной оплате
            current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                'INSERT INTO payments (user_id, count, payment_id, date) VALUES (?, ?, ?, ?)',
                (user_id, count, payment_id, current_date))

        conn.commit()
    except Exception as e:
        print('Error payments query', e)
    finally:
        cursor.close()
        conn.close()


# Проверка формата email
def check_email(email: str):
    pass


# Проверка формата номера телефона (79001234567)
def check_phone(phone: str):
    pass


# Проверка формата ФИО
def check_bio(bio: str):
    pass


# Проверка времени на получения бонуса
def check_time_bonus(user_id: str):
    reg_date_str = users_query(user_id, key=11)
    reg_date = datetime.datetime.strptime(reg_date_str, '%Y-%m-%d %H:%M')
    current_date = datetime.datetime.now()
    time_diff = current_date - reg_date
    if time_diff.total_seconds() < 15 * 60:
        return True
    else:
        return False



# Покупка через yookassa
def pay_order_yoo(user_id: str, bio: str, email: str, key: int):
    try:
        Configuration.account_id = setting.yooid
        Configuration.secret_key = setting.yootoken
        if key == 1:
            payment = Payment.create({
                "amount": {
                    "value": setting.count_sale,
                    "currency": "RUB"
                },
                "capture": True,
                "receipt": {
                    "customer": {
                        "full_name": bio,
                        "email": email
                    },
                    "items": [{
                        "description": setting.name_sale,
                        "amount": {
                            "value": setting.count_sale,
                            "currency": "RUB"
                        },
                        "vat_code": 1,
                        "quantity": "1.00",
                        "payment_subject": "service",
                        "payment_mode": "full_payment"
                    }],
                    "send": True
                },
                "metadata": {
                    "user_id": user_id
                }
            }, uuid.uuid4())
        elif key == 2:
            payment = Payment.create({
                "amount": {
                    "value": setting.count_full,
                    "currency": "RUB"
                },
                "capture": True,
                "receipt": {
                    "customer": {
                        "full_name": bio,
                        "email": email
                    },
                    "items": [{
                        "description": setting.name_full,
                        "amount": {
                            "value": setting.count_full,
                            "currency": "RUB"
                        },
                        "vat_code": 1,
                        "quantity": "1.00",
                        "payment_subject": "service",
                        "payment_mode": "full_payment"
                    }],
                    "send": True
                },
                "metadata": {
                    "user_id": user_id
                }
            }, uuid.uuid4())
        else:
            raise
        return payment.confirmation.confirmation_url
    except Exception as e:
        print('Error create order', e)
