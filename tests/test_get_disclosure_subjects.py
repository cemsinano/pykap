from __future__ import annotations

from unittest.mock import patch, MagicMock

import requests
import pytest

from pykap.get_disclosure_subjects import get_disclosure_subjects


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


_SAMPLE_FR_SUBJECTS = [
    {"disclosureClass": "FR", "subject": "Finansal Rapor", "subjectOid": "aaa111"},
    {"disclosureClass": "FR", "subject": "Faaliyet Raporu", "subjectOid": "bbb222"},
    {"disclosureClass": "FR", "subject": "Ara Dönem Faaliyet Raporu", "subjectOid": "ccc333"},
    {"disclosureClass": "FR", "subject": "Sermaye Piyasası Aracı Notu", "subjectOid": "ddd444"},
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_get_disclosure_subjects_returns_list():
    """Should return the raw list of subject dicts from the API."""
    with patch(
        "pykap.get_disclosure_subjects.requests.get",
        return_value=_make_response(_SAMPLE_FR_SUBJECTS),
    ):
        result = get_disclosure_subjects("FR")

    assert isinstance(result, list)
    assert len(result) == 4


def test_get_disclosure_subjects_correct_keys():
    """Each returned dict should contain disclosureClass, subject, and subjectOid."""
    with patch(
        "pykap.get_disclosure_subjects.requests.get",
        return_value=_make_response(_SAMPLE_FR_SUBJECTS),
    ):
        result = get_disclosure_subjects("FR")

    for item in result:
        assert "disclosureClass" in item
        assert "subject" in item
        assert "subjectOid" in item


def test_get_disclosure_subjects_default_class_is_fr():
    """Default disclosure_class argument should be 'FR'."""
    with patch(
        "pykap.get_disclosure_subjects.requests.get",
        return_value=_make_response(_SAMPLE_FR_SUBJECTS),
    ) as mock_get:
        get_disclosure_subjects()

    call_url = mock_get.call_args[0][0]
    assert "/FR/IGS" in call_url


def test_get_disclosure_subjects_calls_correct_url_for_oda():
    """Should construct the correct URL for the ODA class."""
    with patch(
        "pykap.get_disclosure_subjects.requests.get",
        return_value=_make_response([]),
    ) as mock_get:
        get_disclosure_subjects("ODA")

    call_url = mock_get.call_args[0][0]
    assert "/ODA/IGS" in call_url


def test_get_disclosure_subjects_invalid_class_raises_value_error():
    """An unknown class code should raise ValueError before any HTTP call is made."""
    with pytest.raises(ValueError, match="Invalid disclosure_class"):
        get_disclosure_subjects("INVALID")


def test_get_disclosure_subjects_all_valid_classes_accepted():
    """All three documented valid class codes should be accepted without ValueError."""
    for cls in ("FR", "ODA", "DG"):
        with patch(
            "pykap.get_disclosure_subjects.requests.get",
            return_value=_make_response([]),
        ):
            result = get_disclosure_subjects(cls)
        assert isinstance(result, list)


def test_get_disclosure_subjects_network_failure_raises_connection_error():
    """A requests.RequestException should be re-raised as ConnectionError."""
    with patch(
        "pykap.get_disclosure_subjects.requests.get",
        side_effect=requests.RequestException("connection refused"),
    ):
        with pytest.raises(ConnectionError, match="Failed to reach KAP disclosure subjects API"):
            get_disclosure_subjects("FR")
