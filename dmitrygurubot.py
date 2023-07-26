import telebot
import sqlite3
import datetime
import time

bot = telebot.TeleBot('6360450978:AAGN2oMWGXqhpyZ89Px4huPbtmxklyaSKVM')
channel_check = '-1001979683693'

bonus_message = '<b>Поздравляю!</b> Ты уже на шаг ближе к своей цели!\n\n' \
                'У меня есть для тебя еще одна крутая новость🔥\n\n' \
                'Прямо сейчас я веду набор в свой закрытый телеграмм канал где я каждый день с 1 августа в 12:00 буду выходить в прямой эфир и рассказывать какие конкретные действия я делаю чтобы создать многомиллионную компанию.\n\n' \
                '<u>Доступ к нему будет закрыт 31.07.2023г в 23:59.</u>\n\n' \
                'Если ты хочешь узнать пошаговый план по запуску успешного бизнеса, а именно: как собрать команду, где брать клиентов, как заключать договора, как масштабироваться, как внедрять систему аналитики, как привлекать инвестиции и многие другие бизнес инструменты и процессы, то прямо сейчас оплачивай доступ со скидкой 70% всего <s>3200₽</s>=990₽\n\n' \
                '<b>ВАЖНО!</b>👇\n' \
                'Скидка действует всего 5 минут.\n' \
                'Дальше доступ можно будет приобрести только за полную стоимость.\n\n' \
                'Успей попасть в окружение миллионера по цене одной пиццы 🍕\n\n' \
                '<i>P.s. сразу же после оплаты пришлем тебе приглашение в канал.</i>\n' \
                '<i>P.s.s. этот канал не будет удаляться и останется у тебя как полный пошаговый план</i>\n\n' \
                'Вот кнопка на оплату, скорее оплачивай, время уже идет 👇' \
# Функция для добавления пользователя в базу данных или обновления статуса подписки
def add_or_update_user(user_id, first_name, last_name, phone_number, subscription_status):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    #Проверка, есть ли такая БД
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                phone_number TEXT,
                registration_date TEXT,
                subscription_status BOOLEAN
            )
        ''')
    # Проверяем, существует ли пользователь с таким id в базе данных
    cursor.execute("SELECT id FROM users WHERE id=?", (user_id,))
    existing_user = cursor.fetchone()

    # Если пользователь уже существует, обновляем статус подписки
    if existing_user:
        cursor.execute("UPDATE users SET subscription_status=? WHERE id=?", (subscription_status, user_id))
    else:
        # Получаем текущую дату и время
        current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Добавляем пользователя в базу данных со статусом подписки
        cursor.execute('INSERT INTO users (id, first_name, last_name, phone_number, registration_date, subscription_status) VALUES (?, ?, ?, ?, ?, ?)',
                       (user_id, first_name, last_name, phone_number, current_date, subscription_status))

    conn.commit()
    conn.close()

def check_subscription(chat_id):
    try:
        chat_member = bot.get_chat_member(channel_check, chat_id)
        if chat_member.status == "member":
            # Обновляем статус подписки на True в базе данных
            add_or_update_user(chat_id, '', '', '', True)
            return True
    except telebot.apihelper.ApiException:
        # Обработка исключения, если пользователь не найден в канале
        pass
    return False

def start_bot():
    @bot.message_handler(commands=['start'])
    def start(message):
        chat_id = message.chat.id
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        try:
            phone_number = message.from_user.phone_number  # Допустим, у телеграмм-бота есть такая возможность
        except:
            phone_number = 0

        # Приветственное сообщение
        text = '<b>Привет будущий миллионер</b> 👋\n' \
               'Я покажу тебе, как сделать бизнес с нуля.\n' \
               'Самым <a href="https://t.me/dimonbataysk/103"><u>активным</u></a> я плачу деньги!\n' \
               'Присоединяйся и стань частью истории!\n\n' \
               'Твои три шага к успеху:\n' \
               '1. <i>Подписывайся на канал</i>\n' \
               '2. <i>Делай активность</i>\n' \
               '3. <i>Получай вознаграждение</i>'

        bot.send_message(chat_id, text, parse_mode="html")

        # Добавление пользователя
        add_or_update_user(chat_id, first_name, last_name, phone_number, False)

        # Проверка подписки
        time.sleep(10)
        user_is_subscribed = check_subscription(chat_id)
        if user_is_subscribed == False:
            bot.send_message(chat_id, 'Твой ход. Действуй! 💪')
        # Если пользователь не подписан, то ждём подписки (проблема с потоками?)
        while not user_is_subscribed:
            user_is_subscribed = check_subscription(chat_id)
            time.sleep(5)

        # Если пользователь подписан
        bot.send_message(chat_id, bonus_message, parse_mode='html')

    bot.polling(none_stop=True)

start_bot()