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
from service.telephone import TelephoneService
from settings.database import session

fake = FakeUserAgent()
HEADERS = {'User-Agent': fake.random}
url = 'https://lalafo.kg/kyrgyzstan/mobilnye-telefony-i-aksessuary/mobilnye-telefony'
base_url = 'https://lalafo.kg'
pages_count = config('PAGES_COUNT')
conn = session()
PATH = config('PATH_CHROMEDRIVER')


def lalafo_phones(url: str, pages: int):
    try:
        for page in range(0, pages):
            options = webdriver.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.headless = True
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
                            key = item.text.replace(' ', '').replace("/", "")
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
                            images_list = save_images_for_lalafo(images=link, name='lalafo_tel', key=key)
                            try:
                                description = soup.find('div', class_='description__wrap').get_text(strip=True)
                            except AttributeError:
                                description = None
                            clear_cat = soup.findAll('p', class_='Paragraph secondary')
                            condition = None
                            memory = None
                            ram = None
                            model = None
                            color = None
                            delivery = None
                            additionally = None
                            for cat in clear_cat:
                                match cat.get_text(strip=True).replace(":", ""):

                                    case 'Состояние':
                                        condition = cat.find_next().get_text(strip=True)
                                    case 'Объем памяти':
                                        memory = cat.find_next().get_text(strip=True)
                                    case 'Цвет':
                                        color = cat.find_next().get_text(strip=True)
                                    case 'Модель':
                                        model = cat.find_next().get_text(strip=True)
                                    case 'Дополнительно':
                                        additionally = cat.find_next().get_text(strip=True)
                                    case 'Доставка':
                                        delivery = cat.find_next().get_text(strip=True)
                                    case 'Оперативная память, RAM (ГБ.)':
                                        ram = cat.find_next().get_text(strip=True)
                                    case _:
                                        pass
                            if not TelephoneService.check_record(key=key):
                                TelephoneService.create_record(key=key, title=title, model=model, additionally=additionally,
                                                               color=color, memory=memory, description=description,
                                                               condition=condition, delivery=delivery, ram=ram, price=price,
                                                               created_at=created_at, updated_at=updated_at,
                                                               city_of_sale=region, phone_number=phone_number)
                                phone_id = TelephoneService.get(phone_number=phone_number, model=model, memory=memory,
                                                                price=price)
                                TelephoneService.add_image(image_list=images_list, phone_id=phone_id.id, key=key,
                                                           name='lalafo_tel')
                            print({'Состояние': condition, "Модель": model, "Цвет": color, "объем памяти": memory,
                                   "Дополнительно": additionally,
                                   "Доставка": delivery, "ОЗУ": ram})
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
                                        log_status=response.status_code,
                                        created_at=datetime.datetime.now())
                conn.add(logging)
                conn.commit()
        print(f"[INFO] Parsing page {page + 1} was successfully completed")
    except Exception as ex:
        print(ex)
        logging = LoggingRecord(log=ex,
                                log_name=f"{base_url} - error on request",
                                log_status=response.status_code,
                                created_at=datetime.datetime.now())
        conn.add(logging)
        conn.commit()
    finally:
        try:
            driver.close()
            driver.quit()
        except:
            pass


def run_lalafo_tel():
    lalafo_phones(url=url, pages=int(pages_count) * 7)
