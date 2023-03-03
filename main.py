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
    time.sleep(2)

    soupUrlReq = bs(urlReq.text, 'lxml')
    time.sleep(1)
    # print(soupUrlReq)

    return soupUrlReq


def getAdsList(soupUrlReq):
    adsMainList = set(soupUrlReq.findAll('div', class_="latest_article_each"))
    adsMainList.update(set(soupUrlReq.findAll('div', class_="latest_article_each latest_article_each_coloured")))
    time.sleep(4)
    return adsMainList



def getAdsMainInfo(singleAdText):
    singleAdDict = {}
    adMainInfo = singleAdText.find(
        lambda tag: tag.name == 'div' and tag.get('class') == ['DesktopArticleLayout'])

    if adMainInfo:
        try:
            adLink = 'https://www.ss.ge' + adMainInfo.find('div', class_ = 'latest_desc').find('a').get('href')

            id = re.search(r'[-]\d{7}', adLink)[0][1:]

            title = adMainInfo.find('span', class_ = 'TiTleSpanList').text
            # movieNameRu = adMainInfo.find('div', class_='base-movie-main-info_mainInfo__ZL_u3').find(
            #     'span', class_='styles_mainTitle__IFQyZ styles_activeMovieTittle__kJdJj').text
            #
            # movieNameOrig = adMainInfo.find('div', class_='desktop-list-main-info_secondaryTitleSlot__mc0mI').find(
            #     'span', class_='desktop-list-main-info_secondaryTitle__ighTt')
            # if movieNameOrig != None:
            #     movieNameOrig = movieNameOrig.text
            #     movieYearandDuration = adMainInfo.find(
            #         'span', class_="desktop-list-main-info_secondaryText__M_aus").contents[2]
            # else:
            #     movieNameOrig = movieNameRu
            #     movieYearandDuration = adMainInfo.find(
            #         'span', class_="desktop-list-main-info_secondaryText__M_aus").contents[0]
            #
            # movieCountryTypeDirector = adMainInfo.find(
            #     'span', class_="desktop-list-main-info_truncatedText__IMQRP").contents[0]

            singleAdDict = {
                               'Link': adLink,
                                'Id' : id,
                                'Title' : title
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
    print(list(AdsList)[:3])
    listAdsDicts = [getAdsMainInfo(ad) for ad in AdsList]
    print(listAdsDicts)
    print(len(listAdsDicts))
    with open(r'C:\Users\morozsa\PycharmProjects\flatsadsparser\urlsExample.txt', 'w') as file:
        for adDict in listAdsDicts:
            file.write(adDict['Link'] + '\n')
            file.write(adDict['Id'] + '\n')
            file.write(adDict['Title'] + '\n\n')


