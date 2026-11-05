# Data dictionary: City of Winnipeg Business Licenses

Source: City of Winnipeg Open Data, dataset `d5k3-sfzx`. Figures computed from snapshot `api_20261104` (13,825 rows, snapshot date 2026-11-04) by `src/build_data_dictionary.py`.

**City definitions:** the portal publishes no description for any of the 13 fields. Definitions below are this project's working definitions, based on field names, observed values and the dataset description.

**Sensitivity** (this project's proposed classification, not the City's):

- **Public**: safe to publish row by row.
- **Sensitive**: could identify an individual or a home. Publish aggregated counts only.

Personal project on public data. Not affiliated with or endorsed by the City of Winnipeg.

## Summary

| field                           | API type      | sensitivity   |   blank % |   distinct | quality dimensions                  |
|:--------------------------------|:--------------|:--------------|----------:|-----------:|:------------------------------------|
| folder_type                     | text          | Public        |       0   |          4 | Validity; Consistency               |
| folder_description              | text          | Public        |       0   |          4 | Consistency                         |
| subdescription                  | text          | Public        |       0   |         18 | Validity; Consistency; Completeness |
| trade_name                      | text          | Sensitive     |       0   |        275 | Completeness; Uniqueness            |
| address                         | text          | Sensitive     |      79.8 |        345 | Completeness; Consistency; Validity |
| issue_date                      | calendar_date | Public        |       0   |       3175 | Validity; Consistency               |
| expiry_date                     | calendar_date | Public        |       0   |       2460 | Validity; Timeliness                |
| status                          | text          | Public        |       0   |         10 | Validity; Timeliness; Accuracy      |
| neighbourhood_number            | number        | Public        |       0   |        126 | Validity; Consistency               |
| neighbourhood_name              | text          | Public        |       0   |        125 | Consistency                         |
| electoral_ward                  | text          | Public        |       0   |         16 | Consistency; Timeliness             |
| community_characterization_area | text          | Public        |       0   |         13 | Consistency                         |
| location                        | text          | Sensitive     |      80.5 |        329 | Completeness; Accuracy              |

## Fields

### `folder_type`

Two-letter code for the licence family.

- **Names:** CSV `Folder Type`, API `folder_type` (text)
- **Format rule:** One of LP, LQ, LR, LX. Each code maps to exactly one folder_description.
- **Sensitivity:** Public
- **Blank:** 0 rows (0.0%)  |  **Distinct:** 4
- **Observed:** LX (11,039); LP (1,670); LQ (1,051); LR (65)
- **Known issues:** No published code list; meanings come only from folder_description.
- **Quality dimensions:** Validity; Consistency

### `folder_description`

Label for the licence family (for example 'License - Personal Sales').

- **Names:** CSV `Folder Description`, API `folder_description` (text)
- **Format rule:** One label per folder_type.
- **Sensitivity:** Public
- **Blank:** 0 rows (0.0%)  |  **Distinct:** 4
- **Observed:** License - Rooming Houses (11,039); License - Personal Sales (1,670); License - Personal Services (1,051); License - Residential (65)
- **Known issues:** Uses US spelling 'License'; the City's by-law and this project use 'Licence'.
- **Quality dimensions:** Consistency

### `subdescription`

The licensed activity (for example 'Used Goods Dealer', 'Converted Residential Dwelling').

- **Names:** CSV `Subdescription`, API `subdescription` (text)
- **Format rule:** Each activity belongs to exactly one licence family.
- **Sensitivity:** Public
- **Blank:** 0 rows (0.0%)  |  **Distinct:** 18
- **Observed:** Converted Residential Dwelling (8,254); Converted Residential Dwelling with Shared Facilities (2,726); Used Goods Dealer (888); Body Rub Practitioner (836); Precious Metal Dealer (466); Body Modification Establishment (157); Used Material Yard (112); Antique Dealer (69); Hostel (65); Temporary Trade Show (63); Shared Facility Dwelling (58); Flea Market (32); Body Rub Parlour (31); Bicycle Dealer (25); Auctioneer (15); Escort (15); Independent Escort Agency (12); Rooming House (1)
- **Known issues:** Portal description says the City licenses 12 activities; the data holds more, including historical ones. Personal services (LQ) and residential (LR) have no licences issued after 2021. The April 2026 extract held 8 activities; November holds 18.
- **Quality dimensions:** Validity; Consistency; Completeness

