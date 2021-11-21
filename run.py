import datetime
import os
import sys
import time

import config
from parsing.lalafo_auto import run_lalafo_auto
from parsing.lalafo_household import run_lalafo_household
from parsing.lalafo_statements import run_lalafo_statements
from parsing.lalafo_tel import run_lalafo_tel
from parsing.commercial import run_commercial
from parsing.house_kg import run_house_kg
from parsing.mashina_kg import run_mashina_kg
from parsing.mashina_kg_spare import run_mashina_spare
from parsing.scrap_inst import Inst


def check_config(url: str, login: str, password: str):
    if len(url) == 0:
        sys.exit(f'Файл {url}.txt пуст.')
    elif login == '':
        sys.exit('Логин пуст.')
    elif password == '':
        sys.exit('Пароль пуст.')


def run():
    pars_url = []
    path, dirs, files = next(os.walk("accounts"))
    for file in files:
        with open(f'accounts/{file}', 'r') as f:  # читаем файл с аккаунтами
            for acc in f.readlines():
                pars_url.append(acc.strip('\n'))  # заполняем список
        file_name = file.replace('.txt', '')
        url = config.URL
        login = config.LOGIN
        password = config.PASSWORD
        check_config(url, login, password)
        current_date = datetime.datetime.today()
        parser = Inst(url, login, password)  # Инициализируем класс авторизации
        parser.auth_inst()  # Авторизация в инстаграм
        for user_url in pars_url:
            parser.scrap_post(user_url, current_date, file_name)  # Парсим страницу
        parser.close_browser()  # закрываем браузер
    time.sleep(1)
    print("Парсинг коммерческих машин")
    run_commercial()
    time.sleep(1)
    print("Парсинг House.kg")
    run_house_kg()
    time.sleep(1)
    print("Парсинг легковых машин")
    run_mashina_kg()
    time.sleep(1)
    print("Парсинг запчастей на mashina.kg")
    run_mashina_spare()
    time.sleep(1)
    print("Парсинг машин на lalafo.kg")
    run_lalafo_auto()
    time.sleep(1)
    print("Парсинг бытовой техники на lalafo.kg")
    run_lalafo_household()
    time.sleep(1)
    print("Парсинг недвижимостей на lalafo.kg")
    run_lalafo_statements()
    time.sleep(1)
    print("Парсинг смартфонов на lalafo.kg")
    run_lalafo_tel()
    time.sleep(1)
    pars_url = []
    count = int(conf('PAGES_COUNT'))
    path, dirs, files = next(os.walk("accounts"))
    for file in files:
        with open(f'accounts/{file}', 'r') as f:  # читаем файл с аккаунтами
            for acc in f.readlines():
                pars_url.append(acc.strip('\n'))  # заполняем список
        file_name = file.replace('.txt', '')
        url = config.URL
        login = config.LOGIN
        password = config.PASSWORD
        check_config(url, login, password)
        current_date = datetime.datetime.today()
        parser = Inst(url, login, password)  # Инициализируем класс авторизации
        error = parser.auth_inst()  # Авторизация в инстаграм
        if error != 'error':
            for user_url in pars_url:
                err = parser.scrap_post(user_url, count, current_date, file_name)  # Парсим страницу
                if err == 'error':
                    continue
        else:
            parser.close_browser()
            break
        parser.close_browser()  # закрываем браузер

if __name__ == '__main__':
    run()

