import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG = False
    TESTING = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")


class DevelopmentConfig(Config):
    DEBUG = True
    MONGODB_URI = os.getenv("MONGODB_URI")
    SENTRY_DNS = os.getenv("SENTRY_DNS")


class ProductionConfig(Config):
    MONGODB_URI = os.getenv("MONGODB_URI")
    SENTRY_DNS = os.getenv("SENTRY_DNS")


config_dic = {"dev": DevelopmentConfig, "prod": ProductionConfig}
