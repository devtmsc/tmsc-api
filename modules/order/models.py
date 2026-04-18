from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy import String, DateTime, Integer, Text, ForeignKey, DateTime, func, desc, asc, and_, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from typing import List
from app.fastcore.db.base import Base
from app.fastcore.db.soft_delete import SoftDeleteMixin
from datetime import datetime


class Base(DeclarativeBase):
    pass

class OrderLogModel(Base):
    __tablename__ = "order_log"
    __table_args__ = {"schema": "logs"}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(Integer)
    tracking_code: Mapped[str] = mapped_column(String(30))
    channel: Mapped[int] = mapped_column(Integer)
    input: Mapped[dict] = mapped_column(JSONB)
    output: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    model_config = {
        "from_attributes": True
    }
    

class OrdersModel(SoftDeleteMixin, Base):
    __tablename__ = "orders"
    __table_args__ = {"schema": "customer"}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tracking_code: Mapped[str] = mapped_column(String(30))
    customer_id: Mapped[int] = mapped_column(Integer)
    receiver_name: Mapped[str] = mapped_column(String(200))
    receiver_phone: Mapped[str] = mapped_column(String(30))
    receiver_email: Mapped[str] = mapped_column(String(200))
    receiver_province_code: Mapped[str] = mapped_column(String(10))
    receiver_commune_code: Mapped[str] = mapped_column(String(10))
    receiver_address: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[int] = mapped_column(Integer)
    money_collect: Mapped[int] = mapped_column(Integer)
    total_freight: Mapped[int] = mapped_column(Integer)
    reward_redemptions_id: Mapped[int] = mapped_column(Integer)
    channel: Mapped[str] = mapped_column(String(100))
    items: Mapped[dict] = mapped_column(JSONB)
    delivery_method: Mapped[int] = mapped_column(Integer)
    pickup_scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    returned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    canceled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    canceled_by: Mapped[int] = mapped_column(Integer)
    cancel_reason: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    year_month: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    model_config = {
        "from_attributes": True
    }
