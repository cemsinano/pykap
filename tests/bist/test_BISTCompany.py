from __future__ import annotations

import json
import pytest
from unittest.mock import patch, MagicMock

from pykap.bist.BISTCompany import BISTCompany

MOCK_GENERAL_INFO = {
    'ticker': 'THYAO',
    'name': 'Türk Hava Yolları',
    'summary_page': 'https://www.kap.org.tr/tr/sirket/123',
    'city': 'İstanbul',
    'auditor': 'KPMG',
    'company_id': 'abc123',
}


@pytest.fixture
def thyao(request):
    """Return a BISTCompany('THYAO') with get_general_info mocked out."""
    with patch('pykap.bist.BISTCompany.get_general_info', return_value=MOCK_GENERAL_INFO):
        company = BISTCompany('THYAO')
    return company


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

def test_init_sets_attributes():
    """__init__ should set all attributes from the general-info dict."""
    with patch('pykap.bist.BISTCompany.get_general_info', return_value=MOCK_GENERAL_INFO):
        company = BISTCompany('THYAO')

    assert company.ticker == 'THYAO'
    assert company.name == 'Türk Hava Yolları'
    assert company.summary_page == 'https://www.kap.org.tr/tr/sirket/123'
    assert company.city == 'İstanbul'
    assert company.auditor == 'KPMG'
    assert company.company_id == 'abc123'
    assert company.financial_reports == {}


def test_init_raises_for_unknown_ticker():
    """__init__ should raise ValueError when get_general_info returns None."""
    with patch('pykap.bist.BISTCompany.get_general_info', return_value=None):
        with pytest.raises(ValueError, match="UNKNOWN"):
            BISTCompany('UNKNOWN')


# ---------------------------------------------------------------------------
# get_expected_disclosure_list
# ---------------------------------------------------------------------------

def test_get_expected_disclosure_list(thyao):
    """Should POST to the KAP API and return a list parsed from JSON."""
    mock_payload = [{'type': 'FR', 'date': '2024-01-01'}]
    mock_response = MagicMock()
    mock_response.text = json.dumps(mock_payload)
    mock_response.raise_for_status = MagicMock()

    with patch('pykap.bist.BISTCompany.requests.post', return_value=mock_response) as mock_post:
        result = thyao.get_expected_disclosure_list(count=3)

    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args
    assert call_kwargs.kwargs['json']['mkkMemberOidList'] == ['abc123']
    assert call_kwargs.kwargs['json']['count'] == '3'
    assert isinstance(result, list)
    assert result[0]['type'] == 'FR'


# ---------------------------------------------------------------------------
# get_historical_disclosure_list
# ---------------------------------------------------------------------------

def test_get_historical_disclosure_list(thyao):
    """Should POST to the KAP API and return a list parsed from JSON."""
    mock_payload = [{'disclosureIndex': 99, 'year': 2023, 'ruleTypeTerm': 'Yıllık'}]
    mock_response = MagicMock()
    mock_response.text = json.dumps(mock_payload)
    mock_response.raise_for_status = MagicMock()

    with patch('pykap.bist.BISTCompany.requests.post', return_value=mock_response) as mock_post:
        result = thyao.get_historical_disclosure_list()

    mock_post.assert_called_once()
    assert isinstance(result, list)
    assert result[0]['disclosureIndex'] == 99


# ---------------------------------------------------------------------------
# get_financial_reports
# ---------------------------------------------------------------------------

def test_get_financial_reports(thyao):
    """Should build a dict keyed by period using disclosure list and _get_announcement."""
    minimal_disclosures = [
        {'disclosureIndex': 42, 'year': 2023, 'ruleTypeTerm': 'Yıllık'},
    ]
    mock_financial_data = {'Nakit': 1000.0, 'Borç': 500.0}

    with patch.object(thyao, 'get_historical_disclosure_list', return_value=minimal_disclosures), \
            patch.object(thyao, '_get_announcement', return_value=mock_financial_data):
        result = thyao.get_financial_reports()

    assert isinstance(result, dict)
    assert '2023Yıllık' in result
    period = result['2023Yıllık']
    assert period['year'] == 2023
    assert period['term'] == 'Yıllık'
    assert period['disc_ind'] == 42
    assert period['results'] == mock_financial_data
