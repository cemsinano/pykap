from bs4 import BeautifulSoup
import requests
import json

def get_bist_companies():
    """
    BIST
    :return:
    """
    r = requests.get('https://www.kap.org.tr/tr/bist-sirketler')
    s = BeautifulSoup(r.text,'html5lib')
    all_firms = s.find_all(class_='w-clearfix w-inline-block comp-row')

    companies_dict = dict({'companies': []})
    for firm in all_firms:
        temp_dic = dict()
        ticker = firm.select('div.comp-cell._04.vtable a.vcell')[0].text
        temp_dic['ticker'] = ticker
        name = firm.select('div.comp-cell._14.vtable a.vcell')[0].text
        temp_dic['name'] = name
        for link in firm.select('div.comp-cell._04.vtable a.vcell[href]'):
            summary_page = "https://www.kap.org.tr" + link['href']
        temp_dic['summary_page'] = summary_page
        city = firm.select('div.comp-cell._12.vtable div.vcell')[0].text
        temp_dic['city'] = city
        auditor = firm.select('div.comp-cell._11.vtable a.vcell')[0].text
        temp_dic['auditor'] = auditor
        companies_dict['companies'].append(temp_dic)
    companies_json = json.dumps(companies_dict['companies'], ensure_ascii=False)

    return companies_json

def companies_list():
    companies = get_bist_companies()
