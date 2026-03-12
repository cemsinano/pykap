from __future__ import annotations

from unittest.mock import patch

from pykap.bist_company_list import bist_company_list

MOCK_COMPANIES = [
    {'ticker': 'THYAO', 'name': 'Türk Hava Yolları', 'summary_page': 'https://www.kap.org.tr/tr/sirket/123', 'city': 'İstanbul', 'auditor': 'KPMG'},
    {'ticker': 'AKBNK', 'name': 'Akbank', 'summary_page': 'https://www.kap.org.tr/tr/sirket/456', 'city': 'İstanbul', 'auditor': 'Deloitte'},
]


def test_bist_company_list_returns_list():
    """bist_company_list() should return a plain Python list of strings."""
    with patch('pykap.bist_company_list.get_bist_companies', return_value=MOCK_COMPANIES):
        result = bist_company_list()
    assert isinstance(result, list)
    assert all(isinstance(t, str) for t in result)


def test_bist_company_list_offline_uses_bundled_data():
    """With online=False (default), requests.get must never be called."""
    with patch('pykap.bist_company_list.get_bist_companies', return_value=MOCK_COMPANIES) as mock_gbc, \
            patch('requests.get') as mock_get:
        bist_company_list(online=False)
    mock_get.assert_not_called()
    mock_gbc.assert_called_once_with(online=False, output_format='dict')


def test_bist_company_list_returns_tickers():
    """The returned list should contain the ticker strings from the mocked data."""
    with patch('pykap.bist_company_list.get_bist_companies', return_value=MOCK_COMPANIES):
        result = bist_company_list()
    assert 'THYAO' in result
    assert 'AKBNK' in result
    assert len(result) == 2
