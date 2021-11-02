import time
import requests

from bs4 import BeautifulSoup as Soup
from selenium import webdriver
from selenium.webdriver.common.by import By

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                         ' Chrome/91.0.4472.114 Safari/537.36'}

try:
    second_url = 'https://lalafo.kg/kyrgyzstan/avtomobili-s-probegom'
    driver = webdriver.Chrome(executable_path='/home/makstt/PycharmProjects/parser-sites/parsing/chromedriver')
    driver.get(second_url)
    items = driver.find_elements(By.CLASS_NAME, "AdTileHorizontalTitle")
    for item in items:
        if 'error' not in item.text and 'after' not in item.text:
            time.sleep(2)
            response = requests.get(url=item.get_attribute('href'), headers=HEADERS)
            soup = Soup(response.text, 'html.parser')
            print(item.get_attribute('href'))
            driver.get(url=item.get_attribute('href'))
            detail = driver.find_element(By.CLASS_NAME, 'show-button').click()
            time.sleep(3)
            phone_number = driver.find_element(By.CLASS_NAME, 'phone-wrap')
            print(phone_number.text)
            description = soup.find('div', class_='description__wrap').get_text()
            ul = soup.findAll('ul', class_='details-page__params')
            category = driver.find_element(By.CLASS_NAME, 'details-page__params')
            clear_cat = category.text.split(':')
            print(clear_cat)
            for key, cat in clear_cat:
                match cat:
                    case 'Состояние:':
                        condition = clear_cat[key+1]
                        print(condition)
                    case 'Модель:':
                        model = clear_cat[key+1]
                        print(model)
                    case 'Пробег:':
                        mileage = clear_cat[key+1]
                        print(mileage)
                    case 'Год':
                        year = clear_cat[key+1]
                        print(year)
                    case 'Тип кузова':
                        body_type = clear_cat[key+1]
                        print(body_type)
                    case 'Тип передачи':
                        transmission = clear_cat[key+1]
                        print(transmission)
                    case 'Топливо':
                        engine = clear_cat[key+1]
                        print(engine)
                    case 'Объем двигателя':
                        volume = clear_cat[key+1]
                        print(volume)
                    case 'Цвет':
                        color = clear_cat[key+1]
                        print(color)
                    case 'Руль':
                        steering_wheel = clear_cat[key+1]
                        print(steering_wheel)
                    case 'Наличие':
                        availability = clear_cat[key+1]
                        print(availability)
                    case 'Привод':
                        drive_unit = clear_cat[key+1]
                        print(drive_unit)
                    case _:
                        pass

except Exception as ex:
    print(ex)
finally:
    driver.close()
    driver.quit()
# def parsing_lalafo_cars(url: str, pages: int, headers: Dict):
#     for page in range(0, pages):
#         print(f"Парсинг страницы Lalafo {page + 1}")
#         time.sleep(0.1)
#         response = requests.get(url=url + '?page=' + str(page + 1), headers=headers)
#         soup = Soup(response.text, "html.parser")
#         fh = open(f'templates/none.html', 'w')
#         fh.write(str(soup))
#         fh.close()
#         if response.status_code == 200:
#             items = soup.findAll('div', class_='main-feed__wrapper')
#             print(items)
#             for item in items:
#                 link = item.find('a', class_='AdTileHorizontalTitle ').get('href')
#                 print(link)