### `trade_name`

Operating name of the licensee, when one is registered.

- **Names:** CSV `Trade Name`, API `trade_name` (text)
- **Format rule:** Never blank. '(none)' means no trade name.
- **Sensitivity:** Sensitive: for personal services (LQ), a trade name may identify an individual (NEEDS EVIDENCE). Public for other families.
- **Blank:** 0 rows (0.0%)  |  **Distinct:** 275
- **Observed:** (values not listed: sensitive)
- **Check on this snapshot:** '(none)' placeholder: 12,186 rows
- **Known issues:** '(none)' is a placeholder rather than a true blank, so missing names do not show up as missing. Not unique and cannot identify a business on its own.
- **Quality dimensions:** Completeness; Uniqueness

### `address`

Civic address of the licensed premises (project working definition; no City definition published).

- **Names:** CSV `Address`, API `address` (text)
- **Format rule:** Street number, street name, suffix. Blank only where withheld.
- **Sensitivity:** Sensitive: withheld by the City for rooming houses (LX); published for personal services (LQ), where it may be a home address (NEEDS EVIDENCE); public for business premises (LP, LR).
- **Blank:** 11,038 rows (79.8%)  |  **Distinct:** 345
- **Observed:** (values not listed: sensitive)
- **Check on this snapshot:** blank, by family: LX 11,038
- **Known issues:** Blank for every rooming house record, which looks like deliberate redaction, but no redaction policy is published (NEEDS EVIDENCE). Redaction is inconsistent across families. Street suffixes are not standardized (AVE, ST, Broadway, RD).
- **Quality dimensions:** Completeness; Consistency; Validity

### `issue_date`

Date the licence was issued.

- **Names:** CSV `Issue Date`, API `issue_date` (calendar_date)
- **Format rule:** Valid date. CSV export: 'YYYY Mon DD HH:MM:SS AM'. API: ISO 8601. Stored here as YYYY-MM-DD.
- **Sensitivity:** Public
- **Blank:** 0 rows (0.0%)  |  **Distinct:** 3,175
- **Observed:** 2010-01-04 to 2026-10-30
- **Check on this snapshot:** expiry before issue: 400 rows
- **Known issues:** Some records have an expiry date earlier than the issue date. Format differs between CSV export and API.
- **Quality dimensions:** Validity; Consistency

### `expiry_date`

Date the licence stops being valid.

- **Names:** CSV `Expiry Date`, API `expiry_date` (calendar_date)
- **Format rule:** Valid date, on or after issue_date.
- **Sensitivity:** Public
- **Blank:** 0 rows (0.0%)  |  **Distinct:** 2,460
- **Observed:** 2007-12-31 to 2027-11-24
- **Check on this snapshot:** expired before 2026-11-04: 13,156 rows
- **Known issues:** Expiry before issue on some records (see issue_date). Basis of the 'not expired' test in the downtown funnel.
- **Quality dimensions:** Validity; Timeliness

### `status`

Current lifecycle status of the licence.

- **Names:** CSV `Status`, API `status` (text)
- **Format rule:** One of the observed status values.
- **Sensitivity:** Public
- **Blank:** 0 rows (0.0%)  |  **Distinct:** 10
- **Observed:** Closed (L) (12,790); Issued (628); Ceased Operation (274); Cancelled (118); Converted (4); Approved - New (L) (3); Vacant (3); Converted to Duplex (3); New Application (1); Converted to SFD (1)
- **Check on this snapshot:** 'Issued' but expired before 2026-11-04: 1 row
- **Known issues:** Meaning of the '(L)' suffix is not published (NEEDS EVIDENCE). Only the current status is kept, with no status history. In April 2026, 1,655 records said 'Issued' after their expiry date; in November, 1.
- **Quality dimensions:** Validity; Timeliness; Accuracy

### `neighbourhood_number`

City neighbourhood code.

