import requests
import datetime
import time

from typing import Dict
from bs4 import BeautifulSoup as Soup
from decouple import config
from fake_useragent import FakeUserAgent

from models.logging import LoggingRecord
from service.passenger_car import get_updated_date, get_created_date, crop_and_save_images
from service.real_estate import RealEstateService
from settings.database import session

pages_count = config('PAGES_COUNT')
base_url = 'https://www.house.kg'
urls_list = ['/kupit-kvartiru', '/kupit-dom', '/kupit-kommercheskaia-nedvijimost', '/kupit-uchastok', '/kupit-dachu',
             '/kupit-garaj', '/snyat-kvartiru', '/snyat-dom', '/snyat-kommercheskaia-nedvijimost', '/snyat-uchastok',
             '/snyat-dachu', '/snyat-garaj']
fake = FakeUserAgent()
HEADERS = {'User-Agent': fake.random}
HEADERS_COOKIE = {'User-Agent': fake.random, 'Host': base_url, 'X-Requested-With': 'XMLHttpRequest'}
conn = session()
name = 'house.kg'


# парсинг легковых машин
def house_buy_parsing(url: str, pages: int, headers: Dict):
    # пагинация сайта
    try:
        for page in range(0, pages):
            print(f"Парсинг страницы {page + 1} {url.replace('https://www.house.kg/', '')}")
            time.sleep(0.1)
            response = requests.get(url=url + f'?page={str(page + 1)}', headers=headers)
            if response.status_code == 200:
                soup = Soup(response.text, 'html.parser')
                items = soup.findAll('div', class_='listing')
                for item in items:
                    key = item.find('a').get('href').replace('/details/', '')
                    title = item.find('a').get_text(strip=True)
                    address = item.find('div', class_='address').get_text(strip=True)
                    price = item.find('div', class_='price').get_text(strip=True).replace('$', '')
                    price_addition = item.find('div', class_='price-addition').get_text(strip=True).replace('сом', '')
                    time.sleep(0.1)
                    detail_response = requests.get(url=(base_url + "/details/" + key), headers=headers)
                    if detail_response.status_code == 200:
                        detail_soup = Soup(detail_response.text, 'html.parser')
                        phone_number = detail_soup.find('div', class_='number').get_text(strip=True)
                        create_date = detail_soup.find('span', class_='added-span').get_text(strip=True)
                        try:
                            description = detail_soup.find('p', {'style': 'white-space: pre-line'}).get_text(strip=True)
                        except:
                            description = None
                        created_at = get_created_date(create_date)
                        try:

                            update_date = detail_soup.find('span', class_='upped-span').get_text(strip=True)
                            updated_at = get_created_date(update_date)
                        except AttributeError:
                            updated_at = None
                        images = detail_soup.findAll('div', class_='fotorama')
                        index = 0
                        limit = 6
                        link = []
                        if images and len(images) <= 2:
                            for image in images:
                                detail = image.findAll('a', {'itemprop': 'image'})
                                for d in detail:
                                    link.append(d.get('data-full'))
                                    index += 1
                                    if index == limit:
                                        break
                                images_list = crop_and_save_images(images=link, key=key, name=name)
                        else:
                            images_list = None
                        detail_item = detail_soup.findAll('div', class_='label')
                        list_of_cat = []
                        list_of_pos = []
                        type_of_sentence = None
                        series = None
                        house_type = None
                        floor = None
                        square = None
                        condition = None
                        furniture = None
                        term = None
                        square_area = None
                        repair = None
                        for cat in detail_item:
                            match cat.get_text(strip=True):
                                case 'Тип предложения':
                                    type_of_sentence = cat.findNext().get_text(strip=True)
                                case 'Серия':
                                    series = cat.findNext().get_text(strip=True)
                                case 'Дом':
                                    house_type = cat.findNext().get_text(strip=True)
                                case 'Этаж':
                                    floor = cat.findNext().get_text(strip=True)
                                case "Площадь":
                                    square = cat.findNext().get_text(strip=True)
                                case "Отопление":
                                    list_of_cat.append(cat.get_text(strip=True))
                                    list_of_cat.append('-')
                                    list_of_cat.append(cat.findNext().get_text(strip=True))
                                case "Состояние":
                                    condition = cat.findNext().get_text(strip=True)
                                case "Интернет":
                                    list_of_cat.append(cat.get_text(strip=True))
                                    list_of_cat.append('-')
                                    list_of_cat.append(cat.findNext().get_text(strip=True))
                                case "Санузел":
                                    list_of_cat.append(cat.get_text(strip=True))
                                    list_of_cat.append('-')
                                    list_of_cat.append(cat.findNext().get_text(strip=True))
                                case "Канализация":
                                    list_of_cat.append(cat.get_text(strip=True))
                                    list_of_cat.append('-')
                                    list_of_cat.append(cat.findNext().get_text(strip=True))
                                case "Газ":
                                    list_of_cat.append(cat.get_text(strip=True))
                                    list_of_cat.append('-')
                                    list_of_cat.append(cat.findNext().get_text(strip=True))
                                case "Балкон":
                                    list_of_cat.append(cat.get_text(strip=True))
                                    list_of_cat.append('-')
                                    list_of_cat.append(cat.findNext().get_text(strip=True))
                                case "Парковка":
                                    list_of_cat.append(cat.get_text(strip=True))
                                    list_of_cat.append('-')
                                    list_of_cat.append(cat.findNext().get_text(strip=True))
                                case "Мебель":
                                    furniture = cat.findNext().get_text(strip=True)
                                case "Высота потолков":
                                    list_of_cat.append(cat.get_text(strip=True))
                                    list_of_cat.append('-')
                                    list_of_cat.append(cat.findNext().get_text(strip=True))
                                case "Безопасность":
                                    list_of_cat.append(cat.get_text(strip=True))
                                    list_of_cat.append('-')
                                    list_of_cat.append(cat.findNext().get_text(strip=True))
                                case "Питьевая вода":
                                    list_of_cat.append(cat.get_text(strip=True))
                                    list_of_cat.append('-')
                                    list_of_cat.append(cat.findNext().get_text(strip=True))
                                case "Электричество":
                                    list_of_cat.append(cat.get_text(strip=True))
                                    list_of_cat.append('-')
                                    list_of_cat.append(cat.findNext().get_text(strip=True))
                                case "Пол":
                                    list_of_cat.append(cat.get_text(strip=True))
                                    list_of_cat.append('-')
                                    list_of_cat.append(cat.findNext().get_text(strip=True))
                                case "Входная дверь":
                                    list_of_cat.append(cat.get_text(strip=True))
                                    list_of_cat.append('-')
                                    list_of_cat.append(cat.findNext().get_text(strip=True))
                                case "Возможность рассрочки":
                                    list_of_pos.append(cat.get_text(strip=True))
                                    list_of_pos.append('-')
                                    list_of_pos.append(cat.findNext().get_text(strip=True))
                                case "Возможность обмена":
                                    list_of_pos.append(cat.get_text(strip=True))
                                    list_of_pos.append('-')
                                    list_of_pos.append(cat.findNext().get_text(strip=True))
                                case "Возможность ипотеки":
                                    list_of_pos.append(cat.get_text(strip=True))
                                    list_of_pos.append('-')
                                    list_of_pos.append(cat.findNext().get_text(strip=True))
                                case "Период аренды":
                                    term = cat.findNext().get_text(strip=True)
                                case "Площадь участка":
                                    square_area = cat.findNext().get_text(strip=True)
                                case "Ремонт":
                                    repair = cat.findNext().get_text(strip=True)
                                case _:
                                    pass
                        data_cat = None
                        data_pos = None
                        if list_of_cat:
                            data_cat = ' '.join(str(e) for e in list_of_cat)
                        if list_of_pos:
                            data_pos = ' '.join(str(e) for e in list_of_pos)
                        query = RealEstateService.check_record(house_type=house_type, square=square,
                                                               phone_number=phone_number)
                        if not query:
                            RealEstateService.create_record(key=key, title=title, phone_number=phone_number,
                                                            price=price, city_of_sale=address, description=description,
                                                            type_of_sentence=type_of_sentence, house_type=house_type,
                                                            purpose='buy', series=series, floor=floor, count_room=title,
                                                            square=square, condition=condition, additionally=data_cat,
                                                            furniture=furniture, term=term, possibilities=data_pos,
                                                            created_at=created_at, updated_at=updated_at,
                                                            square_area=square_area, repair=repair)
                            house_id = RealEstateService.get(key=key)
                            RealEstateService.add_image(key=key, image_list=images_list, house_id=house_id.id,
                                                        name=name)
                        print({'Название': title, 'Ключ': key, "Дом": house_type, "Серия": series})
                else:
                    logging = LoggingRecord(log=response.status_code, log_name=f"{base_url} - error on request",
                                            created_at=datetime.datetime.now())
                    conn.add(logging)
                    conn.commit()
            print('[INFO] Parsing was successfully completed')
    except requests.exceptions.ConnectionError as ex:
        logging = LoggingRecord(log=str(ex), log_name=f"{base_url} - error on request",
                                created_at=datetime.datetime.now())
        conn.add(logging)
        conn.commit()


for ul in urls_list:
    house_buy_parsing(url=(base_url+ul), pages=int(pages_count), headers=HEADERS)
