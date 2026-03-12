from __future__ import annotations

import io

from bs4 import BeautifulSoup
import requests
import json
import pandas as pd
import pkgutil


def get_bist_companies(online: bool = False, output_format: str = 'pandas_df', **kwargs) -> pd.DataFrame | str | list:
    """Fetch the list of BIST-listed companies.

    By default (``online=False``) the function returns data from the bundled
    JSON snapshot shipped with the package, which avoids a network request.
    When ``online=True`` the data is scraped live from the KAP website and any
    extra keyword arguments are forwarded to :func:`_get_bist_companies`.

    Args:
        online: When ``False`` (default) use bundled data; when ``True``
            scrape live from KAP.
        output_format: Controls the return type.  Accepted values:

            - ``'pandas_df'`` — returns a :class:`pandas.DataFrame` (default)
            - ``'json'`` — returns a JSON-formatted string
            - ``'dict'`` — returns a plain Python list of dicts
        **kwargs: Additional keyword arguments forwarded to
            :func:`_get_bist_companies` when ``online=True``.

    Returns:
        Company data in the format specified by ``output_format``.
    """
    if(online==False):
        bist_list = pkgutil.get_data(__name__, "data/bist_companies_general.json")
        if(output_format=='pandas_df'):
            return pd.read_json(io.StringIO(bist_list.decode('utf-8')))
        else:
            data = json.loads(bist_list)
            if(output_format=='dict'):
                return data
            elif(output_format=='json'):
                return json.dumps(data, ensure_ascii=False, indent=4)
    elif(online==True):
        return _get_bist_companies(output_format=output_format, **kwargs)


def _get_bist_companies(
    output_format: str = 'pandas_df',
    local_jsoncopy: bool = False,
) -> pd.DataFrame | str | list | None:
    """Scrape the live BIST company list from KAP.

    Fetches the KAP BIST companies page and extracts company data (including
    ``company_id``) from the embedded Next.js server-side data.  Returns
    results in the requested format and optionally writes a local JSON copy.

    Args:
        output_format: Controls the return type.  Accepted values:

            - ``'pandas_df'`` — returns a :class:`pandas.DataFrame` (default)
            - ``'json'`` — returns a JSON-formatted string
            - ``'dict'`` — returns a plain Python list of dicts
        local_jsoncopy: When ``True``, write the scraped data to
            ``./bist_companies_general.json`` in the current working directory.

    Returns:
        Company data in the format specified by ``output_format``, or ``None``
        if ``output_format`` is not a recognised value.
    """
    import re as _re

    try:
        r = requests.get('https://www.kap.org.tr/tr/bist-sirketler', timeout=30)
        r.raise_for_status()
    except requests.RequestException as e:
        raise ConnectionError(f"Failed to fetch BIST company list from KAP: {e}")

    soup = BeautifulSoup(r.text, 'html5lib')
    scripts = soup.find_all('script')
    big_script = max(scripts, key=lambda s: len(s.string or ''))
    raw_js = big_script.string or ''

    match = _re.search(r'self\.__next_f\.push\(\[1,(\".*\")\]\)\s*$', raw_js, _re.DOTALL)
    if not match:
        raise ValueError("Could not find company data in KAP page. The site structure may have changed.")

    content = json.loads(match.group(1))

    pattern = _re.compile(
        r'"mkkMemberOid":"([^"]+)","kapMemberTitle":"([^"]+)",'
        r'"relatedMemberTitle":"([^"]+)","stockCode":"([^"]+)","cityName":"([^"]+)"'
    )

    companies = []
    seen: set = set()
    for m in pattern.finditer(content):
        company_id, name, auditor, stock_codes, city = m.groups()
        for ticker in [t.strip() for t in stock_codes.split(',')]:
            if ticker and ticker not in seen:
                seen.add(ticker)
                companies.append({
                    'ticker': ticker,
                    'name': name,
                    'summary_page': f'https://www.kap.org.tr/tr/sirket/{ticker}',
                    'city': city,
                    'auditor': auditor,
                    'company_id': company_id,
                })

    companies.sort(key=lambda c: c['ticker'])
    companies_json = json.dumps(companies, indent=4, ensure_ascii=False)

    if local_jsoncopy:
        with open('./bist_companies_general.json', 'w', encoding='utf-8') as f:
            json.dump(companies, f, ensure_ascii=False, indent=4)

    if output_format == 'pandas_df':
        return pd.read_json(io.StringIO(companies_json))
    elif output_format == 'json':
        return companies_json
    elif output_format == 'dict':
        return companies


def get_mkkMemberOid(surl: str) -> str:
    """Fetch the MKK member OID (company_id) from the company's KAP summary page.

    Args:
        surl: Full URL of the company's KAP summary page.

    Returns:
        The MKK member OID string extracted from the company logo ``src``
        attribute on the summary page.
    """
    try:
        g = requests.get(url=surl, timeout=30)
        g.raise_for_status()
    except requests.RequestException as e:
        raise ConnectionError(f"Failed to fetch company summary page at {surl}: {e}")
    soup = BeautifulSoup(g.text, 'html5lib')
    logo = soup.select('img.comp-logo')
    if not logo:
        raise ValueError(f"Could not find company logo/ID at {surl}")
    cid = logo[0]['src'].split('/')[-1]
    return cid
