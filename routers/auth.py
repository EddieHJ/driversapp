from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import Drivers

from passlib.context import CryptContext

router = APIRouter(
    prefix="/auth",
    tags=["验证"],
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class DriversResponse(BaseModel):
    username: str = Field(max_length=30)
    password: str = Field(max_length=100)
    role: str = Field(max_length=30)
    fav_brand: str


class Token(BaseModel):
    access_token: str
    token_type: str


SECRET_KEY = "b4aa8b4da1a7bccf673c8ecea2e9504d8de8447dad0e842077d757f5970d029c"
ALGORITHM = "HS256"


def create_jwt_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id, "role": role,
              "exp": datetime.now(timezone.utc) + expires_delta}
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def auth_driver_identity(db, username: str, password: str) -> bool | Drivers:
    driver_model = db.query(Drivers).filter(Drivers.username == username).first()
    if driver_model is None:
        return False
    verified = bcrypt_context.verify(password, driver_model.hashed_password)
    if not verified:
        return False
    return driver_model


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_drivers(db: db_dependency):
    return db.query(Drivers).all()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_driver(db: db_dependency, driver_response: DriversResponse):
    driver_model = Drivers(
        username=driver_response.username,
        hashed_password=bcrypt_context.hash(driver_response.password),
        role=driver_response.role,
        fav_brand=driver_response.fav_brand,
    )
    db.add(driver_model)
    db.commit()


@router.put("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_driver(db: db_dependency, driver_id: int, driver_response: DriversResponse):
    driver_model = db.query(Drivers).filter(Drivers.id == driver_id).first()
    if driver_model is None:
        raise HTTPException(404, "Driver not found")

    driver_model.username = driver_response.username
    driver_model.role = driver_response.role
    driver_model.fav_brand = driver_response.fav_brand

    db.commit()


@router.delete("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_driver(db: db_dependency, driver_id: int):
    driver_model = db.query(Drivers).filter(Drivers.id == driver_id).first()
    if driver_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="删除车手时，找不到车手")
    db.delete(driver_model)
    db.commit()


"""
补充一下，为什么username: str, password: str的形式不如OAuth2？
首先，OAuth2更现代、高级，显得更高大上
其次，OAuth2标准，本质就是比username、password多了几个字段，但基于这多出来的字段可以衍生出很多验证的操作、应用（后面用到就会理解，问GPT吧）
用username\password和OAuth2最后的结果都是一样的，但是还是因为以上高级特性，推荐用OAuth2
"""
@router.post("/token", status_code=status.HTTP_200_OK, response_model=Token)
async def login_for_access_token(form: Annotated[OAuth2PasswordRequestForm, Depends()],db: db_dependency):
    driver = auth_driver_identity(db, form.username, form.password)
    if not driver:
        raise HTTPException(401, "验证用户身份失败")

    token = create_jwt_token(driver.username, driver.id, driver.role, timedelta(minutes=30))
    return {"access_token": token, "token_type": "bearer"}


################################
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")  # token是API的url， but only for Swagger

# 土办法
def decode_jwt(token: str) -> dict:
    try:
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        id: int = payload.get("id")
        role: str = payload.get("role")
        exp: str = payload.get("exp")
        return {"username": username, "id": id}

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

# 高级办法
def decode_jwt_new(token: Annotated[str, Depends(oauth2_bearer)]) -> dict:
    try:
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        id: int = payload.get("id")
        role: str = payload.get("role")
        exp: str = payload.get("exp")
        return {"username": username, "id": id, "role": role}
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

