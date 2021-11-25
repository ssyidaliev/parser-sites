import datetime

from models.commercial_images import CommercialImage
from models.household_images import HouseHoldImage
from models.passenger_car_images import PassengerCarImage
from models.real_estate_images import RealEstateImage
from models.spare_images import SpareImage
from models.telephone_images import TelephoneImage
from settings.database import session

conn = session()


class DeleteImages:
    def __init__(self):
        self.current_date = datetime.datetime.now()
        self.models_list = [CommercialImage, PassengerCarImage, HouseHoldImage, SpareImage, RealEstateImage,
                            TelephoneImage]

    def check_records(self):
        for item in self.models_list:
            record = conn.query(item).all()
            for rec in record:
                if rec.created_at.date() == self.current_date.date() - datetime.timedelta(days=30):
                    print("Удалена изоражение с id=", rec.id)
                    conn.query(item).filter_by(id=rec.id).delete()
        conn.commit()


DeleteImages().check_records()