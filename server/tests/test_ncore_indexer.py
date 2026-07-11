"""
Tesztek a NcoreIndexerDefinition attribútum-felismeréséhez.

A régi implementáció a felbontást és a nyelvet kizárólag az nCore durva
kategória-tagjéből (pl. "hdser_hun") határozta meg, ami két konkrét hibát
okozott:

1. Minden "hd*" kategóriájú találat 720p-nek látszott, még akkor is, ha a
   release név egyértelműen 1080p-t vagy 2160p-t jelzett.
2. A többévados csomagok (pl. "S01-S04") évad-listája a series_parser egy
   külön hibája miatt teljesen elveszett (lásd test_torrent_parsers.py).

Ez a teszt-modul a nCore keresési API valós mintaválaszán (lásd
NCORE_SAMPLE_RESPONSE) és számos további szélsőséges eseten keresztül
ellenőrzi mindkét javítást.
"""

import pytest

from app.modules.indexer_definitions.integrations.ncore import NcoreIndexerDefinition
from app.modules.torrent_streams.utils.series_parser import parse_season_episode

# A feladatban megadott, valódi nCore API válasz (torrents.php?jsons=True) 12
# találata. Minden bejegyzésnél feltüntetjük a kategóriát és a release nevet,
# amik alapján az indexernek helyesen kell felismernie a felbontást, a
# nyelvet és (a series_parser oldalán) az évad-listát is.
NCORE_SAMPLE_RESPONSE = {
    "results": [
        {
            "torrent_id": "3658580",
            "category": "hdser_hun",
            "release_name": "Miraculous.Tales.Of.Ladybug.and.Cat.Noir.S05.720p.DSNP.WEB-DL.DDP5.1.H.264.HUN.FRE.ENG-VARYG",
        },
        {
            "torrent_id": "3375915",
            "category": "xvidser_hun",
            "release_name": "Miraculous - Katicabogár és Fekete Macska kalandjai S04",
        },
        {
            "torrent_id": "3433977",
            "category": "xvidser_hun",
            "release_name": "Miraculous - Katicabogár és Fekete Macska kalandjai S01",
        },
        {
            "torrent_id": "3375876",
            "category": "xvidser_hun",
            "release_name": "Miraculous - Katicabogár és Fekete Macska kalandjai S02",
        },
        {
            "torrent_id": "3434004",
            "category": "xvidser_hun",
            "release_name": "Miraculous - Katicabogár és Fekete Macska kalandjai S03",
        },
        {
            "torrent_id": "3329105",
            "category": "hdser_hun",
            "release_name": "Miraculous - Katicabogár és Fekete Macska kalandjai S01-S04 720p",
        },
        {
            "torrent_id": "3658581",
            "category": "hdser_hun",
            "release_name": "Miraculous.Tales.Of.Ladybug.and.Cat.Noir.S05.1080p.DSNP.WEB-DL.DDP5.1.H.264.HUN.FRE.ENG-VARYG",
        },
        {
            "torrent_id": "3329383",
            "category": "hdser_hun",
            "release_name": "Miraculous - Katicabogár és Fekete Macska kalandjai S01-S04 1080p",
        },
        {
            "torrent_id": "4141749",
            "category": "hdser",
            "release_name": "Miraculous.Tales.Of.Ladybug.and.Cat.Noir.S06.Part1.720p.DSNP.WEB-DL.DDP5.1.H.264-FULCRUM",
        },
        {
            "torrent_id": "4141751",
            "category": "hdser",
            "release_name": "Miraculous.Tales.Of.Ladybug.and.Cat.Noir.S06.Part1.1080p.DSNP.WEB-DL.DDP5.1.H.264-FULCRUM",
        },
        {
            "torrent_id": "3080646",
            "category": "hdser",
            "release_name": "Miraculous.World.New.York.United.Heroez.2020.1080p.HULU.WEB-DL.DDP5.1.H.264-LAZY",
        },
        {
            "torrent_id": "3080574",
            "category": "xvidser",
            "release_name": "Miraculous.World.New.York.United.Heroez.2020.HULU.WEB-DL.DDP5.1.H.264-LAZY",
        },
    ]
}

