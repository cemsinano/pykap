from pykap.get_bist_companies import get_bist_companies

def bist_company_list(online=False):
    if online:
        c_dict = get_bist_companies(online = True, output_format='dict')
    else:
        c_dict = get_bist_companies(online = False,output_format='dict') 

    ticker_list = [c['ticker'] for c in c_dict]
    return ticker_list