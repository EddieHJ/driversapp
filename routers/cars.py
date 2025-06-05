from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import Cars
from routers.auth import decode_jwt, decode_jwt_new

router = APIRouter(
    prefix="/cars",
    tags=["汽车"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
driver_dependency = Annotated[dict, Depends(decode_jwt)]
driver_dependency_new = Annotated[dict, Depends(decode_jwt_new)]


class CarResponse(BaseModel):
    manufacturer: str = Field(max_length=30)
    model: str = Field(max_length=30)
    year: int = Field(gt=1800)


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_cars(driver: driver_dependency_new, db: db_dependency):
    if not driver:
        raise HTTPException(401, "driver not found")

    return db.query(Cars).all()


@router.get("/read_all", status_code=status.HTTP_200_OK)
async def read_all_cars(driver: driver_dependency_new, db: db_dependency):
    if not driver:
        raise HTTPException(401, "driver not found")
    return db.query(Cars).all()


@router.get("/{car_id}", status_code=status.HTTP_200_OK)
async def read_car(db: db_dependency, car_id: int):
    car_model = db.query(Cars).filter(Cars.id == car_id).first()
    if car_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return car_model


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_car(driver: driver_dependency_new, db: db_dependency, car_response: CarResponse):
    if not driver:
        raise HTTPException(401, "driver not found")
    car_model = Cars(**car_response.model_dump(), owner_id=driver.get("id"))
    db.add(car_model)
    db.commit()


@router.put("/{car_id}", status_code=status.HTTP_200_OK)
def update_car(db: db_dependency, car_id: int, car_response: CarResponse):
    car_response_model = db.query(Cars).filter(Cars.id == car_id).first()
    if car_response_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="车型未找到")

    car_response_model.manufacturer = car_response.manufacturer
    car_response_model.model = car_response.model
    car_response_model.year = car_response.year

    db.commit()


@router.delete("/{car_id}", status_code=status.HTTP_200_OK)
def delete_car(db: db_dependency, car_id: int):
    car_response_model = db.query(Cars).filter(Cars.id == car_id).first()
    if car_response_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="要删除的车型未找到")

    db.delete(car_response_model)
    db.commit()
