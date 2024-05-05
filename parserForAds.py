import time
import telebot
from telebot import types

import requestConfig as rc
import re
import datetime as dt
import requests as req
from bs4 import BeautifulSoup as bs
import sys
from auth_data import token
import json
# import random
# import schedule

activeUsrsFile = rf'{sys.path[0]}/toBot/activeUsers.txt'
mainDir = rf'{sys.path[0]}/toBot'

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


def urlMaker(params):
    url = ''
    # print('Please input options like:\nДом/Квартира, Город, Цена до($)')
    # params = list(map(lambda x: str(x).lower().strip(), input().split(',')))
    paramsLenNeeded = 4
    if len(params) != paramsLenNeeded:
        print('Wrong data')
        sys.exit()

    maker = rc.urlMakerDict
    try:
        url = 'https://home.ss.ge/ru/' + maker['недвижимость'] + '/l/' + maker[params['flat/house']] + \
              '/' + maker['аренда']  + '?order=1&page=1&currencyId=2&priceType=1' + \
              f'&municipalityId={maker[params["city"]][0]}&cityIdList={maker[params["city"]][1]}' + \
             f'&priceTo={params["priceTo"]}' + f'&advancedSearch=%7B%22withImageOnly%22%3Atrue%2C%22individualEntityOnly%22%3A{str(params["indEntOnly"]).lower()}%7D'
            
        # print(url)

              
        # url = 'https://home.ss.ge/ru/%D0%BD%D0%B5%D0%B4%D0%B2%D0%B8%D0%B6%D0%B8%D0%BC%D0%BE%D1%81%D1%82%D1%8C/l/%D0%9A%D0%B2%D0%B0%D1%80%D1%82%D0%B8%D1%80%D0%B0/%D0%90%D1%80%D0%B5%D0%BD%D0%B4%D0%B0?cityIdList=95&municipalityId=95&currencyId=2&priceType=1&priceTo=500&advancedSearch=%7B%22withImageOnly%22%3Atrue%2C%22individualEntityOnly%22%3Atrue%7D&order=1&page=1'


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

    with open(rf'{mainDir}/requestPage.html', 'w', encoding='utf-8') as file:
        file.write(urlReq.text)

    # with open(r'C:\Users\morozsa\PycharmProjects\flatsadsparser\requestPage.html', 'r', encoding='utf-8') as file:
    #     urlReq = file.read()
    soupUrlReq = bs(urlReq.text, 'lxml')
    time.sleep(1)
    # print(soupUrlReq)

    return soupUrlReq


def getAdsList(soupUrlReq):
    adsMainList = set(soupUrlReq.find('div', class_="sc-20a31af8-6 fvFQvV").findAll('a'))
    # print(adsMainList)
    # adsMainList.update(set(soupUrlReq.findAll('div', class_="latest_article_each latest_article_each_coloured")))
    time.sleep(2)
    return adsMainList


def getAdsMainInfo(singleAdText):
    # print(singleAdText)
    singleAdDict = {}
    adMainInfo = singleAdText.find(
        lambda tag: tag.name == 'div' and 'sc-802c130b-0' in  tag.get('class', []))
    if adMainInfo:
        try:
            adLink = 'https://home.ss.ge' + singleAdText.get('href')
            print(adLink)

            # id = re.search(r'[-]\d{7}', adLink)[0][1:]
            id = adLink[adLink.rfind('-')+1:] 

            print(id)

            title = adMainInfo.find('h2', class_='sc-6e54cb25-3 gxoxbm listing-detailed-item-title').text

            print(title)

            techInfo = [
                # re.sub(r'[\n\r\s]', "", adMainInfo.find('span', class_='icon-crop_free').text),
                # "Beds: " + re.sub(r'[\n\r\s]', "", adMainInfo.find('span', class_='icon-bed').text)
                adMainInfo.find('span', class_='icon-crop_free').parent.text,
                "Beds: " + adMainInfo.find('span', class_='icon-bed').parent.text
                                    
                    ]
            stairCount = adMainInfo.find('span', class_='icon-stairs')
            if stairCount:
                # techInfo.append(re.sub(r'[\n\r\s]', "", stairCount.text))
                techInfo.append(stairCount.parent.text)
            print(techInfo)

            desc = adMainInfo.find('p', class_='sc-6e54cb25-16 ijRIAC listing-detailed-item-desc').text.strip()

            addTime = str(adMainInfo.find('div', class_='create-date').text.strip())

            addTime = addTime.replace('/', '')
            print(addTime)

            price = re.sub(r'[\n\r\s]', "",
                           adMainInfo.find('span', class_='sc-6e54cb25-2 cikpcz listing-detailed-item-price').text)

            imagesList = [imgAtr.get('src') for imgAtr in adMainInfo.findAll('img', class_='sc-802c130b-3 dLxqKd')]

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


