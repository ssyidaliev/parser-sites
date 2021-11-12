import base64
import datetime
import shutil

from os import mkdir
from models.telephone import Telephone
from models.telephone_images import TelephoneImage
from settings.database import session

conn = session()


class TelephoneService:
    model = Telephone()

    @classmethod
    def check_record(cls, **filters):
        return conn.query(Telephone).filter_by(**filters).all()

    @classmethod
    def get(cls, **filters):
        return conn.query(Telephone).filter_by(**filters).first()

    @classmethod
    def create_record(cls, **filters):
        record = Telephone(**filters)
        conn.add(record)
        conn.commit()
        return True

    @classmethod
    def add_image(cls, phone_id: int, image_list: list, key: str):
        for item in image_list:
            code = base64.b64encode(item)
            image = TelephoneImage(image=code, telephone_id=phone_id, created_at=datetime.datetime.now())
            conn.add(image)
        conn.commit()
        shutil.rmtree(f"images/{key}", ignore_errors=True)
        return True

    @classmethod
    def get_image(cls, key: str, phone_id: int):
        image = conn.query(TelephoneImage.image).filter_by(telephone_id=phone_id).all()
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