# torrent_id -> (elvárt felbontás, elvárt nyelvek halmaza, elvárt évadok)
EXPECTED = {
    # Explicit "720p" a névben -> onnan kell jönnie, nem a kategóriából.
    "3658580": ("720p", {"hun", "eng"}, [5]),
    # Nincs felbontás a névben -> kategória fallback (xvidser -> 480p).
    "3375915": ("480p", {"hun"}, [4]),
    "3433977": ("480p", {"hun"}, [1]),
    "3375876": ("480p", {"hun"}, [2]),
    "3434004": ("480p", {"hun"}, [3]),
    # Többévados ("S01-S04") csomag, explicit "720p" a névben.
    "3329105": ("720p", {"hun"}, [1, 2, 3, 4]),
    # A régi hiba itt adott volna hibás eredményt: a kategória "hdser_hun"
    # minden HD találatot 720p-nek jelölt, holott ez expliciten 1080p.
    "3658581": ("1080p", {"hun", "eng"}, [5]),
    # Ugyanez többévados csomagra: kategória alapján 720p lenne, valójában 1080p.
    "3329383": ("1080p", {"hun"}, [1, 2, 3, 4]),
    # Nincs "_hun" a kategóriában és a névben sincs nyelvjelölés -> ENG fallback.
    "4141749": ("720p", {"eng"}, [6]),
    "4141751": ("1080p", {"eng"}, [6]),
    "3080646": ("1080p", {"eng"}, None),
    "3080574": ("480p", {"eng"}, None),
}


@pytest.fixture(scope="module")
def indexer() -> NcoreIndexerDefinition:
    return NcoreIndexerDefinition()


@pytest.mark.parametrize(
    "torrent", NCORE_SAMPLE_RESPONSE["results"], ids=lambda t: t["torrent_id"]
)
def test_ncore_resolution_and_language_from_sample_response(indexer, torrent):
    torrent_id = torrent["torrent_id"]
    expected_resolution, expected_languages, _ = EXPECTED[torrent_id]

    attribute_ids = indexer._resolve_attribute_ids(
        torrent["category"], torrent["release_name"]
    )

    resolutions = {"2160p", "1080p", "720p", "576p", "540p", "480p"} & set(
        attribute_ids
    )
    languages = {"hun", "eng"} & set(attribute_ids)

    assert resolutions == {expected_resolution}, (
        f"{torrent_id}: várt felbontás {expected_resolution!r}, "
        f"kapott attribute_ids={attribute_ids!r}"
    )
    assert languages == expected_languages, (
        f"{torrent_id}: várt nyelv(ek) {expected_languages!r}, "
        f"kapott attribute_ids={attribute_ids!r}"
    )


@pytest.mark.parametrize(
    "torrent", NCORE_SAMPLE_RESPONSE["results"], ids=lambda t: t["torrent_id"]
)
def test_ncore_sample_season_parsing(torrent):
    torrent_id = torrent["torrent_id"]
    _, _, expected_seasons = EXPECTED[torrent_id]

    seasons, _episodes = parse_season_episode(torrent["release_name"])

    assert seasons == expected_seasons, (
        f"{torrent_id}: várt évadok {expected_seasons!r}, kapott {seasons!r} "
        f"({torrent['release_name']!r})"
    )


def test_ncore_multi_season_pack_regresses_to_720p_without_explicit_resolution(
    indexer,
):
    """
    A "hdser_hun" kategória önmagában nem különbözteti meg a 720p/1080p/2160p
    HD felbontásokat - ha a release névből sem derül ki a felbontás, a
    kategória-fallback (720p) az egyetlen elérhető jelzés.
    """
    attribute_ids = indexer._resolve_attribute_ids(
        "hdser_hun", "Miraculous - Katicabogár és Fekete Macska kalandjai S04"
    )
    assert "720p" in attribute_ids
    assert "1080p" not in attribute_ids
    assert "2160p" not in attribute_ids


