import base64
import datetime
import shutil

from os import mkdir
from models.household import Household
from models.household_images import HouseHoldImage
from settings.database import session

conn = session()


class HouseholdService:
    model = Household()

    @classmethod
    def check_record(cls, **filters):
        return conn.query(Household).filter_by(**filters).all()

    @classmethod
    def get(cls, **filters):
        return conn.query(Household).filter_by(**filters).first()

    @classmethod
    def create_record(cls, **filters):
        record = Household(**filters)
        conn.add(record)
        conn.commit()
        return True

    @classmethod
    def add_image(cls, household_id: int, image_list: list, key: str):
        for item in image_list:
            code = base64.b64encode(item)
            image = HouseHoldImage(image=code, household_id=household_id, created_at=datetime.datetime.now())
            conn.add(image)
            shutil.rmtree(f"images/{key}", ignore_errors=True)
        conn.commit()
        return True

    @classmethod
    def get_image(cls, key: str, household_id: int):
        image = conn.query(HouseHoldImage.image).filter_by(household_id=household_id).all()
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
