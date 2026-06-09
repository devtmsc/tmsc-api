# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Tạo engine PostgreSQL
engine_master = create_engine(
    settings.AUTH_MASTER_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,
    connect_args={"application_name": settings.APP_NAME}
)

engine_replica = create_engine(
    settings.AUTH_REPLICATE_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,
    connect_args={"application_name": settings.APP_NAME}
)

# Tạo session
SessionLocalMaster = sessionmaker(autocommit=False, autoflush=False, bind=engine_master)
SessionLocalReplica = sessionmaker(autocommit=False, autoflush=False, bind=engine_replica)


# Dependency cho FastAPI
def get_master_db():
    with SessionLocalMaster() as session:
        yield session


def get_replica_db():
    with SessionLocalReplica() as session:
        yield session
