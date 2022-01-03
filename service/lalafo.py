import time
import requests

from os import mkdir
from typing import List


def save_images_for_lalafo(images: List, key: str, name: str):
    images_list = []
    for i in range(len(images)):
        try:
            mkdir(f'images/{name}/{key[:7]}-{name}')
        except FileExistsError:
            pass
        time.sleep(0.1)
        p = requests.get(images[i])
        out = open(f"images/{name}/{key[:7]}-{name}/{i}.jpg", "wb")
        out.write(p.content)
        with open(f"images/{name}/{key[:7]}-{name}/{i}.jpg", 'rb') as image:
            images_list.append(image.read())
        out.close()
    return images_list
