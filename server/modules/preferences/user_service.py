import pydash
from fastapi import HTTPException
from modules.attributes.service import AttributesService
from modules.preferences.enums import PreferenceEnum
from modules.preferences.models import UserPreferenceModel
from modules.preferences.repository import UserPreferencesRepository


class UserPreferencesService:
    def __init__(
        self,
        repository: UserPreferencesRepository,
        attributes_service: AttributesService,
    ):
        self._repository = repository
        self._attributes_service = attributes_service

    def find(self, user_id: str) -> list[UserPreferenceModel]:
        """Fetches all preferences for a user, sorted by priority order."""
        return self._repository.find_by_user_id(user_id)

    def find_one_by_preference(
        self, user_id: str, preference: PreferenceEnum
    ) -> UserPreferenceModel | None:
        """Retrieves a user's preference model for a specific category type."""
        return self._repository.find_one_by_preference(user_id, preference)

    def create(
        self,
        user_id: str,
        preference: PreferenceEnum,
        preferred_attribute_ids: list[str],
    ) -> UserPreferenceModel:
        """Creates a user's preference overrides, building the definition and attributes."""
        existing_preference = self.find_one_by_preference(user_id, preference)
        if existing_preference:
            raise HTTPException(
                status_code=400,
                detail=f"A(z) '{preference}' preferenciája már létezik.",
            )

        self._validate_attribute_ids(preference, preferred_attribute_ids)

        all_preferences = self.find(user_id)
        next_order = len(all_preferences)

        return self._repository.create(
            user_id=user_id,
            preference=preference,
            preferred_attribute_ids=preferred_attribute_ids,
            order=next_order,
        )

    def update(
        self,
        user_id: str,
        preference: PreferenceEnum,
        preferred_attribute_ids: list[str],
    ) -> UserPreferenceModel:
        """Updates the preferred attribute list of an existing user preference category."""
        user_preference = self.find_one_by_preference(user_id, preference)
        if not user_preference:
            raise HTTPException(
                status_code=404,
                detail=f"A(z) '{preference.value}' preferenciája nem található.",
            )

        self._validate_attribute_ids(preference, preferred_attribute_ids)

        return self._repository.update(user_preference, preferred_attribute_ids)

    def delete_by_preference(self, user_id: str, preference: PreferenceEnum) -> None:
        user_preference = self.find_one_by_preference(user_id, preference)
        if not user_preference:
            raise HTTPException(
                status_code=404,
                detail=f"A(z) '{preference.value}' preferenciája nem található.",
            )

        self._repository.delete(user_preference)

        self.reorder(user_id)

    def reorder(
        self, user_id: str, preferences: list[PreferenceEnum] | None = None
    ) -> list[UserPreferenceModel]:
        """Sets a new sorting priority list for the user's preference categories."""
        items = self.find(user_id)

        updates: list[tuple[UserPreferenceModel, int]] = []

        if preferences is not None:
            item_map = {item.definition.preference_id: item for item in items}
            for pref in preferences:
                if pref not in item_map:
                    raise HTTPException(
                        status_code=400,
                        detail=f"A(z) '{pref.value}' preferencia nem található.",
                    )

            for idx, pref in enumerate(preferences):
                updates.append((item_map[pref], idx))
        else:
            for idx, item in enumerate(items):
                updates.append((item, idx))

        return self._repository.reorder(user_id, updates)

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
        for attribute_id in attribute_ids:
            if attribute_id not in valid_attribute_ids:
                raise HTTPException(
                    status_code=400,
                    detail=f"A(z) '{attribute_id}' attribútum nem tartozik a(z) '{preference}' preferenciához.",
                )
