from app.fastcore.common.models import DRFStyleBaseModel, DRFCharField, DRFIntField, DRFDateTimeField
from typing import Optional
from datetime import datetime


class CustomerCreateSchema(DRFStyleBaseModel):
    fullname: str = DRFCharField('fullname', max_length=255, required=True, blank=False)
    phone: str = DRFCharField('phone', max_length=50, required=True, blank=False)
    channel: int = DRFIntField('channel', required=True)
    

class CustomerLoginSchema(DRFStyleBaseModel):
    channel: int = DRFIntField('channel', required=True)
    provider: int = DRFIntField('provider', required=True)
    provider_id: Optional[str] = DRFCharField('provider_id', max_length=255, required=False, blank=True)
    customer_id: Optional[int] = DRFIntField('customer_id', required=False)
    nickname: Optional[str] = DRFCharField('nickname', max_length=255, required=False, blank=True)
    first_name: Optional[str] = DRFCharField('first_name', max_length=255, required=False, blank=True)
    last_name: Optional[str] = DRFCharField('last_name', max_length=255, required=False, blank=True)
    avatar_url: Optional[str] = DRFCharField('avatar_url', max_length=255, required=False, blank=True)
    phone: Optional[str] = DRFCharField('phone', max_length=50, required=False, blank=True)
    email: Optional[str] = DRFCharField('email', max_length=100, required=False, blank=True)
    province_code: Optional[str] = DRFCharField('province_code', max_length=20, required=False, blank=True)
    commune_code: Optional[str] = DRFCharField('commune_code', max_length=20, required=False, blank=True)
    address: Optional[str] = DRFCharField('address', max_length=255, required=False, blank=True)
    birthday: Optional[datetime] = DRFDateTimeField('created_from', required=False)
    
    
class SocialCustomerDeleteSchema(DRFStyleBaseModel):
    channel: int = DRFIntField('channel', required=True)
    provider: int = DRFIntField('provider', required=True)
    provider_id: str = DRFCharField('provider_id', max_length=255, required=True, blank=False)
    customer_id: int = DRFIntField('customer_id', required=True)


class ListSchema(DRFStyleBaseModel):
    channel: int = DRFIntField('channel', required=True)
    customer_id: int = DRFIntField('customer_id', required=True)
    page: int = DRFIntField('page', required=True)
    page_size: int = DRFIntField('page_size', required=False, default=10)
    code: Optional[str] = DRFCharField('title', max_length=255, required=False, blank=True)
    status: Optional[int] = DRFIntField('status', required=False)
    created_from: Optional[datetime] = DRFDateTimeField('created_from', required=True)
    created_to: Optional[datetime] = DRFDateTimeField('created_to', required=True)
    
    
class RewardSchema(DRFStyleBaseModel):
    page: int = DRFIntField('page', required=True)
    page_size: int = DRFIntField('page_size', required=False, default=10)
