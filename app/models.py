from sqlalchemy import Column, Integer, String, Date
from app.database import Base

class ParkingEntry(Base):
    __tablename__ = "parking_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, nullable=False)
    entry_date = Column(Date, nullable=False)
    entry_type = Column(String, default="booking")  # μόνο "booking"
    location = Column(String, nullable=False)
