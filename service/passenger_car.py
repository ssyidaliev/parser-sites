import base64
import binascii
import shutil

from models.passenger_car import PassengerCar, PassengerCarImage
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
    def add_image(cls, car_id: int, images_count: int, key: str):
        for i in range(int(images_count)):
            with open(f"images/{key}/{i}.jpg", "rb") as image_file:
                image = PassengerCarImage(image=base64.b64encode(image_file.read()), passenger_car_id=car_id)
                conn.add(image)
        conn.commit()
        shutil.rmtree(f"images/{key}", ignore_errors=True)
        return True

    @classmethod
    def get_image(cls, car_id: int, images_count: int, key: str):
        image = conn.query(PassengerCarImage).filter_by(passenger_car_id=car_id).all()
        for i in range(len(image)):
            try:
                fh = open(f"images/{key}/{i}.jpg", "wb")
                fh.write(base64.b64decode('base64'))
                fh.close()
            except binascii.Error:
                pass
        return True
