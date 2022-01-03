import base64
import datetime
import os
import shutil
import time
import requests

from os import mkdir
from typing import List
from PIL import Image

from models.passenger_car import PassengerCar
from models.passenger_car_images import PassengerCarImage
from settings.database import session

conn = session()


class PassengerCarService:
    model = PassengerCar()

    @classmethod
    def check_record(cls, **filters):
        return conn.query(PassengerCar).filter_by(**filters).all()

    @classmethod
    def get(cls, **filters):
        return conn.query(PassengerCar).filter_by(**filters).first()

    @classmethod
    def create_record(cls, **filters):
        record = PassengerCar(**filters)
        conn.add(record)
        conn.commit()
        return True

    @classmethod
    def add_image(cls, car_id: int, image_list: list, key: str, name: str):
        if image_list:
            for item in image_list:
                code = base64.b64encode(item)
                image = PassengerCarImage(image=code, passenger_car_id=car_id, created_at=datetime.datetime.now())
                conn.add(image)
            conn.commit()
            shutil.rmtree(f'images/{name}/{key}/', ignore_errors=True)
            return True
        return

    @classmethod
    def get_image(cls, key: str, car_id: int):
        image = conn.query(PassengerCarImage.image).filter_by(passenger_car_id=car_id).all()
        try:
            mkdir(f'images/{key}')
        except FileExistsError:
            pass
        if image:
            index = 0
            for item in image:
                code = base64.b64decode(item.image)
                fh = open(f"images/{key}/{index}.jpg", "wb")
                fh.write(code)
                fh.close()
                index += 1
        else:
            print('[INFO] Image does not exist')
        return True


def split_brand_and_model(item: str):
    exceptions = ['Samsung', 'Rover', 'Khodro', 'Wall', 'Trumpchi', 'Martin', 'Romeo']
    change = item.split(' ', 2)[1]
    if change in exceptions:
        brand = item.split(' ', 2)[:2]
        brand = ' '.join(brand)
        model = item.split(' ', 2)[2]
        return brand, model
    else:
        brand = item.split(' ', 1)[0]
        model = item.split(' ', 1)[1]
        return brand, model


def crop_and_save_images(images: List, key: str, name: str):
    images_list = []
    for i in range(len(images)):
        try:
            mkdir(f'images/{name}/{key}')
        except FileExistsError:
            pass
        time.sleep(0.1)
        p = requests.get(images[i])
        out = open(f"images/{name}/{key}/{i}.jpg", "wb")
        out.write(p.content)
        im = Image.open(f"images/{name}/{key}/{i}.jpg")
        out = crop_center(im)
        try:
            out.save(f"images/{name}/{key}/{i}.jpg", quality=95)
        except OSError:
            out.save(f"images/{name}/{key}/{i}.png", quality=95)
        with open(f"images/{name}/{key}/{i}.jpg", 'rb') as image:
            images_list.append(image.read())
        out.close()
    return images_list


# Функция для обрезки изображения по центру.
def crop_center(pil_img) -> Image:
    img_width, img_height = pil_img.size
    if img_width > 1100 and img_height > 800:
        crop_width = 1000
        crop_height = 700
        return pil_img.crop(((img_width - crop_width) // 2,
                             (img_height - crop_height) // 2,
                             (img_width + crop_width) // 2,
                             (img_height + crop_height) // 2))
    elif img_width < 1100 and img_width > 800:
        crop_width = 900
        crop_height = 500
        return pil_img.crop(((img_width - crop_width) // 2,
                             (img_height - crop_height) // 2,
                             (img_width + crop_width) // 2,
                             (img_height + crop_height) // 2))
    elif img_height < 600:
        crop_width = 600
        crop_height = 600
        return pil_img.crop(((img_width - crop_width) // 2,
                             (img_height - crop_height) // 2,
                             (img_width + crop_width) // 2,
                             (img_height + crop_height) // 2))
    elif img_height < img_width:
        crop_width = 800
        crop_height = 500
        return pil_img.crop(((img_width - crop_width) // 2,
                             (img_height - crop_height) // 2,
                             (img_width + crop_width) // 2,
                             (img_height + crop_height) // 2))
    elif img_height > img_width:
        crop_width = 600
        crop_height = 800
        return pil_img.crop(((img_width - crop_width) // 2,
                             (img_height - crop_height) // 2,
                             (img_width + crop_width) // 2,
                             (img_height + crop_height) // 2))
    else:
        crop_width = 650
        crop_height = 650
        return pil_img.crop(((img_width - crop_width) // 2,
                             (img_height - crop_height) // 2,
                             (img_width + crop_width) // 2,
                             (img_height + crop_height) // 2))


def get_created_date(date: str):
    date_item = date.split(".", 1)[0]
    now = datetime.datetime.now()
    clean = date_item.split(" ")
    created_date = clean[1]
    match clean[2]:
        case "д":
            try:
                end_date = datetime.date(day=(now.day - int(created_date)), year=now.year, month=now.month)
            except ValueError:
                if now.month == 1:
                    end_date = datetime.date(day=now.day, year=now.year, month=now.month)
                else:
                    end_date = datetime.date(day=now.day, year=now.year, month=now.month - 1)
            return end_date
        case "дней":
            try:
                end_date = datetime.date(day=(now.day - int(created_date)), year=now.year, month=now.month)
            except ValueError:
                if now.month == 1:
                    end_date = datetime.date(day=now.day, year=now.year, month=now.month)
                else:
                    end_date = datetime.date(day=now.day, year=now.year, month=now.month - 1)
            return end_date
        case "м":
            end_date = now
            return end_date
        case "года":
            end_date = datetime.date(day=now.day, month=now.month, year=(now.year - int(created_date)))
            return end_date
        case "мес":
            try:
                end_date = datetime.date(day=now.day, month=(now.month - int(created_date)), year=now.year)
            except ValueError:
                end_date = datetime.date(day=now.day, year=now.year - 1, month=now.month)
            return end_date
        case "месяца":
            try:
                end_date = datetime.date(day=now.day, month=(now.month - int(created_date)), year=now.year)
            except ValueError:
                end_date = datetime.date(day=now.day, year=now.year - 1, month=now.month)
            return end_date
        case _:
            end_date = now
            return end_date


def get_updated_date(updated_date: str):
    date_item = updated_date.split(".", 1)[0]
    now = datetime.datetime.now()
    clean = date_item.split(" ")
    created_date = clean[0]
    match clean[1]:
        case "д":
            try:
                end_date = datetime.date(day=(now.day - int(created_date)), year=now.year, month=now.month)
            except ValueError:
                if now.month == 1:
                    end_date = datetime.date(day=now.day, year=now.year, month=now.month)
                else:
                    end_date = datetime.date(day=now.day, year=now.year, month=now.month - 1)
            return end_date
        case "м":
            end_date = now
            return end_date
        case "года":
            end_date = datetime.date(day=now.day, month=now.month, year=(now.year - int(created_date)))
            return end_date
        case "мес":
            try:
                end_date = datetime.date(day=now.day, month=(now.month - int(created_date)), year=now.year)
            except ValueError:
                end_date = datetime.date(day=now.day, year=now.year - 1, month=now.month)
            return end_date
        case _:
            end_date = now
            return end_date


def get_convert_date(date: str):
    calendar = ['янв', 'фев', "мар", "апр", "мая", "июня", "июля", "авг", "сен", "окт", "нояб", "дек"]
    date_list = date.split(" ")[1].replace(".", "")
    for i in range(len(calendar)):
        if calendar[i] in date_list:
            return datetime.date(day=int(date.split(" ")[0]), month=i+1, year=int(date.split(" ")[2]))
