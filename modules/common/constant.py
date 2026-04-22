from app.config import settings

CONFIG = {}


CUSTOMER_CHANNEL = {
    1: {'id': 1, 'name': 'E&S Pharma', 'code': 'ES01'}
}

ORDER_STATUS = {
    1: {'id': 1, 'code': 'CREATED', 'name': 'Đã tạo'},
    2: {'id': 2, 'code': 'ACCEPTED', 'name': 'Đã duyệt'},
    3: {'id': 3, 'code': 'PICKED', 'name': 'Đã lấy hàng'},
    4: {'id': 4, 'code': 'DELIVERING', 'name': 'Đang phát hàng'},
    5: {'id': 5, 'code': 'DELIVERED', 'name': 'Đã phát thành công'},
    6: {'id': 6, 'code': 'RETURNING', 'name': 'Đang chuyển hoàn'},
    7: {'id': 7, 'code': 'RETURNED', 'name': 'Chuyển hoàn thành công'},
    8: {'id': 8, 'code': 'CANCELLED', 'name': 'Đã huỷ'},
    9: {'id': 9, 'code': 'PAID', 'name': 'Đã nhận tiền'},
}

ORDER_STATUS_MAPPING = {
    'CREATED': 1,
    'ACCEPTED': 2,
    'PICKED': 3,
    'DELIVERING': 4,
    'DELIVERED': 5,
    'RETURNING': 6,
    'RETURNED': 7,
    'CANCELLED': 8,
    'PAID': 9
}

DELIVERY_METHOD = {
    1: {'id': 1, 'name': 'Giao hàng tận nhà'},
    2: {'id': 2, 'name': 'Lấy hàng tại công ty'}
}

REWARD_REDEMPTION_STATUS = {
    0: {'id': 0, 'name': 'Mới tạo', 'code': 'CREATED'},
    1: {'id': 1, 'name': 'Chờ xử lý', 'code': 'PENDING'},
    2: {'id': 2, 'name': 'Đã xử lý', 'code': 'SUCCESS'},
    3: {'id': 3, 'name': 'Đã huỷ', 'code': 'CANCEL'}
}

REWARD_REDEMPTION_STATUS_MAPPING = {
    'CREATED': 0,
    'PENDING': 1,
    'SUCCESS': 2,
    'CANCEL': 3
}

REWARD_TRANSACTION_TYPE = {
    1: {'id': 1, 'name': 'Thưởng điểm', 'code': 'EARN'},
    2: {'id': 2, 'name': 'Sử dụng điểm', 'code': 'REDEEM'},
    3: {'id': 3, 'name': 'Hoàn điểm', 'code': 'REFUND'}
}

REWARD_TRANSACTION_TYPE_MAPPING = {
    'EARN': 1,
    'REDEEM': 2,
    'REFUND': 3
}

REWARD_TRANSACTION_REFERENCE_TYPE_MAPPING = {
    'EARN': 1,
    'REDEEM': 2,
    'REFUND': 3
}