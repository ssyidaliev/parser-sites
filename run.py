import datetime
import time

from parsing.commercial import run_commercial
from parsing.house_kg import run_house_kg
from parsing.lalafo_auto import run_lalafo_auto
from parsing.lalafo_household import run_lalafo_household
from parsing.lalafo_statements import run_lalafo_statements
from parsing.lalafo_tel import run_lalafo_tel
from parsing.mashina_kg import run_mashina_kg
from parsing.mashina_kg_spare import run_mashina_spare
from scrap_inst import Inst
import config
import sys


def run():
    # pars_url = []
    # with open('accounts.txt', 'r') as f:  # читаем файл с аккаунтами
    #     for acc in f.readlines():
    #         pars_url.append(acc.strip('\n'))  # заполняем список
    # url = config.URL
    # login = config.LOGIN
    # password = config.PASSWORD
    #
    # if len(pars_url) == 0:
    #     sys.exit('Файл accounts.txt пуст.')
    # elif login == '':
    #     sys.exit('Логин пуст.')
    # elif password == '':
    #     sys.exit('Пароль пуст.')
    #
    # current_date = datetime.datetime.today()
    # parser = Inst(url, login, password)  # Инициализируем класс авторизации
    # parser.auth_inst()  # Авторизация в инстаграм
    # for user_url in pars_url:
    #     parser.scrap_post(user_url, 3, current_date)  # Парсим страницу
    # parser.close_browser()  # закрываем браузер
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


if __name__ == '__main__':
    run()

