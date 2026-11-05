# Getting the data

Raw data is not stored in this repository. It is public, but some licence
types (personal services) include addresses and names that may relate to
individuals, so this project publishes code and count-only reports only.

You need two snapshots in `data/raw/`:

**1. November 2026 snapshot (primary dataset), via the City's open data API**

```
python src/ingest_api.py
```

This creates `data/raw/api_YYYYMMDD/` with the records and a metadata file.
A new pull gives today's data, so your numbers will differ from the reports
in this repo, which were produced from the 2026-11-04 pull.

**2. April 2026 extract (baseline), from an earlier project**

Download `Business_Licenses_20260404.csv` from
[downtown-winnipeg-transition-analysis/data](https://github.com/rynetroy/downtown-winnipeg-transition-analysis/tree/main/data)
into `data/raw/`. Expected SHA-256:

```
45C90B0BB569EA5E1D63442FAE7F1CBE3EE99B24265B383FBAE92D7F4E6F341E
```

**3. Neighbourhood boundaries (for the map)**

On data.winnipeg.ca, open the Neighbourhood dataset, export it as CSV and save it as
`data/raw/geo_neighbourhoods_csv/Neighbourhoods_YYYYMMDD.csv`. The copy used for the
reports in this repo was exported 2026-11-04. Expected SHA-256:

    9AD3531E484B789627B8369193997EC5FD149A6394D5370F276167273F8ADF1F

Source: City of Winnipeg Open Data, Business Licenses (dataset `d5k3-sfzx`).
This is a personal project on public data, not affiliated with or endorsed
by the City of Winnipeg.
