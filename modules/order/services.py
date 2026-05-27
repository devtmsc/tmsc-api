import math
from datetime import datetime, timezone
import httpx
from app.config import settings
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session, selectinload
from app.modules.common.session import get_customer_master_db, get_customer_replica_db, get_logs_master_db
from app.fastcore.common.constant import MSG
from app.modules.common.constant import CUSTOMER_CHANNEL, REWARD_REDEMPTION_STATUS_MAPPING, REWARD_TRANSACTION_TYPE_MAPPING, REWARD_TRANSACTION_REFERENCE_TYPE_MAPPING, ORDER_FINAL_STATUSES, ORDER_SUCCESS_STATUSES, ORDER_RETURNED_STATUSES, ORDER_IGNORED_STATUSES, ORDER_CANCELLED_STATUSES
from app.fastcore.common.utility import log_event, get_n_months_ago, format_code, to_end_of_day, get_n_days_ago, is_datetime, has_special_char
from app.fastcore.user.auth_with_api_key import verify_api_key
from app.modules.common.utility import can_redeem_reward, decrease_points, normalize_phone_lib, increase_points, calculate_reward_points
from .models import OrdersModel, OrderLogModel, OrderStatusLogModel
from app.modules.customer.models import CustomersModel, RewardRedemptionsModel, RewardTransactionsModel, LoyaltyConfigsModel
from app.modules.common.caches import CategoryCommuneCache, CategoryOrderStatusCache, CategoryOrderStatusMappingCache, CategoryOrderPartnerCache
from .serializers import OrderSerializer
from . import schemas

router = APIRouter()


@router.get("/status", name="list")
def status_list(status_cache: CategoryOrderStatusCache = Depends(CategoryOrderStatusCache)):
    try:
        db_data = status_cache().get()
        return {'code': MSG['200']['code'], 'message': MSG['200']['message'], 'data': list(db_data.values())}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail={'code': MSG['500']['code'], 'message': MSG['500']['message'], 'system_message': str(e)})
        

