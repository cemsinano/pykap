from __future__ import annotations

from unittest.mock import patch, call

from pykap.get_general_info import get_general_info

MOCK_COMPANIES = [
    {
        'ticker': 'THYAO',
        'name': 'Türk Hava Yolları',
        'summary_page': 'https://www.kap.org.tr/tr/sirket/123',
        'city': 'İstanbul',
        'auditor': 'KPMG',
    },
    {
        'ticker': 'AKBNK',
        'name': 'Akbank',
        'summary_page': 'https://www.kap.org.tr/tr/sirket/456',
        'city': 'İstanbul',
        'auditor': 'Deloitte',
    },
]


def test_get_general_info_known_ticker():
    """Should return the correct dict for a ticker that exists in the company list."""
    with patch('pykap.get_general_info.get_bist_companies', return_value=MOCK_COMPANIES):
        result = get_general_info('THYAO')
    assert result is not None
    assert result['ticker'] == 'THYAO'
    assert result['name'] == 'Türk Hava Yolları'
    assert result['city'] == 'İstanbul'
    assert result['auditor'] == 'KPMG'


def test_get_general_info_unknown_ticker_returns_none():
    """Should return None when the ticker is not present in the company list."""
    with patch('pykap.get_general_info.get_bist_companies', return_value=MOCK_COMPANIES):
        result = get_general_info('XXXXXX')
    assert result is None


def test_get_general_info_passes_online_flag():
    """The online=True flag should be forwarded to get_bist_companies."""
    with patch('pykap.get_general_info.get_bist_companies', return_value=MOCK_COMPANIES) as mock_gbc:
        get_general_info('THYAO', online=True)
    mock_gbc.assert_called_once_with(online=True, output_format='dict')
