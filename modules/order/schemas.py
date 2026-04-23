from app.fastcore.common.models import DRFStyleBaseModel, DRFCharField, DRFIntField, DRFListField, DRFDateTimeField, DRFBooleanField, DRFDictField
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
    image_url: Optional[str] = DRFCharField('image_url', max_length=200, required=False, blank=True)
    
    
class OrderCreateSchema(DRFStyleBaseModel):
    channel: int = DRFIntField('channel', required=True)
    tracking_code: int = DRFIntField('tracking_code', required=True)
    customer_id: Optional[int] = DRFIntField('customer_id', required=False)
    receiver_name: str = DRFCharField('receiver_name', max_length=255, required=True, blank=False)
    receiver_phone: str = DRFCharField('receiver_phone', max_length=50, required=True, blank=False)
    receiver_email: Optional[str] = DRFCharField('receiver_email', max_length=255, required=False, blank=True)
    receiver_province_code: Optional[str] = DRFCharField('receiver_province_code', max_length=10, required=False, blank=True)
    receiver_commune_code: Optional[str] = DRFCharField('receiver_commune_code', max_length=10, required=False, blank=True)
    receiver_address: str = DRFCharField('receiver_address', max_length=255, required=True, blank=False)
    description: Optional[str] = DRFCharField('description', max_length=255, required=False, blank=True)
    money_collect: int = DRFIntField('money_collect', required=True)
    total_freight: Optional[int] = DRFIntField('total_freight', required=False)
    reward_id: Optional[int] = DRFIntField('reward_id', required=False)
    reward_value: Optional[int] = DRFIntField('reward_value', required=False)
    items: Optional[list[OrderItemsSchema]] = DRFListField('items', required=False)
    delivery_method: Optional[int] = DRFIntField('delivery_method', required=False, default=1)
    pickup_scheduled_at: Optional[datetime] = DRFDateTimeField('pickup_scheduled_at', required=False)


class OrderListSchema(DRFStyleBaseModel):
    channel: int = DRFIntField('channel', required=True)
    customer_id: int = DRFIntField('customer_id', required=True)
    page: int = DRFIntField('page', required=True)
    page_size: int = DRFIntField('page_size', required=False, default=10)
    tracking_code: Optional[str] = DRFCharField('title', max_length=255, required=False, blank=True)
    status: Optional[int] = DRFIntField('status', required=False)
    created_from: Optional[datetime] = DRFDateTimeField('created_from', required=True)
    created_to: Optional[datetime] = DRFDateTimeField('created_to', required=True)


class VTPPoDSchema(DRFStyleBaseModel):
    IMAGES: Optional[list[str]] = DRFListField('images', required=False, item_type='str')


class VTPSchema(DRFStyleBaseModel):
    ORDER_NUMBER: str = DRFCharField('ORDER_NUMBER', max_length=50, required=True, blank=False)
    ORDER_REFERENCE: str = DRFCharField('ORDER_REFERENCE', max_length=50, required=True, blank=False)
    ORDER_STATUSDATE: str = DRFCharField('ORDER_STATUSDATE', max_length=50, required=True, blank=False)
    ORDER_STATUS: int = DRFIntField('ORDER_STATUS', required=True)
    STATUS_NAME: str = DRFCharField('STATUS_NAME', max_length=200, required=True, blank=False)
    LOCALION_CURRENTLY: str = DRFCharField('LOCALION_CURRENTLY', max_length=200, required=True, blank=False)
    NOTE: str = DRFCharField('NOTE', max_length=200, required=True, blank=False)
    MONEY_COLLECTION: int = DRFIntField('MONEY_COLLECTION', required=True)
    MONEY_TOTAL: int = DRFIntField('MONEY_TOTAL', required=True)
    PRODUCT_WEIGHT: int = DRFIntField('PRODUCT_WEIGHT', required=True)
    MONEY_COLLECTION_ORIGIN: Optional[int] = DRFIntField('MONEY_COLLECTION_ORIGIN', required=False)
    EMPLOYEE_NAME: Optional[str] = DRFCharField('EMPLOYEE_NAME', max_length=200, required=False, blank=True)
    EMPLOYEE_PHONE: Optional[str] = DRFCharField('EMPLOYEE_PHONE', max_length=200, required=False, blank=True)
    VOUCHER_VALUE: Optional[int] = DRFIntField('PRODUCT_WEIGHT', required=False)
    EXPECTED_DELIVERY_DATE: Optional[str] = DRFCharField('EXPECTED_DELIVERY_DATE', max_length=100, required=False,
                                                         blank=True)
    MONEY_FEECOD: Optional[int] = DRFIntField('MONEY_FEECOD', required=False)
    ORDER_PAYMENT: Optional[int] = DRFIntField('ORDER_PAYMENT', required=False)
    EXPECTED_DELIVERY: Optional[str] = DRFCharField('EXPECTED_DELIVERY', max_length=100, required=False, blank=True)
    ORDER_SERVICE: Optional[str] = DRFCharField('ORDER_SERVICE', max_length=50, required=False, blank=True)
    MONEY_TOTALFEE: Optional[int] = DRFIntField('ORDER_PAYMENT', required=False)
    DETAIL: Optional[list] = DRFListField('DETAIL', required=False)
    IS_RETURNING: Optional[bool] = DRFBooleanField('IS_RETURNING', required=False)
    REASON_CODE: Optional[str] = DRFCharField('REASON_CODE', max_length=50, required=False, blank=True)
    tracking_code: Optional[str] = DRFCharField('tracking_code', max_length=50, required=False, blank=True)
    request_id: Optional[int] = DRFIntField('ORDER_PAYMENT', required=False)
    POD: Optional[VTPPoDSchema]

    model_config = {
        "from_attributes": True
    }


class InputVTPSchema(DRFStyleBaseModel):
    DATA: VTPSchema
    TOKEN: str = DRFCharField('TOKEN', max_length=200, required=False, blank=True)