from commons.loggers.setup_logger import setup_logging
from calc.service.calc_engine import CalcEngine
import logging

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    setup_logging("calc-signal.log")
    logger.info("Started calc-signal")
    c = CalcEngine()
    c.calc_signal()
    logger.info("Finished calc-signal")
