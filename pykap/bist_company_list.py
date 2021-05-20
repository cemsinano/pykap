from .get_bist_companies import get_bist_companies

def bist_company_list():
    c_dict = get_bist_companies(output_format='dict')
    #print(c_dict)
    ticker_list = [c['ticker'] for c in c_dict]
    return ticker_list