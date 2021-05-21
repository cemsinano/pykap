###from pykap.pykap import get_general_info ### ??????

#import pykap.get_general_info as ggi
from pykap.get_general_info import get_general_info
import requests
import json

class BISTCompany(object):
    """
    BIST Company class to store company related fields.
    """

    def __init__(self, ticker):
        self.ticker = ticker
        #self._get_general_info()
        general_info = get_general_info(tick=self.ticker)
        self.name=general_info['name']
        self.summary_page = general_info['summary_page']
        self.city = general_info['city']
        self.auditor = general_info['auditor']
        self.company_id = general_info['company_id']
        self.financial_reports = dict()

    def get_financial_report(self, ):
        return 'bla'

    def get_expected_disclosure_list(self, count=5):
        data = {"mkkMemberOidList": [self.company_id], "count": str(count)}
        response = requests.post(url="https://www.kap.org.tr/tr/api/memberExpectedDisclosure", json=data)
        return json.loads(response.text)

    def get_historical_disclosure_list(self, fromdate = "2020-05-21", todate="2021-05-21",disclosure_type="FR"):
        data = {
            "fromDate": fromdate,
            "toDate": todate,
            "year": "", "prd": "",
            "term": "", "ruleType": "",
            "bdkReview": "",
            "disclosureClass": disclosure_type,
            "index": "", "market": "",
            "isLate": "", "subjectList": [],
            "mkkMemberOidList": [self.company_id],
            "inactiveMkkMemberOidList": [],
            "bdkMemberOidList": [],
            "mainSector": "", "sector": "",
            "subSector": "", "memberType": "IGS",
            "fromSrc": "N", "srcCategory": "",
            "discIndex": []}
        response = requests.post(url="https://www.kap.org.tr/tr/api/memberDisclosureQuery", json=data)
        return json.loads(response.text)

