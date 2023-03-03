import time
import requestConfig as rc
import re

import requests as req
from bs4 import BeautifulSoup as bs
import pandas as pd
import random

url = 'https://ss.ge/ru/%D0%BD%D0%B5%D0%B4%D0%B2%D0%B8%D0%B6%D0%B8%D0%BC%D0%BE%D1%81%D1%82%D1%8C/l/%D0%9A%D0%B2%D0%B0%D1%80%D1%82%D0%B8%D1%80%D0%B0/%D0%90%D1%80%D0%B5%D0%BD%D0%B4%D0%B0?Page=1&RealEstateTypeId=5&RealEstateDealTypeId=1&Sort.SortExpression=%22OrderDate%22%20DESC&MunicipalityId=95&CityIdList=95&PrcSource=2&CommercialRealEstateType=&PriceType=false&CurrencyId=2&PriceTo=500&Context.Request.Query[Query]=&WithImageOnly=true'


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

            id = re.search(r'[-]\d{7}', adLink)[0][1:]

            title = adMainInfo.find('span', class_='TiTleSpanList').text

            techInfo = [re.sub(r'[\n\r\s]',"",adMainInfo.find('div', class_ = 'latest_flat_km').text),
                        re.sub(r'[\n\r\s]',"",adMainInfo.find('div', class_='latest_flat_type').text),
                        re.sub(r'[\n\r\s]',"",adMainInfo.find('div', class_='latest_stair_count').text)
            ]

            addTime = adMainInfo.find('div', class_ = 'add_time').text.strip()

            price = re.sub(r'[\n\r\s]',"",adMainInfo.find('div', class_='price-spot dalla').find('div', class_='latest_price').text)





            singleAdDict = {
                'Link': adLink,
                'Id': id,
                'Title': title,
                'TechInfo' : techInfo,
                'AddTime' : addTime,
                'Price' : price
            }
        except Exception as err:
            print(err)
            print('Error single dict')
    else:
        print('Error single dict')

    return singleAdDict


if __name__ == "__main__":

    AdsList = getAdsList(getSitePageInText(url))
    print(len(AdsList))

    sortedListAdsDicts = sorted([getAdsMainInfo(ad) for ad in AdsList], key= lambda adDict: adDict['AddTime'], reverse=True)





    with open(r'C:\Users\morozsa\PycharmProjects\flatsadsparser\urlsExample.txt', 'w', encoding='utf-8') as file:
        for adDict in sortedListAdsDicts:
            file.write(adDict['Id'] + '\n')
            file.write(adDict['Link'] + '\n')
            file.write(adDict['Title'] + '\n')
            file.write(" ".join(adDict['TechInfo']) + '\n')
            file.write(adDict['Price'] + '\n')
            file.write(adDict['AddTime'] + '\n\n')



