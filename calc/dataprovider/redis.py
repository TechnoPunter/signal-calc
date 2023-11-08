import redis.asyncio
from calc.models.models import Signal
import json

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


def insert_signal(signal: Signal):
    key = f"signal:{signal.scrip}"
    signal_data = signal.model_dump()
    redis_client.set(key, json.dumps(signal_data))


def get_signal(key: str):
    return redis_client.get(key)
