import base64
import datetime
import shutil
from os import mkdir

from models.spare import Spare
from models.spare_images import SpareImage
from settings.database import session

conn = session()


class SpareService:
    @classmethod
    def check_record(cls, **filters):
        return conn.query(Spare).filter_by(**filters).all()

    @classmethod
    def get(cls, **filters):
        return conn.query(Spare).filter_by(**filters).first()

    @classmethod
    def create_record(cls, **filters):
        record = Spare(**filters)
        conn.add(record)
        conn.commit()
        return True

    @classmethod
    def add_image(cls, spare_id: int, image_list: list, key: str, name: str):
        if image_list:
            for item in image_list:
                code = base64.b64encode(item)
                image = SpareImage(image=code, spare_id=spare_id, created_at=datetime.datetime.now())
                conn.add(image)
            conn.commit()
            shutil.rmtree(f"images/{name}/{key}", ignore_errors=True)
            return True
        else:
            return

    @classmethod
    def get_image(cls, key: str, spare_id: int, name: str):
        image = conn.query(SpareImage.image).filter_by(real_estate_id=spare_id).all()
        try:
            mkdir(f'images/{name}/{key}')
        except FileExistsError:
            pass
        if image:
            index = 0
            for item in image:
                code = base64.b64decode(item.image)
                fh = open(f"images/{name}/{key}/{index}.jpg", "wb")
                fh.write(code)
                fh.close()
                index += 1
        else:
            print('[INFO] Image does not exist')
        return True
