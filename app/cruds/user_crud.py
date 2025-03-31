from typing import Optional

from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User  # модель пользователя
from schemas.auth import SignUpRequest  # схема входящих данных при регистрации


def fetch_user(db: Session, email: str) -> User:
    """
    Ищет пользователя в БД по email и возвращает его, если найден.
    """
    return db.query(User).filter(User.email == email).first()


def add_new_user(db: Session, user_data: SignUpRequest) -> User:
    """
    Создаёт новую запись пользователя. Пароль шифруется перед сохранением.
    """
    encrypted_password = generate_password_hash(user_data.password)
    new_user = User(email=user_data.email, password=encrypted_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def is_registered(db: Session, email: str) -> bool:
    """
    Определяет, зарегистрирован ли уже пользователь с данным email.
    """
    return bool(fetch_user(db, email))

def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not check_password_hash(user.password, password):
        return None
    return user

def validate_user_credentials(db: Session, login_info: SignUpRequest) -> Optional[User]:
    """
    Выполняет проверку учетных данных пользователя.
    Возвращает объект пользователя при успешной аутентификации, либо None.
    """
    authenticated_user = authenticate_user(db, login_info.email, login_info.password)
    return authenticated_user if authenticated_user else None