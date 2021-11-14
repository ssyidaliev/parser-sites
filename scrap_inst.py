import base64
import sys
import config
import requests
import selenium
import time
import random

from fake_useragent import FakeUserAgent
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
from bs4 import BeautifulSoup as bs
from models.passenger_car_images import PassengerCarImage
from service.passenger_car import PassengerCarService, conn

fake = FakeUserAgent()
HEADERS = {'User-Agent': fake.random}


class Inst:
    def __init__(self, url_inst, login, password):
        self.url = url_inst
        self.login = login
        self.password = password
        self.data = {'data': {'items': []}}
        self.driver = webdriver.Chrome(executable_path='parsing/chromedriver')

    def auth_inst(self):
        print(datetime.today().strftime(f'%H:%M:%S | Выполняется авторизация в Instagram.'))
        self.driver.get(self.url)
        time.sleep(random.randrange(3, 5))
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.NAME, 'username')))
        self.driver.find_element(By.NAME, 'username').send_keys(self.login)
        passwd = self.driver.find_element(By.NAME, 'password')
        passwd.send_keys(self.password)
        passwd.send_keys(Keys.ENTER)
        time.sleep(4)
        try:
            self.driver.find_element(By.CLASS_NAME, 'ABCxa')
        except NoSuchElementException:
            try:
                err = self.driver.find_element(By.CLASS_NAME, 'eiCW-').text
                self.driver.quit()
                sys.exit(err + '\nРабота завершена с ошибкой.')
            except NoSuchElementException:
                err = self.driver.find_element(By.CLASS_NAME, 'O4QwN').text
                self.driver.quit()
                sys.exit(err + '\nРабота завершена с ошибкой.')

        time.sleep(3)
        print(datetime.today().strftime(f'%H:%M:%S | Авторизация в Instagram выполнена.'))

    def scrap_post(self, url, current_date):
        self.driver.get(url)
        soup = bs(self.driver.page_source, 'html.parser')
        time.sleep(2)
        post_links = []

        for elem in soup.find('article', class_='ySN3v'):
            for el in elem.find_all('a'):
                link = el.get('href')
                post_links.append(config.URL + link)

        for post in post_links:
            user_dict = {}
            self.driver.get(post)
            time.sleep(2)
            soup = bs(self.driver.page_source, 'html.parser')
            date = soup.find('time', class_='Nzb55').get('datetime').replace('T', ' ').replace('Z', '').split(' ')[0]
            created_at = datetime.strptime(date, "%Y-%m-%d")

            if soup.find('video', class_='tWeCl') is not None:
                print('Пост видео, пропускаем.')
                if current_date - timedelta(days=5) == created_at:
                    break
                continue

            # img
            try:
                img = []
                i_class = soup.find('div', class_='KL4Bh')
                img.append(i_class.find('img', class_='FFVAD').get('src'))
                try:
                    button = self.driver.find_element(By.CLASS_NAME, '_6CZji')
                except selenium.common.exceptions.NoSuchElementException:
                    button = None
                index = 0
                finish = 6
                while True:
                    if button and index < finish:
                        try:
                            self.driver.find_element(By.CLASS_NAME, '_6CZji').click()
                        except selenium.common.exceptions.NoSuchElementException:
                            break
                        time.sleep(1)
                        img.append(i_class.find('img', class_='FFVAD').get('src'))
                        index += 1
                    else:
                        break
            except AttributeError:
                continue

            # title
            title = soup.find('div', class_='C4VMK').find_all('span')[-1].text
            user_dict['url'] = url
            user_dict['img'] = img
            user_dict['title'] = title
            self.write_json(user_dict)
            if not PassengerCarService.check_record(title=title):
                PassengerCarService.create_record(title=title)
                car_id = PassengerCarService.get(title=title)
                for item in img:
                    response = requests.get(url=item, headers=HEADERS)
                    file = url.replace("https://instagram.", "").replace("/", "")
                    if response.status_code == 200:
                        out = open(f'images/instagram/{file}.jpg', 'wb')
                        out.write(response.content)
                    with open(f'images/instagram/{file}.jpg', 'rb') as image_file:
                        code = base64.b64encode(image_file.read())
                    record = PassengerCarImage(image=code, passenger_car_id=car_id.id, created_at=current_date)
                    conn.add(record)
                conn.commit()
                out.close()
            if current_date - timedelta(days=5) == created_at:
                break

    def close_browser(self):
        print('Работа завершена.')
        self.driver.quit()

    def write_json(self, info):
        self.data['data']['items'].append(info)
        print(self.data)