def dictToFile(ListAdsDicts: list, userId:int):
    path = mainDir + rf'/{str(userId)}/Output/{dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt'
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

    return "Success wrote to Output"


def existence_check(listAdsDicts: list, userId:int):
    filePath = mainDir + rf'/{str(userId)}/existingId.txt'
    with open(filePath, 'r') as file:
        existingIds = [line.strip() for line in file.readlines()]
    print(existingIds)
    itemsToBot = [item for item in listAdsDicts if item['Id'] not in existingIds]
    newIds = [item['Id'] for item in itemsToBot]
    print('Len of new items:',len(itemsToBot))

    with open(filePath, 'w') as file:
        for id in (existingIds + newIds):
            file.write(str(id) + '\n')
    return itemsToBot

def get_user_info(id: int):
    curParams = {}
    try:
        dirPath = rf'{mainDir}/{str(id)}'
        with open(dirPath + r'/user_info.json', 'r') as file:
            curParams = json.loads(file.read())
    except Exception as err:
        print(err)

    return curParams


def makeActUserParams(activeUsrsFile: str):
    actUserParamsDict = {}
    activeUsersSetInt = get_active_users_set(activeUsrsFile)
    for userId in activeUsersSetInt:
        userInfo = get_user_info(userId).get('searchParams')
        if userInfo:
            actUserParamsDict[userId] = userInfo
    # print(actUserParamsDict)
    return actUserParamsDict


def getResponsesForActUsers(actUserParamsDict):
    responsesForActUsers = {}
    for userId, params in actUserParamsDict.items():
        try:
            url = urlMaker(params)
            print(f'Actual page:{url}')

            AdsList = getAdsList(getSitePageInText(url))
            # sortedListAdsDicts = sorted([getAdsMainInfo(ad) for ad in AdsList],
            #                             key=lambda adDict: dt.datetime.strptime(adDict['AddTime'], "%d.%m.%Y %H:%M"),
            #                             reverse=True)
            sortedListAdsDicts = [getAdsMainInfo(ad) for ad in AdsList]
            ###existence_check
            finalListAdsDicts = existence_check(sortedListAdsDicts, userId)
            responsesForActUsers[userId] = finalListAdsDicts
            print(dictToFile(finalListAdsDicts,userId))
        except Exception as err:
            print(f'Smth went wrong while getting info from url:\n{err}')
    return responsesForActUsers


def get_ads_for_all_users():
    print('Start get_ads_for_all_users')
    responses = {}

    # bot = telebot.TeleBot(token)

    # def transform_and_send(responsesForActUsers: dict):
    #     for userId, response in responsesForActUsers.items():
    #         for singleAd in response:
    #
    #             textMessage = f"[{singleAd['Title']}]({singleAd['Link']})\n" \
    #                           f"{' '.join(singleAd['TechInfo'])}\n" + \
    #                           f"{singleAd['Price']}\n{singleAd['Desc']}\n" + \
    #                           f"{singleAd['AddTime']}\n"
    #             print(textMessage)
    #             images = []
    #             imagesFromResponse = singleAd['ImagesList']
    #
    #             if imagesFromResponse:
    #                 img1 = types.InputMediaPhoto(imagesFromResponse[-1], caption=textMessage, parse_mode='Markdown')
    #                 images.append(img1)
    #             print(f'Images after first:{images}')
    #             for i in range(len(imagesFromResponse) - 1):
    #                 imgNext = types.InputMediaPhoto(imagesFromResponse[i])
    #                 images.append(imgNext)
    #             print(f'Images finally:{images}')
    #             try:
    #                 bot.send_media_group(userId, images)
    #             except Exception as err:
    #                 print(f'Fail to send message:\n{err}')
    #     return 'Finished transform and sending messages'

    actUsrParams = makeActUserParams(activeUsrsFile)
    print(actUsrParams)
    if actUsrParams:
        responses = getResponsesForActUsers(actUsrParams)
        print(responses)
        # print(transform_and_send(responses))
    else:
        print('Nothing to send')
    return responses

# schedule.every(10).seconds.do(ads_to_bot, token)
#
# while True:
#     schedule.run_pending()
if __name__ == '__main__':

    get_ads_for_all_users()

#
# if __name__ == "__main__":
#     # url = urlMaker()
#     # print(f'Actual page:{url}')
#     #
#     # AdsList = getAdsList(getSitePageInText(url))
#     # print(len(AdsList))
#     #
#     # sortedListAdsDicts = sorted([getAdsMainInfo(ad) for ad in AdsList], key=lambda adDict: dt.datetime.strptime(adDict['AddTime'], "%d.%m.%Y %H:%M"),
#     #                             reverse=True)
#     # adsIdList = [item['Id'] for item in sortedListAdsDicts]
#     # adsToBot(adsIdList, sortedListAdsDicts)
#     try:
#         main()
#     except Exception as err:
#         print(err)


# print(activeUsersSetInt)

# print(dictToFile(sortedListAdsDicts))
