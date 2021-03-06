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
from settings.database import session

fake = FakeUserAgent()
HEADERS = {'User-Agent': fake.random}
url = 'https://lalafo.kg/kyrgyzstan/avtomobili-s-probegom'
base_url = 'https://lalafo.kg'
pages_count = config('PAGES_COUNT')
conn = session()
PATH = config('PATH_CHROMEDRIVER')


def lalafo_cars(url: str, pages: int):
    try:
        for page in range(0, pages):
            options = webdriver.ChromeOptions()
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("start-maximized")
            options.add_argument("disable-infobars")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--headless")
            driver = webdriver.Chrome(executable_path=PATH,
                                      options=options)
            try:
                time.sleep(2)
                driver.get(url=(url + '?page=' + str(page)))
                time.sleep(5)
                items = driver.find_elements(By.CLASS_NAME, "AdTileHorizontalTitle")
                try:
                    region = driver.find_element(By.CLASS_NAME, "meta-info__city ").text
                except:
                    region = None
                created_at = driver.find_element(By.CLASS_NAME, 'AdTileHorizontalDate').text
                driver.find_element(By.CLASS_NAME, 'AdTileHorizontalCallBtnTitle').click()
                time.sleep(3)
                phone_number = driver.find_element(By.CLASS_NAME, 'AdTileHorizontalCallBtnTitle').text
                for item in items:
                    if 'error' not in item.text and 'after' not in item.text:
                        response = requests.get(url=item.get_attribute('href'), headers=HEADERS)
                        if response.status_code == 200:
                            soup = Soup(response.text, 'html.parser')
                            title = item.text
                            key = item.text.replace(' ', '')
                            brand = item.text.split(" ")[0]
                            price = soup.find('span', class_='heading').get_text().replace('USD', '').replace("KGS", "")
                            date = soup.find('span', class_='text-inline')
                            try:
                                updated_at = get_convert_date(date.find_next().find_next().find_next().find_next().get_text(strip=True))
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
                            images_list = save_images_for_lalafo(images=link, name='lalafo_cars', key=key)
                            try:
                                description = soup.find('div', class_='description__wrap').get_text(strip=True)
                            except AttributeError:
                                description = None
                            clear_cat = soup.findAll('p', class_='Paragraph secondary')
                            condition = None
                            model = None
                            mileage = None
                            year = None
                            body_type = None
                            transmission = None
                            engine = None
                            volume = None
                            color = None
                            steering_wheel = None
                            availability = None
                            drive_unit = None
                            for cat in clear_cat:
                                match cat.get_text(strip=True):
                                    case '??????????????????:':
                                        condition = cat.find_next().get_text(strip=True)
                                    case '????????????:':
                                        model = cat.find_next().get_text(strip=True)
                                    case '????????????:':
                                        mileage = cat.find_next().get_text(strip=True)
                                    case '??????:':
                                        year = cat.find_next().get_text(strip=True)
                                    case '?????? ????????????:':
                                        body_type = cat.find_next().get_text(strip=True)
                                    case '?????? ????????????????:':
                                        transmission = cat.find_next().get_text(strip=True)
                                    case '??????????????:':
                                        engine = cat.find_next().get_text(strip=True)
                                    case '?????????? ??????????????????:':
                                        volume = cat.find_next().get_text(strip=True)
                                    case '????????:':
                                        color = cat.find_next().get_text(strip=True)
                                    case '????????:':
                                        steering_wheel = cat.find_next().get_text(strip=True)
                                    case '??????????????:':
                                        availability = cat.find_next().get_text(strip=True)
                                    case '????????????:':
                                        drive_unit = cat.find_next().get_text(strip=True)
                                    case _:
                                        pass
                            print({'??????????????????': condition, "????????????": model, "????????????": mileage, "?????? ??????????????": year,
                                   "??????????": body_type,
                                   "??????": transmission, "??????????": engine,
                                   "??????????": volume, "????????": color, "????????": steering_wheel,
                                   "??????????????": availability, "????????????": drive_unit})
                            if not PassengerCarService.check_record(key=key):
                                PassengerCarService.create_record(key=key, title=title, brand=brand, model=model,
                                                                  year_of_issue=year, body_type=body_type,
                                                                  mileage=mileage, phone_number=phone_number,
                                                                  color=color, engine=engine, transmission_type=transmission,
                                                                  drive_unit=drive_unit, steering_wheel=steering_wheel,
                                                                  condition=condition, price=price,
                                                                  created_at=created_at, updated_at=updated_at,
                                                                  availability=availability, city_of_sale=region,
                                                                  description=description)
                                car_id = PassengerCarService.get(model=model, brand=brand, phone_number=phone_number)
                                PassengerCarService.add_image(image_list=images_list, car_id=car_id.id, key=key,
                                                              name='lalafo_cars')
                        else:
                            logging = LoggingRecord(log=item.get_attribute('href'),
                                                    log_name=base_url,
                                                    log_status=response.status_code,
                                                    created_at=datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
                            conn.add(logging)
                            conn.commit()
            except Exception as ex:
                logging = LoggingRecord(log=url,
                                        log_name=base_url,
                                        log_status=ex,
                                        created_at=datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
                conn.add(logging)
                conn.commit()
            print(f"[INFO] Parsing page {page + 1} was successfully completed")
    except Exception as ex:
        logging = LoggingRecord(log=url,
                                log_name=base_url,
                                log_status=ex,
                                created_at=datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
        conn.add(logging)
        conn.commit()
    finally:
        try:
            driver.close()
            driver.quit()
        except:
            pass


def run_lalafo_auto():
    lalafo_cars(url=url, pages=int(pages_count) * 7)
