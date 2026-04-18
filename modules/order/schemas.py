from app.fastcore.common.models import DRFStyleBaseModel, DRFCharField, DRFIntField, DRFListField, DRFDateTimeField
from typing import Optional
from datetime import datetime


class OrderItemsSchema(DRFStyleBaseModel):
    product_id: Optional[int] = DRFIntField('product_id', required=False)
    name: str = DRFCharField('name', max_length=255, required=True, blank=False)
    quantity: Optional[int] = DRFIntField('quantity', required=False, default=1)
    subtotal: Optional[int] = DRFIntField('subtotal', required=False, default=0)
    subtotal_tax: Optional[int] = DRFIntField('subtotal_tax', required=False, default=0)
    total: Optional[int] = DRFIntField('total', required=False, default=0)
    total_tax: Optional[int] = DRFIntField('total_tax', required=False, default=0)
    
    
class OrderCreateSchema(DRFStyleBaseModel):
    channel: int = DRFIntField('channel', required=True)
    tracking_code: int = DRFIntField('tracking_code', required=True)
    customer_id: Optional[int] = DRFIntField('customer_id', required=False)
    receiver_name: str = DRFCharField('receiver_name', max_length=255, required=True, blank=False)
    receiver_phone: str = DRFCharField('receiver_phone', max_length=50, required=True, blank=False)
    receiver_email: Optional[str] = DRFCharField('receiver_email', max_length=255, required=False, blank=True)
    receiver_province_code: Optional[str] = DRFCharField('receiver_province_code', max_length=10, required=False, blank=True)
    receiver_commune_code: Optional[str] = DRFCharField('receiver_commune_code', max_length=10, required=False, blank=True)
    receiver_address: str = DRFCharField('receiver_phone', max_length=255, required=True, blank=False)
    description: Optional[str] = DRFCharField('description', max_length=255, required=False, blank=True)
    money_collect: int = DRFIntField('money_collect', required=True)
    total_freight: Optional[int] = DRFIntField('money_collect', required=False)
    reward_id: Optional[int] = DRFIntField('reward_id', required=False)
    reward_value: Optional[int] = DRFIntField('reward_value', required=False)
    items: Optional[list[OrderItemsSchema]] = DRFListField('items', required=False)
