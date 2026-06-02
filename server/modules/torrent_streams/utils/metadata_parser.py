import re
from collections import defaultdict

from modules.attributes.models import AttributeModel
from modules.preferences.models import PreferenceModel


class TorrentMetadataParser:
    def __init__(
        self,
        name: str,
        attributes: list[AttributeModel],
        preferences: list[PreferenceModel],
    ):
        self._name = name.lower()

        # 1. Preferenciák viselkedésének (multiple) kigyűjtése (string kulcsokkal)
        self._preference_multiple_map: dict[str, bool] = {
            pref.id: pref.multiple for pref in preferences
        }

        # 2. Attribútumok szétválogatása: Regexes keresendők vs. Fallback értékek
        self._grouped_attributes: dict[str | None, list[AttributeModel]] = defaultdict(
            list
        )
        self._fallbacks: dict[str | None, AttributeModel] = {}

        for attr in attributes:
            # Type narrowing: Ha biztosan string, mehet a keresendők közé
            if isinstance(attr.pattern, str) and attr.pattern.strip():
                self._grouped_attributes[attr.preference_id].append(attr)
            else:
                self._fallbacks[attr.preference_id] = attr

    def parse(self) -> list[AttributeModel]:
        matched_attributes: list[AttributeModel] = []

        # Az összes létező kategória azonosítója (stringek és a None)
        all_pref_ids = set(self._grouped_attributes.keys()) | set(
            self._fallbacks.keys()
        )

        for pref_id in all_pref_ids:
            category_matched = False

            # Ha nincs preference_id (pl. egyedi tagek, mint a 3D), ott több találatot is engedünk
            is_multiple = (
                self._preference_multiple_map.get(pref_id, False) if pref_id else True
            )

            for attr in self._grouped_attributes.get(pref_id, []):
                # Biztonsági ellenőrzés a típusellenőrző megnyugtatására a cikluson belül is
                if not isinstance(attr.pattern, str):
                    continue

                # Jelenleg itt történik a fordítás minden alkalommal
                pattern = re.compile(attr.pattern, re.IGNORECASE)

                if pattern.search(self._name):
                    matched_attributes.append(attr)
                    category_matched = True

                    # EARLY EXIT
                    if not is_multiple:
                        break

            # Fallback kezelés, ha semmi nem illeszkedett az adott kategóriában
            if not category_matched and pref_id in self._fallbacks:
                matched_attributes.append(self._fallbacks[pref_id])

        return matched_attributes
