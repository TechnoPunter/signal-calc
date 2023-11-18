import redis.asyncio
from calc.models.models import Signal, SignalHistory
import json

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


def insert_signal(signal: Signal):
    signal_data = signal.model_dump()
    redis_client.set(f"signal:{signal.scrip}", json.dumps(signal_data))


def insert_signal_history(signal_hist: SignalHistory, scrip: str, timestamp: str):
    signal_hist_data = signal_hist.model_dump()
    redis_client.set(f"signal_history:{scrip}_{timestamp}", json.dumps(signal_hist_data))


def get_signal(key: str):
    return redis_client.get(key)
