import datetime
import time

from os import mkdir
from typing import Dict, List
from PIL import Image
import requests
from bs4 import BeautifulSoup as Soup
from decouple import config
from fake_useragent import FakeUserAgent

from service.passenger_car import PassengerCarService

pages_count = config('PAGES_COUNT')
base_url = 'https://www.mashina.kg'
second_url = 'https://lalafo.kg/kyrgyzstan/avtomobili-s-probegom'
urls_list = 'https://www.mashina.kg/search/all/'
fake = FakeUserAgent()
HEADERS = {'User-Agent': fake.random}
HEADERS_COOKIE = {'User-Agent': fake.random, 'Host': 'www.mashina.kg', 'X-Requested-With': 'XMLHttpRequest'}


# парсинг легковых машин
def vehicles_cars(url: str, pages: int, headers: Dict):
    # пагинация сайта
    for page in range(0, pages):
        print(f"Парсинг страницы mashina.kg {page + 1}")
        time.sleep(0.1)
        response = requests.get(url=url + '/search/all/?page=' + str(page + 1), headers=headers)
        soup = Soup(response.text, "html.parser")
        if response.status_code == 200:
            items = soup.findAll('div', class_='list-item')
            for item in items:
                name = item.find('h2', class_='name').get_text(strip=True)
                brand, model = split_brand_and_model(name)
                updated_date = item.find('span', class_='date').get_text(strip=True)
                update_item = updated_date.split(".", 1)[0]
                updated_at = get_updated_date(update_item)
                price = item.find('p', class_='price').findNext().get_text(strip=True).replace('$', '')
                key = item.find_next().get('href').replace('/details/', '')
                # запрос на детальную ссылку
                time.sleep(0.1)
                several_response = requests.get(url=url + item.find_next().get('href'), headers=headers)
                several_soup = Soup(several_response.text, 'html.parser')
                if several_response.status_code == 200:
                    title = several_soup.find('div', class_='head-left').findNext().get_text(strip=True)
                    sev_item = several_soup.find_all('div', id='home')
                    images = several_soup.findAll('div', class_='fotorama')
                    date = several_soup.find('div', class_='head-left').findNext().findNext().findNext().get_text(
                        strip=True)
                    date_item = date.split(".", 1)[0]
                    created_at = get_date(date_item)
                    time.sleep(0.1)
                    number = requests.get(url=(base_url + '/details/' + key + '/givemereal'), headers=HEADERS_COOKIE)
                    clear_number = Soup(number.text, 'html.parser').get_text(strip=True)
                    others = several_soup.find('h2', class_='comment').get_text(strip=True)
                    link = []
                    # Забираю все ссылки на изображения
                    for image in images:
                        detail = image.findAll('a', {'alt': 'image'})
                        for d in detail:
                            link.append(d.get('data-full'))
                        images_count = crop_and_save_images(images=link, key=key)
                    # Забираю характеристика машины
                    year_of_issue = None
                    mileage = None
                    body_type = None
                    color = None
                    engine = None
                    transmission_type = None
                    drive_unit = None
                    steering_wheel = None
                    condition = None
                    customs = None
                    exchange = None
                    availability = None
                    region = None
                    for item1 in sev_item:
                        core_item = item1.findAll('div', class_='field-label')
                        for cat in core_item:
                            match cat.get_text():
                                case 'Год выпуска':
                                    year_of_issue = cat.find_next().get_text()
                                case 'Пробег':
                                    mileage = cat.find_next().get_text()
                                case 'Кузов':
                                    body_type = cat.find_next().get_text()
                                case 'Цвет':
                                    color = cat.find_next().get_text()
                                case 'Двигатель':
                                    engine = cat.find_next().get_text()
                                case 'Коробка':
                                    transmission_type = cat.find_next().get_text()
                                case 'Привод':
                                    drive_unit = cat.find_next().get_text()
                                case 'Руль':
                                    steering_wheel = cat.find_next().get_text()
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
                                    pass
                query = PassengerCarService.check_record(model=model, brand=brand, phone_number=clear_number)
                if not query:
                    PassengerCarService.create_record(key=key, title=title, brand=brand, model=model,
                                                      phone_number=clear_number,
                                                      year_of_issue=year_of_issue, body_type=body_type, mileage=mileage,
                                                      color=color,
                                                      engine=engine, transmission_type=transmission_type,
                                                      drive_unit=drive_unit,
                                                      steering_wheel=steering_wheel, condition=condition,
                                                      customs=customs,
                                                      price=price,
                                                      created_at=created_at, updated_at=updated_at,
                                                      availability=availability,
                                                      exchange=exchange, city_of_sale=region, description=others)
                    car_id = PassengerCarService.get(key=key)
                    PassengerCarService.add_image(key=key, images_count=images_count, car_id=car_id.id)
                print({'Название': title, 'Ключ': key, "Марка": brand, "Модель": model})
        else:
            print("[INFO] Something went wrong")
    print("[INFO] Parsing was successfully completed")


