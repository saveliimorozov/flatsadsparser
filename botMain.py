import time
import telebot

import datetime as dt

from auth_data import token
import json


def telegram_bot(token):
    from telebot import types
    bot = telebot.TeleBot(token)

    def get_user_info(id:int):
        dirPath = rf'C:\Users\morozsa\PycharmProjects\flatsadsparser\toBot\{str(id)}'
        with open(dirPath + r'\user_info.json', 'r') as file:
            curParams = json.loads(file.read())

        return curParams



    @bot.message_handler(commands=['start'])
    def start_message(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Set params")
        btn2 = types.KeyboardButton("Learn more about bot")
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, f"Hello, {message.from_user.first_name}! " \
                                          f"You can find flats in Georgia here.\nPlease use menu below.",
                         reply_markup=markup)

    @bot.message_handler(content_types=['text'])
    def text_message_handler(message):
        try:
            import os.path

            dirPath = rf'C:\Users\morozsa\PycharmProjects\flatsadsparser\toBot\{str(message.chat.id)}'
            # print(dirPath)
            # print(message.chat)
            if not os.path.exists(dirPath):
                os.mkdir(dirPath)
                os.mkdir(dirPath + r'\Logs')
                os.mkdir(dirPath + r'\Output')
                with open(dirPath + r'\user_info.json', 'w') as file:
                    json.dump({'id': message.chat.id,
                               'username': message.chat.username,
                               'first_name': message.chat.first_name,
                               'last_name': message.chat.last_name,
                               'searchParams': {'city': None,
                                                'flat/house': None,
                                                'priceTo': None
                                                }
                               }, file)

            def set_params(message):
                curParams = get_user_info(message.chat.id).get('searchParams')
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn1 = types.KeyboardButton("City")
                btn2 = types.KeyboardButton("Flat/House")
                btn3 = types.KeyboardButton("Price to($)")
                btn4 = types.KeyboardButton("Main menu")
                markup.add(btn1, btn2, btn3, btn4)

                bot.send_message(message.chat.id, f'Please use the menu below to edit params.\n' \
                                                      f'Your current params: {curParams}', reply_markup=markup)

            if message.text == 'City':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn1 = types.KeyboardButton("Tbilisi")
                btn2 = types.KeyboardButton("Kobuleti")
                btn3 = types.KeyboardButton("⏎")
                markup.add(btn1, btn2, btn3)
                bot.send_message(message.chat.id, 'Choose a city', reply_markup=markup)

            elif message.text == 'Set params':
                set_params(message)


            elif message.text == '⏎':
                set_params(message)

            elif message.text == 'Tbilisi' or message.text == 'Kobuleti':
                curParams = get_user_info(message.chat.id)
                print(curParams)

                curParams['searchParams']['city'] = message.text
                print(curParams)
                with open(dirPath + r'\user_info.json', 'w') as file:
                    json.dump(curParams, file)
                    bot.send_message(message.chat.id, f'Success! Current city: {message.text}')
                    time.sleep(1)
                set_params(message)
            elif message.text == 'Flat/House':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn1 = types.KeyboardButton("Flat")
                btn2 = types.KeyboardButton("House")
                btn3 = types.KeyboardButton("⏎")
                markup.add(btn1, btn2, btn3)
                bot.send_message(message.chat.id, 'Choose a property type', reply_markup=markup)

            elif message.text == 'Flat' or message.text == 'House':
                curParams = get_user_info(message.chat.id)
                print(curParams)

                curParams['searchParams']['flat/house'] = message.text
                print(curParams)
                with open(dirPath + r'\user_info.json', 'w') as file:
                    json.dump(curParams, file)
                    bot.send_message(message.chat.id, f'Success! Current property type: {message.text}')
                    time.sleep(1)
                set_params(message)

            elif message.text == 'Price to($)':
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn3 = types.KeyboardButton("⏎")
                markup.add(btn3)
                bot.send_message(message.chat.id, 'Send max price per month(in USD):', reply_markup=markup)

            elif message.text.isdigit():
                curParams = get_user_info(message.chat.id)
                print(curParams)

                curParams['searchParams']['priceTo'] = message.text
                print(curParams)
                with open(dirPath + r'\user_info.json', 'w') as file:
                    json.dump(curParams, file)
                    bot.send_message(message.chat.id, f'Success! Current max price in USD: {message.text}')
                    time.sleep(1)
                set_params(message)




            else:
                start_message(message)

        except Exception as err:
            print(f'Something went wrong...\n{err}')

    bot.infinity_polling()

telegram_bot(token)