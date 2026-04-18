from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from app.modules.common.session import get_customer_master_db, get_customer_replica_db
from app.fastcore.common.constant import MSG
from app.modules.common.utility import normalize_phone_lib
from app.fastcore.user.auth_with_api_key import verify_api_key
from .models import CustomersModel, SocialCustomersModel
from .serializers import CustomerSerializer
from app.modules.common.caches import CategoryCommuneCache

from . import schemas

router = APIRouter()


@router.post("/create", name="create")
def create(info: schemas.CustomerCreateSchema, db: Session = Depends(get_customer_master_db), api_key: str = Depends(verify_api_key),):
    try:
        phone = normalize_phone_lib(info.phone)
        db_data = db.query(CustomersModel).filter(
            CustomersModel.phone == phone, CustomersModel.channel == info.channel).first()
        if db_data:
            return {'code': 'existed', 'message': 'Số điện thoại đã tồn tại', 'data': db_data.id}

        new_customer = CustomersModel(
            fullname=info.fullname, phone=phone, channel=info.channel, status=True)
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)

        return {'code': MSG['200']['status_code'], 'message': MSG['200']['status_code'], 'data': new_customer.id}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail={
                            'code': MSG['500']['status_code'], 'message': MSG['500']['message'], 'system_message': str(e)})


