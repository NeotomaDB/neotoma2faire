# Test fixtures

## `downloads_24.json`

A pinned response from `GET https://api.neotomadb.org/v2.0/data/downloads/24`.

The fixture currently in this folder was written as a **stub** because the
sandbox that generated it could not reach the live Neotoma API. To replace it
with a real snapshot, run the helper script from the repo root:

```bash
uv run python -c "
import json, urllib.request
url = 'https://api.neotomadb.org/v2.0/data/downloads/24'
body = json.loads(urllib.request.urlopen(url, timeout=30).read())
with open('tests/fixtures/downloads_24.json', 'w') as f:
    json.dump(body, f, indent=2)
print('refreshed')
"
```

Re-run the test suite afterwards. Snapshot tests that compare against the
`.xlsx` deliverable will need to be regenerated when the fixture changes —
see `tests/test_make_template_e2e.py` (created in Week 1, Day 6).
