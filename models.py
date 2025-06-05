from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base


class Drivers(Base):
    __tablename__ = 'drivers'

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String)
    fav_brand = Column(String)

    # add one column
    phone_number = Column(Integer, nullable=True)

class Cars(Base):
    __tablename__ = 'cars'

    id = Column(Integer, primary_key=True, nullable=False)
    manufacturer = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=True)

    # add one column
    owner_id = Column(Integer, ForeignKey('drivers.id'))  # 这个外键，怎么和Drivers的id关联上的？
