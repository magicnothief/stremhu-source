import re
from collections import defaultdict
from typing import TypeAlias

from modules.attributes.models import AttributeModel
from modules.preferences.models import PreferenceModel

PreferenceMultipleMap: TypeAlias = dict[str, bool]
PatternAttributeTuple: TypeAlias = tuple[re.Pattern[str], AttributeModel]
GroupedAttributes: TypeAlias = dict[str | None, list[PatternAttributeTuple]]
FallbackAttributes: TypeAlias = dict[str | None, AttributeModel]


class TorrentNameParserService:
    def __init__(
        self,
        attributes: list[AttributeModel],
        preferences: list[PreferenceModel],
    ):
        # 1. Preferenciák viselkedésének (multiple) kigyűjtése
        self._preference_multiple_map: PreferenceMultipleMap = {
            pref.id: pref.multiple for pref in preferences
        }

        # 2. Attribútumok csoportosítása és regexek előfordítása
        self._grouped_attributes: GroupedAttributes = defaultdict(list)
        self._fallbacks: FallbackAttributes = {}

        for attr in attributes:
            if isinstance(attr.pattern, str) and attr.pattern.strip():
                # Pre-compile constraints with IGNORECASE
                pattern = re.compile(attr.pattern, re.IGNORECASE)
                self._grouped_attributes[attr.preference_id].append((pattern, attr))
            else:
                self._fallbacks[attr.preference_id] = attr

    def parse(
        self,
        name: str,
        external_fallbacks: list[AttributeModel] | None = None,
    ) -> list[AttributeModel]:
        """Parses the torrent name and returns the matched AttributeModel objects.

        If a category does not have a match from the name, it falls back to the
        provided external_fallbacks first, and then to the database default fallback.
        """
        name_lower = name.lower()
        matched_attributes: list[AttributeModel] = []

        # Külső fallback attribútumok indexelése kategória szerint a gyors kereséshez
        external_fallback_map: dict[str | None, AttributeModel] = {}
        if external_fallbacks:
            for attr in external_fallbacks:
                external_fallback_map[attr.preference_id] = attr

        all_pref_ids = set(self._grouped_attributes.keys()) | set(
            self._fallbacks.keys()
        )

        for pref_id in all_pref_ids:
            category_matched = False
            is_multiple = (
                self._preference_multiple_map.get(pref_id, False) if pref_id else True
            )

            for pattern, attr in self._grouped_attributes.get(pref_id, []):
                if pattern.search(name_lower):
                    matched_attributes.append(attr)
                    category_matched = True

                    if not is_multiple:
                        break

            # Fallback logika, ha az adott kategóriában nem találtunk egyezést a névben
            if not category_matched:
                if pref_id in external_fallback_map:
                    matched_attributes.append(external_fallback_map[pref_id])
                elif pref_id in self._fallbacks:
                    matched_attributes.append(self._fallbacks[pref_id])

        return matched_attributes
