from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy import String, DateTime, Integer, Text, ForeignKey, DateTime, func, desc, asc, and_, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from typing import List
from app.fastcore.db.base import Base
from app.fastcore.db.soft_delete import SoftDeleteMixin
from datetime import datetime


class Base(DeclarativeBase):
    pass


class SocialCustomersModel(Base):
    __tablename__ = "social_customers"
    __table_args__ = {"schema": "customer"}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(30))
    provider_id: Mapped[str] = mapped_column(String(100))
    customer_id: Mapped[int] = mapped_column(ForeignKey('customer.customers.id'))
    nickname: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    avatar_url: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(100))
    channel: Mapped[int] = mapped_column(Integer)
    
    customer: Mapped["CustomersModel"] = relationship(back_populates="social")
    
    model_config = {
        "from_attributes": True
    }
    

class CustomersModel(Base):
    __tablename__ = "customers"
    __table_args__ = {"schema": "customer"}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(30))
    address: Mapped[str] = mapped_column(String(255))
    province_code: Mapped[str] = mapped_column(String(10))
    commune_code: Mapped[str] = mapped_column(String(10))
    status: Mapped[bool] = mapped_column(Boolean)
    sale_id: Mapped[int] = mapped_column(Integer)
    birthday: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    avatar_url: Mapped[str] = mapped_column(String(255))
    channel: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    social: Mapped[List[SocialCustomersModel]] = relationship(back_populates="customer")
    
    model_config = {
        "from_attributes": True
    }
