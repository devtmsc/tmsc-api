from datetime import datetime, timezone
from typing import List, Any
from app.fastcore.common.utility import to_dict, get_field_value, update_field_value, get_value_from_dict, format_datetime, format_code, time_ago, add_hours, hours_to_days_hours, get_field_label
from app.modules.common.utility import get_update_status_ticket, get_update_status_ticket_detail, view_update_ticket, view_update_ticket_detail
from app.constant import TICKET_STATUS, TICKET_PRIORITY, TICKET_FEEDBACK_TYPE, TICKET_OVERDUE_STATUS, TICKET_FINAL_STATUSES, TICKET_HISTORY_ACTION


def detail_to_dict(obj):
    data = {
        c.name: getattr(obj, c.name)
        for c in obj.__table__.columns
    }

    # thêm relationship
    if hasattr(obj, "details"):
        data["details"] = [detail_to_dict(d) for d in obj.details]

    if hasattr(obj, "feedbacks"):
        data["feedbacks"] = [detail_to_dict(f) for f in obj.feedbacks]
        
    if hasattr(obj, "history"):
        data["history"] = [detail_to_dict(f) for f in obj.history]

    return data


class TicketSerializer:
    @classmethod
    def serialize_list(cls, objects: List[Any] = [], context: dict = None, fields: List[str] = None):
        result = []
        users_cache = context['users_cache']().get()
        now = datetime.now(timezone.utc)

        for item in objects:
            item = to_dict(item)

            ticket_id = get_field_value(item, 'id')
            update_field_value(item, 'ticket_code', format_code(ticket_id))

            status = get_field_value(item, 'status')
            update_field_value(item, 'status_name', get_value_from_dict(
                dictionary=TICKET_STATUS, key_path=status, default={}).get('name', ''))

            priority = get_field_value(item, 'priority')
            update_field_value(item, 'priority_name', get_value_from_dict(
                dictionary=TICKET_PRIORITY, key_path=priority, default={}).get('name', ''))

            user_id = get_field_value(item, 'user_id')
            update_field_value(item, 'user_email', get_value_from_dict(
                dictionary=users_cache, key_path=user_id, default={}).get('email', ''))
            
            ticket_relations = get_field_value(item, 'ticket_relations')
            ticket_relations_name = []
            if ticket_relations:
                for it in ticket_relations:
                    ticket_relations_name.append(format_code(it))
            update_field_value(item, 'ticket_relations_name', ticket_relations_name)

            created_at = get_field_value(item, 'created_at')
            update_field_value(item, 'created_time', format_datetime(created_at, '%Y/%m/%d %H:%M'))
            update_field_value(item, 'created_time_ago', time_ago(created_at))

            estimated_at = get_field_value(item, 'estimated_at')
            estimated_at = estimated_at.replace(
                tzinfo=timezone.utc) if estimated_at.tzinfo is None else estimated_at
            if (status not in TICKET_FINAL_STATUSES) and (estimated_at < now):
                update_field_value(item, 'overdue_status', get_value_from_dict(
                    dictionary=TICKET_OVERDUE_STATUS, key_path=1, default={}).get('id', ''))
                update_field_value(item, 'overdue_status_name', get_value_from_dict(
                    dictionary=TICKET_OVERDUE_STATUS, key_path=1, default={}).get('name', ''))
            else:
                update_field_value(item, 'overdue_status', get_value_from_dict(
                    dictionary=TICKET_OVERDUE_STATUS, key_path=2, default={}).get('id', ''))
                update_field_value(item, 'overdue_status_name', get_value_from_dict(
                    dictionary=TICKET_OVERDUE_STATUS, key_path=2, default={}).get('name', ''))

            if fields:
                item = {k: v for k, v in item.items() if k in fields}

            result.append(item)
        return result


def feedback_serializer(it, users_cache):
    feedback_created_at = get_field_value(it, 'created_at')
    update_field_value(it, 'created_time', format_datetime(feedback_created_at, '%Y/%m/%d %H:%M'))
    update_field_value(it, 'created_time_ago', time_ago(feedback_created_at))

    feedback_type = get_field_value(it, 'type')
    update_field_value(it, 'type_name', get_value_from_dict(
        dictionary=TICKET_FEEDBACK_TYPE, key_path=feedback_type, default={}).get('name', ''))
    update_field_value(it, 'type_color', get_value_from_dict(
        dictionary=TICKET_FEEDBACK_TYPE, key_path=feedback_type, default={}).get('color', ''))

    feedback_user_id = get_field_value(it, 'user_id')
    update_field_value(it, 'user_email', get_value_from_dict(
        dictionary=users_cache, key_path=feedback_user_id, default={}).get('email', ''))
    update_field_value(it, 'user_avatar', get_value_from_dict(
        dictionary=users_cache, key_path=feedback_user_id, default={}).get('avatar', ''))
    return it

