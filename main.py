from fastapi import FastAPI
import models
from database import engine
from routers import cars, drivers, auth, admin

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(cars.router)
app.include_router(auth.router)
app.include_router(drivers.router)
app.include_router(admin.router)
