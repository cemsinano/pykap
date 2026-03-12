from __future__ import annotations

from .get_bist_companies import get_bist_companies


def get_general_info(tick: str, online: bool = False) -> dict | None:
    """Return general info dict for a company by ticker, or None if not found.

    Looks up the company identified by ``tick`` in the BIST company list and
    returns the corresponding metadata dictionary.

    Args:
        tick: The ticker symbol to look up (e.g. ``'THYAO'``).
        online: When ``True``, fetch live data from KAP instead of using the
            bundled snapshot.  Defaults to ``False``.

    Returns:
        A dict with the following keys if the ticker is found:

        - ``ticker`` — ticker symbol
        - ``name`` — company name
        - ``summary_page`` — URL of the KAP company summary page
        - ``city`` — city where the company is registered
        - ``auditor`` — name of the auditing firm

        Returns ``None`` if ``tick`` is not present in the company list.
    """
    c_dict = get_bist_companies(online=online, output_format='dict')
    if tick in [c['ticker'] for c in c_dict]:
        return list(filter(lambda d: d['ticker'] in [tick], c_dict))[0]
    else:
        return None
