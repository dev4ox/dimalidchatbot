import telebot
import sqlite3
import datetime
import time
from telebot import types
import key

bot = telebot.TeleBot(key.tgtoken)

# Приветственное сообщение
welcome_mes = '<b>Привет будущий миллионер</b> 👋\n' \
               'Я покажу тебе, как сделать бизнес с нуля.\n' \
               'Самым активным я плачу деньги!\n' \
               'Присоединяйся и стань частью истории!\n\n' \
               'Твои три шага к успеху:\n' \
               '1. <i>Подписывайся на канал</i>\n' \
               '2. <i>Делай активность</i>\n' \
               '3. <i>Получай вознаграждение</i>'
# Бонусное сообщение
bonus_mes = '<b>Поздравляю!</b> Ты уже на шаг ближе к своей цели!\n\n' \
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
                'Вот кнопка на оплату, скорее оплачивай, время уже идет 👇'

# Покупка через ЮКасса
def buy_sub(user_id):
    url = 't.me/gurutda'
    return url




# Функция для добавления пользователя в базу данных или обновления статуса подписки
def add_or_update_user(user_id, username, first_name, last_name, subpub, subpriv, buy_sub):
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    reg_date TEXT,
                    subpub BOOLEAN,
                    subpriv BOOLEAN,
                    buy_sub INTEGER
                )
            ''')
        # Проверяем, существует ли пользователь с таким id в базе данных
        cursor.execute("SELECT id FROM users WHERE id=?", (user_id,))
        existing_user = cursor.fetchone()
        # Если пользователь уже существует, обновляем статус подписки
        if existing_user:
            cursor.execute("UPDATE users SET subpub=? WHERE id=?", (subpub, user_id))
        else:
            # Получаем текущую дату и время
            current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Добавляем пользователя в базу данных со статусом подписки
            cursor.execute('INSERT INTO users (id, username, first_name, last_name, reg_date, subpub, subpriv, buy_sub) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                           (user_id, username, first_name, last_name, current_date, subpub, subpriv, buy_sub))
        conn.commit()
    except Exception as e:
        pass
    finally:
        conn.close()

# Проверка подписки
def check_pubsub(user_id, check_channel):
    try:
        chat_member = bot.get_chat_member(user_id, check_channel)
        if chat_member.status == 'member' or chat_member.status == 'administrator':
            # Обновляем статус подписки на True в базе данных
            add_or_update_user(user_id, '', '', '', True, '', '')
            return True
    except telebot.apihelper.ApiException:
        pass
    return False

def admin_add_user(message):
    bot.send_message()

#Обработка команды start
def command_start(message, user_id):
    bot.send_message(user_id, welcome_mes, parse_mode="html", reply_to_message_id=bot.send_photo(user_id, open('welcome.jpg', 'rb')).message_id)
    # Добавление пользователя
    add_or_update_user(user_id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, False, False, 0)
    # Проверка подписки
    user_is_subscribed = check_pubsub(user_id, key.channel_public)
    if user_is_subscribed == False:
        bot.send_message(user_id, '<b>Твой ход. Действуй!</b> 💪', parse_mode='html')
    while not user_is_subscribed:
        user_is_subscribed = check_pubsub(user_id, key.channel_public)
        time.sleep(5)
    # Если пользователь подписан
    buy_button = types.InlineKeyboardMarkup(row_width=1)
    buy_button.add(types.InlineKeyboardButton(text='💎 Купить доступ', callback_data='user_buy_sub'))
    bot.send_message(user_id, bonus_mes, parse_mode='html', reply_markup=buy_button)

# Обработка команды admin
def command_admin(message, user_id):
    admin_button = types.InlineKeyboardMarkup(row_width=2)
    admin_button.add(
        types.InlineKeyboardButton(text='Пользователи', callback_data='admin_view_user'),
        types.InlineKeyboardButton(text='Добавить в БД', callback_data='admin_add_user')
    )
    bot.send_message(user_id, 'Меню админа', reply_markup=admin_button)


def start_bot():
    @bot.message_handler(commands=['start', 'admin'])
    def welcome(message):
        user_id = message.chat.id
        if message.text == '/start':
            command_start(message, user_id)
        elif message.text == '/admin' and user_id in key.admin_id:
            command_admin(message, user_id)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_inline(call):
        if call.data == 'user_buy_sub':
            buy_sub(call.message)
        if call.data == 'admin_view_user':
            pass
        if call.data == 'admin_add_user':
            admin_add_user(call.message)

    bot.polling(none_stop=True)
start_bot()
