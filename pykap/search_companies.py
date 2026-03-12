from __future__ import annotations
import requests


def search_companies(query: str) -> list[dict]:
    """Search BIST companies by name or ticker keyword using KAP's search API.

    Args:
        query: Search keyword (company name or ticker symbol).

    Returns:
        List of matching company dicts with keys: name, ticker, company_id.

    Raises:
        ConnectionError: If the KAP API cannot be reached.
    """
    try:
        response = requests.post(
            "https://www.kap.org.tr/tr/api/search/combined",
            json={"keyword": query},
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise ConnectionError(f"Failed to reach KAP search API: {e}")

    data = response.json()

    # The API returns a list of category objects; find the companyOrFunds category
    company_or_funds = []
    for category_obj in data:
        if category_obj.get("category") == "companyOrFunds":
            company_or_funds = category_obj.get("results", [])
            break

    return [
        {
            "name": item["searchValue"],
            "ticker": item["cmpOrFundCode"].upper(),
            "company_id": item["memberOrFundOid"],
        }
        for item in company_or_funds
        if item.get("searchType") == "C"
    ]
