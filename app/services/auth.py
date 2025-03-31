from datetime import datetime, timedelta
import jwt
from core.config import settings
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session
from core.config import settings
from db.__init__ import obtain_db
from models.user import User
from schemas.auth import SignUpRequest


def generate_token(payload: dict, expires_in: timedelta = None) -> str:
    """
    Формирует JWT-токен с заданными данными и сроком действия.
    """
    token_payload = payload.copy()
    expiry = datetime.utcnow() + (expires_in if expires_in else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    token_payload.update({"exp": expiry})
    return jwt.encode(token_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/login/")

def retrieve_user_from_token(req: Request, session: Session = Depends(obtain_db)) -> User:
    token_value = req.cookies.get("access_token")
    if not token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не обнаружен в cookies"
        )

    try:
        token_payload = jwt.decode(token_value, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_identifier = token_payload.get("user_id")
        if user_identifier is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Не удалось извлечь данные пользователя из токена"
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Истек срок действия токена"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Получен некорректный токен"
        )

    user_record = session.query(User).filter(User.id == user_identifier).first()
    if user_record is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )
    return user_record
