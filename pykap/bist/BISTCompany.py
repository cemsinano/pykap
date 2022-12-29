###from pykap.pykap import get_general_info ### ??????

#import pykap.get_general_info as ggi
from pykap.get_general_info import get_general_info
import requests
import json
from bs4 import BeautifulSoup
import regex as re
import pandas as pd
from datetime import datetime,timedelta
import os




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
        self.output_dir = None



    def get_expected_disclosure_list(self, count=5):
        data = {"mkkMemberOidList": [self.company_id], "count": str(count)}
        response = requests.post(url="https://www.kap.org.tr/tr/api/memberExpectedDisclosure", json=data)
        return json.loads(response.text)

    def get_historical_disclosure_list(self, fromdate = datetime.today().date() - timedelta(days = 365), todate=datetime.today().date(),disclosure_type="FR", subject = 'financial report'):
        """ Get historical disclosure list.
        args:
            ...
            subject (str):
                4028328d594c04f201594c5155dd0076 is 'operating review' "faliyet raporu"
                4028328c594bfdca01594c0af9aa0057 is 'financial report' 'finansal rapor'

        """
        if(subject == '4028328d594c04f201594c5155dd0076' or subject =='operating review'):
            subjectno = '4028328d594c04f201594c5155dd0076'
        elif(subject == '4028328c594bfdca01594c0af9aa0057' or subject =='financial report'):
            subjectno = '4028328c594bfdca01594c0af9aa0057'
        else:
            raise ValueError('Provide a valid subject!')


        data = {
            "fromDate": str(fromdate),
            "toDate": str(todate),
            "year": "", "prd": "",
            "term": "", "ruleType": "",
            "bdkReview": "",
            "disclosureClass": disclosure_type,
            "index": "", "market": "",
            "isLate": "", "subjectList": [subjectno],
            "mkkMemberOidList": [self.company_id],
            "inactiveMkkMemberOidList": [],
            "bdkMemberOidList": [],
            "mainSector": "", "sector": "",
            "subSector": "", "memberType": "IGS",
            "fromSrc": "N", "srcCategory": "",
            "discIndex": []}
        response = requests.post(url="https://www.kap.org.tr/tr/api/memberDisclosureQuery", json=data)
        return json.loads(response.text)

    def get_financial_reports(self, fromdate = datetime.today().date() - timedelta(days = 365), todate=datetime.today().date()):
        fin_reports = dict()
        disclosurelist = self.get_historical_disclosure_list(fromdate = fromdate, todate=todate)  # subject has FINANCIAL REPORT as default FOR NOW!!!
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

    def _get_announcement(self, announcement_no ='846388' ,lang='tr'):
        anurl = "https://www.kap.org.tr/"+ lang +"/Bildirim/" + str(self.__announcement_no)

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


    def save_operating_review(self, output_dir='OperatingReviews', fromdate = datetime.today().date() - timedelta(days = 365), todate=datetime.today().date()):
        #self.__path=path # for now save to the current directory
        oper_reports = dict()
        disclist = self.get_historical_disclosure_list(fromdate=fromdate, todate=todate, subject="4028328d594c04f201594c5155dd0076")
        self.output_dir = output_dir
        for disclosure in disclist:
            period = str(disclosure['year']) + disclosure['ruleTypeTerm'].replace(" ", "")
            self.__orperiod = period
            # fin_reports['period'] = str(disclosure['year']) + disclosure['ruleTypeTerm'].replace(" ", "")
            oper_reports[period] = dict()
            oper_reports[period]['year'] = disclosure['year']
            oper_reports[period]['term'] = disclosure['ruleTypeTerm']
            oper_reports[period]['disc_ind'] = disclosure['disclosureIndex']
            self.__announcement_no = oper_reports[period]['disc_ind']
            oper_reports[period]['filename'] = self._save_operating_report_file()
        self.operating_reports = oper_reports
        self.__announcement_no = None


    def _save_operating_report_file(self,lang='tr'):
        anurl = "https://www.kap.org.tr/"+ lang +"/Bildirim/" + str(self.__announcement_no)

        r = requests.get(anurl)
        soup = BeautifulSoup(r.text, 'html5lib')
        pdf_report_link = soup.select('a.modal-attachment.type-xsmall.bi-sky-black.maximize')
        url = 'https://www.kap.org.tr' + pdf_report_link[0]['href']

        with requests.Session() as req:
            r = req.get(url)
            if r.status_code == 200 and r.headers['Content-Type'] == "application/pdf":
                name = self.name.replace(' ', '').replace('.','') + "_" + self.__orperiod

                #name = r.url[name:]
                print(f"Saving {name}.pdf")
                file_name = name+'.pdf'
                if self.output_dir == 'OperatingReviews':
                    outpath = "OperatingReviews"
                else:
                    outpath = self.output_dir
                completeName = os.path.join(outpath, file_name)
                if not os.path.exists(outpath):
                    os.makedirs(outpath)
                with open(f"{completeName}", 'wb') as f:
                    f.write(r.content)
                print(f"Saved to {outpath} directory.")
                return file_name


