# chicago-images — the Chicago Building Atlas image store

The image files behind the [Chicago Building Atlas](https://chicago.polecat.live/) research
browsers, served by this repository's own GitHub Pages site at
**https://kevinrhaas.github.io/chicago-images/**. They moved here from
[kevinrhaas/chicago](https://github.com/kevinrhaas/chicago) on 2026-10-02 so the collection can
grow past what that site's 1 GB Pages limit could hold alongside the 4D app.

**This repository holds bytes, not records.** Every file belongs to a record in kevinrhaas/chicago,
which says what it shows, where the original lives (`catalog_url`, `image_url`), who made it, when,
and on what rights basis it may be copied. `MANIFEST.json` in each collection folder lists every file
with its record, source and rights, so nothing here is ever unsourced.

| path | what |
|---|---|
| `prairie-1904/files/<record-id>.jpg` | display derivative, long side ≤ 1400 px (≤ 2000 for maps, plates and drawings) |
| `prairie-1904/files/<record-id>-thumb.jpg` | 400–480 px thumbnail |
| `prairie-1904/MANIFEST.json` | every file → record id, title, source URLs, rights, sha256, bytes — generated |

## Rules

- **Only public-domain or no-known-restrictions items are stored.** Everything else stays a link
  to its holder in the record. The rights basis for each file is in `MANIFEST.json`.
- **Files are written by tools, never by hand.**
  - `chicago/prairie_1904_v1/tools/fetch_image.py` in kevinrhaas/chicago fetches and derives an
    image straight into a clone of this repository, which sits beside the chicago clone.
  - `tools/sync_image_store.py` there writes `MANIFEST.json` here and `research/images/STORE.json`
    there.
- **Nothing is deleted while a record cites it.** A file goes only when its record drops its
  local copy, and the sync tool then reports it as an orphan.
- **Size.** A GitHub Pages site may publish 1 GB. When this one nears that, a second store
  repository is added; the viewer's base URL lives in one place (`STORE.json`).

## Publishing

`.github/workflows/pages.yml` publishes the whole repository to Pages on every push to `main`.
Pages has to be switched on once in the repository settings: **Settings → Pages → Build and
deployment → Source: GitHub Actions**.
