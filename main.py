import telebot
import time
from telebot import types
import setting
import function
import bot_text

bot = telebot.TeleBot(setting.tgtoken)

# При успешной оплате
def successful_payment(message, count, payment_id):
    function.payments_query(message.chat.id, count, payment_id, 1)
    # Обработка успешной оплаты
    bot.send_message(setting.id_channel_info,
                     f'Пользователь: {message.from_user.first_name} {message.from_user.last_name}\n'
                     f'Ник: @{message.from_user.username}, id: {message.chat.id}\n'
                     f'Купил подписку за {count} RUB\n')


# Покупка подписки
def user_buy_sub(message, bio, email):
    try:
        if function.check_time_bonus(message.chat.id):
            buy_button = types.InlineKeyboardMarkup(row_width=1)
            buy_button.add(types.InlineKeyboardButton(bot_text.buy_sale_button,
                                                      url=function.pay_order_yoo(message.chat.id, bio, email, 1)))
            bot.send_message(message.chat.id, bot_text.buy_sale, reply_markup=buy_button)
        else:
            buy_button = types.InlineKeyboardMarkup(row_width=1)
            buy_button.add(types.InlineKeyboardButton(bot_text.buy_full_button,
                                                      url=function.pay_order_yoo(message.chat.id, bio, email, 2)))
            bot.send_message(message.chat.id, bot_text.buy_full, reply_markup=buy_button)
    except Exception as e:
        print('Error buy sub', e)
    finally:
        pass


# Получение данных пользователя для покупки
def user_give_info(message):
    pass


# Проверка подписки
def check_subscribe(user_id, check_channel):
    try:
        chat_member = bot.get_chat_member(check_channel, user_id)
        if chat_member.status == 'member' or chat_member.status == 'administrator':
            # Обновляем статус подписки public
            function.users_query(user_id, sub_pub=True, key=1)
            return True
    except telebot.apihelper.ApiException as e:
        print('Error check sub', e)
    return False

def user_give_bonus(message):
    user_id = message.chat.id
    subpub_button = types.InlineKeyboardMarkup(row_width=1)
    subpub_button.add(types.InlineKeyboardButton(bot_text.notsub_button, url=setting.url_channel_public))
    bonus_button = types.InlineKeyboardMarkup(row_width=1)
    bonus_button.add(types.InlineKeyboardButton(bot_text.bonus_button, callback_data='user_buy_sub'))
    if not check_subscribe(setting.id_channel_public, user_id):
        bot.send_message(user_id, bot_text.notsub, reply_markup=subpub_button)
    # Проверка подписки
    while True:
        user_is_subscribed = check_subscribe(user_id, setting.id_channel_public)
        if user_is_subscribed:
            bot.send_message(user_id, bot_text.bonus, parse_mode='html', reply_markup=bonus_button)
            break
        time.sleep(5)


def start_bot():
    @bot.message_handler(commands=['start', 'admin'])
    def welcome(message):
        user_id = message.chat.id
        if message.text == '/start':
            # Запрос к БД с проверкой/добавлением пользователя
            function.users_query(user_id, message.from_user.username, message.from_user.first_name)
            # Отправка приветственного сообщения
            welcome_button = types.InlineKeyboardMarkup(row_width=1)
            welcome_button.add(types.InlineKeyboardButton(bot_text.welcome_button, callback_data='user_give_bonus'))
            with open('welcome.jpg', 'rb') as photo:
                bot.send_photo(user_id, photo=photo, parse_mode='html', caption=bot_text.welcome,
                               reply_markup=welcome_button)

        elif message.text == '/admin' and user_id in setting.admin_id:
            admin_button = types.InlineKeyboardMarkup(row_width=2)
            admin_button.add(
                types.InlineKeyboardButton(text='Пользователи', callback_data='admin_view_user'),
                types.InlineKeyboardButton(text='Добавить в БД', callback_data='admin_add_user')
            )
            bot.send_message(user_id, 'Меню администратора', reply_markup=admin_button)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_inline(call):
        if call.data == 'user_buy_sub':
            user_buy_sub(call.message)
        if call.data == 'user_give_bonus':
            user_give_bonus(call.message)
        if call.data == 'admin_view_user':
            pass
        if call.data == 'admin_add_user':
            pass

    bot.polling(none_stop=True)


if __name__ == '__main__':
    function.create_db()
    def infinity_start():
        try:
            start_bot()
        except:
            infinity_start()
    infinity_start()