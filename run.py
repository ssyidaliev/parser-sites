import datetime
import os
import shutil
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
from decouple import config as conf


def check_config(url: str, login: str, password: str):
    if len(url) == 0:
        sys.exit(f'Файл {url}.txt пуст.')
    elif login == '':
        sys.exit('Логин пуст.')
    elif password == '':
        sys.exit('Пароль пуст.')


def make_dir():
    try:
        os.mkdir('images/mashina.kg')
        os.mkdir('images/spare')
        os.mkdir('images/house.kg')
        os.mkdir('images/instagram')
        os.mkdir('images/lalafo_cars')
        os.mkdir('images/lalafo_house')
        os.mkdir('images/lalafo_household')
        os.mkdir('images/lalafo_tel')
        os.mkdir('images/lalafo_statements')
    except FileExistsError:
        pass


def remove_dir():
    shutil.rmtree('images/mashina.kg/')
    shutil.rmtree('images/spare/', ignore_errors=True)
    shutil.rmtree('images/house.kg/', ignore_errors=True)
    shutil.rmtree('images/instagram/', ignore_errors=True)
    shutil.rmtree('images/lalafo_cars/', ignore_errors=True)
    shutil.rmtree('images/lalafo_house/', ignore_errors=True)
    shutil.rmtree('images/lalafo_household/', ignore_errors=True)
    shutil.rmtree('images/lalafo_tel/', ignore_errors=True)
    shutil.rmtree('images/lalafo_statements/', ignore_errors=True)


def run():
    make_dir()
    # print("Парсинг коммерческих машин")
    # run_commercial()
    # time.sleep(1)
    # print("Парсинг House.kg")
    # run_house_kg()
    # time.sleep(1)
    # print("Парсинг легковых машин")
    # run_mashina_kg()
    # time.sleep(1)
    # print("Парсинг запчастей на mashina.kg")
    # run_mashina_spare()
    # time.sleep(1)
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
    # time.sleep(1)
    # pars_url = []
    # count = int(conf('PAGES_COUNT'))
    # path, dirs, files = next(os.walk("accounts"))
    # for file in files:
    #     with open(f'accounts/{file}', 'r') as f:  # читаем файл с аккаунтами
    #         for acc in f.readlines():
    #             pars_url.append(acc.strip('\n'))  # заполняем список
    #     file_name = file.replace('.txt', '')
    #     url = config.URL
    #     login = config.LOGIN
    #     password = config.PASSWORD
    #     check_config(url, login, password)
    #     current_date = datetime.datetime.today()
    #     parser = Inst(url, login, password)  # Инициализируем класс авторизации
    #     error = parser.auth_inst()  # Авторизация в инстаграм
    #     if error != 'error':
    #         for user_url in pars_url:
    #             err = parser.scrap_post(user_url, count, current_date, file_name)  # Парсим страницу
    #             if err == 'error':
    #                 continue
    #     else:
    #         parser.close_browser()
    #         break
    #     parser.close_browser()  # закрываем браузер
    # remove_dir()


if __name__ == '__main__':
    run()

