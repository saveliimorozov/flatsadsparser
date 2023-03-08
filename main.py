import time
import requestConfig as rc
import re
import datetime as dt
import requests as req
from bs4 import BeautifulSoup as bs
import sys
import pandas as pd
import random

flatTbilisiWithPage = 'https://ss.ge/ru/%D0%BD%D0%B5%D0%B4%D0%B2%D0%B8%D0%B6%D0%B8%D0%BC%D0%BE%D1%81%D1%82%D1%8C/l/%D0%9A%D0%B2%D0%B0%D1%80%D1%82%D0%B8%D1%80%D0%B0/%D0%90%D1%80%D0%B5%D0%BD%D0%B4%D0%B0?Page=1&RealEstateTypeId=5&RealEstateDealTypeId=1&Sort.SortExpression=%22OrderDate%22%20DESC&MunicipalityId=95&CityIdList=95&PrcSource=2&CommercialRealEstateType=&PriceType=false&CurrencyId=2&PriceTo=500&Context.Request.Query[Query]=&WithImageOnly=true'

houseKobuleti = 'https://ss.ge/ru/%D0%BD%D0%B5%D0%B4%D0%B2%D0%B8%D0%B6%D0%B8%D0%BC%D0%BE%D1%81%D1%82%D1%8C/l/%D0%94%D0%BE%D0%BC/%D0%90%D1%80%D0%B5%D0%BD%D0%B4%D0%B0?Sort.SortExpression=%22OrderDate%22%20DESC&RealEstateTypeId=4&RealEstateDealTypeId=1&MunicipalityId=3&CityIdList=14&PrcSource=2&CommercialRealEstateType=&PriceType=false&CurrencyId=2&PriceTo=600&Context.Request.Query[Query]=&WithImageOnly=true&AreaOfYardFrom=&AreaOfYardTo='

houseTbilisiWithPage = 'https://ss.ge/ru/%D0%BD%D0%B5%D0%B4%D0%B2%D0%B8%D0%B6%D0%B8%D0%BC%D0%BE%D1%81%D1%82%D1%8C/l/%D0%94%D0%BE%D0%BC/%D0%90%D1%80%D0%B5%D0%BD%D0%B4%D0%B0?Page=2&RealEstateTypeId=4&RealEstateDealTypeId=1&MunicipalityId=95&CityIdList=95&PrcSource=2&CommercialRealEstateType=&PriceType=false&CurrencyId=2&PriceTo=500&Context.Request.Query[Query]=&WithImageOnly=true&AreaOfYardFrom=&AreaOfYardTo=&Sort.SortExpression=%22OrderDate%22%20DESC'

flatKobuletiWithPage = 'https://ss.ge/ru/%D0%BD%D0%B5%D0%B4%D0%B2%D0%B8%D0%B6%D0%B8%D0%BC%D0%BE%D1%81%D1%82%D1%8C/l/%D0%9A%D0%B2%D0%B0%D1%80%D1%82%D0%B8%D1%80%D0%B0/%D0%90%D1%80%D0%B5%D0%BD%D0%B4%D0%B0?Page=1&RealEstateTypeId=5&RealEstateDealTypeId=1&Sort.SortExpression=%22OrderDate%22%20DESC&MunicipalityId=3&CityIdList=14&PrcSource=2&CommercialRealEstateType=&PriceType=false&CurrencyId=2&PriceTo=600&Context.Request.Query[Query]=&WithImageOnly=true'


def urlMaker():
    print('Please input options like:\nДом/Квартира, ')
    params = list(map(lambda x: str(x).lower().strip(), input().split(',')))

    if len(params) != 1:
        print('Wrong data')
        sys.exit()

    maker = rc.urlMakerDict
    try:
        url = 'https://ss.ge/ru/' + maker['недвижимость'] + '/l/' + maker[params[0]] + '/' + maker['аренда'] + '/'
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
                'ImagesList': imagesList
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
        for adDict in sortedListAdsDicts:
            file.write(adDict['Id'] + '\n')
            file.write(adDict['Link'] + '\n')
            file.write(adDict['Title'] + '\n')
            file.write(" ".join(adDict['TechInfo']) + '\n')
            file.write(adDict['Price'] + '\n')
            file.write(adDict['AddTime'] + '\n')
            file.write("\n".join(adDict['ImagesList']) + '\n\n')

    return 'Success write to file'


if __name__ == "__main__":
    url = urlMaker()
    print(f'Actual page:{url}')

    AdsList = getAdsList(getSitePageInText(url))
    print(len(AdsList))

    sortedListAdsDicts = sorted([getAdsMainInfo(ad) for ad in AdsList], key=lambda adDict: dt.datetime.strptime(adDict['AddTime'], "%d.%m.%Y %H:%M"),
                                reverse=True)

    print(dictToFile(sortedListAdsDicts))
