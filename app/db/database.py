from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings  # settings.DATABASE_URL должен содержать адрес вашей БД

DATABASE_URI = settings.DATABASE_URL

db_engine = create_engine(
    DATABASE_URI,
    connect_args={"check_same_thread": False}  # Обязательный аргумент для SQLite
)

DBSession = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

BaseModel = declarative_base()

def initialize_database():
    """
    Подключаем модели для регистрации в BaseModel.metadata и создаем таблицы,
    если они еще не созданы.
    """
    from models import user, word, corpus  # Импортируем модели для их регистрации
    BaseModel.metadata.create_all(bind=db_engine)
