from fastapi import FastAPI, HTTPException, Depends, Response
from sqlalchemy.orm import Session

from db.database import initialize_database
from models.corpus import Corpus
from models.user import User

from schemas.auth import SignUpRequest, UserResponse
from cruds.user_crud import is_registered, add_new_user, validate_user_credentials
from schemas.corpus import CorpusesResponse, CorpusInput
from schemas.fuzzy_search import RequestModel
from services.auth import generate_token, retrieve_user_from_token
from db.__init__ import obtain_db
from services.fuzzy_search.run_search import execute_search_algorithm
from services.text_processing import create_corpus_entry, store_words

from fastapi import FastAPI

app = FastAPI(
    title="Fuzzy Search API",
    description="API приложение для нечеткого поиска",
    debug=True)

initialize_database()


@app.post("/sign-up/",
          tags=["Accounts"],
          summary="Регистрация пользователя по email")
def register_account(req: SignUpRequest, response: Response, db: Session = Depends(obtain_db)):
    """
    Проверяет, зарегистрирован ли уже пользователь с указанным email.
    Если пользователь отсутствует, создаёт новую запись и генерирует JWT-токен доступа.
    Возвращает данные зарегистрированного пользователя.

    Пример входящего запроса:
    {
        "email": "user@example.com",
        "password": "securepassword123"
    }

    Пример ответа:
    {
        "id": 1,
        "email": "user@example.com",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    """
    if is_registered(db, req.email):
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    user_entry = add_new_user(db, req)
    token_str = generate_token({"user_id": user_entry.id})
    response.set_cookie(key="access_token", value=token_str, httponly=True)
    return {"id": user_entry.id, "email": user_entry.email, "token": token_str}


@app.post("/login/",
          tags=['Accounts'],
          summary="Аутентификация пользователя")
def login_user(credentials: SignUpRequest, response: Response, db: Session = Depends(obtain_db)):
    """
    Проверяет наличие пользователя с указанным email и корректность пароля.
    Если данные верны, создается новый JWT-токен, который записывается в cookies.
    Возвращает данные пользователя вместе с токеном.

    Пример входящего запроса:
    {
        "email": "user@example.com",
        "password": "securepassword123"
    }

    Пример ответа:
    {
        "id": 1,
        "email": "user@example.com",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    """
    user_obj = validate_user_credentials(db, credentials)
    if not user_obj:
        raise HTTPException(status_code=401, detail="Неверные данные для входа")
    jwt_token = generate_token({"user_id": user_obj.id})
    response.set_cookie(key="access_token", value=jwt_token, httponly=True)
    return {"id": user_obj.id, "email": user_obj.email, "token": jwt_token}


@app.get(
    "/users/me/",
    response_model=UserResponse,
    tags=["Accounts"],
    summary="Получение данных о своем аккаунте"
)
def get_my_profile(current_user: User = Depends(retrieve_user_from_token)):
    """
    Возвращает информацию об авторизованном пользователе.

    Для доступа необходимо передать токен через cookies.

    Пример ответа:
    {
      "id": 1,
      "email": "user@example.com"
    }
    """
    return {"user_id": current_user.id, "email": current_user.email}


@app.post("/upload_corpus",
          tags=["Corpuses"],
          summary="Загружает корпус текста для индексации и поиска")
def upload_text_corpus(payload: CorpusInput, db: Session = Depends(obtain_db)):
    """
    Загружает текстовый корпус для индексации и поиска.

    Пример запроса:
    {
        "corpus_name": "example_corpus",
        "text": "This is a sample text for the corpus."
    }
    Пример ответа:
    {
        "corpus_id": 1,
        "message": "Corpus uploaded successfully"
    }
    """
    corpus_record = create_corpus_entry(db, payload)
    store_words(db, corpus_record.corpus_id, payload.text)
    return {
        "corpus_id": corpus_record.corpus_id,
        "message": "Corpus uploaded successfully"
    }


@app.get("/corpuses",
         tags=["Corpuses"],
         summary="Получить список текстовых корпусов",
         response_model=CorpusesResponse)
def retrieve_corpora(session: Session = Depends(obtain_db)):
    """
    Возвращает перечень текстовых корпусов с их идентификаторами и именами.

    Пример ответа:
    {
      "corpuses": [
         {"corpus_id": 1, "corpus_name": "example_corpus"},
         {"corpus_id": 2, "corpus_name": "another_corpus"}
      ]
    }
    """
    corpus_list = session.query(Corpus).all()
    # Преобразуем объекты в словари с нужными полями
    result = [
        {"corpus_id": corpus.corpus_id, "corpus_name": corpus.name} for corpus in corpus_list
    ]
    return {"corpuses": result}


@app.post("/search_algorithm",
          tags=['Fuzzy search'],
          summary="Алгоритмы 'Расстояние Дамерау-Левенштейна' и 'Алгоритм Bitap (Wu и Manber)' для нечёткого поиска")
def search_algorithm(request: RequestModel, db: Session = Depends(obtain_db)):
    """
    Позволяет задать слово для поиска, выбрать алгоритм поиска и указать корпус,
    который будет использоваться для анализа. Возвращает время выполнения алгоритма и результаты поиска.

    Пример запроса:
    {
        "word": "example",
        "algorithm": "damerau",  # или "bitap"
        "corpus_id": 1
    }

    Пример ответа:
    {
        "execution_time": 0.0023,
        "results": [
            {"word": "example", "distance": 0},
            {"word": "sample", "distance": 2}
        ]
    }
    """
    results, elapsed = execute_search_algorithm(request, db)
    if results is False:
        raise HTTPException(status_code=401, detail="Указанный алгоритм не реализован в приложении")
    return {
        "execution_time": elapsed,
        "results": results
    }
