from .get_bist_companies import get_bist_companies
from .bist_company_list import bist_company_list


def get_general_info(tick, online=False):
    tick_list = bist_company_list(online=online) # save it don't call again and again...
    c_dict = get_bist_companies(output_format='dict')
    if (tick in tick_list):
       return list(filter(lambda d: d['ticker'] in [tick], c_dict))[0]