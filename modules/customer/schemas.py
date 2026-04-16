from app.fastcore.common.models import DRFStyleBaseModel, DRFCharField


class CustomerCreateSchema(DRFStyleBaseModel):
    fullname: str = DRFCharField('fullname', max_length=255, required=True, blank=False)
    phone: str = DRFCharField('phone', max_length=50, required=True, blank=False)
    