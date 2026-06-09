from sqlalchemy import Column, Integer, String, DateTime, SmallInteger
from app.fastcore.db.base import Base
from sqlalchemy.dialects.postgresql import ARRAY


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100))
    phone = Column(String(100))
    fullname = Column(String(200))
    avatar = Column(String(100))
    is_active = Column(SmallInteger)
    department = Column(ARRAY(Integer))
    position = Column(Integer)
    google_sub = Column(String(200))
    last_login_at = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    model_config = {
        "from_attributes": True
    }