@router.post("/create", name="create")
def create(info: schemas.OrderCreateSchema, db: Session = Depends(get_customer_master_db), db_logs: Session = Depends(get_logs_master_db), api_key: str = Depends(verify_api_key),):
    try:
        if info.channel not in CUSTOMER_CHANNEL:
            raise HTTPException(status_code=422, detail={
                                    'code': MSG['422']['code'], 'message': 'Channel không hợp lệ'})
        
        if str(info.tracking_code).isdigit():
            tracking_code = format_code(int(info.tracking_code), str(CUSTOMER_CHANNEL[info.channel].get('code')).upper(), 1)
            if not tracking_code:
                raise HTTPException(status_code=400, detail={
                                        'code': MSG['404']['code'], 'message': 'Lỗi sinh mã đơn hàng'})
        else:
            tracking_code = info.tracking_code
            
        #check tracking_code đã tồn tại hay chưa
        order = db.query(OrdersModel).filter(OrdersModel.tracking_code == tracking_code, OrdersModel.channel == info.channel).first()
        if order:
            # Đã tồn tại
            if info.receiver_name:
                if has_special_char(info.receiver_name):
                    if not order.receiver_name:
                        order.receiver_name = info.receiver_name
                elif info.receiver_name != order.receiver_name:
                    order.receiver_name = info.receiver_name
                    
            if info.receiver_phone:
                if has_special_char(info.receiver_phone):
                    if not order.receiver_phone:
                        order.receiver_phone = info.receiver_phone
                elif info.receiver_phone != order.receiver_phone:
                    order.receiver_phone = info.receiver_phone
                    
            if info.receiver_email:
                if has_special_char(info.receiver_email):
                    if not order.receiver_email:
                        order.receiver_email = info.receiver_email
                elif info.receiver_email != order.receiver_email:
                    order.receiver_email = info.receiver_email
            
            if info.receiver_province_code and (info.receiver_province_code != order.receiver_province_code):
                order.receiver_province_code = info.receiver_province_code
                
            if info.receiver_commune_code and (info.receiver_commune_code != order.receiver_commune_code):
                order.receiver_commune_code = info.receiver_commune_code
                
            if info.receiver_address:
                if has_special_char(info.receiver_address):
                    if not order.receiver_address:
                        order.receiver_address = info.receiver_address
                elif info.receiver_address != order.receiver_address:
                    order.receiver_address = info.receiver_address
                
            if info.description and (info.description != order.description):
                order.description = info.description
                
            if info.money_collect != order.money_collect:
                order.money_collect = info.money_collect
                
            if info.total_freight and (info.total_freight != order.total_freight):
                order.total_freight = info.total_freight
                
            if info.carrier_code and (info.carrier_code != order.carrier_code):
                order.carrier_code = info.carrier_code
                
            if info.carrier_tracking_code and (info.carrier_tracking_code != order.carrier_tracking_code):
                order.carrier_tracking_code = info.carrier_tracking_code
        else:
            # Chưa tồn tại
            customer_id = 0
            if info.customer_id:
                customer_id = info.customer_id
                # có truyền id khách hàng => check tồn tại
                customer = db.query(CustomersModel).filter(
                    CustomersModel.id == info.customer_id, CustomersModel.channel == info.channel).first()
                if not customer:
                    raise HTTPException(status_code=404, detail={
                                        'code': MSG['404']['code'], 'message': 'Mã tài khoản khách hàng không tồn tại'})
                
                if info.reward_id == 1:
                    # sử dụng điểm tích luỹ
                    if info.reward_value and info.reward_value > 0:
                        if not can_redeem_reward(customer.reward_points, info.reward_value, db, RewardRedemptionsModel):
                            raise HTTPException(status_code=400, detail={
                                'code': MSG['400']['code'], 'message': 'Bạn không đủ điểm thưởng để đổi phần thưởng này, hãy kiểm tra lại điểm thưởng hiện có'})

                        description = 'Sử dụng điểm tích luỹ để mua sản phẩm'
                        # tạo redeem
                        
                        
                        new_points = decrease_points(db, CustomersModel, info.customer_id, info.reward_value)
                        new_redeem = RewardRedemptionsModel(customer_id=info.customer_id, total_points_used=info.reward_value,
                                                status=REWARD_REDEMPTION_STATUS_MAPPING['SUCCESS'], description=description, reward_id=info.reward_id, 
                                                channel=info.channel, code=tracking_code, balance_after=new_points)
                        new_transaction = RewardTransactionsModel(customer_id=info.customer_id, transaction_type=REWARD_TRANSACTION_TYPE_MAPPING['REDEEM'],
                                                                point=info.reward_value, balance_after=new_points, reference_type=REWARD_TRANSACTION_REFERENCE_TYPE_MAPPING['REDEEM'], 
                                                                reference_id=None, description=description, transaction_code=tracking_code,
                                                                channel=info.channel)
                        db.add(new_redeem)
                        db.add(new_transaction)
            else:
                if info.reward_id:
                    raise HTTPException(status_code=400, detail={
                                'code': MSG['400']['code'], 'message': 'Bạn chưa đăng nhập, không thể sử dụng điểm thưởng'})
                    
                if has_special_char(info.receiver_phone):
                    raise HTTPException(status_code=400, detail={
                                'code': MSG['400']['code'], 'message': 'Bạn chưa đăng nhập, số điện thoại không đúng định dạng'})
                    
                phone = normalize_phone_lib(info.receiver_phone)
                
                # check customer, nếu chưa có thì tạo tài khoản
                customer = db.query(CustomersModel).filter(CustomersModel.phone == phone, CustomersModel.channel == info.channel).first()
                if customer:
                    # đã có tài khoản
                    customer_id = customer.id
                else:
                    # chưa có tài khoản
                    new_customer = CustomersModel(
                        fullname=info.receiver_name, phone=phone, channel=info.channel, status=True, reward_points=0)
                    db.add(new_customer)
                    db.commit()
                    db.refresh(new_customer)
                    customer_id = new_customer.id
                    
            items = None
            if info.items:
                items = [item.model_dump() for item in info.items]
                
            new_order = OrdersModel(tracking_code=tracking_code, customer_id=customer_id, receiver_name=info.receiver_name, receiver_phone=info.receiver_phone,
                                    receiver_email=info.receiver_email, receiver_province_code=info.receiver_province_code, channel=info.channel, 
                                    receiver_commune_code=info.receiver_commune_code, receiver_address=info.receiver_address, description=info.description,
                                    status=1, money_collect=info.money_collect, total_amount=info.money_collect, total_freight=info.total_freight, items=items,
                                    delivery_method=info.delivery_method, pickup_scheduled_at=info.pickup_scheduled_at, reward_value=info.reward_value, reward_id=info.reward_id,
                                    year_month=get_n_months_ago(0), datecreated=get_n_days_ago(0), last_accessed_at=datetime.now(timezone.utc))
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
    conditions.append(OrdersModel.channel == filter.channel)

    if filter.created_from:
        conditions.append(OrdersModel.created_at >= filter.created_from)

    if filter.created_to:
        conditions.append(OrdersModel.created_at <= to_end_of_day(filter.created_to))

    if filter.tracking_code:
        # ticketcode
        conditions.append(OrdersModel.tracking_code == filter.tracking_code)

    return conditions


