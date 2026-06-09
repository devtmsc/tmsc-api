import re
import requests
from sqlalchemy import func, update
from fastapi import HTTPException
from app.modules.common.constant import CONFIG, DELIVERY_METHOD


def normalize_phone_lib(phone: str) -> str:
    import phonenumbers
    
    parsed = phonenumbers.parse(phone, "VN")
    if not phonenumbers.is_valid_number(parsed):
        raise ValueError("Invalid phone")

    # format về quốc tế
    e164 = phonenumbers.format_number(
        parsed, phonenumbers.PhoneNumberFormat.E164
    )

    # đổi về 0xxxxxxxx
    return "0" + e164[3:]


# kiểm tra khách hàng yêu cầu đổi thưởng
def can_redeem_reward(current_points: int, points: int, db: any, model: any):
    total_pending_points = db.query(func.coalesce(func.sum(model.total_points_used), 0)).filter(model.status == 0).scalar()
    
    if (current_points - total_pending_points) >= points:
        # đủ điểm 
        return True
    else:
        # không đủ điểm
        return False

# increase reward point
def increase_points(db, model, customer_id: int, amount: int):
    stmt = (
        update(model)
        .where(model.id == customer_id)
        .values(reward_points=model.reward_points + amount)
        .returning(model.reward_points)
    )
    result = db.execute(stmt)
    new_points = result.scalar_one_or_none()
    
    if new_points is None:
        raise HTTPException("Lỗi đổi thưởng")
    
    return new_points


# decrease reward point
def decrease_points(db, model, customer_id: int, amount: int):
    stmt = (
        update(model)
        .where(
            model.id == customer_id,
            model.reward_points >= amount
        )
        .values(reward_points=model.reward_points - amount)
        .returning(model.reward_points)
    )

    result = db.execute(stmt)
    new_points = result.scalar_one_or_none()
    
    if new_points is None:
        raise HTTPException("Bạn không đủ điểm để đổi thưởng")
    
    return new_points


# increase reward point
def increase_stock(db, model, reward_id: int, amount: int):
    stmt = (
        update(model)
        .where(model.id == reward_id)
        .values(stock=model.stock + amount)
        .returning(model.stock)
    )
    result = db.execute(stmt)
    new_points = result.scalar_one_or_none()
    
    if new_points is None:
        raise HTTPException("Lỗi đổi thưởng")
    
    return new_points


# decrease reward point
def decrease_stock(db, model, reward_id: int, amount: int):
    stmt = (
        update(model)
        .where(
            model.id == reward_id,
            model.stock >= amount
        )
        .values(stock=model.stock - amount)
        .returning(model.stock)
    )

    result = db.execute(stmt)
    new_points = result.scalar_one_or_none()
    
    if new_points is None:
        raise HTTPException("Không đủ phần thưởng trong kho")
    
    return new_points


def calculate_reward_points(total_amount, money_unit_step, points_reward_step):
    if money_unit_step <= 0:
            return 0
    return int((total_amount / money_unit_step) * points_reward_step)


def format_money(v):
    return f"{v:,.0f}".replace(",", ".")


def is_valid_tmsc_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@tmsc-vn\.com$'
    return re.match(pattern, email) is not None


def send_order_telegram(info, tracking_code, channel_name):
    delivery_method_name = 'Giao hàng tại địa chỉ'
    if info.delivery_method in DELIVERY_METHOD:
        delivery_method_name = DELIVERY_METHOD[info.delivery_method].get('name')
    
    msg = (
        f"<b>🛒 Đơn hàng mới</b>\n"
        f"Mã đơn: <code>{tracking_code}</code>\n"
        f"Tổng tiền: <b>{format_money(info.money_collect)} đ</b>\n\n"

        f"<b>👤 Thông tin khách hàng</b>\n"
        f"Tên: {info.receiver_name}\n"
        f"SĐT: <code>{info.receiver_phone}</code>\n"
        f"Email: {info.receiver_email}\n"
        f"Địa chỉ: {info.receiver_address}\n\n"

        f"<b>🚚 Vận chuyển</b>\n"
        f"Kênh: {channel_name}\n"
        f"Hình thức: {delivery_method_name}\n"
        f"Lịch lấy: {info.pickup_scheduled_at if info.pickup_scheduled_at is not None else ''}\n\n"

        f"<b>📦 Sản phẩm</b>\n"
    )

    # loop items
    if info.items:
        for i, item in enumerate(info.items, 1):
            msg += (
                f"{i}. {item.name}\n"
                f"   SL: {item.quantity} | "
                f"Giá: {format_money(item.total)} đ\n"
            )
    
    url = f"https://api.telegram.org/bot{CONFIG['BOT_TOKEN']}/sendMessage"
    payload = {
        "chat_id": CONFIG['ORDER_CHAT_ID'],
        "text": msg,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload, timeout=10)
