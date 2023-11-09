import os
import shutil
import subprocess
import pandas as pd
import logging
from urllib.request import urlopen

logger = logging.getLogger(__name__)

SYMBOL_MASTER = "https://api.shoonya.com/NSE_symbols.txt.zip"
SCRIP_MAP = {'BAJAJ_AUTO-EQ': 'BAJAJ-AUTO-EQ', 'M_M-EQ': 'M&M-EQ'}


class Symbols:
    def __init__(self):
        zip_file_name = 'NSE_symbols.zip'
        token_file_name = 'NSE_symbols.txt'

        # extracting zipfile from URL
        with urlopen(SYMBOL_MASTER) as response, open(zip_file_name, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

            # extracting required file from zipfile
            command = 'unzip -o ' + zip_file_name
            subprocess.call(command, shell=True)

        # deleting the zipfile from the directory
        os.remove(zip_file_name)

        # loading data from the file
        self.symbols = pd.read_csv(token_file_name)
        os.remove(token_file_name)

    def get_token(self, scrip):
        logger.debug(f"Getting token for {scrip}")
        symbol = scrip.replace("NSE_", "")
        symbol = symbol + "-EQ"
        symbol = SCRIP_MAP.get(symbol, symbol)
        # todo check for invalid token
        return str(self.symbols.loc[self.symbols.TradingSymbol == symbol]['Token'].iloc[0])


if __name__ == '__main__':
    import calc.loggers.setup_logger

    s = Symbols()
    print(s.get_token("NSE_ONGC"))
