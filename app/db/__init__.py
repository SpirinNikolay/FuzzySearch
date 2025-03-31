from db.database import DBSession


def obtain_db():
    """
    Зависимость для создания сессии базы данных.
    Сессия открывается, используется и затем закрывается.
    """
    session = DBSession()
    try:
        yield session
    finally:
        session.close()
