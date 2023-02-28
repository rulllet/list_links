import telebot
from telebot import types
import json
import datetime
import configparser


config = configparser.ConfigParser() 
config.read("settings.ini")
bot = telebot.TeleBot(config["Telegram"]["token"])


def get_data():
    with open("data.json", "r", encoding="utf-8") as my_data:
        result_json = my_data.read()
    result_json = json.loads(result_json)
    return result_json


def data_user(data_user) -> None:
    if data_user.is_bot != True:
        user = (datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), str(data_user.id), 
                'https://t.me/' + data_user.username, data_user.first_name, data_user.last_name)
        with open("data_users.txt", "a") as file:
            file.write(" ".join(user) + '\n')


def greetings_message(data_bot):
    greetings_menu = types.InlineKeyboardMarkup()
    button_catalog = types.InlineKeyboardButton('Список ссылок', callback_data='catalog')
    greetings_menu.add(button_catalog)
    for instructions_button in data_bot["instructions"]:
        greetings_menu.add(types.InlineKeyboardButton(instructions_button["question"], 
                                                      callback_data=instructions_button["call_back_data"]))
    return greetings_menu


@bot.message_handler(commands=['start'])
def start(message):
    data_user(message.from_user)
    data_bot = get_data()
    try:
        bot.delete_message(message.chat.id, message.message_id-1)
    except:
        print("Сообщение не найдено")
    bot.send_message(message.chat.id, data_bot["greetings"].format(message.from_user), 
                     reply_markup=greetings_message(data_bot))


@bot.callback_query_handler(func=lambda call:True)
def catalog(call):
    data_bot = get_data()
    catalog_menu = types.InlineKeyboardMarkup()
    for link_list in data_bot["link_list"]:
        catalog_menu.add(types.InlineKeyboardButton(link_list["name_link"], url=link_list["url_link"]))
    button_back = types.InlineKeyboardButton("Назад", callback_data='back')
    catalog_menu.add(button_back)

    if call.data == 'catalog':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text="Список ссылок".format(call.message.from_user), reply_markup=catalog_menu)
    elif call.data[0:11] == 'instruction':
        for instruction_answer in data_bot["instructions"]:
            if instruction_answer["call_back_data"] == call.data:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=instruction_answer["answer"].format(call.message.from_user), 
                              reply_markup=types.InlineKeyboardMarkup().add(button_back))
    elif call.data == 'back':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=data_bot["greetings"].format(call.message.from_user), 
                              reply_markup=greetings_message(data_bot))
    else:
        bot.send_message(call.message.chat.id, 'Упс что-то пошло не так, перезапустите бота')

bot.polling(none_stop=True)