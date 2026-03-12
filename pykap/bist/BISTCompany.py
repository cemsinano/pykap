from __future__ import annotations

import datetime

from pykap.get_general_info import get_general_info
import requests
import json
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime as _datetime, timedelta


class BISTCompany(object):
    """Represents a BIST-listed company and wraps KAP API calls.

    Fetches company metadata from the KAP (Public Disclosure Platform) API on
    initialisation and exposes methods for retrieving disclosure lists,
    financial reports, and operating-review PDFs for that company.
    """

    def __init__(self, ticker: str) -> None:
        """Initialize BISTCompany by fetching company metadata from KAP for the given ticker."""
        self.ticker = ticker
        general_info = get_general_info(tick=self.ticker)
        if general_info is None:
            raise ValueError(f"Ticker '{ticker}' not found in BIST company list.")
        self.name = general_info['name']
        self.summary_page = general_info['summary_page']
        self.city = general_info['city']
        self.auditor = general_info['auditor']
        self.company_id = general_info['company_id']
        self.financial_reports = dict()

    def get_expected_disclosure_list(self, count: int = 5) -> list:
        """Fetch the list of upcoming expected disclosures for this company.

        Args:
            count: Number of expected disclosures to retrieve.

        Returns:
            A list of dicts, each describing an expected disclosure event.
        """
        data = {"mkkMemberOidList": [self.company_id], "count": str(count)}
        try:
            response = requests.post(url="https://www.kap.org.tr/tr/api/memberExpectedDisclosure", json=data, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to fetch expected disclosures for {self.ticker}: {e}")
        return json.loads(response.text)

    def get_historical_disclosure_list(
        self,
        fromdate: datetime.date = _datetime.today().date() - timedelta(days=365),
        todate: datetime.date = _datetime.today().date(),
        disclosure_type: str = "FR",
        subject: str = "4028328c594bfdca01594c0af9aa0057",
    ) -> list:
        """Fetch the historical disclosure list for this company.

        Args:
            fromdate: Start date of the query window (inclusive).
            todate: End date of the query window (inclusive).
            disclosure_type: KAP disclosure class code (e.g. ``"FR"`` for
                financial reports).
            subject: UUID identifying the disclosure subject on KAP.
                Known values:

                - ``"4028328c594bfdca01594c0af9aa0057"`` — finansal rapor
                  (financial report)
                - ``"4028328d594c04f201594c5155dd0076"`` — faaliyet raporu
                  (operating review)

        Returns:
            A list of dicts, each describing a historical disclosure entry.
        """
        data = {
            "fromDate": str(fromdate),
            "toDate": str(todate),
            "year": "", "prd": "",
            "term": "", "ruleType": "",
            "bdkReview": "",
            "disclosureClass": disclosure_type,
            "index": "", "market": "",
            "isLate": "", "subjectList": [subject],
            "mkkMemberOidList": [self.company_id],
            "inactiveMkkMemberOidList": [],
            "bdkMemberOidList": [],
            "mainSector": "", "sector": "",
            "subSector": "", "memberType": "IGS",
            "fromSrc": "N", "srcCategory": "",
            "discIndex": []}
        try:
            response = requests.post(url="https://www.kap.org.tr/tr/api/memberDisclosureQuery", json=data, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to fetch historical disclosures for {self.ticker}: {e}")
        return json.loads(response.text)

    def get_financial_reports(self) -> dict:
        """Fetch and parse all available financial report data for this company.

        Returns:
            A dict keyed by period string (e.g. ``'2023Yıllık'``), where each
            value is a dict containing ``year``, ``term``, ``disc_ind``, and
            ``results`` (the parsed financial line items).
        """
        fin_reports = dict()
        disclosurelist = self.get_historical_disclosure_list()  # subject has FINANCIAL REPORT as default FOR NOW!!!
        for disclosure in disclosurelist:
            period = str(disclosure['year']) + disclosure['ruleTypeTerm'].replace(" ", "")
            # fin_reports['period'] = str(disclosure['year']) + disclosure['ruleTypeTerm'].replace(" ", "")
            fin_reports[period] = dict()
            fin_reports[period]['year'] = disclosure['year']
            fin_reports[period]['term'] = disclosure['ruleTypeTerm']
            fin_reports[period]['disc_ind'] = disclosure['disclosureIndex']
            self.__announcement_no = fin_reports[period]['disc_ind']
            fin_reports[period]['results'] = self._get_announcement()
        self.financial_reports = fin_reports
        self.__announcement_no = None
        return fin_reports

    def _get_announcement(self, lang: str = 'tr') -> dict | None:
        """Parse financial statement data from a KAP announcement page.

        Args:
            lang: Language code used in the KAP URL (default ``'tr'``).

        Returns:
            A dict mapping line item names to their values, or ``None`` if the
            announcement page does not contain a financial report.
        """
        anurl = "https://www.kap.org.tr/" + lang + "/Bildirim/" + str(self.__announcement_no)

        try:
            r = requests.get(anurl, timeout=30)
            r.raise_for_status()
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to fetch announcement {self.__announcement_no}: {e}")
        soup = BeautifulSoup(r.text, 'html5lib')

        for part in soup.find_all('h1'):
            if re.search("Finansal Rapor.*", part.text):
                colName = 'col'
                cols = [colName]

                str3 = '.*_role_.*data-input-row.*presentation-enabled'
                trTagClass = re.compile(str3)

                labelClass = "gwt-Label multi-language-content content-tr"
                currDataClass = re.compile("taxonomy-context-value.*")

                df = pd.DataFrame(columns=cols)

                i = 0
                hitTa = 0
                hitFy = 0
                lst = set()

                for EachPart in soup.find_all('tr', {"class": trTagClass}):
                    for ep in EachPart.find_all(True, {"class": labelClass}):
                        label = ep.get_text()
                        label = label.strip(' \n\t')

                        if label == "Ticari Alacaklar":
                            hitTa = hitTa + 1
                            if hitTa == 2:
                                label = "Ticari Alacaklar1"

                        if label == "Finansal Yatırımlar":
                            hitFy = hitFy + 1
                            if hitFy == 2:
                                label = "Finansal Yatırımlar1"

                        df.rename(index={i: label}, inplace=True)

                        res = EachPart.find('td', {"class": currDataClass})
                        if res is None:
                            continue
                        value = res.text
                        value = value.strip(' \n\t')
                        if not lst.__contains__(label):
                            lst.add(label)
                            if value:
                                df.loc[label, colName] = float(value.replace('.', '').replace(',', '.'))
                            else:
                                df.loc[label, colName] = value
                            i = i + 1
                df = df.replace('', 0)
                return pd.DataFrame.to_dict(df)[colName]

    def save_operating_review(self) -> None:
        """Download and save all operating review (faaliyet raporu) PDFs for this company to the current directory."""
        oper_reports = dict()
        disclist = self.get_historical_disclosure_list(subject="4028328d594c04f201594c5155dd0076")
        for disclosure in disclist:
            period = str(disclosure['year']) + disclosure['ruleTypeTerm'].replace(" ", "")
            self.__orperiod = period
            oper_reports[period] = dict()
            oper_reports[period]['year'] = disclosure['year']
            oper_reports[period]['term'] = disclosure['ruleTypeTerm']
            oper_reports[period]['disc_ind'] = disclosure['disclosureIndex']
            self.__announcement_no = oper_reports[period]['disc_ind']
            oper_reports[period]['filename'] = self._save_operating_report_file()
        self.operating_reports = oper_reports
        self.__announcement_no = None

    def _save_operating_report_file(self, lang: str = 'tr') -> str | None:
        """Download a single operating review PDF and save it to the current directory.

        Args:
            lang: Language code used in the KAP URL (default ``'tr'``).

        Returns:
            The filename of the saved PDF, or ``None`` if the file could not be
            downloaded.
        """
        anurl = "https://www.kap.org.tr/" + lang + "/Bildirim/" + str(self.__announcement_no)

        try:
            r = requests.get(anurl, timeout=30)
            r.raise_for_status()
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to fetch announcement {self.__announcement_no}: {e}")
        soup = BeautifulSoup(r.text, 'html5lib')
        pdf_report_link = soup.select('a.modal-attachment.type-xsmall.bi-sky-black.maximize')
        if not pdf_report_link:
            raise ValueError(f"No PDF attachment found for announcement {self.__announcement_no}")
        url = 'https://www.kap.org.tr' + pdf_report_link[0]['href']

        with requests.Session() as req:
            r = req.get(url, timeout=30)
            if r.status_code == 200 and r.headers['Content-Type'] == "application/pdf":
                name = self.name.replace(' ', '').replace('.', '') + "_" + self.__orperiod

                print(f"Saving {name}.pdf")
                file_name = name + '.pdf'
                try:
                    with open(f"{name}.pdf", 'wb') as f:
                        f.write(r.content)
                except IOError as e:
                    raise IOError(f"Failed to write PDF file '{file_name}': {e}")
                print(f"Saved to the current directory.")
                return file_name
