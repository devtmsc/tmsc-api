from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.modules.common.session import get_customer_master_db, get_customer_replica_db
from app.fastcore.common.constant import MSG
from app.modules.common.utility import normalize_phone_lib
from app.fastcore.user.auth_with_api_key import verify_api_key
from .models import CustomersModel

from . import schemas

router = APIRouter()


@router.post("/create", name="create")
def create(info: schemas.CustomerCreateSchema, db: Session = Depends(get_customer_master_db), api_key: str = Depends(verify_api_key)):
    try:
        phone = normalize_phone_lib(info.phone)

        db_data = db.query(CustomersModel).filter(
            CustomersModel.phone == phone).first()
        if db_data:
            return {'code': 'existed', 'message': 'Số điện thoại đã tồn tại', 'data': db_data.id}

        new_customer = CustomersModel(fullname=info.fullname, phone=phone, status=True)
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)

        return {'code': MSG['200']['status_code'], 'message': MSG['200']['status_code'], 'data': new_customer.id}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail={
                            'code': MSG['500']['status_code'], 'message': MSG['500']['message'], 'system_message': str(e)})
