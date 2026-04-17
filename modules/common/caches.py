from fastapi import Depends
from sqlalchemy.orm import Session, selectinload
from app.fastcore.common.caches import CustomCache
from app.modules.common.session import get_category_replica_db
from app.modules.category.models import ProvinceModel, CommuneModel


class CacheNames:
    KEY_CATEGORY_PROVINCE = 'category_province_cache'
    KEY_CATEGORY_COMMUNE = 'category_commune_cache'


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