- **Names:** CSV `Neighbourhood Number`, API `neighbourhood_number` (number)
- **Format rule:** Text code in the form D.DDD (for example 3.170). Must keep all three decimals.
- **Sensitivity:** Public
- **Blank:** 0 rows (0.0%)  |  **Distinct:** 126
- **Observed:** 126 distinct values (not listed)
- **Check on this snapshot:** not in D.DDD format (blanks excluded): 3 rows
- **Known issues:** Published as a number, so trailing zeros can be lost: '3.17' instead of '3.170'. 398 rows in the April extract and 3 in November (CRESTVIEW appears as both 2.21 and 2.210).
- **Quality dimensions:** Validity; Consistency

### `neighbourhood_name`

City neighbourhood name.

- **Names:** CSV `Neighbourhood Name`, API `neighbourhood_name` (text)
- **Format rule:** One name per neighbourhood_number.
- **Sensitivity:** Public
- **Blank:** 0 rows (0.0%)  |  **Distinct:** 125
- **Observed:** 125 distinct values (not listed)
- **Check on this snapshot:** names with more than one code: 1
- **Known issues:** One-to-one with neighbourhood_number except where the code lost its trailing zero. Spelling differs from the City's neighbourhood boundary file in places (for example 'PORTAGE- ELLICE' versus 'Portage-Ellice'), so joins need names normalized.
- **Quality dimensions:** Consistency

### `electoral_ward`

City Council electoral ward.

- **Names:** CSV `Electoral Ward`, API `electoral_ward` (text)
- **Format rule:** One of the City's ward names.
- **Sensitivity:** Public
- **Blank:** 0 rows (0.0%)  |  **Distinct:** 16
- **Observed:** Daniel McIntyre (4,240); Fort Rouge - East Fort Garry (2,925); Mynarski (2,330); Point Douglas (1,611); St Boniface (1,588); River Heights - Fort Garry (251); Elmwood - East Kildonan (190); St Vital (177); St James (160); Transcona (127); North Kildonan (58); Old Kildonan (56); Charleswood - Tuxedo - Westwood (49); St Norbert - Seine River (36); Waverley West (14); St James - Brooklands - Weston (13)
- **Check on this snapshot:** neighbourhoods under more than one ward name: 1
- **Known issues:** POLO PARK appears under two ward names ('St James' and 'St James - Brooklands - Weston'), possibly a ward boundary or name change over time (NEEDS EVIDENCE). Not stated whether the ward is as of the licence date or today.
- **Quality dimensions:** Consistency; Timeliness

### `community_characterization_area`

City planning area. Its 'Downtown' value covers downtown and surrounding neighbourhoods; this project's definition of downtown comes from CentrePlan 2050 instead (decision D-010).

- **Names:** CSV `Community Characterization Area`, API `community_characterization_area` (text)
- **Format rule:** One of the observed area names.
- **Sensitivity:** Public
- **Blank:** 0 rows (0.0%)  |  **Distinct:** 13
- **Observed:** Downtown (5,849); Point Douglas (2,462); St Boniface (1,592); West End (1,540); River Heights (1,210); River East (248); St James Assiniboia (222); St Vital (180); Inkster (146); Transcona (127); Seven Oaks (116); Fort Garry (101); Assiniboine South (32)
- **Known issues:** Not stated whether the area is as of the licence date or today. 'Downtown' here is much wider than the CentrePlan 2050 downtown (see metadata/downtown_definitions.csv). Neighbourhoods with no licence records never appear, so the data alone cannot list which neighbourhoods an area contains.
- **Quality dimensions:** Consistency

### `location`

Map point for the address, as longitude and latitude.

- **Names:** CSV `Location`, API `location` (text)
- **Format rule:** WKT text 'POINT (longitude latitude)'.
- **Sensitivity:** Sensitive: same as address, since it is precise enough to locate a building.
- **Blank:** 11,124 rows (80.5%)  |  **Distinct:** 329
- **Observed:** (values not listed: sensitive)
- **Check on this snapshot:** address present but no point: 86 rows
- **Known issues:** Blank wherever address is blank, plus some records that have an address but no point.
- **Quality dimensions:** Completeness; Accuracy