@router.post("/login", name="view")
def create(info: schemas.CustomerLoginSchema, db: Session = Depends(get_customer_master_db), api_key: str = Depends(verify_api_key), commune_cache: CategoryCommuneCache = Depends(CategoryCommuneCache)):
    try:
        if (info.provider == 0) and not info.customer_id:
            raise HTTPException(status_code=422, detail={
                                'code': MSG['422']['status_code'], 'message': 'Dữ liệu không hợp lệ, bạn chưa truyền mã khách hàng'})
        if (info.provider > 0) and not info.provider_id:
            raise HTTPException(status_code=422, detail={
                                'code': MSG['422']['status_code'], 'message': 'Dữ liệu không hợp lệ, bạn chưa truyền mã khách hàng'})

        is_existed = False
        phone = None
        if info.phone:
            phone = normalize_phone_lib(info.phone)

        if info.provider == 0:
            # khách đăng ký
            customer = db.query(CustomersModel).filter(
                CustomersModel.id == info.customer_id, CustomersModel.channel == info.channel).first()
            if not customer:
                raise HTTPException(status_code=404, detail={
                                    'code': MSG['404']['status_code'], 'message': 'Mã tài khoản khách hàng không tồn tại'})

            is_existed = True
        else:
            # khách đăng nhập qua FB, Gmail
            social_customer = db.query(SocialCustomersModel).filter(SocialCustomersModel.provider == info.provider,
                                                                    SocialCustomersModel.provider_id == info.provider_id, SocialCustomersModel.channel == info.channel).first()
            if social_customer:
                # Đã có tài khoản
                if info.customer_id:
                    # có truyền info.customer_id là liên kết tài khoản với customer_id này.
                    if info.customer_id != social_customer.customer_id:
                        # đã liên kết với 1 tài khoản khác
                        raise HTTPException(status_code=400, detail={
                                            'code': MSG['400']['status_code'], 'message': 'Tài khoản Gmail/Facebook của bạn đã được liên kết với 1 tài khoản khác của hệ thống!'})

                customer = db.query(CustomersModel).filter(
                    CustomersModel.id == social_customer.customer_id, CustomersModel.channel == info.channel).first()
                if not customer:
                    raise HTTPException(status_code=404, detail={
                                        'code': MSG['404']['status_code'], 'message': 'Mã tài khoản khách hàng không tồn tại'})

                is_existed = True
                if info.nickname:
                    social_customer.nickname = info.nickname

                if info.first_name:
                    social_customer.first_name = info.first_name

                if info.last_name:
                    social_customer.last_name = info.last_name

                if info.avatar_url:
                    social_customer.avatar_url = info.avatar_url

                if phone:
                    social_customer.phone = phone

                if info.email:
                    social_customer.email = info.email

            else:
                if info.customer_id:
                    # có truyền info.customer_id là liên kết tài khoản với customer_id này.
                    customer = db.query(CustomersModel).filter(
                        CustomersModel.id == info.customer_id, CustomersModel.channel == info.channel).first()
                    if not customer:
                        raise HTTPException(status_code=404, detail={
                                            'code': MSG['404']['status_code'], 'message': 'Mã tài khoản khách hàng không tồn tại'})
                    else:
                        social_customer = SocialCustomersModel(channel=info.channel, provider=info.provider, provider_id=info.provider_id, customer_id=customer.id, nickname=info.nickname, first_name=info.first_name,
                                                               last_name=info.last_name, avatar_url=info.avatar_url, phone=info.phone, email=info.email)
                        db.add(social_customer)
                else:
                    if phone:
                        customer = db.query(CustomersModel).filter(
                            CustomersModel.phone == phone, CustomersModel.channel == info.channel).first()
                        if customer:
                            # sdt đã có tài khoản
                            social_customer = SocialCustomersModel(channel=info.channel, provider=info.provider, provider_id=info.provider_id, customer_id=customer.id, nickname=info.nickname, first_name=info.first_name,
                                                                   last_name=info.last_name, avatar_url=info.avatar_url, phone=info.phone, email=info.email)
                            db.add(social_customer)
                        else:
                            # sdt chưa có tài khoản, tạo mới
                            social_customer = SocialCustomersModel(channel=info.channel, provider=info.provider, provider_id=info.provider_id, nickname=info.nickname, first_name=info.first_name,
                                                                   last_name=info.last_name, avatar_url=info.avatar_url, phone=info.phone, email=info.email)

                            # Chưa có tài khoản
                            customer = CustomersModel(
                                fullname=f"{info.first_name} {info.last_name}", phone=phone, channel=1, status=True, social=[social_customer])
                            db.add(customer)
                    else:
                        raise HTTPException(status_code=422, detail={
                                            'code': MSG['422']['status_code'], 'message': 'Dữ liệu không hợp lệ, bạn chưa truyền số điện thoại'})

        if is_existed:
            # đã tồn tại thì update lại thông tin
            if info.first_name or info.last_name:
                customer.fullname = f"{info.first_name} {info.last_name}"

            if info.avatar_url:
                customer.avatar_url = info.avatar_url

            if info.email:
                customer.email = info.email

            if info.province_code:
                customer.province_code = info.province_code

            if info.commune_code:
                customer.commune_code = info.commune_code

            if info.address:
                customer.address = info.address

            if info.birthday:
                customer.birthday = info.birthday

        db.commit()
        db.refresh(customer)

        customer_data = db.query(CustomersModel).filter(
            CustomersModel.id == customer.id).options(selectinload(CustomersModel.social)).all()

        data = CustomerSerializer.serialize_list(customer_data, context={'commune_cache': commune_cache},
                                                 fields=['id', 'fullname', 'phone', 'email', 'address', 'province_code', 'commune_code', 'status',
                                                         'birthday', 'avatar_url', 'channel', 'channel_name', 'commune_name', 'province_name',
                                                         'created_time', 'created_time_ago', 'birthday', 'reward_points', 'social'])

        return {'code': MSG['200']['code'], 'message': MSG['200']['message'], 'data': data[0]}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail={
                            'code': MSG['500']['code'], 'message': MSG['500']['message'], 'system_message': str(e)})


@router.delete("/social", name="delete")
def delete_social(info: schemas.SocialCustomerDeleteSchema, db: Session = Depends(get_customer_master_db), api_key: str = Depends(verify_api_key)):
    try:
        social_customer = db.query(SocialCustomersModel).filter(SocialCustomersModel.provider == info.provider, SocialCustomersModel.provider_id == info.provider_id, 
                                                                SocialCustomersModel.channel == info.channel, SocialCustomersModel.customer_id == info.customer_id).first()
        if not social_customer:
            raise HTTPException(status_code=404, detail={
                                            'code': MSG['404']['status_code'], 'message': 'Tài khoản liên kết không tồn tại'})
        db.delete(social_customer)
        db.commit()
        return {'code': MSG['200']['code'], 'message': MSG['200']['message']}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail={'code': MSG['500']['status_code'], 'message': MSG['500']['message'], 'system_message': str(e)})