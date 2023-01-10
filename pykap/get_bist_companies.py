from bs4 import BeautifulSoup
import requests
import json
import pandas as pd
import pkgutil

def get_bist_companies(online = False,output_format = 'pandas_df', **kwargs):
    if(online==False):
        bist_list = pkgutil.get_data(__name__, "data/bist_companies_general.json")
        if(output_format=='pandas_df'):
            return pd.read_json(bist_list)
        else:
            data = json.loads(bist_list)
            if(output_format=='dict'):
                return data
            elif(output_format=='json'):
                return json.dumps(data, ensure_ascii=False, indent=4)
    elif(online==True):
        return _get_bist_companies(output_format = output_format, **kwargs)


def _get_bist_companies(output_format = 'pandas_df', add_company_id = False, local_jsoncopy = False):
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
        #for firm in all_firms:
        temp_dic = dict()
        ticker = firm.select('div.comp-cell._04.vtable a.vcell')[0].text
        temp_dic['ticker'] = ticker
        name = firm.select('div.comp-cell._14.vtable a.vcell')[0].text
        temp_dic['name'] = name
        link = firm.select("div.comp-cell._04.vtable a.vcell")[0]
        temp_dic['summary_page'] = "https://www.kap.org.tr" + link['href']
        city = firm.select('div.comp-cell._12.vtable div.vcell')[0].text
        temp_dic['city'] = city
        auditor = firm.select('div.comp-cell._11.vtable a.vcell')[0].text
        temp_dic['auditor'] = auditor

        if add_company_id:
            company_id = get_mkkMemberOid(temp_dic['summary_page'])
            temp_dic['company_id'] = company_id

        companies_dict['companies'].append(temp_dic)

    companies_json = json.dumps(companies_dict['companies'],indent = 4, ensure_ascii=False)
    #try:
    if local_jsoncopy:
        with open('./bist_companies_general.json', 'w', encoding='utf-8') as f:
            json.dump(companies_dict['companies'], f, ensure_ascii=False, indent=4)

    if (output_format == 'pandas_df'):
        output_companies=pd.DataFrame(companies_dict['companies'])
        return output_companies
    elif (output_format == 'json'):
        return companies_json
    elif (output_format == 'dict'):
        return companies_dict['companies']



def get_mkkMemberOid(surl):
    g = requests.get(url=surl)
    soup = BeautifulSoup(g.text, 'html5lib')
    cid = soup.select('img.comp-logo')[0]['src'].split('/')[-1]
    return cid