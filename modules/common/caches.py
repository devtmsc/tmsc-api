from fastapi import Depends
from sqlalchemy.orm import Session, selectinload
from app.fastcore.common.caches import CustomCache
from app.modules.common.session import get_category_replica_db
from app.modules.category.models import ChannelModel, ProvinceModel, OrderStatusModel, OrderReasonModel, OrderPartnerModel, OrderStatusMappingModel


class CacheNames:
    KEY_CATEGORY_CHANNEL = 'category_channel_cache'
    KEY_CATEGORY_PROVINCE = 'category_province_cache'
    KEY_CATEGORY_COMMUNE = 'category_commune_cache'
    
    KEY_CATEGORY_ORDER_PARTNER = 'category_order_partner_cache'
    KEY_CATEGORY_ORDER_STATUS = 'category_order_status_cache'
    KEY_CATEGORY_ORDER_REASON = 'category_order_reason_cache'
    KEY_CATEGORY_ORDER_STATUS_MAPPING = 'category_order_status_mapping_cache'


class CategoryProvinceCache(CustomCache):
    def __init__(self, db: Session = Depends(get_category_replica_db)):
        super().__init__(CacheNames.KEY_CATEGORY_PROVINCE, self.data)
        self.db = db

    def data(self):
        db_data = self.db.query(ProvinceModel.code, ProvinceModel.name,
                                ProvinceModel.description, ProvinceModel.synonym).all()
        return {row[0]: {'code': row[0], 'name': row[1], 'description': row[2], 'synonym': row[3]} for row in db_data}


class CategoryCommuneCache(CustomCache):
    def __init__(self, db: Session = Depends(get_category_replica_db)):
        super().__init__(CacheNames.KEY_CATEGORY_COMMUNE, self.data)
        self.db = db

    def data(self):
        data = {}
        db_data = self.db.query(ProvinceModel).options(
            selectinload(ProvinceModel.communes)).all()
        for row in db_data:
            if row.communes:
                for item in row.communes:
                    if item.code not in data:
                        data[item.code] = {'code': item.code, 'name': item.name, 'description': item.description,
                                           'province_code': item.province_code, 'synonym': item.synonym, 'province_name': row.name}
        return data


class CategoryChannelCache(CustomCache):
    def __init__(self, db: Session = Depends(get_category_replica_db)):
        super().__init__(CacheNames.KEY_CATEGORY_CHANNEL, self.data)
        self.db = db

    def data(self):
        db_data = self.db.query(ChannelModel.id, ChannelModel.name).all()
        return {row[0]: {'id': row[0], 'name': row[1]} for row in db_data}
    

class CategoryOrderPartnerCache(CustomCache):
    def __init__(self, db: Session = Depends(get_category_replica_db)):
        super().__init__(CacheNames.KEY_CATEGORY_ORDER_PARTNER, self.data)
        self.db = db

    def data(self):
        db_data = self.db.query(OrderPartnerModel.code, OrderPartnerModel.name, OrderPartnerModel.tracking_url).all()
        return {row[0]: {'code': row[0], 'name': row[1], 'tracking_url': row[2]} for row in db_data}


class CategoryOrderStatusCache(CustomCache):
    def __init__(self, db: Session = Depends(get_category_replica_db)):
        super().__init__(CacheNames.KEY_CATEGORY_ORDER_STATUS, self.data)
        self.db = db

    def data(self):
        db_data = self.db.query(OrderStatusModel.code, OrderStatusModel.name, OrderStatusModel.color).all()
        return {row[0]: {'code': row[0], 'name': row[1], 'color': row[2]} for row in db_data}
    

class CategoryOrderReasonCache(CustomCache):
    def __init__(self, db: Session = Depends(get_category_replica_db)):
        super().__init__(CacheNames.KEY_CATEGORY_ORDER_REASON, self.data)
        self.db = db

    def data(self):
        data = {}
        db_data = self.db.query(OrderReasonModel.partner_code, OrderStatusModel.code, OrderStatusModel.name, OrderReasonModel.type).all()
        for row in db_data:
            if row[0] not in data:
                data[row[0]] = {}
            
            data[row[0]][row[1]] = {'partner_code': row[0], 'code': row[1], 'name': row[2], 'type': row[3]}
        
        return db_data
    

class CategoryOrderStatusMappingCache(CustomCache):
    def __init__(self, db: Session = Depends(get_category_replica_db)):
        super().__init__(CacheNames.KEY_CATEGORY_ORDER_STATUS_MAPPING, self.data)
        self.db = db

    def data(self):
        data = {}
        db_data = self.db.query(OrderStatusMappingModel.partner_code, OrderStatusMappingModel.partner_status_code, OrderStatusMappingModel.status_code, OrderStatusMappingModel.name).all()
        for row in db_data:
            if row[0] and row[1]:
                if row[0] not in data:
                    data[row[0]] = {}
                
                data[row[0]][row[1]] = {'partner_code': row[0], 'partner_status_code': row[1], 'status_code': row[2], 'name': row[3]}
        
        return data


