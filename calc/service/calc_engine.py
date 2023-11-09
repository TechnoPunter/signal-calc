import concurrent.futures
import datetime
import logging
import time

import pyotp
from NorenRestApiPy.NorenApi import NorenApi
from apscheduler.schedulers.background import BackgroundScheduler

from calc.config.reader import cfg
from calc.dataprovider.redis import insert_signal
from calc.models.models import Signal
from calc.utils.utils import Symbols

logger = logging.getLogger(__name__)

DEBUG = False


class CalcEngine:
    api = NorenApi(host='https://api.shoonya.com/NorenWClientTP/',
                   websocket='wss://api.shoonya.com/NorenWSTP/')

    def __init__(self, acct: str = 'Trader-V2-Mahi'):
        self.scheduler = BackgroundScheduler()
        self.start_scheduler()
        self.symbols = Symbols()
        creds = cfg['shoonya']
        if creds is None:
            raise Exception(f'Unable to find creds for')
        cred = creds[acct]
        logger.info(f"api_login: About to call api.login with {cred}")
        resp = self.api.login(userid=cred['user'],
                              password=cred['pwd'],
                              twoFA=pyotp.TOTP(cred['token']).now(),
                              vendor_code=cred['vc'],
                              api_secret=cred['apikey'],
                              imei=cred['imei'])
        # todo add retry mechanism
        logger.info(f"api login response {resp}")

    @staticmethod
    def get_signal_by_ts(scrip: str, ts: list):
        """
        Get Low High based on ts
        :param scrip:
        :param ts:
        :return:
        """
        # create signal based on ts
        low = float(ts[0]["intl"])
        high = float(ts[0]["inth"])

        for item in ts:
            intl = float(item["intl"])
            inth = float(item["inth"])
            if intl < low:
                low = intl
            if inth > high:
                high = inth

        signal = Signal(scrip=scrip, low=low, high=high)
        return signal

    def get_scrip_ts_data(self, scrip: str):
        """
        Gets OHLC time series data from API for given scrip
        :return:
        """
        # make call to shoonya api
        ts = self.api.get_time_price_series("NSE", self.symbols.get_token(scrip))
        logger.debug(f'Result of shoonya api {ts}')
        return scrip, ts

    def process_portfolio_scrips(self, scrips: list):
        """
        Gets OHLC data for entire trading portfolio & calculate & store the signal
        :param scrips:
        :param scrips: List of scrips to process in the format NSE_SYMBOL e.g. NSE_ONGC
        :return:
        """
        logger.info(f"Starting Processing for {len(scrips)} scrips")
        results = []

        # schedule job

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(scrips)) as executor:
            futures = [executor.submit(self.get_scrip_ts_data, scrip) for scrip in scrips]
            for future in concurrent.futures.as_completed(futures):
                scrip, ts = future.result()
                if ts is not None:
                    signal = self.get_signal_by_ts(scrip, ts)
                    insert_signal(signal)
                    results.append(f"{signal}")
                else:
                    logger.info(f'time series none')
        logger.debug(results)
        logger.info(f"Finished Processing for {len(scrips)} scrips")

    # def execute_for_every_interval(self, interval: int, scrips: list = []):
    #     # Define the job function
    #     self.process_portfolio_scrips(scrips)

    # logger.info(f'executing every {interval} min')
    #
    # while True:
    #     self.process_portfolio_scrips(scrips)
    #     time.sleep(interval * 60)

    # def scheduled_task():
    #     self.get_portfolio_ts_data(scrips)
    #
    # self.scheduler.add_job(
    #     scheduled_task,
    #     trigger=CronTrigger(second="0", minute=f"*/{interval}", hour="*", day_of_week="mon-fri"),
    #     id="my_scheduled_task"
    # )
    # logger.info("Here")

    def calc_signal(self):
        """
        For each of the portfolio scrip calculate low and high and store in redis with key signal:{scrip}
        :return:
        """
        calc_config = cfg["calc"]
        if calc_config is None:
            raise Exception(f'Unable to find calc configuration')
        scrips = calc_config["scrips"]
        if scrips is None:
            raise Exception(f'Unable to find scrips for calc')

        if len(scrips) == 0:
            logger.warning(f'Zero scrips !!')
        else:
            logger.info("Starting engine")
            current_time = datetime.datetime.now().time()
            end_time = datetime.time(15, 30)  # 3:30 PM
            if DEBUG:
                current_time = datetime.time(10, 30)
            logger.info(f"Starting Schedule @ {current_time} will run till {end_time}")
            if current_time <= end_time:
                while True:
                    self.process_portfolio_scrips(scrips)
                    time.sleep(1 * 60)

            # else:
            #     self.scheduler.add_job(
            #         self.execute_for_every_interval,  # Pass the function as a callable
            #         trigger=CronTrigger(hour=9, minute=15, second=0, day_of_week="mon-fri"),
            #         args=(1, scrips),  # Pass the function arguments
            #         id="get_portfolio_ts_data_job"
            #     )
            #     logger.info("scheduled at 9:30 am")

    def start_scheduler(self):
        # Start the scheduler
        self.scheduler.start()

    def stop_scheduler(self):
        # Stop the scheduler if it's running
        try:
            self.scheduler.shutdown()
        except Exception as e:
            logger.info(f"Scheduler is not running !!")


if __name__ == '__main__':
    import calc.loggers.setup_logger
    DEBUG = True
    logger.info("Started Calc Engine")
    c = CalcEngine()
    c.calc_signal()
