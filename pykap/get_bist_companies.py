from bs4 import BeautifulSoup
import requests
import json
import pandas as pd


'''
firms_dict =dict()
for firm in all_firms:
    ticker = firm.select('div.comp-cell._04.vtable a.vcell')[0].text
    firms_dict[ticker] = {'ticker': ticker}
    name = firm.select('div.comp-cell._14.vtable a.vcell')[0].text
    firms_dict[ticker]['name'] = name
    for link in firm.select('div.comp-cell._04.vtable a.vcell[href]'):
        summary_page = "https://www.kap.org.tr" + link['href']
    firms_dict[ticker]['summary_page'] = summary_page
    city = firm.select('div.comp-cell._12.vtable div.vcell')[0].text
    firms_dict[ticker]['city'] = city
    auditor = firm.select('div.comp-cell._11.vtable a.vcell')[0].text
    firms_dict[ticker]['auditor'] = auditor
    
pd.DataFrame.from_dict(firms_dict,orient = 'index') 
'''

def get_bist_companies(output_format = 'pandas_df'):
    """
    output_format: 'pandas_df' or 'json' or 'dict'
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
    companies_json = json.dumps(companies_dict['companies'],indent = 4, ensure_ascii=False)
    #try:

    if (output_format == 'pandas_df'):
        output_companies=pd.read_json(companies_json)
        return output_companies
    elif (output_format == 'json'):
        return companies_json
    elif (output_format == 'dict'):
        return companies_dict['companies']

    #except:
    #    print("An exception occurred")


# def bist_company_list():
#     c_dict = get_bist_companies(output_format='dict')
#     #print(c_dict)
#     ticker_list = [c['ticker'] for c in c_dict]
#     return ticker_list
#
# def get_general_info(tick):
#     tick_list = bist_company_list() # save it don't call again and again...
#     c_dict = get_bist_companies(output_format='dict')
#     if (tick in tick_list):
#        return list(filter(lambda d: d['ticker'] in [tick], c_dict))[0]