@router.get("/list", name="list")
def get_list(request: Request, filter: schemas.OrderListSchema = Depends(), db: Session = Depends(get_customer_replica_db), api_key: str = Depends(verify_api_key), commune_cache: CategoryCommuneCache = Depends(CategoryCommuneCache), order_status_cache: CategoryOrderStatusCache = Depends(CategoryOrderStatusCache), order_partner_cache: CategoryOrderPartnerCache = Depends(CategoryOrderPartnerCache)):
    try:
        conditions = order_filter(request, filter)
        
        if filter.status:
            conditions.append(OrdersModel.status == filter.status)

        query = db.query(OrdersModel).filter(*conditions)
        
        total = query.count()  # tổng record
        data = query.order_by(OrdersModel.created_at.desc()).offset((filter.page - 1) * filter.page_size).limit(filter.page_size).all()

        return {'code': MSG['200']['code'], 'message': MSG['200']['message'],
                "data": OrderSerializer.serialize_list(data, context={'commune_cache': commune_cache, 'order_status_cache': order_status_cache, 'order_partner_cache': order_partner_cache}),
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


async def ghtk_sync(tracking_code: str):
    url = f"{settings.GHTK_URL}services/shipment/v2/{tracking_code}"

    headers = {
        "Token": settings.GHTK_TOKEN,
        "X-Client-Source": settings.GHTK_X_CLIENT_SOURCE,
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=headers)

        # check HTTP status
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"GHTK API error: {response.text}"
            )

        data = response.json()

        # check success (handle cả string và boolean)
        if data.get("success") in [True, "true"]:
            return data.get("order")

        return None

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Request to GHTK failed: {str(e)}"
        )