def parsing_lalafo_cars(url: str, pages: int, headers: Dict):
    for page in range(0, pages):
        print(f"Парсинг страницы Lalafo {page + 1}")
        time.sleep(0.1)
        response = requests.get(url=url + '?page=' + str(page + 1), headers=headers)
        soup = Soup(response.text, "html.parser")
        fh = open(f'templates/none.html', 'w')
        fh.write(str(soup))
        fh.close()
        if response.status_code == 200:
            items = soup.findAll('div', class_='main-feed__wrapper')
            print(items)
            for item in items:
                link = item.find('a', class_='AdTileHorizontalTitle ').get('href')
                print(link)


def split_brand_and_model(item: str):
    exceptions = ['Samsung', 'Rover', 'Khodro', 'Wall', 'Trumpchi', 'Martin', 'Romeo']
    change = item.split(' ', 2)[1]
    if change in exceptions:
        brand = item.split(' ', 2)[:2]
        brand = ' '.join(brand)
        model = item.split(' ', 2)[2]
        return brand, model
    else:
        brand = item.split(' ', 1)[0]
        model = item.split(' ', 1)[1]
        return brand, model


def crop_and_save_images(images: List, key: str):
    for i in range(len(images)):
        try:
            mkdir(f'images/{key}')
        except FileExistsError:
            pass
        time.sleep(0.1)
        p = requests.get(images[i])
        out = open(f"images/{key}/{i}.jpg", "wb")
        out.write(p.content)
        im = Image.open(f"images/{key}/{i}.jpg")
        out = crop_center(im)
        out.save(f"images/{key}/{i}.jpg", quality=95)
        out.close()
    return len(images)


# Функция для обрезки изображения по центру.
def crop_center(pil_img) -> Image:
    img_width, img_height = pil_img.size
    if img_width > 1100 and img_height > 800:
        crop_width = 1000
        crop_height = 700
        return pil_img.crop(((img_width - crop_width) // 2,
                             (img_height - crop_height) // 2,
                             (img_width + crop_width) // 2,
                             (img_height + crop_height) // 2))
    elif img_width < 1100 and img_width > 800:
        crop_width = 900
        crop_height = 500
        return pil_img.crop(((img_width - crop_width) // 2,
                             (img_height - crop_height) // 2,
                             (img_width + crop_width) // 2,
                             (img_height + crop_height) // 2))
    elif img_height < 600:
        crop_width = 600
        crop_height = 600
        return pil_img.crop(((img_width - crop_width) // 2,
                             (img_height - crop_height) // 2,
                             (img_width + crop_width) // 2,
                             (img_height + crop_height) // 2))
    elif img_height < img_width:
        crop_width = 800
        crop_height = 500
        return pil_img.crop(((img_width - crop_width) // 2,
                             (img_height - crop_height) // 2,
                             (img_width + crop_width) // 2,
                             (img_height + crop_height) // 2))
    elif img_height > img_width:
        crop_width = 600
        crop_height = 800
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


def get_date(date_item: str):
    now = datetime.datetime.now()
    clean = date_item.split(" ")
    created_date = clean[1]
    match clean[2]:
        case "д":
            try:
                end_date = datetime.date(day=(now.day - int(created_date)), year=now.year, month=now.month)
            except ValueError:
                end_date = datetime.date(day=now.day, year=now.year, month=now.month - 1)
            return end_date
        case "м":
            end_date = now
            return end_date
        case "года":
            end_date = datetime.date(day=now.day, month=now.month, year=(now.year - int(created_date)))
            return end_date
        case "мес":
            try:
                end_date = datetime.date(day=now.day, month=(now.month - int(created_date)), year=now.year)
            except ValueError:
                end_date = datetime.date(day=now.day, year=now.year - 1, month=now.month)
            return end_date
        case _:
            end_date = now
            return end_date


def get_updated_date(date_item: str):
    now = datetime.datetime.now()
    clean = date_item.split(" ")
    created_date = clean[0]
    match clean[1]:
        case "д":
            try:
                end_date = datetime.date(day=(now.day - int(created_date)), year=now.year, month=now.month)
            except ValueError:
                end_date = datetime.date(day=now.day, year=now.year, month=now.month - 1)
            return end_date
        case "м":
            end_date = now
            return end_date
        case "года":
            end_date = datetime.date(day=now.day, month=now.month, year=(now.year - int(created_date)))
            return end_date
        case "мес":
            try:
                end_date = datetime.date(day=now.day, month=(now.month - int(created_date)), year=now.year)
            except ValueError:
                end_date = datetime.date(day=now.day, year=now.year - 1, month=now.month)
            return end_date
        case _:
            end_date = now
            return end_date


# vehicles_cars(url=base_url, pages=int(pages_count), headers=HEADERS)
parsing_lalafo_cars(url=second_url, pages=int(pages_count), headers=HEADERS)