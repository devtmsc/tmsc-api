from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from typing import List
from app.fastcore.db.base import Base


class Base(DeclarativeBase):
    pass


class CommuneModel(Base):
    __tablename__ = "commune"
    __table_args__ = {"schema": "category"}
    
    code: Mapped[str] = mapped_column(primary_key=True)
    province_code: Mapped[str] = mapped_column(ForeignKey('category.province.code'))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    synonym: Mapped[list[str]] = mapped_column(ARRAY(String))
    
    province: Mapped["ProvinceModel"] = relationship(back_populates="communes")\
    
    model_config = {
        "from_attributes": True
    }
    

class ProvinceModel(Base):
    __tablename__ = "province"
    __table_args__ = {"schema": "category"}
    
    code: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    synonym: Mapped[list[str]] = mapped_column(ARRAY(String))
    
    communes: Mapped[List[CommuneModel]] = relationship(back_populates="province")
    
    model_config = {
        "from_attributes": True
    }


class ChannelModel(Base):
    __tablename__ = "channel"
    __table_args__ = {"schema": "category"}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    
    model_config = {
        "from_attributes": True
    }


class OrderPartnerModel(Base):
    __tablename__ = "order_partner"
    __table_args__ = {"schema": "category"}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(255))
    tracking_url: Mapped[str] = mapped_column(String(255))
    
    model_config = {
        "from_attributes": True
    }


class OrderReasonModel(Base):
    __tablename__ = "order_reason"
    __table_args__ = {"schema": "category"}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    partner_code: Mapped[str] = mapped_column(String(20))
    code: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(255))
    type: Mapped[int] = mapped_column(Integer)
    
    model_config = {
        "from_attributes": True
    }


class OrderStatusModel(Base):
    __tablename__ = "order_status"
    __table_args__ = {"schema": "category"}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(255))
    color: Mapped[str] = mapped_column(String(255))
    
    model_config = {
        "from_attributes": True
    }


class OrderStatusMappingModel(Base):
    __tablename__ = "order_status_mapping"
    __table_args__ = {"schema": "category"}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    partner_code: Mapped[str] = mapped_column(String(20))
    status_code: Mapped[int] = mapped_column(Integer)
    partner_status_code: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(255))
    
    model_config = {
        "from_attributes": True
    }

