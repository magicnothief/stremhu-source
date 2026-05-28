import pydash
from fastapi import HTTPException
from modules.attributes.service import AttributesService
from modules.preferences.enums import PreferenceEnum
from modules.preferences.models import SystemPreferenceModel
from modules.preferences.repository import SystemPreferencesRepository


class SystemPreferencesService:
    def __init__(
        self,
        repository: SystemPreferencesRepository,
        attributes_service: AttributesService,
    ):
        self._repository = repository
        self._attributes_service = attributes_service

    def find(self) -> list[SystemPreferenceModel]:
        """Fetches all system-level preferences sorted by priority order."""
        return self._repository.find_all()

    def find_one_by_preference(
        self, preference: PreferenceEnum
    ) -> SystemPreferenceModel | None:
        """Retrieves the system preference for a specific category type."""
        return self._repository.find_one_by_preference(preference)

    def _validate_attribute_ids(
        self, preference: PreferenceEnum, attribute_ids: list[str]
    ) -> None:
        """Validates that all provided attribute IDs are unique and belong to the given preference category."""
        if pydash.duplicates(attribute_ids):
            raise HTTPException(
                status_code=400,
                detail="Egy attribútum nem szerepelhet többször ugyanazon preferencián belül.",
            )

        db_attributes = self._attributes_service.get_by_preference(preference)
        valid_attribute_ids = {attr.id for attr in db_attributes}
        for attr_id in attribute_ids:
            if attr_id not in valid_attribute_ids:
                raise HTTPException(
                    status_code=400,
                    detail=f"A(z) '{attr_id}' attribútum nem tartozik a(z) '{preference}' preferenciához.",
                )

    def create(
        self,
        preference: PreferenceEnum,
        preferred_attribute_ids: list[str],
    ) -> SystemPreferenceModel:
        """Creates a system-level preference with ordered preferred attributes."""
        existing = self.find_one_by_preference(preference)
        if existing:
            return self.update(preference, preferred_attribute_ids)

        self._validate_attribute_ids(preference, preferred_attribute_ids)

        all_prefs = self.find()
        next_order = len(all_prefs)

        return self._repository.create(
            preference=preference,
            preferred_attribute_ids=preferred_attribute_ids,
            order=next_order,
        )

    def update(
        self,
        preference: PreferenceEnum,
        preferred_attribute_ids: list[str],
    ) -> SystemPreferenceModel:
        """Updates the preferred attribute list of an existing system preference."""
        system_pref = self.find_one_by_preference(preference)
        if not system_pref:
            return self.create(preference, preferred_attribute_ids)

        self._validate_attribute_ids(preference, preferred_attribute_ids)

        return self._repository.update(system_pref, preferred_attribute_ids)

    def delete_by_preference(self, preference: PreferenceEnum) -> None:
        """Deletes a system preference category."""
        system_pref = self.find_one_by_preference(preference)
        if not system_pref:
            return

        self._repository.delete(system_pref)

        self.reorder()

    def reorder(
        self, preferences: list[PreferenceEnum] | None = None
    ) -> list[SystemPreferenceModel]:
        """Sets a new sorting priority list for the system preference categories."""
        items = self.find()

        if preferences is not None:
            item_map = {item.definition.preference_id: item for item in items}
            for pref in preferences:
                if pref not in item_map:
                    raise HTTPException(
                        status_code=400,
                        detail=f"A(z) '{pref.value}' preferencia nem található.",
                    )
            updates = []
            for idx, pref in enumerate(preferences):
                updates.append((item_map[pref], idx))
        else:
            updates = []
            for idx, item in enumerate(items):
                updates.append((item, idx))

        return self._repository.reorder(updates)