@router.get("/sync-status")
async def sync_status(tracking_code: Optional[str] = None, db: Session = Depends(get_customer_replica_db), order_status_mapping_cache: CategoryOrderStatusMappingCache = Depends(CategoryOrderStatusMappingCache)):
    try:
        list_carrier = ['ghtk']
        
        order_status_mapping = order_status_mapping_cache().get()
        if not order_status_mapping:
            raise HTTPException(status_code=400, detail={
                                    'code': MSG['400']['code'], 'message': 'Lỗi danh sách trạng thái'})
        conditions = [OrdersModel.carrier_code.in_(list_carrier), OrdersModel.carrier_tracking_code.is_not(None), OrdersModel.datecreated >= get_n_days_ago(90)]
        conditions.append(or_(
                and_(
                    OrdersModel.status.notin_(ORDER_FINAL_STATUSES),
                ),
                and_(
                    OrdersModel.status.in_(ORDER_FINAL_STATUSES),
                    or_(
                        and_(OrdersModel.completed_at >= get_n_days_ago(3)),
                        and_(OrdersModel.canceled_at >= get_n_days_ago(3)),
                    )
                )
            ))
        if tracking_code:
            conditions.append(OrdersModel.tracking_code==tracking_code)
        
        order = db.query(OrdersModel).filter(*conditions).order_by(OrdersModel.last_accessed_at.asc()).first()
        if not order:
            return {'code': MSG['200']['code'], 'message': 'Đã xử lý hết'}

        if order.carrier_code == 'ghtk':
            data = await ghtk_sync(order.carrier_tracking_code)
            
            if data:
                status_mapping = order_status_mapping[order.carrier_code]
                partner_status = str(data.get('status'))
                if partner_status in status_mapping:
                    status = status_mapping[partner_status].get('status_code')
                else:
                    raise HTTPException(status_code=400, detail={
                                        'code': MSG['400']['code'], 'message': f'Trạng thái không tồn tại {order.carrier_code} - {data.get('status')}'})
                
                if (status not in ORDER_IGNORED_STATUSES) and (status != order.status):
                    order.status = status
                    if status in ORDER_CANCELLED_STATUSES:
                        order.canceled_at = datetime.now(timezone.utc)
                        order.picked_at = None
                        order.completed_at = None
                        order.returned_at = None
                    else:
                        order.canceled_at = None
                        if data.get('pick_date'):
                            pick_date = is_datetime(data.get('pick_date'), '%Y-%m-%d')
                            if pick_date:
                                order.picked_at = pick_date
                        if data.get('deliver_date'):
                            deliver_date = is_datetime(data.get('deliver_date'), '%Y-%m-%d')
                            if deliver_date:
                                if order.status in ORDER_RETURNED_STATUSES:
                                    order.completed_at = None
                                    order.returned_at = deliver_date
                                else:
                                    order.completed_at = deliver_date
                                    order.returned_at = None
                
                if order.total_freight != data.get('ship_money'):
                    order.total_freight = data.get('ship_money')
                
                if order.money_collect != data.get('pick_money'):
                    order.money_collect = data.get('pick_money')
                    
                if order.total_amount != data.get('value'):
                    order.total_amount = data.get('value')
                
                if order.total_freight != data.get('weight'):
                    order.total_freight = data.get('weight')
                        
        order.last_accessed_at = datetime.now(timezone.utc)
        db.commit()
        
        return {'code': MSG['200']['code'], 'message': f'Thành công - {order.tracking_code}'}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail={'code': MSG['500']['status_code'], 'message': MSG['500']['message'], 'system_message': str(e)})


