# PyKap

Python wrapper for [KAP (Kamuyu Aydınlatma Platformu)](https://www.kap.org.tr) — the Public Disclosure Platform for Capital Markets Board of Turkey and Borsa Istanbul (BIST).

## Installation

```sh
pip install pykap
```

## Features

- List all BIST-listed companies (759+ tickers, bundled or live)
- Search companies by name or ticker
- Get company general info (name, city, auditor, company ID)
- Fetch expected and historical disclosure lists
- Fetch disclosures by type (activity reports, corporate governance, sustainability, etc.)
- List available disclosure subjects
- Parse financial statement data from announcements
- Download operating review PDFs

---

## Usage

### List all BIST tickers

```python
import pykap

tickers = pykap.bist_company_list()
# ['A1CAP', 'A1YEN', 'ACSEL', ...]
```

### Get company list

```python
import pykap

# Offline (bundled data, fast — default)
df = pykap.get_bist_companies()                          # pandas DataFrame
companies = pykap.get_bist_companies(output_format='dict')  # list of dicts

# Live from KAP (always up to date)
df = pykap.get_bist_companies(online=True)
```

### Search companies by name or ticker

```python
import pykap

results = pykap.search_companies("Türk Hava")
# [{'name': 'TÜRK HAVA YOLLARI A.O.', 'ticker': 'THYAO', 'company_id': '...'}]

results = pykap.search_companies("AKBNK")
```

### Get general info for a specific company

```python
import pykap

info = pykap.get_general_info(tick='AKBNK')
# {'ticker': 'AKBNK', 'name': '...', 'city': '...', 'auditor': '...', 'company_id': '...', 'summary_page': '...'}
```

### List disclosure subjects

```python
import pykap

# disclosure_class: 'FR' (financial), 'ODA' (material events), 'DG' (other)
subjects = pykap.get_disclosure_subjects('FR')
# [{'disclosureClass': 'FR', 'subject': 'Finansal Rapor', 'subjectOid': '...'}, ...]
```

---

### BISTCompany class

```python
import pykap

comp = pykap.BISTCompany('BIMAS')
# Attributes: ticker, name, city, auditor, summary_page, company_id
```

#### Expected disclosures

```python
comp.get_expected_disclosure_list(count=5)
```

#### Historical disclosures

```python
from datetime import date

comp.get_historical_disclosure_list(
    fromdate=date(2024, 1, 1),
    todate=date(2025, 1, 1),
    disclosure_type="FR",           # disclosure class
    subject="4028328c594bfdca01594c0af9aa0057"  # finansal rapor
)
```

Known subject UUIDs:
- `4028328c594bfdca01594c0af9aa0057` — Finansal Rapor (Financial Report)
- `4028328d594c04f201594c5155dd0076` — Faaliyet Raporu (Activity Report)

#### Disclosures by type

```python
# disclosure_type: 'FAR', 'KYUR', 'SUR', 'KDP', 'DEG'
reports = comp.get_disclosures('FAR')   # Faaliyet Raporu (Activity Reports)
reports = comp.get_disclosures('KYUR')  # Corporate Governance Compliance
reports = comp.get_disclosures('SUR')   # Sustainability Reports
reports = comp.get_disclosures('KDP')   # Dividend Policy
reports = comp.get_disclosures('DEG')   # Valuation Reports

# Each item: title, stockCode, publishDate, disclosureIndex, year, period, summary
print(reports[0]['title'], reports[0]['publishDate'])
```

#### Financial reports (parsed data)

```python
fin = comp.get_financial_reports()
# {'2024Yıllık': {'year': 2024, 'term': 'Yıllık', 'disc_ind': ..., 'results': {...}}, ...}
```

#### Save operating review PDFs

```python
comp.save_operating_review()
# Saves PDFs to the current directory
```

---

## License

MIT © Cem Sinan Ozturk