def convert_value(code: str, value: str):
    if code == 'status' and value:
        return get_value_from_dict(dictionary=TICKET_STATUS, key_path=value, default={}).get('name', '')

def history_serializer(it, users_cache):
    history_created_at = get_field_value(it, 'created_at')
    update_field_value(it, 'created_time', format_datetime(history_created_at, '%Y/%m/%d %H:%M'))
    update_field_value(it, 'created_time_ago', time_ago(history_created_at))

    history_action = get_field_value(it, 'action')
    update_field_value(it, 'action_name', get_value_from_dict(
        dictionary=TICKET_HISTORY_ACTION, key_path=history_action, default={}).get('name', ''))
    update_field_value(it, 'action_color', get_value_from_dict(
        dictionary=TICKET_HISTORY_ACTION, key_path=history_action, default={}).get('color', ''))

    history_user_id = get_field_value(it, 'user_id')
    update_field_value(it, 'user_email', get_value_from_dict(
        dictionary=users_cache, key_path=history_user_id, default={}).get('email', ''))
    update_field_value(it, 'user_avatar', get_value_from_dict(
        dictionary=users_cache, key_path=history_user_id, default={}).get('avatar', ''))
    
    history_data = get_field_value(it, 'data')
    if history_data:
        for item in history_data:
            update_field_value(item, 'name', str(get_field_label(item.get('code'))).lower())
            update_field_value(item, 'after_data_value', convert_value(item.get('code'), item.get('after_data')))
            update_field_value(item, 'before_data_value', convert_value(item.get('code'), item.get('before_data')))
    
    return it


