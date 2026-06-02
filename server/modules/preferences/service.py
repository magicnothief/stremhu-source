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

    def sync_to_db(self):
        self._repository.sync_to_db()
