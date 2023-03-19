import time

import telebot

import requestConfig as rc
import re
import datetime as dt
import requests as req
from bs4 import BeautifulSoup as bs
import sys
from auth_data import token
import json
import random
import schedule


def urlMaker(params):
    # print('Please input options like:\nДом/Квартира, Город, Цена до($),  Кол-во объявлений(20, 40, 60...)')
    # params = list(map(lambda x: str(x).lower().strip(), input().split(',')))
    paramsLenNeeded = 3
    if len(params) != paramsLenNeeded:
        print('Wrong data')
        sys.exit()

    maker = rc.urlMakerDict
    try:
        url = 'https://ss.ge/ru/' + maker['недвижимость'] + '/l/' + maker[params['flat/house']] + \
              '/' + maker['аренда'] + '/' + '?Sort.SortExpression=%22OrderDate%22%20DESC' + \
              f'&MunicipalityId={maker[params["city"]][0]}&CityIdList={maker[params["city"]][1]}' + \
              '&CurrencyId=2' + f'&PriceTo={params["priceTo"]}' + '&Page=1' + \
              '&Context.Request.Query[Query]=&WithImageOnly=true'


    except Exception as err:
        print('Nonexistent data')
        print(err)

    return url


def getSitePageInText(url: str):
    urlReq = req.get(url,
                     cookies=rc.cookies,
                     headers=rc.headers)

    time.sleep(1)
    print(urlReq)
    time.sleep(1)

    with open(r'C:\Users\morozsa\PycharmProjects\flatsadsparser\requestPage.html', 'w', encoding='utf-8') as file:
        file.write(urlReq.text)

    # with open(r'C:\Users\morozsa\PycharmProjects\flatsadsparser\requestPage.html', 'r', encoding='utf-8') as file:
    #     urlReq = file.read()
    soupUrlReq = bs(urlReq.text, 'lxml')
    time.sleep(1)
    # print(soupUrlReq)

    return soupUrlReq


def getAdsList(soupUrlReq):
    adsMainList = set(soupUrlReq.findAll('div', class_="latest_article_each"))
    adsMainList.update(set(soupUrlReq.findAll('div', class_="latest_article_each latest_article_each_coloured")))
    time.sleep(2)
    return adsMainList


def getAdsMainInfo(singleAdText):
    singleAdDict = {}
    adMainInfo = singleAdText.find(
        lambda tag: tag.name == 'div' and tag.get('class') == ['DesktopArticleLayout'])

    if adMainInfo:
        try:
            adLink = 'https://www.ss.ge' + adMainInfo.find('div', class_='latest_desc').find('a').get('href')
            print(adLink)

            id = re.search(r'[-]\d{7}', adLink)[0][1:]

            print(id)

            title = adMainInfo.find('span', class_='TiTleSpanList').text

            print(title)

            techInfo = [re.sub(r'[\n\r\s]', "", adMainInfo.find('div', class_='latest_flat_km').text),
                        re.sub(r'[\n\r\s]', "", adMainInfo.find('div', class_='latest_flat_type').text)
                        ]
            stairCount = adMainInfo.find('div', class_='latest_stair_count')
            if stairCount:
                techInfo.append(re.sub(r'[\n\r\s]', "", stairCount.text))
            print(techInfo)

            desc = adMainInfo.find('div', class_='DescripTionListB').text.strip()

            addTime = str(adMainInfo.find('div', class_='add_time').text.strip())

            addTime = addTime.replace('/', '')
            print(addTime)

            price = re.sub(r'[\n\r\s]', "",
                           adMainInfo.find('div', class_='price-spot dalla').find('div', class_='latest_price').text)

            imagesList = [imgAtr.get('data-src') for imgAtr in adMainInfo.findAll('img', class_='owl-lazy')]

            singleAdDict = {
                'Link': adLink,
                'Id': id,
                'Title': title,
                'TechInfo': techInfo,
                'AddTime': addTime,
                'Price': price,
                'ImagesList': imagesList,
                'Desc': desc
            }
        except Exception as err:
            print(err)
            print('Error single dict')
    else:
        print('Error single dict')

    return singleAdDict


def dictToFile(ListAdsDicts: list):
    path = rf'C:\Users\morozsa\PycharmProjects\flatsadsparser\Output\adsOutput{dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt'
    with open(path, 'w', encoding='utf-8') as file:
        for adDict in ListAdsDicts:
            file.write(adDict['Id'] + '\n')
            file.write(adDict['Link'] + '\n')
            file.write(adDict['Title'] + '\n')
            file.write(" ".join(adDict['TechInfo']) + '\n')
            file.write(adDict['Price'] + '\n')
            file.write(adDict['Desc'] + '\n')
            file.write(adDict['AddTime'] + '\n')
            file.write("\n".join(adDict['ImagesList']) + '\n\n')
            wholeString = f"{adDict['Id']}\n {adDict['Link']}\n" + \
                            f"{adDict['Title']}\n{''.join(adDict['TechInfo'])}\n" + \
                            f"{adDict['Price']}\n{adDict['Desc']}\n" + \
                            f"{adDict['AddTime']}\n{' '.join(adDict['ImagesList'])}\n\n"



    return wholeString


def adsToBot(adsIdList: list, listAdsDicts: list):
    with open(r'C:\Users\morozsa\PycharmProjects\flatsadsparser\toBot\existingIds.txt', 'r+') as file:
        existingIds = {line.strip() for line in file.readlines()}
        # print(existingIds)
        itemsToBot = [item for item in listAdsDicts if item['Id'] not in existingIds]
        print(len(itemsToBot))
        file.seek(0, 2)
        for item in itemsToBot:
            file.write('\n' + item['Id'])


def telegram_bot(token):
    from telebot import types
    bot = telebot.TeleBot(token)

    def get_user_info(id:int):
        dirPath = rf'C:\Users\morozsa\PycharmProjects\flatsadsparser\toBot\{str(id)}'
        with open(dirPath + r'\user_info.json', 'r') as file:
            curParams = json.loads(file.read())

        return curParams


    def ads_to_bot():

        url = urlMaker(get_user_info(362247085).get('searchParams'))
        print(f'Actual page:{url}')

        AdsList = getAdsList(getSitePageInText(url))
        print(len(AdsList))

        sortedListAdsDicts = sorted([getAdsMainInfo(ad) for ad in AdsList], key=lambda adDict: dt.datetime.strptime(adDict['AddTime'], "%d.%m.%Y %H:%M"),
                                    reverse=True)
        print(wholeString := dictToFile(sortedListAdsDicts))
        bot.send_message(362247085, wholeString)




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

    # schedule.every(1).minutes.do(ads_to_bot)
    ads_to_bot()

    bot.polling()
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)


if __name__ == "__main__":
    # url = urlMaker()
    # print(f'Actual page:{url}')
    #
    # AdsList = getAdsList(getSitePageInText(url))
    # print(len(AdsList))
    #
    # sortedListAdsDicts = sorted([getAdsMainInfo(ad) for ad in AdsList], key=lambda adDict: dt.datetime.strptime(adDict['AddTime'], "%d.%m.%Y %H:%M"),
    #                             reverse=True)
    # adsIdList = [item['Id'] for item in sortedListAdsDicts]
    # adsToBot(adsIdList, sortedListAdsDicts)
    telegram_bot(token)

    # print(dictToFile(sortedListAdsDicts))
