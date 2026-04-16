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
    password = Column(String(255))
    role_id = Column(Integer)
    is_active = Column(SmallInteger)
    last_activity = Column(DateTime)
    department = Column(ARRAY(Integer))
    position = Column(Integer)
    last_login_at = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)

    model_config = {
        "from_attributes": True
    }
    
    @property
    def created_time(self):
        return self.created_at.strftime("%Y%m%d %H:%M") if self.created_at else None