class TicketDetailSerializer:
    @classmethod
    def serialize_list(cls, objects: List[Any] = [], context: dict = None, fields: List[str] = None):
        result = []
        users_cache = context['users_cache']().get()
        department_cache = context['department_cache']().get()
        current_user = context['current_user']
        now = datetime.now(timezone.utc)

        for item in objects:
            item = detail_to_dict(item)

            ticket_id = get_field_value(item, 'id')
            update_field_value(item, 'ticket_code', format_code(ticket_id))

            status = get_field_value(item, 'status')
            update_field_value(item, 'status_name', get_value_from_dict(
                dictionary=TICKET_STATUS, key_path=status, default={}).get('name', ''))

            priority = get_field_value(item, 'priority')
            update_field_value(item, 'priority_name', get_value_from_dict(
                dictionary=TICKET_PRIORITY, key_path=priority, default={}).get('name', ''))

            user_id = get_field_value(item, 'user_id')
            update_field_value(item, 'user_email', get_value_from_dict(
                dictionary=users_cache, key_path=user_id, default={}).get('email', ''))

            from_department = get_field_value(item, 'from_department')
            from_department_name = []
            if from_department:
                for it in from_department:
                    from_department_name.append(get_value_from_dict(
                        dictionary=department_cache, key_path=it, default={}).get('name', ''))
            update_field_value(item, 'from_department_name',
                               from_department_name)

            to_department = get_field_value(item, 'to_department')
            to_department_name = []
            if to_department:
                for it in to_department:
                    to_department_name.append(get_value_from_dict(
                        dictionary=department_cache, key_path=it, default={}).get('name', ''))
            update_field_value(item, 'to_department_name', to_department_name)

            assignees = get_field_value(item, 'assignees')
            assignees_email = []
            if assignees:
                for it in assignees:
                    assignees_email.append(get_value_from_dict(
                        dictionary=users_cache, key_path=it, default={}).get('email', ''))
            update_field_value(item, 'assignees_email', assignees_email)
            
            ticket_relations = get_field_value(item, 'ticket_relations')
            ticket_relations_name = []
            if ticket_relations:
                for it in ticket_relations:
                    ticket_relations_name.append(format_code(it))
            update_field_value(item, 'ticket_relations_name', ticket_relations_name)

            created_at = get_field_value(item, 'created_at')
            update_field_value(item, 'created_time', format_datetime(
                created_at, '%Y/%m/%d %H:%M'))
            update_field_value(item, 'created_time_ago', time_ago(created_at))

            estimated_at = get_field_value(item, 'estimated_at')
            if estimated_at:
                update_field_value(item, 'estimated_time', format_datetime(
                    estimated_at, '%Y/%m/%d %H:%M'))
            else:
                update_field_value(item, 'estimated_time', '')

            estimated_at = estimated_at.replace(tzinfo=timezone.utc) if estimated_at.tzinfo is None else estimated_at
            if (status not in TICKET_FINAL_STATUSES) and (estimated_at < now):
                update_field_value(item, 'overdue_status', get_value_from_dict(
                    dictionary=TICKET_OVERDUE_STATUS, key_path=1, default={}).get('id', ''))
                update_field_value(item, 'overdue_status_name', get_value_from_dict(
                    dictionary=TICKET_OVERDUE_STATUS, key_path=1, default={}).get('name', ''))
            else:
                update_field_value(item, 'overdue_status', get_value_from_dict(
                    dictionary=TICKET_OVERDUE_STATUS, key_path=2, default={}).get('id', ''))
                update_field_value(item, 'overdue_status_name', get_value_from_dict(
                    dictionary=TICKET_OVERDUE_STATUS, key_path=2, default={}).get('name', ''))

            completed_at = get_field_value(item, 'completed_at')
            if completed_at:
                update_field_value(item, 'completed_time', format_datetime(
                    completed_at, '%Y/%m/%d %H:%M'))
            else:
                update_field_value(item, 'completed_time', '')

            completed_by = get_field_value(item, 'completed_by')
            if completed_by:
                update_field_value(item, 'completed_by_email', get_value_from_dict(
                    dictionary=users_cache, key_path=completed_by, default={}).get('email', ''))
            else:
                update_field_value(item, 'completed_by_email', '')

            canceled_at = get_field_value(item, 'canceled_at')
            if canceled_at:
                update_field_value(item, 'canceled_time', format_datetime(
                    canceled_at, '%Y/%m/%d %H:%M'))
            else:
                update_field_value(item, 'canceled_time', '')

            canceled_by = get_field_value(item, 'canceled_by')
            if canceled_by:
                update_field_value(item, 'canceled_by_email', get_value_from_dict(
                    dictionary=users_cache, key_path=completed_by, default={}).get('email', ''))
            else:
                update_field_value(item, 'canceled_by_email', '')
                
            overdue_hours = get_field_value(item, 'overdue_hours')
            if overdue_hours:
                update_field_value(item, 'overdue_hours_name', hours_to_days_hours(overdue_hours))
            else:
                update_field_value(item, 'overdue_hours_name', '')

            feedbacks = get_field_value(item, 'feedbacks')
            if feedbacks:
                for it in feedbacks:
                    it = feedback_serializer(it, users_cache)
            
            history = get_field_value(item, 'history')
            if history:
                for it in history:
                    it = history_serializer(it, users_cache)
                    
            # ticket_detail
            ticket_detail = get_field_value(item, 'details')
            if ticket_detail:
                for it in ticket_detail:
                    detail_status = get_field_value(it, 'status')
                    update_field_value(it, 'status_name', get_value_from_dict(
                        dictionary=TICKET_STATUS, key_path=detail_status, default={}).get('name', ''))

                    detail_priority = get_field_value(it, 'priority')
                    update_field_value(it, 'priority_name', get_value_from_dict(
                        dictionary=TICKET_PRIORITY, key_path=detail_priority, default={}).get('name', ''))

                    detail_to_department = get_field_value(it, 'to_department')
                    detail_to_department_name = []
                    if detail_to_department:
                        for i in detail_to_department:
                            detail_to_department_name.append(get_value_from_dict(
                                dictionary=department_cache, key_path=i, default={}).get('name', ''))
                    update_field_value(it, 'to_department_name', detail_to_department_name)

                    detail_assignees = get_field_value(it, 'assignees')
                    detail_assignees_email = []
                    if detail_assignees:
                        for i in detail_assignees:
                            detail_assignees_email.append(get_value_from_dict(
                                dictionary=users_cache, key_path=i, default={}).get('email', ''))
                    update_field_value(it, 'assignees_email',
                                       detail_assignees_email)

                    detail_created_at = get_field_value(it, 'created_at')
                    update_field_value(it, 'created_time', format_datetime(
                        detail_created_at, '%Y/%m/%d %H:%M'))
                    update_field_value(it, 'created_time_ago',
                                       time_ago(detail_created_at))

                    detail_estimated_at = get_field_value(it, 'estimated_at')
                    if detail_estimated_at:
                        update_field_value(it, 'estimated_time', format_datetime(
                            detail_estimated_at, '%Y/%m/%d %H:%M'))
                    else:
                        update_field_value(it, 'estimated_time', '')

                    detail_estimated_at = detail_estimated_at.replace(
                        tzinfo=timezone.utc) if detail_estimated_at.tzinfo is None else detail_estimated_at
                    if (detail_status not in TICKET_FINAL_STATUSES) and (detail_estimated_at < now):
                        update_field_value(it, 'overdue_status', get_value_from_dict(
                            dictionary=TICKET_OVERDUE_STATUS, key_path=1, default={}).get('id', ''))
                        update_field_value(it, 'overdue_status_name', get_value_from_dict(
                            dictionary=TICKET_OVERDUE_STATUS, key_path=1, default={}).get('name', ''))
                    else:
                        update_field_value(it, 'overdue_status', get_value_from_dict(
                            dictionary=TICKET_OVERDUE_STATUS, key_path=2, default={}).get('id', ''))
                        update_field_value(it, 'overdue_status_name', get_value_from_dict(
                            dictionary=TICKET_OVERDUE_STATUS, key_path=2, default={}).get('name', ''))

                    detail_completed_at = get_field_value(it, 'completed_at')
                    if detail_completed_at:
                        update_field_value(it, 'completed_time', format_datetime(
                            detail_completed_at, '%Y/%m/%d %H:%M'))
                    else:
                        update_field_value(it, 'completed_time', '')

                    detail_completed_by = get_field_value(it, 'completed_by')
                    if detail_completed_by:
                        update_field_value(it, 'completed_by_email', get_value_from_dict(
                            dictionary=users_cache, key_path=detail_completed_by, default={}).get('email', ''))
                    else:
                        update_field_value(it, 'completed_by_email', '')

                    detail_canceled_at = get_field_value(it, 'canceled_at')
                    if detail_canceled_at:
                        update_field_value(it, 'canceled_time', format_datetime(
                            detail_canceled_at, '%Y/%m/%d %H:%M'))
                    else:
                        update_field_value(it, 'canceled_time', '')

                    detail_canceled_by = get_field_value(it, 'canceled_by')
                    if detail_canceled_by:
                        update_field_value(it, 'canceled_by_email', get_value_from_dict(
                            dictionary=users_cache, key_path=detail_canceled_by, default={}).get('email', ''))
                    else:
                        update_field_value(it, 'canceled_by_email', '')
                    
                    overdue_hours_detail = get_field_value(it, 'overdue_hours')
                    if overdue_hours_detail:
                        update_field_value(it, 'overdue_hours_name', hours_to_days_hours(overdue_hours_detail))
                    else:
                        update_field_value(it, 'overdue_hours_name', '')

                    detail_feedback = get_field_value(it, 'feedbacks')
                    if detail_feedback:
                        for i in detail_feedback:
                            i = feedback_serializer(i, users_cache)
                            
                    detail_history = get_field_value(it, 'history')
                    if detail_history:
                        for i in detail_history:
                            i = history_serializer(i, users_cache)
                            
                    update_field_value(it, 'accept_status', get_update_status_ticket_detail(current_user.get('uuid'), user_id, current_user.get('role_id'), current_user.get('position'),
                                                   current_user.get('department'), from_department, to_department, status, detail_status, assignees))
                    update_field_value(it, 'can_update', view_update_ticket_detail(current_user.get('uuid'), user_id, current_user.get('role_id'), current_user.get('position'),
                                                   current_user.get('department'), from_department, to_department, status, detail_status))
            
            update_field_value(item, 'accept_status', get_update_status_ticket(current_user.get('uuid'), user_id, current_user.get('role_id'), current_user.get('position'),
                                                   current_user.get('department'), from_department, to_department, status, assignees))
            update_field_value(item, 'can_update', view_update_ticket(current_user.get('uuid'), user_id, current_user.get('role_id'), current_user.get('position'),
                                                   current_user.get('department'), from_department, to_department, status))
            
            if fields:
                item = {k: v for k, v in item.items() if k in fields}

            result.append(item)
        return result


