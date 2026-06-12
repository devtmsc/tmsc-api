from sqlalchemy import Column, Integer, String, DateTime, SmallInteger
from app.fastcore.db.base import Base
from sqlalchemy.dialects.postgresql import ARRAY


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100))
    role_id = Column(Integer)
    last_activity = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    model_config = {
        "from_attributes": True
    }

