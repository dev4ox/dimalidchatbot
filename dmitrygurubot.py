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
                'Скидка действует <b>15 минут</b>.\n' \
                'Дальше доступ можно будет приобрести только за полную стоимость.\n\n' \
                'Успей попасть в окружение миллионера по цене одной пиццы 🍕\n\n' \
                '<i>P.s. сразу же после оплаты пришлем тебе приглашение в канал.</i>\n' \
                '<i>P.s.s. этот канал не будет удаляться и останется у тебя как полный пошаговый план</i>\n\n' \
                'Вот кнопка на оплату, скорее оплачивай, время уже идет 👇'


# Функция для добавления пользователя в базу данных или обновления статуса подписки
def db_query(user_id:str, username:str, first_name:str, last_name:str, subpub:bool, subpriv:bool, buy_sub:int, parametr:int):
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
        # Обновление статуса подписки на паблик
        if existing_user and parametr == 1:
            cursor.execute("UPDATE users SET subpub=? WHERE id=?", (subpub, user_id))
        # Обновление стоимости, за которую была куплена подписка
        elif existing_user and parametr == 2:
            cursor.execute("UPDATE users SET buy_sub=? WHERE id=?", (buy_sub, user_id))
        # Обновление статуса подписки на приват
        elif existing_user and parametr == 3:
            cursor.execute("UPDATE users SET subpriv=? WHERE id=?", (subpriv, user_id))
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


# Покупка через ЮКасса
def buy_sub(message, count:str):
    # Создание объекта счета на оплату
    invoice = telebot.types.InlineKeyboardMarkup()
    item = telebot.types.LabeledPrice(label='Оплата', amount=int(count+'00'))  # 100 копеек, то есть 1 рубль
    # Отправка запроса на оплату
    bot.send_invoice(message.chat.id, title='💎 Приватный доступ 💎',
                     description='Покупка доступа к закрытому каналу\n "Делаем 10 миллионов" | Реалити (бонус)',
                     provider_token=key.yootoken,
                     currency='RUB', prices=[item], start_parameter='pay_001', invoice_payload=count)


# Приглашение в приватный канал
def user_invite_subpriv(user_id):
    invite_priv_button = types.InlineKeyboardMarkup(row_width=1)
    invite_priv_button.add(types.InlineKeyboardButton(text='Приватный канал', url=key.url_channel_privat))
    try:
        db_query(user_id, '', '', '', '', True, '', 3)
        bot.send_message(user_id, 'Твой доступ в приватный канал\n👇👇👇', reply_markup=invite_priv_button)
        return True
    except telebot.apihelper.ApiException as e:
        return False


# Проверка подписки
def check_pubsub(check_channel, user_id):
    try:
        chat_member = bot.get_chat_member(check_channel, user_id)
        if chat_member.status == 'member' or chat_member.status == 'administrator':
            # Обновляем статус подписки на True в базе данных
            db_query(user_id, '', '', '', True, '', '', 1)
            return True
    except telebot.apihelper.ApiException:
        pass
    return False


def user_give_bonus(message):
    user_id = message.chat.id
    subpub_button = types.InlineKeyboardMarkup(row_width=1)
    subpub_button.add(types.InlineKeyboardButton(text='Подписаться', url=key.url_channel_public))
    buy_button = types.InlineKeyboardMarkup(row_width=1)
    buy_button.add(types.InlineKeyboardButton(text='Забрать бонус', callback_data='user_buy_sub'))
    if check_pubsub(key.id_channel_public, user_id) == False:
        bot.send_message(user_id, 'Сначала подпишись на канал', reply_markup=subpub_button)
    # Проверка подписки
    while True:
        user_is_subscribed = check_pubsub(key.id_channel_public, user_id)
        if user_is_subscribed == True:
            bot.send_message(user_id, bonus_mes, parse_mode='html', reply_markup=buy_button)
            break
        time.sleep(5)



def admin_add_user(message):
    pass


#Обработка команды start
def command_start(message, user_id):
    # Запрос к БД с проверкой/добавления пользователя
    db_query(user_id, message.from_user.username, message.from_user.first_name, message.from_user.last_name,
                       False, False, 0, 1)
    # Отправка приветственного сообщения
    bonus_button = types.InlineKeyboardMarkup(row_width=1)
    bonus_button.add(types.InlineKeyboardButton(text='💰 Твой бонус 💰', callback_data='user_give_bonus'))
    with open('welcome.jpg', 'rb') as photo:
        bot.send_photo(chat_id=user_id, photo=photo, parse_mode='html', caption=welcome_mes, reply_markup=bonus_button)


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
            buy_sub(call.message, '100')
            # if True:
            #     buy_sub(call.message, '990')
            # else:
            #     buy_sub(call.message, '3200')
        if call.data == 'admin_view_user':
            pass
        if call.data == 'admin_add_user':
            admin_add_user(call.message)
        if call.data == 'user_give_bonus':
            user_give_bonus(call.message)

    @bot.pre_checkout_query_handler(func=lambda query: True)
    def checkout(query):
        # Подтверждение оплаты
        bot.answer_pre_checkout_query(query.id, ok=True)

    @bot.message_handler(content_types=['successful_payment'])
    def successful_payment(message):
        sub_count = int(message.successful_payment.invoice_payload)
        db_query(message.chat.id, '', '', '', '', '', sub_count, 2)
        user_invite_confirm = user_invite_subpriv(message.chat.id)
        # Обработка успешной оплаты
        bot.send_message(key.id_channel_info, f'Пользователь: {message.from_user.first_name} {message.from_user.last_name}\n'
                                              f'Ник: @{message.from_user.username}, id: {message.chat.id}\n'
                                              f'Купил подписку за {sub_count} RUB\n'
                                              f'Статус подписки: {user_invite_confirm}')

    bot.polling(none_stop=True)
start_bot()
