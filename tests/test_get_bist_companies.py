from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

import pandas as pd

from pykap.get_bist_companies import get_bist_companies

MINIMAL_COMPANIES = [
    {
        'ticker': 'THYAO',
        'name': 'Türk Hava Yolları',
        'summary_page': 'https://www.kap.org.tr/tr/sirket/123',
        'city': 'İstanbul',
        'auditor': 'KPMG',
    }
]

MINIMAL_JSON_BYTES = json.dumps(MINIMAL_COMPANIES, ensure_ascii=False).encode('utf-8')

# Minimal Next.js streaming HTML that mimics the KAP site's embedded company data
_COMPANY_DATA = json.dumps([
    {"mkkMemberOid": "abc123", "kapMemberTitle": "Türk Hava Yolları",
     "relatedMemberTitle": "KPMG", "stockCode": "THYAO", "cityName": "İstanbul",
     "relatedMemberOid": "aud001", "kapMemberType": "IGS"}
], ensure_ascii=False, separators=(',', ':'))
MINIMAL_HTML = (
    '<html><body>'
    '<script>self.__next_f.push([1,'
    + json.dumps(
        f'4:["$","div",null,{{"children":["$L3a",null,{{"data":'
        f'[{{"code":"T","content":{_COMPANY_DATA}}}]}}]}}]'
    )
    + '])</script>'
    '</body></html>'
)


def test_get_bist_companies_offline_returns_dataframe():
    """With online=False and output_format='pandas_df', should return a DataFrame."""
    with patch('pkgutil.get_data', return_value=MINIMAL_JSON_BYTES):
        result = get_bist_companies(online=False, output_format='pandas_df')
    assert isinstance(result, pd.DataFrame)
    assert 'ticker' in result.columns


def test_get_bist_companies_offline_returns_dict():
    """With online=False and output_format='dict', should return a list of dicts."""
    with patch('pkgutil.get_data', return_value=MINIMAL_JSON_BYTES):
        result = get_bist_companies(online=False, output_format='dict')
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]['ticker'] == 'THYAO'


def test_get_bist_companies_offline_returns_json():
    """With online=False and output_format='json', should return a JSON string."""
    with patch('pkgutil.get_data', return_value=MINIMAL_JSON_BYTES):
        result = get_bist_companies(online=False, output_format='json')
    assert isinstance(result, str)
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert parsed[0]['ticker'] == 'THYAO'


def test_get_bist_companies_online_calls_requests():
    """With online=True, should scrape the KAP page and return data."""
    mock_response = MagicMock()
    mock_response.text = MINIMAL_HTML
    mock_response.raise_for_status = MagicMock()

    with patch('pykap.get_bist_companies.requests.get', return_value=mock_response) as mock_get:
        result = get_bist_companies(online=True, output_format='dict')

    mock_get.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]['ticker'] == 'THYAO'
    assert result[0]['name'] == 'Türk Hava Yolları'
    assert result[0]['city'] == 'İstanbul'
    assert result[0]['auditor'] == 'KPMG'
    assert result[0]['company_id'] == 'abc123'
    assert result[0]['summary_page'] == 'https://www.kap.org.tr/tr/sirket/THYAO'
