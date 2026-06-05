from fastapi import HTTPException, status
from modules.preferences.models import PreferenceModel
from modules.preferences.repository import PreferencesRepository


class PreferencesService:
    def __init__(
        self,
        repository: PreferencesRepository,
    ):
        self._repository = repository

    def get_list(self) -> list[PreferenceModel]:
        return self._repository.find_list()

    def find_by_id(
        self,
        id: str,
    ) -> PreferenceModel | None:
        return self._repository.find_by_id(id)

    def get_by_id(
        self,
        id: str,
    ) -> PreferenceModel:
        preference = self._repository.find_by_id(id)

        if not preference:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="A felhasználó nem található.",
            )

        return preference

    def sync_to_db(self):
        self._repository.sync_to_db()
