from app.config import settings

CONFIG = {
    'BOT_TOKEN': "8858659686:AAEP9WJ-KzKpRgyEJFNAACYDuHXKNEByjfQ",
    'ORDER_CHAT_ID': "-1003665874080"
}

ORDER_FINAL_STATUSES = [8, 11, 12]
ORDER_SUCCESS_STATUSES = [8]
ORDER_RETURNED_STATUSES = [11]
ORDER_CANCELLED_STATUSES = [12]
ORDER_IGNORED_STATUSES = [20]

DELIVERY_METHOD = {
    1: {'id': 1, 'name': 'Lấy hàng tại công ty'},
    2: {'id': 2, 'name': 'Giao hàng tận nhà'}
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