import re
from typing import Dict

import requests
from bs4 import BeautifulSoup as Soup
from decouple import config
from fake_useragent import FakeUserAgent

pages_count = config('PAGES_COUNT')
base_url = 'https://www.mashina.kg'
urls_list = 'https://www.mashina.kg/search/all/'
ua = FakeUserAgent()
HEADERS = {'User-Agent': ua.random}


def vehicles_cars(url: str, pages: int, headers: Dict):
    for page in range(0, pages):
        print(f"Парсинг страницы {page + 1}")
        response = requests.get(url=url + '/search/all/?page=' + str(page + 1), headers=headers)
        soup = Soup(response.text, "html.parser")
        if response.status_code == 200:
            items = soup.findAll('div', class_='list-item')
            for item in items:
                exceptions = ['Samsung', 'Rover', 'Khodro', 'Wall', 'Trumpchi', 'Martin', 'Romeo']
                name = item.find('h2', class_='name').get_text(strip=True)
                change = name.split(' ', 2)[1]
                if change in exceptions:
                    brand = name.split(' ', 2)[:2]
                    brand = ' '.join(brand)
                    model = name.split(' ', 2)[2]
                else:
                    brand = name.split(' ', 1)[0]
                    model = name.split(' ', 1)[1]
                price = item.find('p', class_='price').findNext().get_text(strip=True)
                key = item.find_next().get('href').replace('/details/', '')
                several_response = requests.get(url=url + item.find_next().get('href'), headers=headers)
                several_soup = Soup(several_response.text, 'html.parser')
                if several_response.status_code == 200:
                    sev_item = several_soup.find_all('div', id='home')
                    images = several_soup.findAll('div', class_='fotorama')
                    link = []
                    for image in images:
                        link.append(image.find('a', {'alt': 'image'}).get('data-full'))
                    print(link)
                    # for item1 in sev_item:
                    #     core_item = item1.findAll('div', class_='field-label')
                    #     for year in core_item:
                    #         match year.get_text():
                    #             case 'Год выпуска':
                    #                 print({'year': year.find_next().get_text()})
                    #             case 'Пробег':
                    #                 print({'Пробег': year.find_next().get_text()})
                    #             case 'Кузов':
                    #                 print({'Кузов': year.find_next().get_text()})
                    #             case 'Цвет':
                    #                 print({'Цвет': year.find_next().get_text()})
                    #             case 'Двигатель':
                    #                 print({'Двигатель': year.find_next().get_text()})
                    #             case 'Коробка':
                    #                 print({'Коробка': year.find_next().get_text()})
                    #             case 'Привод':
                    #                 print({'Привод': year.find_next().get_text()})
                    #             case 'Руль':
                    #                 print({'Руль': year.find_next().get_text()})
                    #             case 'Состояние':
                    #                 print({'Состояние': year.find_next().get_text()})
                    #             case 'Таможня':
                    #                 print({'Таможня': year.find_next().get_text()})
                    #             case 'Обмен':
                    #                 print({'Обмен': year.find_next().get_text()})
                    #             case 'Прочее':
                    #                 print({'Прочее': year.find_next().get_text()})
                    #             case 'Наличие':
                    #                 print({'Наличие': year.find_next().get_text()})
                    #             case 'Рассрочка':
                    #                 print({'Рассрочка': year.find_next().get_text()})
                    #             case 'Регион, город продажи':
                    #                 print({'Регион, город продажи': year.find_next().get_text()})
                    #             case 'VIN':
                    #                 print({'VIN': year.find_next().get_text()})
                    #             case _:
                    #                 print("------------------------------------------------------------------")
        else:
            print("[INFO] Something went wrong")
    print("[INFO] Parsing was successfully completed")


vehicles_cars(url=base_url, pages=int(pages_count), headers=HEADERS)