@router.get("/process-order-reward")
async def process_order_reward(tracking_code: Optional[str] = None, db: Session = Depends(get_customer_replica_db), order_status_mapping_cache: CategoryOrderStatusMappingCache = Depends(CategoryOrderStatusMappingCache)):
    try:
        conditions = [OrdersModel.datecreated >= get_n_days_ago(90), OrdersModel.status.in_(ORDER_SUCCESS_STATUSES), OrdersModel.is_rewarded == 0, OrdersModel.completed_at < get_n_days_ago(2), OrdersModel.customer_id > 0]
        if tracking_code:
            conditions.append(OrdersModel.tracking_code==tracking_code)
        
        order = db.query(OrdersModel).filter(*conditions).order_by(OrdersModel.created_at.asc()).first()
        if not order:
            return {'code': MSG['200']['code'], 'message': 'Đã xử lý hết'}

        if order.total_amount and order.total_amount > 0:
            description = f'Thưởng điểm tích luỹ khi mua đơn hàng {order.tracking_code}'
            
            loyalty_configs = db.query(LoyaltyConfigsModel).filter(LoyaltyConfigsModel.status == True).first()
            if not loyalty_configs:
                raise HTTPException(status_code=400, detail={
                                        'code': MSG['400']['code'], 'message': 'Cấu hình đổi điểm không tồn tại'})
            
            point = calculate_reward_points(order.total_amount, loyalty_configs.money_unit_step, loyalty_configs.points_reward_step)
            
            # tạo redeem
            new_points = increase_points(db, CustomersModel, order.customer_id, point)
            new_transaction = RewardTransactionsModel(customer_id=order.customer_id, transaction_type=REWARD_TRANSACTION_TYPE_MAPPING['EARN'],
                                                    point=point, balance_after=new_points, reference_type=REWARD_TRANSACTION_REFERENCE_TYPE_MAPPING['EARN'], 
                                                    reference_id=None, description=description, transaction_code=order.tracking_code,
                                                    channel=order.channel)
            db.add(new_transaction)
        
        order.is_rewarded = 1
        
        db.commit()
        
        return {'code': MSG['200']['code'], 'message': f'Thành công - {order.tracking_code}'}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail={'code': MSG['500']['status_code'], 'message': MSG['500']['message'], 'system_message': str(e)})
        

@router.post("/vtp-webhook")
def vtp_webhook(input: schemas.InputVTPSchema, db_logs: Session = Depends(get_logs_master_db)):
    try:
        output = {"code": MSG['200']['status_code'], 'message': MSG['200']['message']}
        new_data = OrderStatusLogModel(carrier_code='vtp', status=0, year_month=get_n_months_ago(0), 
                                       input=input.model_dump(mode="json"), output=output)
        db_logs.add(new_data)
        db_logs.commit()
        return output
    except HTTPException as e:
        if e.status_code not in [404, 422]:
            output = {"code": MSG['400']['code'], 'message': str(e)}
            new_data = OrderStatusLogModel(carrier_code='vtp', status=2, year_month=get_n_months_ago(0), 
                                       input=input.model_dump(mode="json"), output=output)
            db_logs.add(new_data)
            db_logs.commit()
        raise e
    except Exception as e:
        output = {"code": MSG['400']['code'], 'message': str(e)}
        new_data = OrderStatusLogModel(carrier_code='vtp', status=2, year_month=get_n_months_ago(0), 
                                    input=input.model_dump(mode="json"), output=output)
        db_logs.add(new_data)
        db_logs.commit()
        raise HTTPException(status_code=500,
                            detail={'code': MSG['500']['status_code'], 'message': MSG['500']['message']})
        

@router.post("/ghtk-webhook")
def ghtk_webhook(input: schemas.InputGHTKSchema, db_logs: Session = Depends(get_logs_master_db)):
    try:
        output = {"code": MSG['200']['status_code'], 'message': MSG['200']['message']}
        new_data = OrderStatusLogModel(carrier_code='ghtk', status=0, year_month=get_n_months_ago(0), 
                                       input=input.model_dump(mode="json"), output=output)
        db_logs.add(new_data)
        db_logs.commit()
        return output
    except HTTPException as e:
        if e.status_code not in [404, 422]:
            output = {"code": MSG['400']['code'], 'message': str(e)}
            new_data = OrderStatusLogModel(carrier_code='ghtk', status=2, year_month=get_n_months_ago(0), 
                                       input=input.model_dump(mode="json"), output=output)
            db_logs.add(new_data)
            db_logs.commit()
        raise e
    except Exception as e:
        output = {"code": MSG['400']['code'], 'message': str(e)}
        new_data = OrderStatusLogModel(carrier_code='ghtk', status=2, year_month=get_n_months_ago(0), 
                                    input=input.model_dump(mode="json"), output=output)
        db_logs.add(new_data)
        db_logs.commit()
        raise HTTPException(status_code=500,
                            detail={'code': MSG['500']['status_code'], 'message': MSG['500']['message']})
