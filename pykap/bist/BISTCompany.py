###from pykap.pykap import get_general_info ### ??????

#import pykap.get_general_info as ggi
from pykap.get_general_info import get_general_info

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
