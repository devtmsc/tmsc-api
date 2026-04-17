from datetime import datetime, timezone
from typing import List, Any
from app.fastcore.common.utility import to_dict, get_field_value, update_field_value, get_value_from_dict, format_datetime, format_code, time_ago, add_hours, hours_to_days_hours, get_field_label
from app.modules.common.constant import CUSTOMER_CHANNEL


class CustomerSerializer:
    @classmethod
    def serialize_list(cls, objects: List[Any] = [], context: dict = None, fields: List[str] = None):
        result = []
        commune_cache = context['commune_cache']().get()

        for item in objects:
            item = to_dict(item)

            commune_code = get_field_value(item, 'commune_code')
            update_field_value(item, 'commune_name', get_value_from_dict(dictionary=commune_cache, key_path=commune_code, default={}).get('name', ''))
            update_field_value(item, 'province_name', get_value_from_dict(dictionary=commune_cache, key_path=commune_code, default={}).get('province_name', ''))
            
            channel = get_field_value(item, 'channel')
            update_field_value(item, 'channel_name', get_value_from_dict(dictionary=CUSTOMER_CHANNEL, key_path=channel, default={}).get('name', ''))
            
            created_at = get_field_value(item, 'created_at')
            update_field_value(item, 'created_time', format_datetime(created_at, '%Y/%m/%d %H:%M'))
            update_field_value(item, 'created_time_ago', time_ago(created_at))
            
            birthday = get_field_value(item, 'birthday')
            if birthday:
                update_field_value(item, 'birthday', format_datetime(birthday, '%Y/%m/%d %H:%M'))

            if fields:
                item = {k: v for k, v in item.items() if k in fields}

            result.append(item)
        return result

