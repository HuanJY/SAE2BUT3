import os

class Config:
    SECRET_KEY = 'IY4AaZAmVdNQHGTssARb3yutVbd27hKT'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/sae_economy_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
