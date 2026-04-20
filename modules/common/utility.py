from sqlalchemy import func, update
from fastapi import HTTPException
from app.fastcore.common.constant import MSG


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
    
    if (current_points - total_pending_points) > points:
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
        .values(points=model.reward_points + amount)
    )
    db.execute(stmt)


# decrease reward point
def decrease_points(db, model, customer_id: int, amount: int):
    stmt = (
        update(model)
        .where(
            model.id == customer_id,
            model.points >= amount
        )
        .values(points=model.points - amount)
    )

    result = db.execute(stmt)

    if result.rowcount == 0:
        raise HTTPException(status_code=400, detail={
                'code': MSG['400']['code'], 'message': 'Bạn không đủ điểm để đổi phần thưởng này'})
    

# increase reward point
def increase_stock(db, model, reward_id: int, amount: int):
    stmt = (
        update(model)
        .where(model.id == reward_id)
        .values(stock=model.stock + amount)
    )
    db.execute(stmt)


# decrease reward point
def decrease_stock(db, model, reward_id: int, amount: int):
    stmt = (
        update(model)
        .where(
            model.id == reward_id,
            model.stock >= amount
        )
        .values(stock=model.stock - amount)
    )

    result = db.execute(stmt)

    if result.rowcount == 0:
        raise Exception("Not enough points")
    