class TestResolutionDetectionRegressions:
    """
    Célzott regressziós tesztek arra a hibára, hogy a régi implementáció
    minden "hd*" kategóriájú találatot 720p-nek jelölt, függetlenül attól,
    hogy a release név 1080p-t vagy 2160p-t tartalmazott.
    """

    @pytest.mark.parametrize(
        ("category", "release_name", "expected_resolution"),
        [
            ("hd", "Movie.2024.720p.WEB-DL.x264-GROUP", "720p"),
            ("hd", "Movie.2024.1080p.WEB-DL.x264-GROUP", "1080p"),
            ("hd", "Movie.2024.2160p.UHD.WEB-DL.x265-GROUP", "2160p"),
            ("hd_hun", "Movie.2024.1080p.BluRay.x264.HUN-GROUP", "1080p"),
            ("hdser", "Show.S01E01.2160p.NF.WEB-DL.DDP5.1.x265-GROUP", "2160p"),
            # Nincs felbontás a névben -> kategória fallback.
            ("hd", "Movie 2024 HUN", "720p"),
            ("xvid", "Movie 2024 HUN", "480p"),
        ],
    )
    def test_resolution_matches_release_name_over_category(
        self, indexer, category, release_name, expected_resolution
    ):
        attribute_ids = indexer._resolve_attribute_ids(category, release_name)
        resolutions = {"2160p", "1080p", "720p", "576p", "480p"} & set(attribute_ids)
        assert resolutions == {expected_resolution}


class TestMultiSeasonRangeRegressions:
    """
    Célzott regressziós tesztek a _parse_season_list hibájára, ami miatt
    minden olyan évad-tartomány, ahol a felső határ is "S" előtaggal
    szerepelt (pl. "S01-S04", "S01 to S28"), teljesen None-t adott vissza.
    """

    @pytest.mark.parametrize(
        ("release_name", "expected_seasons"),
        [
            # Az eredetileg megadott hibás eset.
            ("Show.Name.S01-S04.COMPLETE.720p.WEB-DL.x264-GROUP", [1, 2, 3, 4]),
            # Dupla számjegyű határok.
            ("Show.Name.S01-S12.COMPLETE.1080p.WEB-DL.x264-GROUP", list(range(1, 13))),
            # Szóközzel körülvett kötőjel.
            ("Show Name S01 - S13 Complete", list(range(1, 14))),
            # "to" elválasztó mindkét oldalon "S" előtaggal.
            ("Show Name Complete Seasons S01 to S28", list(range(1, 29))),
            # Csak a felső határ visel "S" előtagot.
            ("Show Name Season 1-10 Complete", list(range(1, 11))),
            # Csak az alsó határ visel "S" előtagot (szélsőséges eset).
            ("Show Name S1-10 Complete", list(range(1, 11))),
            # "season" szó mindkét oldalon.
            ("Show Name Season1-Season4 Complete", [1, 2, 3, 4]),
            # Egyetlen évad (nem tartomány) - nem szabad regressziót okoznia.
            ("Show.Name.S05.Complete.720p-GROUP", [5]),
            # Vessző-elválasztott lista, nem tartomány.
            ("Show Name Seasons 1, 2, 3 Complete", [1, 2, 3]),
        ],
    )
    def test_season_range_parsing(self, release_name, expected_seasons):
        seasons, _episodes = parse_season_episode(release_name)
        assert seasons == expected_seasons

    def test_descending_range_is_not_silently_swapped(self):
        # Fordított sorrendű "tartomány" (S04-S01) nem valódi tartomány;
        # a meglévő _expand_range logika ilyenkor csak a kezdőértéket adja
        # vissza, ahelyett hogy hibásan felcserélné a határokat.
        seasons, _episodes = parse_season_episode(
            "Show.Name.S04-S01.COMPLETE.720p-GROUP"
        )
        assert seasons == [4]

    def test_unreasonably_large_range_is_capped(self):
        # Az _expand_range 100-as felső korlátja miatt egy nyilvánvalóan
        # hibás/túl nagy tartomány nem generálhat száznál több elemet.
        seasons, _episodes = parse_season_episode(
            "Show.Name.S01-S99.COMPLETE.720p-GROUP"
        )
        assert seasons is not None
        assert len(seasons) <= 101
        assert seasons[0] == 1
