import requests

from typing import Dict
from bs4 import BeautifulSoup as Soup
from decouple import config
from fake_useragent import FakeUserAgent

from models.logging import LoggingRecord
from service.passenger_car import *
from settings.database import session

pages_count = config('PAGES_COUNT')
base_url = 'https://www.mashina.kg/partssearch/all/'
urls = 'https://www.mashina.kg'
fake = FakeUserAgent()
HEADERS = {'User-Agent': fake.random}
HEADERS_COOKIE = {'User-Agent': fake.random, 'Host': 'www.mashina.kg', 'X-Requested-With': 'XMLHttpRequest'}
conn = session()


def spare_parsing(url: str, pages: int, headers: Dict):
    # пагинация сайта
    try:
        for page in range(0, pages):
            print(f"Парсинг страницы mashina.kg {page + 1}")
            time.sleep(0.1)
            response = requests.get(url=url + str(page + 1), headers=headers)
            soup = Soup(response.text, "html.parser")
            if response.status_code == 200:
                items = soup.findAll('div', class_='list-item')
                for item in items:
                    name = item.find('h2', class_='name').get_text(strip=True)
                    try:
                        updated_date = item.find('span', class_='date').get_text(strip=True)
                        updated_at = get_updated_date(updated_date)  # добавить проверку
                    except:
                        updated_at = None
                    price = item.find('p', class_='price').findNext().get_text(strip=True).replace('$', '')
                    key = item.find_next().get('href').replace('/details/', '')
                    # запрос на детальную ссылку
                    time.sleep(0.1)
                    several_response = requests.get(url=urls + item.find_next().get('href'), headers=headers)
                    several_soup = Soup(several_response.text, 'html.parser')
                    print(urls + item.find_next().get('href'))
                    if several_response.status_code == 200:
                        title = several_soup.find('div', class_='head-left').findNext().get_text(strip=True)
                        sev_item = several_soup.find_all('div', id='home')
                        images = several_soup.findAll('div', class_='fotorama')
                        time.sleep(0.1)
                        number = several_soup.find('div', class_='number').get_text(strip=True)
                        description = several_soup.find('h2', class_='comment').get_text(strip=True)
                        link = []
                        limit = 6
                        index = 0
                        if len(images) <= 2 and images:
                            for image in images:
                                detail = image.findAll('a', {'alt': 'image'})
                                for d in detail:
                                    link.append(d.get('data-full'))
                                    index += 1
                                    if index == limit:
                                        break
                                images_list = crop_and_save_images(images=link, key=key, name='mashina.kg')
                        else:

                            images_list = None
                        several_item = several_soup.findAll('div', id='home')
                        for item1 in several_item:
                            core_item = item1.findAll('div', class_='field-label')
                            model = None
                            condition = None
                            availability = None
                            others = None
                            for cat in core_item:
                                match cat.get_text():
                                    case 'Марка':
                                        model = cat.find_next().get_text()
                                    case 'Состояние':
                                        condition = cat.find_next().get_text()
                                    case 'Наличие':
                                        availability = cat.find_next().get_text()
                                    case _:
                                        others = cat.get_text()


    except requests.exceptions.ConnectionError as ex:
        logging = LoggingRecord(log=str(ex), log_name=f"{base_url} - error on request",
                                created_at=datetime.datetime.now())
        conn.add(logging)
        conn.commit()


spare_parsing(url=base_url, pages=int(pages_count), headers=HEADERS)