from app.fastcore.common.models import DRFStyleBaseModel, DRFCharField


class TokenRefreshRequest(DRFStyleBaseModel):
    refresh_token: str = DRFCharField(
        'refresh_token', required=True, blank=False)
