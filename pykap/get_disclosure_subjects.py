from __future__ import annotations
import requests

VALID_DISCLOSURE_CLASSES = {"FR", "ODA", "DG"}


def get_disclosure_subjects(disclosure_class: str = "FR") -> list[dict]:
    """Fetch available disclosure subjects for a given disclosure class.

    Args:
        disclosure_class: Class code. Known values: 'FR', 'ODA', 'DG'.

    Returns:
        List of dicts with keys: disclosureClass, subject, subjectOid.

    Raises:
        ConnectionError: If the KAP API cannot be reached.
        ValueError: If an invalid disclosure_class is provided.
    """
    if disclosure_class not in VALID_DISCLOSURE_CLASSES:
        raise ValueError(
            f"Invalid disclosure_class '{disclosure_class}'. "
            f"Must be one of: {sorted(VALID_DISCLOSURE_CLASSES)}"
        )

    try:
        response = requests.get(
            f"https://www.kap.org.tr/tr/api/disclosure/subjects/{disclosure_class}/IGS",
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise ConnectionError(f"Failed to reach KAP disclosure subjects API: {e}")

    return response.json()
