import math
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, selectinload
from app.modules.common.session import get_customer_master_db, get_customer_replica_db, get_logs_master_db
from app.fastcore.common.constant import MSG
from app.modules.common.constant import ORDER_STATUS_MAPPING, CUSTOMER_CHANNEL
from app.fastcore.common.utility import log_event, get_n_months_ago, format_code, to_end_of_day
from app.fastcore.user.auth_with_api_key import verify_api_key
from .models import OrdersModel, OrderLogModel
from app.modules.customer.models import CustomersModel
from app.modules.common.caches import CategoryCommuneCache
from .serializers import OrderSerializer
from . import schemas

router = APIRouter()


@router.post("/create", name="create")
def create(info: schemas.OrderCreateSchema, db: Session = Depends(get_customer_master_db), db_logs: Session = Depends(get_logs_master_db), api_key: str = Depends(verify_api_key),):
    try:
        if info.channel not in CUSTOMER_CHANNEL:
            raise HTTPException(status_code=422, detail={
                                    'code': MSG['422']['code'], 'message': 'Channel không hợp lệ'})
            
        if info.customer_id:
            # có truyền id khách hàng => check tồn tại
            customer = db.query(CustomersModel).filter(
                CustomersModel.id == info.customer_id, CustomersModel.channel == info.channel).first()
            if not customer:
                raise HTTPException(status_code=404, detail={
                                    'code': MSG['404']['code'], 'message': 'Mã tài khoản khách hàng không tồn tại'})

        tracking_code = format_code(info.tracking_code, str(CUSTOMER_CHANNEL[info.channel].get('code')).upper(), 7)
        if not tracking_code:
            raise HTTPException(status_code=400, detail={
                                    'code': MSG['404']['code'], 'message': 'Lỗi sinh mã đơn hàng'})
        
        items = None
        if info.items:
            items = [item.model_dump() for item in info.items]

        new_order = OrdersModel(tracking_code=tracking_code, customer_id=info.customer_id, receiver_name=info.receiver_name, receiver_phone=info.receiver_phone,
                                receiver_email=info.receiver_email, receiver_province_code=info.receiver_province_code, 
                                receiver_commune_code=info.receiver_commune_code, receiver_address=info.receiver_address, description=info.description,
                                status=ORDER_STATUS_MAPPING['CREATED'], money_collect=info.money_collect, total_freight=info.total_freight, items=items,
                                delivery_method=info.delivery_method, pickup_scheduled_at=info.pickup_scheduled_at,
                                year_month=get_n_months_ago(0))
        db.add(new_order)
        db.commit()
        
        
        resp = {'code': MSG['200']['code'], 'message': MSG['200']['message'], 'data': tracking_code}
        log_event(db_logs, OrderLogModel, {'customer_id': info.customer_id, 'tracking_code': tracking_code, 'channel': info.channel, 'input': info.model_dump(mode="json"), 'output': resp})
        return resp
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail={
                            'code': MSG['500']['code'], 'message': MSG['500']['message'], 'system_message': str(e)})


def order_filter(request:Request, filter: schemas.OrderListSchema):
    conditions = []
    conditions.append(OrdersModel.customer_id == filter.customer_id)

    if filter.created_from:
        conditions.append(OrdersModel.created_at >= filter.created_from)

    if filter.created_to:
        conditions.append(OrdersModel.created_at <= to_end_of_day(filter.created_to))

    if filter.tracking_code:
        # ticketcode
        conditions.append(OrdersModel.tracking_code == filter.tracking_code)

    return conditions


@router.get("/list", name="list")
def get_list(request: Request, filter: schemas.OrderListSchema = Depends(), db: Session = Depends(get_customer_replica_db), api_key: str = Depends(verify_api_key), commune_cache: CategoryCommuneCache = Depends(CategoryCommuneCache)):
    try:
        conditions = order_filter(request, filter)
        
        if filter.status:
            conditions.append(OrdersModel.status == filter.status)

        query = db.query(OrdersModel).filter(*conditions)
        
        total = query.count()  # tổng record
        data = query.order_by(OrdersModel.created_at.desc()).offset((filter.page - 1) * filter.page_size).limit(filter.page_size).all()

        return {'code': MSG['200']['code'], 'message': MSG['200']['message'],
                "data": OrderSerializer.serialize_list(data, context={'commune_cache': commune_cache}),
                "pagination": {
                    "page": filter.page,
                    "limit": filter.page_size,
                    "total": total,
                    "total_pages": math.ceil(total/filter.page_size)
        }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail={
                            'code': MSG['500']['code'], 'message': MSG['500']['message'], 'system_message': str(e)})

