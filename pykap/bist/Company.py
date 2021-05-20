

class Company(object):
    """
    BIST Company class to store company related fields.
    """

    def __init__(self, ticker):
        self.ticker = ticker
        self._get_general_info()

    def _get_general_info(self):
        return "bla"