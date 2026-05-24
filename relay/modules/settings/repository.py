from modules.settings.models import SettingModel
from sqlalchemy.orm import Session


class SettingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_one(self, key: str) -> SettingModel | None:
        return self.db.query(SettingModel).filter(SettingModel.key == key).first()

    def create_or_update(self, key: str, value: dict) -> SettingModel:
        record = self.find_one(key)
        if record:
            record.value = value
        else:
            record = SettingModel(key=key, value=value)
            self.db.add(record)
        self.db.flush()
        return record
