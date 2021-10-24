import re
from os import mkdir
from typing import Dict
from PIL import Image
import requests
from bs4 import BeautifulSoup as Soup
from decouple import config
from fake_useragent import FakeUserAgent

pages_count = config('PAGES_COUNT')
base_url = 'https://www.mashina.kg'
urls_list = 'https://www.mashina.kg/search/all/'
ua = FakeUserAgent()
HEADERS = {'User-Agent': ua.random}


# Функция для обрезки изображения по центру.
def crop_center(pil_img) -> Image:
    img_width, img_height = pil_img.size
    if img_width > img_height:
        crop_width = 1200
        crop_height = 600
        return pil_img.crop(((img_width - crop_width) // 2,
                             (img_height - crop_height) // 2,
                             (img_width + crop_width) // 2,
                             (img_height + crop_height) // 2))
    else:
        crop_width = 650
        crop_height = 650
        return pil_img.crop(((img_width - crop_width) // 2,
                             (img_height - crop_height) // 2,
                             (img_width + crop_width) // 2,
                             (img_height + crop_height) // 2))


# парсинг легковых машин
def vehicles_cars(url: str, pages: int, headers: Dict):
    # пагинация сайта
    for page in range(0, pages):
        print(f"Парсинг страницы {page + 1}")
        response = requests.get(url=url + '/search/all/?page=' + str(page + 1), headers=headers)
        soup = Soup(response.text, "html.parser")
        if response.status_code == 200:
            items = soup.findAll('div', class_='list-item')
            for item in items:
                # для исключений двойные названия
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
                # запрос на детальную ссылку
                several_response = requests.get(url=url + item.find_next().get('href'), headers=headers)
                several_soup = Soup(several_response.text, 'html.parser')
                if several_response.status_code == 200:
                    sev_item = several_soup.find_all('div', id='home')
                    images = several_soup.findAll('div', class_='fotorama')
                    link = []
                    # Забираю все ссылки на изображения
                    for image in images:
                        detail = image.findAll('a', {'alt': 'image'})
                        for d in detail:
                            link.append(d.get('data-full'))
                    # Прохожусь по картинками для скачивания и добавления в базу
                    for i in range(len(link)):
                        try:
                            mkdir(f'images/{key}')
                        except FileExistsError:
                            pass
                        p = requests.get(link[i])
                        out = open(f"images/{key}/{i}.jpg", "wb")
                        out.write(p.content)
                        im = Image.open(f"images/{key}/{i}.jpg")
                        out = crop_center(im)
                        out.save(f"images/{key}/{i}.jpg", quality=95)
                        out.close()
                    # Забираю характеристика машины
                    for item1 in sev_item:
                        core_item = item1.findAll('div', class_='field-label')
                        for cat in core_item:
                            match cat.get_text():
                                case 'Год выпуска':
                                    print({'cat': cat.find_next().get_text()})
                                case 'Пробег':
                                    print({'Пробег': cat.find_next().get_text()})
                                case 'Кузов':
                                    print({'Кузов': cat.find_next().get_text()})
                                case 'Цвет':
                                    print({'Цвет': cat.find_next().get_text()})
                                case 'Двигатель':
                                    print({'Двигатель': cat.find_next().get_text()})
                                case 'Коробка':
                                    print({'Коробка': cat.find_next().get_text()})
                                case 'Привод':
                                    print({'Привод': cat.find_next().get_text()})
                                case 'Руль':
                                    print({'Руль': cat.find_next().get_text()})
                                case 'Состояние':
                                    print({'Состояние': cat.find_next().get_text()})
                                case 'Таможня':
                                    print({'Таможня': cat.find_next().get_text()})
                                case 'Обмен':
                                    print({'Обмен': cat.find_next().get_text()})
                                case 'Прочее':
                                    print({'Прочее': cat.find_next().get_text()})
                                case 'Наличие':
                                    print({'Наличие': cat.find_next().get_text()})
                                case 'Рассрочка':
                                    print({'Рассрочка': cat.find_next().get_text()})
                                case 'Регион, город продажи':
                                    print({'Регион, город продажи': cat.find_next().get_text()})
                                case 'VIN':
                                    print({'VIN': cat.find_next().get_text()})
                                case _:
                                    pass
        else:
            print("[INFO] Something went wrong")
    print("[INFO] Parsing was successfully completed")


vehicles_cars(url=base_url, pages=int(pages_count), headers=HEADERS)
