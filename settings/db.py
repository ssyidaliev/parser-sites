import psycopg2
from decouple import config

try:
    connection = psycopg2.connect(dbname=config('DB_NAME'),
                                  user=config('DB_USER'),
                                  password=config('DB_PASSWORD'),
                                  host=config('DB_HOST'))
    connection.commit()
except Exception as _ex:
    print("[INFO] Exception while error working with PostgreSQL", _ex)
finally:
    if connection:
        connection.close()
        print("[INFO] PostgreSQL connection closed")
