from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy import String, DateTime, Integer, Text, ForeignKey, DateTime, func, desc, asc, and_, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from typing import List
from app.fastcore.db.base import Base
from app.fastcore.db.soft_delete import SoftDeleteMixin
from datetime import datetime


class Base(DeclarativeBase):
    pass


class SocialCustomersModel(SoftDeleteMixin, Base):
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
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    customer: Mapped["CustomersModel"] = relationship(back_populates="social")
    
    model_config = {
        "from_attributes": True
    }
    

class CustomersModel(SoftDeleteMixin, Base):
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
    reward_points: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    social: Mapped[List[SocialCustomersModel]] = relationship(back_populates="customer")
    
    model_config = {
        "from_attributes": True
    }


class RewardsModel(SoftDeleteMixin, Base):
    __tablename__ = "rewards"
    __table_args__ = {"schema": "customer"}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    points_required: Mapped[int] = mapped_column(Integer)
    stock: Mapped[int] = mapped_column(Integer)
    image: Mapped[str] = mapped_column(String(255))
    status: Mapped[bool] = mapped_column(Boolean)
    available_from: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    available_to: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    model_config = {
        "from_attributes": True
    }


class RewardRedemptionsModel(Base):
    __tablename__ = "reward_redemptions"
    __table_args__ = {"schema": "customer"}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(Integer)
    total_points_used: Mapped[int] = mapped_column(Integer)
    status: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String(255))
    code: Mapped[str] = mapped_column(String(255))
    reward_id: Mapped[int] = mapped_column(Integer)
    channel: Mapped[int] = mapped_column(Integer)
    balance_after: Mapped[int] = mapped_column(Integer)
    accepted_by: Mapped[str] = mapped_column(String(255))
    accepted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    canceled_by: Mapped[str] = mapped_column(String(255))
    canceled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    cancel_reason: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    model_config = {
        "from_attributes": True
    }
    

class RewardTransactionsModel(Base):
    __tablename__ = "reward_transactions"
    __table_args__ = {"schema": "customer"}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(Integer)
    transaction_type: Mapped[int] = mapped_column(Integer)
    point: Mapped[int] = mapped_column(Integer)
    balance_after: Mapped[int] = mapped_column(Integer)
    reference_id: Mapped[int] = mapped_column(Integer)
    reference_type: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String(255))
    transaction_code: Mapped[str] = mapped_column(String(255))
    channel: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    model_config = {
        "from_attributes": True
    }
