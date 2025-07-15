import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Загружаем переменные из файла .env
from database.models import Base
from config import load_config
config = load_config()

# Конфигурация PostgreSQL
DB_CONFIG = {
    "protocol": "postgresql+asyncpg",
    "user": config.db.user,
    "password": config.db.password,
    "host": config.db.host,
    "port": config.db.port,
    "db_name": config.db.database
}



# Настройка подключения к базе данных
protocol = "postgresql+psycopg2"
username = DB_CONFIG.get("user")  # 🔹 Логин от PostgreSQL
password = DB_CONFIG.get("password")  # 🔹 Пароль от PostgreSQL
server = DB_CONFIG.get("host")    # 🔹 Например, localhost или IP
port = DB_CONFIG.get("port")              # 🔹 Порт (по умолчанию 5432)
database = DB_CONFIG.get("db_name")  # 🔹 Название базы данных

connection_string = f"{protocol}://{username}:{password}@{server}:{port}/{database}"
print(connection_string)

# Создание движка для подключения к базе данных
engine = create_engine(connection_string)

# Создание таблиц
Base.metadata.create_all(bind=engine)
