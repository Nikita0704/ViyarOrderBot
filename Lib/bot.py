import config
import telebot
from telebot import types
from string import Template
import time

bot = telebot.TeleBot(config.TOKEN)

user_dict = {}


class User:
    def __init__(self, city):
        self.city = city

        keys = ['fullname', 'phone', 'mail', 'deliveryAdress', 'choice', 'next', 'orderDate', 'photo']

        for key in keys:
            self.key = None


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item1 = types.KeyboardButton('Створити замовлення')
    markup.add(item1)

    bot.send_message(message.chat.id,
                     'Вітаю в боті для швидкого створення замовлення, {0.first_name}'.format(message.from_user),
                     reply_markup=markup)


@bot.message_handler(content_types=['text'])
def user_reg(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    itembtn1 = types.KeyboardButton('Київ')
    itembtn2 = types.KeyboardButton('Одеса')
    itembtn3 = types.KeyboardButton('Дніпро')
    itembtn4 = types.KeyboardButton('Харків')
    itembtn5 = types.KeyboardButton('Львів')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5)

    msg = bot.send_message(message.chat.id, 'Оберіть ваше місто', reply_markup=markup)
    bot.register_next_step_handler(msg, process_city_step)


def process_city_step(message):
    try:
        chat_id = message.chat.id
        user_dict[chat_id] = User(message.text)

        markup = types.ReplyKeyboardRemove(selective=False)

        msg = bot.send_message(chat_id, "Вкажіть ваше Прізвище та Імя", reply_markup=markup)
        bot.register_next_step_handler(msg, process_fullname_step)

    except Exception as e:
        bot.reply_to(message, 'Щось пішло не так1!')


def process_fullname_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.fullname = message.text

        msg = bot.send_message(chat_id, 'Вкажіть ваш номер телефону')
        bot.register_next_step_handler(msg, process_phone_step)
    except Exception as e:
        bot.reply_to(message, 'Щось пішло не так!')


def process_phone_step(message):
    try:
        int(message.text)

        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.phone = message.text

        msg = bot.send_message(chat_id, 'Вкажіть свою електронну адресу')
        bot.register_next_step_handler(msg, process_mail_step)

    except Exception as e:
        bot.reply_to(message, 'Щось пішло не так!')


def process_mail_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.mail = message.text

        msg = bot.send_message(chat_id, 'Вкажіть адресу')
        bot.register_next_step_handler(msg, next_step)
    except Exception as e:
        bot.reply_to(message, 'Щось пішло не так!')


def next_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.deliveryAdress = message.text
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        itembtn1 = types.KeyboardButton('Так')
        itembtn2 = types.KeyboardButton('Ні')

        markup.add(itembtn1, itembtn2)

        msg = bot.send_message(message.chat.id, 'Бажаєте додати зображення?', reply_markup=markup)
        bot.register_next_step_handler(msg, choice)
    except Exception as e:
        bot.reply_to(message, 'Щось пішло не так!')


def choice(message):
    try:
        if message.chat.type == 'private':
            if message.text == 'Так':
                chat_id = message.chat.id
                user = user_dict[chat_id]
                user.choice = message.text

                msg = bot.send_message(chat_id, 'Додайте фото')
                bot.register_next_step_handler(msg, process_photo_step)
            else:
                chat_id = message.chat.id
                user = user_dict[chat_id]
                user.choice = message.text

                msg = bot.send_message(message.chat.id, 'Опишіть бажаний результат замовлення')
                bot.register_next_step_handler(msg, process_orderDate_step)
    except Exception as e:
        bot.reply_to(message, 'Щось пішло не так!')


def process_photo_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.photo = message.text

        bot.send_photo(config.CHANNEL_ID, message.photo[-1].file_id, user.fullname)

        msg = bot.send_message(message.chat.id, 'Опишіть бажаний результат замовлення')
        bot.register_next_step_handler(msg, process_orderDate_step)
    except Exception as e:
        bot.reply_to(message, 'Щось пішло не так!')


def process_orderDate_step(message):
    # try:
    chat_id = message.chat.id
    user = user_dict[chat_id]
    user.orderDate = message.text
    # Ваша заявка
    bot.send_message(chat_id, getRegData(user, 'Ваша заявка', message.from_user.first_name + "\nНайближчим часом з вами зв'яжеться наш адміністратор"), parse_mode='Markdown')
    # Отправить в группу
    bot.send_message(config.CHANNEL_ID, getRegData(user, 'Заявка от бота', bot.get_me().username),
                     parse_mode='Markdown')


# except Exception as e:
#     bot.reply_to(message, 'Щось пішло не так!')

def getRegData(user, title, name):
    t = Template('$title *$name* \n Місто: *$userCity* \n ПІБ: *$fullname* \n Номер телефону: *$phone* \n '
                 'Почта: *$mail* \n Адреса доставки: *$deliveryAdress* \n Опис замовлення: *$orderDate* \n')

    return t.substitute({
        'title': title,
        'name': name,
        'userCity': user.city,
        'fullname': user.fullname,
        'phone': user.phone,
        'mail': user.mail,
        'deliveryAdress': user.deliveryAdress,
        'orderDate': user.orderDate,


    })


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()

if __name__ == '__main__':  # чтобы код выполнялся только при запуске в виде сценария, а не при импорте модуля
    try:
        bot.polling(none_stop=True)  # запуск бота
    except Exception as e:
        print(e)  # или import traceback; traceback.print_exc() для печати полной инфы
        time.sleep(15)
