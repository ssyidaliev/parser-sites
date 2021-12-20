import datetime
import time
import requests

from bs4 import BeautifulSoup as Soup
from decouple import config
from fake_useragent import FakeUserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By

from models.logging import LoggingRecord
from service.lalafo import save_images_for_lalafo
from service.passenger_car import PassengerCarService, get_convert_date
from service.real_estate import RealEstateService
from settings.database import session

fake = FakeUserAgent()
HEADERS = {'User-Agent': fake.random}
url = 'https://lalafo.kg/kyrgyzstan/nedvizhimost'
base_url = 'https://lalafo.kg'
pages_count = config('PAGES_COUNT')
conn = session()
PATH = config('PATH_CHROMEDRIVER')


def lalafo_statements(url: str, pages: int):
    try:
        for page in range(0, pages):
            options = webdriver.ChromeOptions()
            options.add_argument("headless")
            driver = webdriver.Chrome(executable_path=PATH,
                                      options=options)
            try:
                driver.get(url=(url + '?page=' + str(page)))
                time.sleep(3)
                items = driver.find_elements(By.CLASS_NAME, "AdTileHorizontalTitle")
                try:
                    region = driver.find_element(By.CLASS_NAME, "meta-info__city ").text
                except:
                    region = None
                created_at = driver.find_element(By.CLASS_NAME, 'AdTileHorizontalDate').text
                driver.find_element(By.CLASS_NAME, 'AdTileHorizontalCallBtnTitle').click()
                time.sleep(1)
                phone_number = driver.find_element(By.CLASS_NAME, 'AdTileHorizontalCallBtnTitle').text
                for item in items:
                    if 'error' not in item.text and 'after' not in item.text:
                        time.sleep(0.1)
                        response = requests.get(url=item.get_attribute('href'), headers=HEADERS)
                        if response.status_code == 200:
                            soup = Soup(response.text, 'html.parser')
                            title = item.text
                            key = item.text.replace(' ', '')
                            name = item.text.split(" ")[0]
                            price = soup.find('span', class_='heading').get_text(strip=True)
                            date = soup.find('span', class_='text-inline')
                            try:
                                updated_at = get_convert_date(
                                    date.find_next().find_next().find_next().find_next().get_text(strip=True))
                            except AttributeError:
                                updated_at = None
                            link = []
                            index = 0
                            limit = 6
                            images = soup.findAll('div', class_='slick-track')
                            if len(images) >= 2:
                                for image in images:
                                    detail = image.findAll('source')
                                    for d in detail:
                                        link.append(d.get('srcset'))
                                        index += 1
                                        if index == limit:
                                            break
                            images_list = save_images_for_lalafo(images=link, name='lalafo_statements', key=key)
                            try:
                                description = soup.find('div', class_='description__wrap').get_text(strip=True)
                            except AttributeError:
                                description = None
                            clear_cat = soup.findAll('p', class_='Paragraph secondary')
                            condition = None
                            count_room = None
                            type_of_sentence = None
                            house_type = None
                            purpose = None
                            series = None
                            floor = None
                            square = None
                            square_area = None
                            furniture = None
                            term = None
                            deposit = None
                            animal = None
                            possibilities = None
                            additionally = None
                            stone_throw = None
                            repair = None
                            list_of_cat = []
                            list_of_pos = []
                            for cat in clear_cat:
                                match cat.get_text(strip=True).replace(":", ""):
                                    case 'Количество комнат':
                                        count_room = cat.find_next().get_text(strip=True)
                                    case 'Этаж':
                                        floor = cat.find_next().get_text(strip=True)
                                    case 'Район':
                                        list_of_cat.append(cat.get_text(strip=True))
                                        list_of_cat.append(cat.find_next().get_text(strip=True))
                                    case 'Тип предложения':
                                        type_of_sentence = cat.find_next().get_text(strip=True)
                                    case 'Ремонт':
                                        repair = cat.find_next().get_text(strip=True)
                                    case 'Год постройки':
                                        list_of_cat.append(cat.get_text(strip=True))
                                        list_of_cat.append(cat.find_next().get_text(strip=True))
                                    case 'Балкон, лоджия':
                                        list_of_cat.append(cat.get_text(strip=True))
                                        list_of_cat.append(cat.find_next().get_text(strip=True))
                                    case 'Площадь (м2)':
                                        square = cat.find_next().get_text(strip=True)
                                    case 'Животные':
                                        animal = cat.find_next().get_text(strip=True)
                                    case 'Количество этажей':
                                        list_of_cat.append(cat.get_text(strip=True))
                                        list_of_cat.append(cat.find_next().get_text(strip=True))
                                    case 'Серия':
                                        series = cat.find_next().get_text(strip=True)
                                    case 'Отопление':
                                        list_of_cat.append(cat.get_text(strip=True))
                                        list_of_cat.append(cat.find_next().get_text(strip=True))
                                    case 'Материал стен':
                                        list_of_cat.append(cat.get_text(strip=True))
                                        list_of_cat.append(cat.find_next().get_text(strip=True))
                                    case 'Окна (направленность)':
                                        list_of_cat.append(cat.get_text(strip=True))
                                        list_of_cat.append(cat.find_next().get_text(strip=True))
                                    case 'Защита территории':
                                        list_of_cat.append(cat.get_text(strip=True))
                                        list_of_cat.append(cat.find_next().get_text(strip=True))
                                    case 'Удобства':
                                        list_of_cat.append(cat.get_text(strip=True))
                                        list_of_cat.append(cat.find_next().get_text(strip=True))
                                    case 'Дополнительно':
                                        additionally = cat.find_next().get_text(strip=True)
                                    case 'Площадь участка (соток)':
                                        square_area = cat.find_next().get_text(strip=True)
                                    case 'Назначение':
                                        purpose = cat.find_next().get_text(strip=True)
                                    case 'Правоустанавливающие документы':
                                        purpose = cat.find_next().get_text(strip=True)
                                    case _:
                                        pass
                            data_cat = None
                            if list_of_cat:
                                data_cat = ' '.join(str(e) for e in list_of_cat)
                            if not RealEstateService.check_record(key=key):
                                RealEstateService.create_record(key=key, title=title, count_room=count_room, floor=floor,
                                                                city_of_sale=region, repair=repair,
                                                                phone_number=phone_number,
                                                                type_of_sentence=type_of_sentence,
                                                                condition=condition, price=price, series=series,
                                                                created_at=created_at, updated_at=updated_at,
                                                                possibilities=data_cat, animal=animal,
                                                                additionally=additionally, square=square,
                                                                square_area=square_area, purpose=purpose,
                                                                description=description)
                                state_id = RealEstateService.get(phone_number=phone_number, title=title)
                                RealEstateService.add_image(image_list=images_list, house_id=state_id.id, key=key,
                                                            name='lalafo_statements')
                            print({'Состояние': condition, "Дом": name, "Серия": series, "Этаж": floor,
                                   "Тип предложения": type_of_sentence,
                                   "Район": region, "Ремонт": repair,
                                   "Площадь (м2)": square, "Дополнительно": list_of_cat, 'Количество комнат:': count_room})
                        else:
                            logging = LoggingRecord(log=item.get_attribute('href'),
                                                    log_name=base_url,
                                                    log_status=response.status_code,
                                                    created_at=datetime.datetime.now())
                            conn.add(logging)
                            conn.commit()
            except Exception as ex:
                logging = LoggingRecord(log=ex,
                                        log_name=f"{base_url} - error on request",
                                        log_status='lalafo_household',
                                        created_at=datetime.datetime.now())
                conn.add(logging)
                conn.commit()
            print(f"[INFO] Parsing page {page + 1} was successfully completed")
    except Exception as ex:
        print(ex)
        logging = LoggingRecord(log=ex,
                                log_name=f"{base_url} - error on request",
                                log_status='lalafo_statements',
                                created_at=datetime.datetime.now())
        conn.add(logging)
        conn.commit()
    finally:
        try:
            driver.close()
            driver.quit()
        except:
            pass


def run_lalafo_statements():
    lalafo_statements(url=url, pages=int(pages_count)*7)
