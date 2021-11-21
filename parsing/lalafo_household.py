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
from service.passenger_car import get_convert_date
from service.household import HouseholdService
from settings.database import session

fake = FakeUserAgent()
HEADERS = {'User-Agent': fake.random}
url = 'https://lalafo.kg/kyrgyzstan/bytovaya-tekhnika'
base_url = 'https://lalafo.kg'
pages_count = config('PAGES_COUNT')
conn = session()
PATH = config('PATH_CHROMEDRIVER')


def lalafo_household(url: str, pages: int):
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
            try:
                created_at = driver.find_element(By.CLASS_NAME, 'AdTileHorizontalDate').text
            except:
                created_at = None
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
                        images_list = save_images_for_lalafo(images=link, name='lalafo_household', key=key)
                        try:
                            description = soup.find('div', class_='description__wrap').get_text(strip=True)
                        except AttributeError:
                            description = None
                        clear_cat = soup.findAll('p', class_='Paragraph secondary')
                        condition = None
                        delivery = None
                        additionally = None
                        for cat in clear_cat:
                            match cat.get_text(strip=True).replace(":", ""):

                                case 'Состояние':
                                    condition = cat.find_next().get_text(strip=True)
                                case 'Дополнительно':
                                    additionally = cat.find_next().get_text(strip=True)
                                case 'Доставка':
                                    delivery = cat.find_next().get_text(strip=True)
                                case _:
                                    pass
                        if not HouseholdService.check_record(key=key):
                            HouseholdService.create_record(key=key, title=title, additionally=additionally,
                                                           description=description,
                                                           condition=condition, delivery=delivery, price=price,
                                                           created_at=created_at, updated_at=updated_at,
                                                           city_of_sale=region, phone_number=phone_number)
                            household_id = HouseholdService.get(phone_number=phone_number, condition=condition,
                                                                price=price)
                            HouseholdService.add_image(image_list=images_list, name='lalafo_household',
                                                       household_id=household_id.id, key=key)
                        print({'Состояние': condition,
                               "Дополнительно": additionally,
                               "Доставка": delivery})
                    else:
                        logging = LoggingRecord(log=item.get_attribute('href'),
                                                log_name=base_url,
                                                log_status=response.status_code,
                                                created_at=datetime.datetime.now())
                        conn.add(logging)
                        conn.commit()
            print(f"[INFO] Parsing page {page + 1} was successfully completed")
        except Exception as ex:
            print(ex)
            logging = LoggingRecord(log=ex,
                                    log_name=f"{base_url} - error on request",
                                    log_status='lalafo_household',
                                    created_at=datetime.datetime.now())
            conn.add(logging)
            conn.commit()
        finally:
            driver.close()
            driver.quit()


def run_lalafo_household():
    lalafo_household(url=url, pages=int(pages_count) * 7)
