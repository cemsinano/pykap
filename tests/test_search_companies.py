from __future__ import annotations

from unittest.mock import patch, MagicMock

import requests
import pytest

from pykap.search_companies import search_companies


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_response(json_data, status_code=200):
    """Build a mock requests.Response-like object."""
    mock = MagicMock()
    mock.json.return_value = json_data
    mock.status_code = status_code
    mock.raise_for_status = MagicMock()
    return mock


_SAMPLE_API_RESPONSE = [
    {"category": "combined", "results": []},
    {"category": "subjects", "results": []},
    {
        "category": "companyOrFunds",
        "results": [
            {
                "searchValue": "TÜRK HAVA YOLLARI A.O.",
                "searchType": "C",
                "actionKey": "companyFundAction",
                "memberOrFundOid": "4028e4a140f2ed720140f376bebb01a7",
                "subjectOid": None,
                "marketOid": None,
                "discType": None,
                "year": -1,
                "period": -1,
                "cmpOrFundCode": "thyao",
                "indexList": None,
            }
        ],
    },
]

_FUND_API_RESPONSE = [
    {"category": "combined", "results": []},
    {"category": "subjects", "results": []},
    {
        "category": "companyOrFunds",
        "results": [
            {
                "searchValue": "SOME FUND",
                "searchType": "F",   # fund, not company
                "memberOrFundOid": "abc",
                "cmpOrFundCode": "sfnd",
            }
        ],
    },
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_search_companies_returns_filtered_list():
    """Should return a list of company dicts (searchType == 'C') with correct keys."""
    with patch("pykap.search_companies.requests.post", return_value=_make_response(_SAMPLE_API_RESPONSE)):
        result = search_companies("THYAO")

    assert isinstance(result, list)
    assert len(result) == 1
    company = result[0]
    assert company["name"] == "TÜRK HAVA YOLLARI A.O."
    assert company["ticker"] == "THYAO"
    assert company["company_id"] == "4028e4a140f2ed720140f376bebb01a7"


def test_search_companies_ticker_is_uppercased():
    """Ticker should always be returned in uppercase regardless of API casing."""
    with patch("pykap.search_companies.requests.post", return_value=_make_response(_SAMPLE_API_RESPONSE)):
        result = search_companies("thyao")

    assert result[0]["ticker"] == "THYAO"


def test_search_companies_filters_out_funds():
    """Results with searchType != 'C' (e.g. funds) should be excluded."""
    with patch("pykap.search_companies.requests.post", return_value=_make_response(_FUND_API_RESPONSE)):
        result = search_companies("sfnd")

    assert result == []


def test_search_companies_empty_results():
    """Should return an empty list when companyOrFunds has no results."""
    empty_response = [
        {"category": "combined", "results": []},
        {"category": "subjects", "results": []},
        {"category": "companyOrFunds", "results": []},
    ]
    with patch("pykap.search_companies.requests.post", return_value=_make_response(empty_response)):
        result = search_companies("XYZNOTFOUND")

    assert result == []


def test_search_companies_missing_category_returns_empty():
    """If the companyOrFunds category is absent from the response, return empty list."""
    sparse_response = [
        {"category": "combined", "results": []},
    ]
    with patch("pykap.search_companies.requests.post", return_value=_make_response(sparse_response)):
        result = search_companies("anything")

    assert result == []


def test_search_companies_network_failure_raises_connection_error():
    """A requests.RequestException should be re-raised as ConnectionError."""
    with patch(
        "pykap.search_companies.requests.post",
        side_effect=requests.RequestException("timeout"),
    ):
        with pytest.raises(ConnectionError, match="Failed to reach KAP search API"):
            search_companies("THYAO")
