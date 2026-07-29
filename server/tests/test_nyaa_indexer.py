import asyncio

import httpx
import pytest

from app.modules.indexer_definitions.integrations.nyaa import (
    NyaaIndexerDefinition,
    _AnimeEntry,
    _is_anime_meta,
    _normalize,
    _parse_release_title,
)
from app.modules.indexer_definitions.schemas.internal import IndexerDefinitionTorrent

FRIEREN_EPISODE_1 = "[SubsPlease] Sousou no Frieren - 01 (1080p) [A].mkv"
FRIEREN_EPISODE_2 = "[SubsPlease] Sousou no Frieren - 02 (1080p) [B].mkv"
FRIEREN_BATCH = "[SubsPlease] Sousou no Frieren S2 (01-10) (1080p) [Batch]"
OTHER_ANIME_EPISODE = "[SubsPlease] Kaiju No. 8 - 01 (1080p) [B].mkv"

FRIEREN_TITLES = {"sousou no frieren"}
FRIEREN_BASE_TITLES = ["sousou no frieren"]


def create_release(name: str, torrent_id: str, seeders: int):
    return (
        name,
        IndexerDefinitionTorrent(
            torrent_id=torrent_id,
            download_url=f"https://nyaa.si/download/{torrent_id}.torrent",
            seeders=seeders,
        ),
    )


def create_definition(releases: list, queried: list[str] | None = None):
    definition = NyaaIndexerDefinition()

    async def fake_search(query: str, release_group: str):
        _ = release_group
        if queried is not None:
            queried.append(query)
        return releases

    definition._search = fake_search

    return definition


def search_release_group(definition: NyaaIndexerDefinition, queries: list[str]):
    return asyncio.run(
        definition._search_release_group(
            "SubsPlease",
            queries,
            FRIEREN_TITLES,
            FRIEREN_BASE_TITLES,
        )
    )


def test_releases_without_seeders_are_dropped():
    """
    A 0 seederes torrent nem játszható le.

    A TorrentSourceProvider viszont minden visszaadott torrenthez letölti a
    .torrent fájlt, ezért itt kell kiszűrni - nem a stream szűrőben.
    """
    definition = create_definition(
        [
            create_release(FRIEREN_EPISODE_1, "1", 0),
            create_release(FRIEREN_EPISODE_2, "2", 7),
        ]
    )

    torrents = search_release_group(definition, ["sousou no frieren"])

    assert [torrent.torrent_id for torrent in torrents] == ["2"]


def test_unrelated_releases_are_dropped():
    definition = create_definition(
        [
            create_release(FRIEREN_EPISODE_1, "1", 5),
            create_release(OTHER_ANIME_EPISODE, "2", 5),
        ]
    )

    torrents = search_release_group(definition, ["sousou no frieren"])

    assert [torrent.torrent_id for torrent in torrents] == ["1"]


def test_query_loop_stops_at_first_matching_variant():
    """A címváltozatok ugyanarra az animére mutatnak, ezért az első találat elég."""
    queried: list[str] = []
    definition = create_definition(
        [create_release(FRIEREN_EPISODE_1, "1", 5)],
        queried,
    )

    search_release_group(definition, ["sousou no frieren", "frieren"])

    assert queried == ["sousou no frieren"]


def test_query_loop_continues_while_there_is_no_match():
    queried: list[str] = []
    definition = create_definition([], queried)

    search_release_group(definition, ["sousou no frieren", "frieren"])

    assert queried == ["sousou no frieren", "frieren"]


def test_only_japanese_animation_counts_as_anime():
    assert _is_anime_meta({"genres": ["Animation", "Action"], "country": "Japan"})

    # Nyugati rajzfilm: animáció, de nem anime
    assert not _is_anime_meta(
        {"genres": ["Animation", "Comedy"], "country": "United States"}
    )

    # Élőszereplős japán sorozat
    assert not _is_anime_meta({"genres": ["Drama"], "country": "Japan"})
    assert not _is_anime_meta({})


BLEACH_TITLES = {"bleach", "bleach sennen kessen hen"}
BLEACH_TYBW_RELEASE = (
    "[Erai-raws] Bleach: Sennen Kessen Hen - Soukoku Tan - 14 [1080p][MultiSub]"
)


def match_release(release_name: str, titles: set[str], strict: bool):
    definition = NyaaIndexerDefinition()
    release_title = _normalize(_parse_release_title(release_name))

    return definition._matches(release_title, titles, sorted(titles), strict=strict)


def test_sequel_is_not_served_for_the_original_series():
    """
    A Bleach és a Bleach: Sennen Kessen-hen egy IMDb azonosító alá tartozik.

    Az évad ismeretében csak a kért sorozat kiadásait fogadjuk el, különben az
    eredeti sorozat 14. epizódja helyett a folytatásét kapná a felhasználó.
    """
    assert not match_release(BLEACH_TYBW_RELEASE, {"bleach"}, strict=True)

    # A folytatás saját évadánál viszont pont ez a kiadás kell
    assert match_release(
        BLEACH_TYBW_RELEASE,
        {"bleach sennen kessen hen soukoku tan"},
        strict=True,
    )


def test_season_marker_still_matches_in_strict_mode():
    """Az évad-jelölő nem tehet különbséget: "Frieren S2" = "Frieren"."""
    assert match_release(
        "[SubsPlease] Sousou no Frieren S2 - 10 (1080p) [A].mkv",
        {"sousou no frieren"},
        strict=True,
    )
    assert match_release(
        "[Erai-raws] Mairimashita Iruma-kun 4th Season - 17 [1080p][MultiSub]",
        {"mairimashita iruma kun"},
        strict=True,
    )