class TicketFeedbackSerializer:
    @classmethod
    def serialize_list(cls, objects: List[Any] = [], context: dict = None, fields: List[str] = None):
        result = []
        users_cache = context['users_cache']().get()
        
        for item in objects:
            item = to_dict(item)
            
            item = feedback_serializer(item, users_cache)
            if fields:
                    item = {k: v for k, v in item.items() if k in fields}

            result.append(item)
        
        return result
    

class TicketTemplateSerializer:
    @classmethod
    def serialize_list(cls, objects: List[Any] = [], context: dict = None, fields: List[str] = None):
        result = []
        for item in objects:
            item = detail_to_dict(item)

            ticket_id = get_field_value(item, 'id')
            update_field_value(item, 'ticket_code', format_code(ticket_id))

            estimate_time = get_field_value(item, 'estimate_time')
            update_field_value(item, 'estimated_at', add_hours(estimate_time))

            # ticket_detail
            ticket_detail = get_field_value(item, 'details')
            if ticket_detail:
                for it in ticket_detail:
                    estimate_time_detail = get_field_value(it, 'estimate_time')
                    update_field_value(it, 'estimated_at', add_hours(estimate_time_detail))
            
            if fields:
                item = {k: v for k, v in item.items() if k in fields}

            result.append(item)
        return result