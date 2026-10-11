#!/usr/bin/env python3
"""Fetch every queued image into the store, as a reference copy with its credit.

    python3 tools/fetch_queue.py prairie-1904            # fetch what fetch-results.json lacks
    python3 tools/fetch_queue.py prairie-1904 --retry    # and retry the ones that failed

Reads <collection>/fetch-queue.json (written in kevinrhaas/chicago from the library's records)
and writes, for each entry, <collection>/files/<id>.jpg (long side <= its max, JPEG q80) and
<id>-thumb.jpg (<= 400 px), the same derivatives chicago/prairie_1904_v1/tools/fetch_image.py
makes, then records the outcome in <collection>/fetch-results.json: the `local` block the
record takes, or the error. The original is never kept; its URL is where it lives.

Why it runs here (in this repository's Actions) and not beside the records: the owner asked on
2026-10-11 that the photographs the library only links (chicagology and other sites) be brought
in with their attribution so every building is checked against them, and the sessions that
build the houses cannot reach those hosts. Each copy is a REFERENCE copy: kept so a build can be
compared with the picture, credited wherever it is shown, never made into a texture or traced,
and deleted if its holder asks.
"""
import hashlib, io, json, sys, time, urllib.request
from pathlib import Path
from PIL import Image

Image.MAX_IMAGE_PIXELS = 400_000_000
UA = 'Mozilla/5.0 (compatible; ChicagoBuildingAtlas/1.0; +https://chicago.polecat.live; research reference copies)'


def fetch(url):
    err = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'image/*,*/*;q=0.8'})
            return urllib.request.urlopen(req, timeout=120).read(), None
        except Exception as e:  # noqa: BLE001 — every failure is recorded, none is fatal
            err = f'{type(e).__name__}: {e}'
            time.sleep(2 * 2 ** attempt)
    return None, err


def derive(raw, rid, mx, out):
    im = Image.open(io.BytesIO(raw))
    im.seek(0)
    if im.mode not in ('RGB', 'L'):
        im = im.convert('RGB')
    w, h = im.size
    local = {}
    for name, size, key in ((f'{rid}.jpg', mx, 'display'), (f'{rid}-thumb.jpg', 400, 'thumb')):
        c = im.copy()
        c.thumbnail((size, size), Image.LANCZOS)
        p = out / name
        c.save(p, 'JPEG', quality=80, optimize=True, progressive=True)
        local[key] = 'research/images/files/' + name
        local[key + '_bytes'] = p.stat().st_size
    local.update(original_px=[w, h], original_sha256=hashlib.sha256(raw).hexdigest(),
                 original_bytes=len(raw))
    return local


def main(argv):
    if not argv:
        sys.exit(__doc__)
    col = Path(argv[0])
    queue = json.loads((col / 'fetch-queue.json').read_text())['queue']
    res_file = col / 'fetch-results.json'
    results = json.loads(res_file.read_text()) if res_file.exists() else {}
    out = col / 'files'
    out.mkdir(parents=True, exist_ok=True)
    done = failed = 0
    for q in queue:
        rid = q['id']
        was = results.get(rid)
        if was and (was.get('local') or '--retry' not in argv):
            continue
        raw, err = fetch(q['url'])
        if raw is None:
            results[rid] = {'error': err, 'url': q['url'], 'tried': time.strftime('%Y-%m-%d')}
            failed += 1
            print(f'FAIL {rid}: {err}', flush=True)
            continue
        try:
            local = derive(raw, rid, int(q.get('max') or 1400), out)
        except Exception as e:  # noqa: BLE001 — a page served instead of an image, say
            results[rid] = {'error': f'not an image: {type(e).__name__}: {e}', 'url': q['url'],
                            'tried': time.strftime('%Y-%m-%d'), 'bytes': len(raw)}
            failed += 1
            print(f'FAIL {rid}: not an image', flush=True)
            continue
        local.update(fetched_from=q['url'], fetched=time.strftime('%Y-%m-%d'))
        results[rid] = {'local': local, 'reference_copy': {
            'basis': 'owner, 2026-10-11: reference copy with attribution (kevinrhaas/chicago T-2368)',
            'credit': q.get('credit')}}
        done += 1
        print(f'ok   {rid} {local["original_px"]}', flush=True)
        if done % 20 == 0:
            res_file.write_text(json.dumps(results, indent=1, ensure_ascii=False, sort_keys=True) + '\n')
    res_file.write_text(json.dumps(results, indent=1, ensure_ascii=False, sort_keys=True) + '\n')
    print(f'fetched {done}, failed {failed}, {len(results)} recorded')


if __name__ == '__main__':
    main(sys.argv[1:])
