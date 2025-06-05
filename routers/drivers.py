from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Drivers
from routers.auth import decode_jwt_new

router = APIRouter(
    prefix="/drivers",
    tags=["车手"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
driver_dependency = Annotated[dict, Depends(decode_jwt_new)]

@router.put("/add_phone/{phone}", status_code=200)
async def add_phone(db: db_dependency, driver: driver_dependency, phone: int):
    if not driver:
        raise HTTPException(status_code=404, detail="加电话的时候driver not found")

    driver_model = db.query(Drivers).filter(Drivers.username==driver.get("username")).first()
    driver_model.phone_number = phone
    db.commit()


# 获取当前身份
@router.get("/", status_code=200)
async def get_drivers(db: db_dependency, driver: driver_dependency):
    if not driver:
        raise HTTPException(status_code=404, detail="driver not found")

    return db.query(Drivers).filter(Drivers.id==driver.get("id")).first()