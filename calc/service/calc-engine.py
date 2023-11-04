import logging
import pyotp
from NorenRestApiPy.NorenApi import NorenApi
from calc.config.reader import cfg

logger = logging.getLogger(__name__)


class CalcEngine:
    api = NorenApi(host='https://api.shoonya.com/NorenWClientTP/',
                   websocket='wss://api.shoonya.com/NorenWSTP/')

    def __init__(self, acct: str = 'Trader-V2-Mahi'):
        creds = cfg['shoonya']
        if creds is None:
            raise Exception(f'Unable to find creds for')
        cred = creds[acct]
        logger.debug(f"api_login: About to call api.login with {cred}")
        resp = self.api.login(userid=cred['user'],
                              password=cred['pwd'],
                              twoFA=pyotp.TOTP(cred['token']).now(),
                              vendor_code=cred['vc'],
                              api_secret=cred['apikey'],
                              imei=cred['imei'])
        logger.info(f"api login response {resp}")

    def get_scrip_ts_data(self, scrip: str, tf: str = "1"):
        """
        Gets OHLC time series data from API for given scrip
        :return:
        """

    def get_portfolio_ts_data(self, tf: str = "1"):
        """
        Gets OHLC data for entire trading portfolio
        :param tf:
        :return:
        """
        # 1. Get list of scrips
        # 2. Call get_scrip_ts_data in multi threading
        # with Pool() as pool:
        #     for result in pool.imap_unordered(self.run_scenario, calc.scrips from cfg):
        #         pass

    def calc_signal(self):
        """
        For each of the portfolio scrip calculate low and high and store in redis with key signal:{scrip}
        :return:
        """


if __name__ == '__main__':
    import calc.loggers.setup_logger

    c = CalcEngine()
