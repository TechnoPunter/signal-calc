from fastapi import FastAPI
from calc.models.models import SignalReq, SignalResp, Signal
import redis
import json
import uvicorn

app = FastAPI()

# Create a Redis connection
redis_client = redis.asyncio.StrictRedis(host='localhost', port=6379, db=0)


@app.post("/signal", response_model=SignalResp)
async def get_signal(signal_req: SignalReq):
    ltp = float(signal_req.ltp)
    key = f"signal:{signal_req.scrip}"
    signal_data = await redis_client.get(key)
    signal_resp = SignalResp(signal="Hold")
    if not signal_data:
        return signal_resp
    signal_data = json.loads(signal_data)
    if ltp <= signal_data.get("low"):
        signal_resp.signal = "Long"
    elif ltp >= signal_data.get("high"):
        signal_resp.signal = "Short"
    return signal_resp


@app.post("/load_signal")
async def load_signal(signal: Signal):
    key = f"signal:{signal.scrip}"
    signal_data = signal.model_dump()
    await redis_client.set(key, json.dumps(signal_data))
    return "Ok"


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
