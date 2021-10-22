import requests
from bs4 import BeautifulSoup as Soup
from decouple import config

from utils import HEADERS

pages_count = config("PAGES_COUNT")
urls_list = 'https://www.mashina.kg/search/all/'

for page in range(1, int(pages_count)):
    print(f"Парсинг страницы {page}")
    response = requests.get(url=urls_list, headers=HEADERS)
    soup = Soup(response.text, "html.parser")
    if response.status_code == 200:
        items = soup.findAll('div', class_='list-item')
        for item in items:
            print(item.find('a').get('href'))
    else:
        print("Что-то пошло не так")
