from __future__ import annotations

from .get_bist_companies import get_bist_companies
import pandas as pd


def bist_company_list(online: bool = False) -> list[str]:
    """Return list of all BIST ticker symbols.

    Uses bundled data by default; pass ``online=True`` to fetch live from KAP.

    Args:
        online: When ``False`` (default) return tickers from the bundled JSON
            snapshot.  When ``True`` scrape the current list from KAP.

    Returns:
        A list of ticker symbol strings (e.g. ``['THYAO', 'AKBNK', ...]``).
    """
    if online:
        c_dict = get_bist_companies(online=True, output_format='dict')
    else:
        c_dict = get_bist_companies(online=False, output_format='dict')

    ticker_list = [c['ticker'] for c in c_dict]
    return ticker_list
