from typing import Dict
from bs4 import BeautifulSoup as Soup
from decouple import config
from fake_useragent import FakeUserAgent

from models.logging import LoggingRecord
from service.commercial import CommercialService
from service.passenger_car import *
from settings.database import session

pages_count = config('PAGES_COUNT')
base_url = 'https://www.mashina.kg'
urls_list = '/commercialsearch/all/'
fake = FakeUserAgent()
HEADERS = {'User-Agent': fake.random}
HEADERS_COOKIE = {'User-Agent': fake.random, 'Host': 'www.mashina.kg', 'X-Requested-With': 'XMLHttpRequest'}
conn = session()


# парсинг легковых машин
def vehicles_cars(url: str, pages: int, headers: Dict):
    # пагинация сайта
    try:
        for page in range(0, pages):
            print(f"Парсинг страницы mashina.kg коммерческие стр-{page + 1}")
            time.sleep(0.1)
            response = requests.get(url=url + str(page + 1), headers=headers)
            soup = Soup(response.text, "html.parser")
            if response.status_code == 200:
                items = soup.findAll('div', class_='list-item')
                for item in items:
                    try:
                        name = item.find('h2', class_='name').get_text(strip=True)
                        brand, model = split_brand_and_model(name)
                        try:
                            updated_date = item.find('span', class_='date').get_text(strip=True)
                            updated_at = get_updated_date(updated_date)  # добавить проверку
                        except:
                            updated_at = None
                        price = item.find('p', class_='price').findNext().get_text(strip=True).replace('$', '')
                        key = item.find_next().get('href').replace('/details/', '')
                        # запрос на детальную ссылку
                        time.sleep(0.1)
                        several_response = requests.get(url=base_url + item.find_next().get('href'), headers=headers)
                        several_soup = Soup(several_response.text, 'html.parser')
                        if several_response.status_code == 200:
                            title = several_soup.find('div', class_='head-left').findNext().get_text(strip=True)
                            sev_item = several_soup.find_all('div', id='home')
                            images = several_soup.findAll('div', class_='fotorama')
                            try:
                                date = several_soup.find('div',
                                                         class_='head-left').findNext().findNext().findNext().get_text(
                                    strip=True)
                                created_at = get_created_date(date)
                            except:
                                created_at = None
                            time.sleep(0.1)
                            number = requests.get(url=(base_url + '/details/' + key + '/givemereal'),
                                                  headers=HEADERS_COOKIE)
                            clear_number = Soup(number.text, 'html.parser').get_text(strip=True)
                            description = several_soup.find('h2', class_='comment').get_text(strip=True)
                            link = []
                            # Забираю все ссылки на изображения
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
                            # Забираю характеристика машины
                            year_of_issue = None
                            mileage = None
                            color = None
                            engine = None
                            transmission_type = None
                            drive_unit = None
                            condition = None
                            customs = None
                            exchange = None
                            availability = None
                            region = None
                            others = None
                            for item1 in sev_item:
                                core_item = item1.findAll('div', class_='field-label')
                                for cat in core_item:
                                    match cat.get_text():
                                        case 'Год выпуска':
                                            year_of_issue = cat.find_next().get_text()
                                        case 'Пробег':
                                            mileage = cat.find_next().get_text()
                                        case 'Цвет':
                                            color = cat.find_next().get_text()
                                        case 'Двигатель':
                                            engine = cat.find_next().get_text()
                                        case 'Коробка':
                                            transmission_type = cat.find_next().get_text()
                                        case 'Привод':
                                            drive_unit = cat.find_next().get_text()
                                        case 'Состояние':
                                            condition = cat.find_next().get_text()
                                        case 'Таможня':
                                            customs = cat.find_next().get_text()
                                        case 'Обмен':
                                            exchange = cat.find_next().get_text()
                                        case 'Наличие':
                                            availability = cat.find_next().get_text()
                                        case 'Регион, город продажи':
                                            region = cat.find_next().get_text()
                                        case _:
                                            others = cat.get_text(strip=True)
                        else:
                            logging = LoggingRecord(log=(url + item.find_next().get('href'), 'error on this link'),
                                                    log_name=f"{base_url} - error on request",
                                                    log_status=several_response.status_code,
                                                    created_at=datetime.datetime.now())
                            conn.add(logging).commit()
                        query = CommercialService.check_record(model=model, brand=brand, phone_number=clear_number)
                        if not query:
                            CommercialService.create_record(key=key, title=title, brand=brand, model=model,
                                                            phone_number=clear_number,
                                                            year_of_issue=year_of_issue,
                                                            mileage=mileage,
                                                            color=color,
                                                            engine=engine, transmission_type=transmission_type,
                                                            drive_unit=drive_unit, condition=condition,
                                                            customs=customs,
                                                            price=price,
                                                            created_at=created_at, updated_at=updated_at,
                                                            availability=availability,
                                                            exchange=exchange, city_of_sale=region,
                                                            description=description, other=others)
                            car_id = CommercialService.get(key=key)
                            CommercialService.add_image(key=key, image_list=images_list, car_id=car_id.id)
                    except AttributeError:
                        pass
                    print({'Название': title, 'Ключ': key, "Марка": brand, "Модель": model})
            else:
                logging = LoggingRecord(log=(url + '/search/all/?page=' + str(page + 1), 'error on this link'),
                                        log_name=f"{base_url} - error on request", log_status=response.status_code,
                                        created_at=datetime.datetime.now())
                conn.add(logging).commit()
                print("[INFO] Something went wrong")
        print("[INFO] Parsing was successfully completed")
    except requests.exceptions.ConnectionError as ex:
        logging = LoggingRecord(log=str(ex), log_name=f"{base_url} - error on request",
                                created_at=datetime.datetime.now())
        conn.add(logging)
        conn.commit()
        print("[INFO] Something went wrong")


def run_commercial():
    vehicles_cars(url=(base_url + urls_list), pages=int(pages_count), headers=HEADERS)
