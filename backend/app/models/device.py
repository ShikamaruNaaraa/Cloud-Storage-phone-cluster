from sqlalchemy import Column, Integer, String, Enum, BigInteger, TIMESTAMP, ForeignKey
from app.core.database import Base

class Device(Base):
    __tablename__ = "devices"

    device_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    device_name = Column(String(255))
    status = Column(Enum("ONLINE", "OFFLINE"), nullable=False, default="OFFLINE")
    last_heartbeat = Column(TIMESTAMP, nullable=False)

    storage_capacity = Column(BigInteger, nullable=False)
    available_storage = Column(BigInteger, nullable=False)

