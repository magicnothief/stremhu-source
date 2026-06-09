import sqlalchemy as sa
from common.logger import logger
from modules.attributes.models import AttributeModel
from modules.indexer_accounts.models import IndexerAccountModel
from modules.preferences.models import PreferenceModel
from modules.preferences.seeds import DEFAULT_PREFERENCES
from sqlalchemy.orm import Session, contains_eager


class PreferencesRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_list(self) -> list[PreferenceModel]:
        return (
            self.db.query(PreferenceModel)
            .outerjoin(
                AttributeModel,
                sa.and_(
                    PreferenceModel.id == AttributeModel.preference_id,
                    sa.or_(
                        AttributeModel.type != "indexer_definition",
                        self.db.query(IndexerAccountModel.indexer_id)
                        .filter(IndexerAccountModel.indexer_id == AttributeModel.id)
                        .exists(),
                    ),
                ),
            )
            .options(contains_eager(PreferenceModel.attributes))
            .all()
        )

    def find_by_id(self, id: str) -> PreferenceModel | None:
        return self.db.query(PreferenceModel).filter(PreferenceModel.id == id).first()

    def sync_to_db(self):
        """Szinkronizálja a kódbázisban definiált preferenciákat az adatbázissal.

        Frissíti a meglévőket, beszúrja az újakat, és törli azokat, amelyek
        kikerültek a kódból.
        """

        code_ids = {pref.id for pref in DEFAULT_PREFERENCES}

        deleted_count = (
            self.db.query(PreferenceModel)
            .filter(PreferenceModel.id.not_in(code_ids))
            .delete(synchronize_session=False)
        )
        if deleted_count > 0:
            logger.info(f"🗑️ Törölve {deleted_count} elavult kategória a DB-ből.")

        for pref in DEFAULT_PREFERENCES:
            db_pref = (
                self.db.query(PreferenceModel)
                .filter(PreferenceModel.id == pref.id)
                .first()
            )

            if db_pref:
                if (
                    db_pref.name != pref.name
                    or db_pref.description != pref.description
                    or db_pref.emoji != pref.emoji
                ):
                    db_pref.name = pref.name
                    db_pref.description = pref.description
                    db_pref.emoji = pref.emoji
            else:
                new_pref = PreferenceModel(
                    id=pref.id,
                    name=pref.name,
                    description=pref.description,
                    emoji=pref.emoji,
                )
                self.db.add(new_pref)

        self.db.commit()
