# PyKap

KAP (Public Disclosure Platform) Documentation Wrapper for Capital Markets Board of Turkey and Borsa Istanbul Public Disclosures.


### Installation

```sh
pip install pykap
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
get_bist_companies() # default output format is pandas df (can be json or dict, as well)
```


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
