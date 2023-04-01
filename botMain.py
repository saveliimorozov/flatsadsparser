import time
import telebot
import parser
import threading
import datetime as dt

from auth_data import token
import json


activeUsrsFile = r'D:\SAVELII\Python projects\flatsadsparser\toBot\activeUsers.txt'
mainDir = r'D:\SAVELII\Python projects\flatsadsparser\toBot'

botCreator = '@armpitwife'

def get_active_users_set(activeUsrsFile: str):
    with open(activeUsrsFile, 'r') as file:
        activeUsersSetStr = set(file.read().split(';'))
        activeUsersSetStr.discard('')
        activeUsersSetInt = set()
        print(activeUsersSetStr)
        if activeUsersSetStr:
            activeUsersSetInt = {int(user) for user in activeUsersSetStr}
        print(f'Active users list: {activeUsersSetInt}')
        return activeUsersSetInt





def telegram_bot(token):
    from telebot import types
    bot = telebot.TeleBot(token)

    def get_user_info(id: int):
        dirPath = mainDir + '\\' + str(id)
        with open(dirPath + r'\user_info.json', 'r') as file:
            curParams = json.loads(file.read())

        return curParams

    valuesDictFwd = {
        'ON✅': True,
        'OFF❌': False
    }
    valuesDictBack = {v: k for k, v in valuesDictFwd.items()}






    @bot.message_handler(commands=['start'])
    def start_message(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Set params")
        btn2 = types.KeyboardButton("Learn more about bot")
        btn3 = types.KeyboardButton("On/Off sending")
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, f"Hello, {message.from_user.first_name}! " \
                                          f"You can find flats in Georgia here.\nPlease use menu below.",
                         reply_markup=markup)

    @bot.message_handler(content_types=['text'])
    def text_message_handler(message):
        dirPath = mainDir + '\\' + str(message.chat.id)
        try:
            import os.path

            # dirPath = mainDir + '\\' + str(message.chat.id)
            # print(dirPath)
            # print(message.chat)
            if not os.path.exists(dirPath):
                os.mkdir(dirPath)
                os.mkdir(dirPath + r'\Logs')
                os.mkdir(dirPath + r'\Output')
                with open(dirPath + r'\existingId.txt', 'w') as file:
                    pass
                with open(dirPath + r'\user_info.json', 'w') as file:
                    json.dump({'id': message.chat.id,
                               'username': message.chat.username,
                               'first_name': message.chat.first_name,
                               'last_name': message.chat.last_name,
                               'searchParams': {'city': 'Tbilisi',
                                                'flat/house': 'Flat',
                                                'priceTo': 500
                                                },
                               'activeFlag': False
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
            def on_off_sending(message):
                curParams = get_user_info(message.chat.id)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn1 = types.KeyboardButton("ON✅")
                btn2 = types.KeyboardButton("OFF❌")
                btn3 = types.KeyboardButton("Main menu")
                markup.add(btn1, btn2, btn3)
                bot.send_message(message.chat.id, f'You can enable and disable sending messages with new ads.\n'
                                                  f'Current status: {valuesDictBack[curParams.get("activeFlag")]} ',
                                 reply_markup=markup)

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




            elif message.text == 'On/Off sending':
                on_off_sending(message)



            elif message.text == 'ON✅' or message.text == 'OFF❌':

                curParams = get_user_info(message.chat.id)
                print(curParams)

                curParams['activeFlag'] = valuesDictFwd[message.text]
                print(curParams)
                with open(dirPath + r'\user_info.json', 'w') as file:
                    json.dump(curParams, file)
                    bot.send_message(message.chat.id, f'Success! Current status: {message.text}')
                    time.sleep(1)

                activeUsersSetInt = get_active_users_set(activeUsrsFile)

                print(message.chat.id in activeUsersSetInt, valuesDictFwd[message.text] )
                if (message.chat.id in activeUsersSetInt) != valuesDictFwd[message.text]:

                    if message.chat.id in activeUsersSetInt:
                        activeUsersSetInt.discard(message.chat.id)
                    else:
                        activeUsersSetInt.add(message.chat.id)
                    with open(activeUsrsFile, 'w') as file:
                        for user in activeUsersSetInt:
                            file.write(str(user) + ";")
                on_off_sending(message)


            elif message.text == 'Learn more about bot':
                bot.send_message(message.chat.id, f'Author: {botCreator}')









            else:
                start_message(message)

        except Exception as err:
            print(f'Something went wrong...\n{err}')
        finally:
            with open(dirPath + rf'\Logs\{message.chat.username} log.txt', 'a', encoding='utf-8') as file:
                tconv = lambda x: time.strftime("%d.%m.%Y %H:%M:%S",
                                                time.localtime(x))  # Конвертация даты в читабельный вид
                file.write(f'{tconv(message.date)}: {message.text}\n')



    def send_ads_to_users(activeUsersSetInt):
        while True:
            responses = parser.get_ads_for_all_users()
            def transform_and_send(responsesForActUsers: dict):
                for userId, response in responsesForActUsers.items():
                    for singleAd in response:

                        textMessage = f"[{singleAd['Title']}]({singleAd['Link']})\n" \
                                      f"{' '.join(singleAd['TechInfo'])}\n" + \
                                      f"{singleAd['Price']}\n{singleAd['Desc']}\n" + \
                                      f"{singleAd['AddTime']}\n"
                        print(textMessage)
                        images = []
                        imagesFromResponse = singleAd['ImagesList']

                        if imagesFromResponse:
                            img1 = types.InputMediaPhoto(imagesFromResponse[-1], caption=textMessage,
                                                         parse_mode='Markdown')
                            images.append(img1)
                        print(f'Images after first:{images}')
                        for i in range(len(imagesFromResponse) - 1):
                            imgNext = types.InputMediaPhoto(imagesFromResponse[i])
                            images.append(imgNext)
                        print(f'Images finally:{images}')
                        try:
                            bot.send_media_group(userId, images)
                        except Exception as err:
                            print(f'Fail to send message:\n{err}')
                return 'Finished transform and sending messages'
            transform_and_send(responses)
            time.sleep(120)


    send_thread = threading.Thread(target=send_ads_to_users,daemon=True, args=(get_active_users_set(activeUsrsFile),))
    send_thread.start()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
    # bot.polling()


if __name__ == '__main__':
    telegram_bot(token)