def test_without_season_the_looser_matching_is_kept():
    """Évad nélkül (pl. film) marad a régi, megengedőbb illesztés."""
    assert match_release(BLEACH_TYBW_RELEASE, BLEACH_TITLES, strict=False)


def test_season_entries_are_selected_by_tvdb_season():
    entries = [
        _AnimeEntry(
            anilist_id=269, entry_type="TV", tvdb_season=1, tvdb_episode_offset=None
        ),
        _AnimeEntry(
            anilist_id=116674, entry_type="TV", tvdb_season=17, tvdb_episode_offset=None
        ),
    ]

    selected = NyaaIndexerDefinition._select_season_entries(entries, 1)
    assert [entry.anilist_id for entry in selected] == [269]

    selected = NyaaIndexerDefinition._select_season_entries(entries, 17)
    assert [entry.anilist_id for entry in selected] == [116674]

    # Évad nélkül mindent visszaadunk
    assert len(NyaaIndexerDefinition._select_season_entries(entries, None)) == 2


def test_entries_without_season_data_are_used_as_fallback():
    """
    A Fribb listában az eredeti sorozatnál gyakran hiányzik az évad.

    A Bleach alapsorozatának nincs évadszáma, a Sennen Kessen-hen évadai
    viszont 17-esként szerepelnek - az 1. évadra így is az alapsorozat kell.
    """
    original = _AnimeEntry(
        anilist_id=269, entry_type="TV", tvdb_season=None, tvdb_episode_offset=None
    )
    sequel = _AnimeEntry(
        anilist_id=116674, entry_type="TV", tvdb_season=17, tvdb_episode_offset=None
    )

    selected = NyaaIndexerDefinition._select_season_entries([original, sequel], 1)
    assert [entry.anilist_id for entry in selected] == [269]

    selected = NyaaIndexerDefinition._select_season_entries([original, sequel], 17)
    assert [entry.anilist_id for entry in selected] == [116674]


def create_rate_limited_response(retry_after: str | None = None):
    headers = {"Retry-After": retry_after} if retry_after else {}
    request = httpx.Request("GET", "https://nyaa.si/download/1.torrent")
    return httpx.Response(
        httpx.codes.TOO_MANY_REQUESTS,
        headers=headers,
        request=request,
    )


def download_with_responses(monkeypatch, responses: list):
    """A super().download_torrent() helyett a megadott válaszokat adja vissza."""
    definition = NyaaIndexerDefinition()
    calls = {"count": 0}
    delays: list[float] = []

    async def fake_download(self, download_url: str):
        _ = self, download_url
        result = responses[calls["count"]]
        calls["count"] += 1
        if isinstance(result, BaseException):
            raise result
        return result

    async def fake_sleep(delay: float):
        delays.append(delay)

    monkeypatch.setattr(
        "app.modules.indexer_definitions.base_indexer_definition."
        "BaseIndexerDefinition.download_torrent",
        fake_download,
    )
    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    return definition, calls, delays


def test_rate_limited_download_is_retried(monkeypatch):
    """
    A 429 nem hiba, hanem várni kell.

    Enélkül a rate limitre futó kiadások némán hiányoznának a listából.
    """
    rate_limited = httpx.HTTPStatusError(
        "429",
        request=httpx.Request("GET", "https://nyaa.si/download/1.torrent"),
        response=create_rate_limited_response(),
    )
    definition, calls, delays = download_with_responses(
        monkeypatch,
        [rate_limited, rate_limited, b"torrent-bytes"],
    )

    result = asyncio.run(definition.download_torrent("/download/1.torrent"))

    assert result == b"torrent-bytes"
    assert calls["count"] == 3
    # Növekvő várakozás a próbálkozások között
    assert delays == [1.5, 3.0]


def test_retry_after_header_is_respected(monkeypatch):
    rate_limited = httpx.HTTPStatusError(
        "429",
        request=httpx.Request("GET", "https://nyaa.si/download/1.torrent"),
        response=create_rate_limited_response(retry_after="4"),
    )
    definition, _, delays = download_with_responses(
        monkeypatch,
        [rate_limited, b"torrent-bytes"],
    )

    asyncio.run(definition.download_torrent("/download/1.torrent"))

    assert delays == [4.0]


def test_non_rate_limit_errors_are_not_retried(monkeypatch):
    not_found = httpx.HTTPStatusError(
        "404",
        request=httpx.Request("GET", "https://nyaa.si/download/1.torrent"),
        response=httpx.Response(
            httpx.codes.NOT_FOUND,
            request=httpx.Request("GET", "https://nyaa.si/download/1.torrent"),
        ),
    )
    definition, calls, _ = download_with_responses(monkeypatch, [not_found])

    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(definition.download_torrent("/download/1.torrent"))

    assert calls["count"] == 1


def test_release_title_is_extracted_from_release_name():
    assert _parse_release_title(FRIEREN_EPISODE_1) == "Sousou no Frieren"

    # Erai-raws: a címben is van kötőjel, az epizódszám a legutolsó
    assert (
        _parse_release_title(
            "[Erai-raws] Mushoku Tensei III - Isekai Ittara Honki Dasu - 04 "
            "[1080p CR WEB-DL AVC AAC][MultiSub][63594405].mkv"
        )
        == "Mushoku Tensei III - Isekai Ittara Honki Dasu"
    )

    # Batch kiadás: nincs epizódszám
    assert _parse_release_title(FRIEREN_BATCH) == "Sousou no Frieren S2"
