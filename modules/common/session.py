# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Tạo engine PostgreSQL
engine_master = create_engine(
    settings.MASTER_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,
    connect_args={"application_name": settings.APP_NAME}
)

engine_replica = create_engine(
    settings.REPLICATE_DATABASE_URL,
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
def get_category_master_db():
    db = SessionLocalMaster()
    try:
        db.execute(text(settings.DATABASE_SEARCH_PATH_CATEGORY))
        # Kiểm tra search_path hiện tại (tùy chọn, để debug)
        yield db
    finally:
        db.close()


def get_category_replica_db():
    db = SessionLocalReplica()
    try:
        db.execute(text(settings.DATABASE_SEARCH_PATH_CATEGORY))
        # Kiểm tra search_path hiện tại (tùy chọn, để debug)
        yield db
    finally:
        db.rollback()
        db.close()


def get_logs_master_db():
    db = SessionLocalMaster()
    try:
        db.execute(text(settings.DATABASE_SEARCH_PATH_LOGS))
        # Kiểm tra search_path hiện tại (tùy chọn, để debug)
        yield db
    finally:
        db.close()


def get_logs_replica_db():
    db = SessionLocalReplica()
    try:
        db.execute(text(settings.DATABASE_SEARCH_PATH_LOGS))
        # Kiểm tra search_path hiện tại (tùy chọn, để debug)
        yield db
    finally:
        db.rollback()
        db.close()
        

def get_customer_master_db():
    db = SessionLocalMaster()
    try:
        db.execute(text(settings.DATABASE_SEARCH_PATH_CUSTOMER))
        # Kiểm tra search_path hiện tại (tùy chọn, để debug)
        yield db
    finally:
        db.close()


def get_customer_replica_db():
    db = SessionLocalReplica()
    try:
        db.execute(text(settings.DATABASE_SEARCH_PATH_CUSTOMER))
        # Kiểm tra search_path hiện tại (tùy chọn, để debug)
        yield db
    finally:
        db.rollback()
        db.close()

