# Data source exploration

Early exploration notebooks for each API/data source we're pulling from. Each
one hits the live API (or a bulk download, for Form990), and drops the raw
response plus a flattened CSV under that source's `input/`/`output/` folders
so we can see the actual shape of the data before committing to a schema in
`extract/`.

| Folder | Source | Notes |
| --- | --- | --- |
| `Congress/` | [Congress.gov API](https://api.congress.gov/) | Bills, actions, amendments, text versions |
| `FEC/` | [openFEC API](https://api.open.fec.gov/developers/) | Committees, Schedules A/B/E |
| `Form990/` | IRS 990 bulk XML + [ProPublica Nonprofit Explorer API](https://projects.propublica.org/nonprofits/api) | See `extract/irs990_schema_notes.md` for schema quirks found along the way |
| `LDA/` | [Senate LDA API](https://lda.senate.gov/api/) | Filings, registrants, clients, lobbying activities |
| `ProPublica/` | ProPublica Nonprofit Explorer API | Org search/detail, filings |

`utility.py` holds the shared endpoint URLs used across all of these
notebooks. Each notebook expects to be run from its own folder (e.g.
`Congress/`) and reaches one level up for `utility.py`, `my_secrets.py`
(gitignored, local API keys), and the repo-root `.env`.

This is exploratory/reference material, not part of the production pipeline -
the real parsing and extraction logic lives in `extract/`.
