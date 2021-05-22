###from pykap.pykap import get_general_info ### ??????

#import pykap.get_general_info as ggi
from pykap.get_general_info import get_general_info
import requests
import json
from bs4 import BeautifulSoup
import regex as re
import pandas as pd
from datetime import datetime,timedelta




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

    def get_historical_disclosure_list(self, fromdate = datetime.today().date() - timedelta(days = 365), todate=datetime.today().date(),disclosure_type="FR", subject ="4028328c594bfdca01594c0af9aa0057"):
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
        response = requests.post(url="https://www.kap.org.tr/tr/api/memberDisclosureQuery", json=data)
        return json.loads(response.text)

    def get_financial_reports(self):
        fin_reports = dict()
        disclosurelist = self.get_historical_disclosure_list()
        for disclosure in disclosurelist:
            period = str(disclosure['year']) + disclosure['ruleTypeTerm'].replace(" ", "")
            # fin_reports['period'] = str(disclosure['year']) + disclosure['ruleTypeTerm'].replace(" ", "")
            fin_reports[period] = dict()
            fin_reports[period]['year'] = disclosure['year']
            fin_reports[period]['term'] = disclosure['ruleTypeTerm']
            fin_reports[period]['disc_ind'] = disclosure['disclosureIndex']
            self.announcement_no = fin_reports[period]['disc_ind']
            fin_reports[period]['results'] = self._get_announcement()
        self.financial_reports = fin_reports
        return fin_reports

    def _get_announcement(self, announcement_no ='846388' ,lang='tr'):
        anurl = "https://www.kap.org.tr/"+ lang +"/Bildirim/" + str(self.announcement_no)

        r = requests.get(anurl)
        #s = BeautifulSoup(r.text, 'html5lib')
        #all_firms = s.find_all(class_='w-clearfix w-inline-block comp-row')

        #r = requests.get('https://www.kap.org.tr/tr/Bildirim/846388')
        soup = BeautifulSoup(r.text, 'html5lib')
        #soup = BeautifulSoup(currPage.text, 'html.parser')

        for part in soup.find_all('h1'):
            if re.search("Finansal Rapor.*", part.text):
                #reportType = "Finansal Rapor"
                #stockName = soup.find('div', {"class": "type-medium type-bold bi-sky-black"})
                #stockCode = soup.find('div', {"class": "type-medium bi-dim-gray"})
                #year = ""
                #period = ""

                '''
                for p in soup.find_all('div', {"class": "w-col w-col-3 modal-briefsumcol"}):
                    for y in p.find_all('div', {"type-small bi-lightgray"}):
                        if y.text == "Yıl":
                            year = y.find_next('div').text
                            #print("year: ", year)
                        if y.text == "Periyot":
                            period = y.find_next('div').text
                            if period == "Yıllık":
                                period = "12"
                            elif period == "9 Aylık":
                                period = "09"
                            elif period == "6 Aylık":
                                period = "06"
                            elif period == "3 Aylık":
                                period = "03"
                            #print("period: ", period)
                '''


                #colName = year + period
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


