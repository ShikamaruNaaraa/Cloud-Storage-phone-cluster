from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = (
    "mysql+mysqlconnector://storage_user:1234@localhost/phone_storage"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # auto-reconnect if MySQL drops connection
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()
