# PyKap

KAP (Public Disclosure Platform) Documentation Wrapper for Capital Markets Board of Turkey and Borsa Istanbul Public Disclosures.


### Installation

```sh
pip install pykap # currently not an option
```

From the repository:
```sh
pip install git+https://gitlab.com/cemsinan/PyKap.git
```


### Usage

#### To list all of the BIST Companies

```python
from pykap.bist_company_list import bist_company_list
bist_company_list()
```

#### Get General Info for all of the BIST Companies

```python
from pykap.get_bist_companies import get_bist_companies
get_bist_companies(online = False, output_format = 'pandas_df')
```
Default output format is pandas df (can be json or dict, as well). 

`online` mode enables to get the most up-to-date company list from KAP's website. 
However, it takes time to parse. It is suggested to use `online=False`, unless otherwise is necessary.  


#### Get General Info for a specific company

```python
from pykap.get_general_info import get_general_info
get_general_info(tick='AKBNK')
```


#### BISTCompany Class:

```python
from pykap.bist import BISTCompany
comp = BISTCompany(ticker='BIMAS') # initialize a BISTCompany object
```
When A BISTCompany object is initialized, some general information attributes (`ticker`, `name`, `summary_page`, `city`, `auditor`) get filled for this company.

##### Get Expected Disclosures List:

```python
comp.get_expected_disclosure_list(count=10)
```

##### Get Historical Disclosures List:

```python
# "4028328c594bfdca01594c0af9aa0057" #for 'finansal rapor'
report_type="4028328d594c04f201594c5155dd0076" #for "faliyet raporu"       
comp.get_historical_disclosure_list(fromdate = "2020-05-21", todate="2021-05-21",disclosure_type="FR", subject=report_type)
```

##### Save Operating Review Report PDF File:

```python
cmp.save_operating_review()
```

Check your current directory for saved pdf document.
