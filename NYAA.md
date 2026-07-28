# Nyaa.si indexer (SubsPlease / Erai-raws)

Anime indexer for stremhu-source, plus the parsing and cleanup changes it needs
to actually produce streams.

| File | Change |
| --- | --- |
| `server/app/modules/indexer_definitions/integrations/nyaa.py` | the indexer (new) |
| `server/app/modules/torrent_streams/utils/series_parser.py` | anime season+episode naming |
| `server/app/modules/indexer_definitions/base_indexer_definition.py` | `supports_hit_and_run` property |
| `server/app/modules/indexers/service.py` | honour it during cleanup |
| `server/tests/` | anime fixtures + cleanup rule tests |

## Using it

Build from this repo (`docker compose build`), then add **Nyaa** under indexers
in the web UI. It is a public tracker, so `_login` only checks that nyaa.si is
reachable — **any username and password works**.

## How the IMDb lookup works

`_fetch_torrents()` receives only an IMDb ID and nyaa knows nothing about IMDb,
so the integration resolves the mapping itself:

| Step | Source | Cached |
| --- | --- | --- |
| `tt…` → AniList IDs (per season, with TVDB season + episode offset) | [Fribb/anime-lists](https://github.com/Fribb/anime-lists) | `data/cache/nyaa_anime_index.json`, 7 days |
| AniList ID → romaji / English title + synonyms | AniList GraphQL | in memory, 7 days |
| fallback when the anime is not in the list | Cinemeta | in memory, 7 days |
| search results | nyaa RSS | in memory, 10 min |

Queries are built from the **official titles only** (romaji and English). The
subtitle after `:` and any season markers are stripped and the result is capped
at 6 words, because nyaa's search ANDs its terms together — the full
*Saikyou Degarashi Ouji no Anyaku Teii Arasoi: Munou wo Enjiru…* title returns
nothing, and the English *Mushoku Tensei: Jobless Reincarnation* returns nothing
because the releases are romaji. Synonyms are used to filter results, never to
search: they are what makes *Detective Conan* findable when AniList's romaji is
*Meitantei Conan*.

Results come from nyaa's RSS feed (`?page=rss&c=1_2&f=0&u=<group>`), which
carries seeders, infohash and category, restricted to **Anime –
English-translated** and to the `SubsPlease` and `Erai-raws` uploaders. Every
hit is re-checked against the known titles, capped at 75 torrents per show
(the source provider downloads a `.torrent` for each one).

Resolution, source and codec are parsed downstream from the release name.
Language is passed as an `eng` fallback attribute, since the names carry no
language token.

## Season markers in `series_parser.py`

Whether a stream reaches the client is decided by `SeriesParser`, which the
indexer cannot influence. Before this change, every release whose name carried
an explicit season marker was dropped: the parser consumed the season and
returned no episode. `4th Season - 17` was worse — it read *season 17*.

Two patterns fix it, anchored to shapes that only appear in anime naming
(`clean_torrent_name()` collapses `" - "` to a space before the parser runs, so
these arrive as `s2 10` and `4th season 17`):

| Pattern | Handles | Before | After |
| --- | --- | --- | --- |
| `PATTERN_SEASON_EPISODE_PAIR` | `Show S4 - 17` | `s=[4] e=[]` | `s=[4] e=[17]` |
| `PATTERN_ORDINAL_SEASON_EPISODE` | `Show 4th Season - 17` | `s=[17] e=[]` | `s=[4] e=[17]` |
| `PATTERN_ORDINAL_SEASON` | `Show 4th Season [Batch]` | `s=[17]` | `s=[4]` |

The trailing `(?![\d-])` guard and the 3-digit cap on the episode number are
what keep season packs safe: without them `Show S01 001-100` would look like a
single episode, and `StreamFileResolver`'s exact-episode shortcut would hand
back the pack's largest file for every episode request. `S01 (01-24)`,
`S01 Part 2`, `S01 1080p WEB-DL` and `4. évad` are all left alone — verified
against 150 live releases from both groups plus scene and Hungarian names: 36
changes, all anime, all corrections, and **no existing snapshot changed**.

## Cleanup: seed timer instead of Hit'n'Run

Nyaa has no Hit'n'Run rules, so `_fetch_hit_and_run_ids()` returns an empty
list — and `find_for_cleanup()` reads an empty list as "no torrent needs
keeping". With no `keep_seed_seconds` set it then applies **no filter at all**,
deleting every non-persisted torrent of that indexer at the nightly cleanup.

`BaseIndexerDefinition.supports_hit_and_run` (default `True`) now guards this.
Nyaa returns `False`, so `cleanup_torrent_by_rules()` skips the Hit'n'Run list
entirely and only the seed timer can remove its torrents:

| Setting | Result for nyaa |
| --- | --- |
| Hit'n'Run on, no timer | nothing is deleted |
| Hit'n'Run on, 7 day timer | deleted 7 days after last playback |
| per-account 3 day timer | deleted 3 days after last playback |

The other indexers are unaffected — they inherit `True`. Set the timer globally
in the UI under *Automatikus torrent törlés*, or per-indexer via
`PUT /api/indexers/nyaa` with `{"keepSeedSeconds": 259200}`.

## Not handled: absolute numbering

`[SubsPlease] Detective Conan - 1208` parses as `s=[12] e=[8]`, so
absolute-numbered long-runners (Conan, One Piece) return nothing. Fixing it
means translating the requested season/episode into the absolute number using
the `tvdb_season` / `tvdb_episode_offset` fields — already parsed into
`_AnimeEntry` from Fribb's list and currently unused. The obstacle is that
`StreamFileResolver` receives a `SeriesInfo` but no IMDb ID, so the mapping is
not reachable from where the decision is made.
