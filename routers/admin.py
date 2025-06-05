from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Drivers, Cars
from routers.auth import decode_jwt_new

router = APIRouter(
    prefix="/admin",
    tags=["管理"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
driver_dependency = Annotated[dict, Depends(decode_jwt_new)]

@router.delete("/car/{car_id}", status_code=204)
async def delete_as_admin(car_id: int, driver: driver_dependency, db: db_dependency):
    if not driver:
        raise HTTPException(401)
    if driver.get("role") != "admin":
        raise HTTPException(401, "您不是管理员")

    car_model = db.query(Cars).filter(Cars.id == car_id).first()
    if car_model is None:
        raise HTTPException(404)
    db.delete(car_model)
    db.commit()

