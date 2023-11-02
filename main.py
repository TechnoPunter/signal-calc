from fastapi import FastAPI, HTTPException
from models import Todo, SignalReq, SignalResp, Signal
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
    signal_data = json.loads(await redis_client.get(key))
    signal_resp = SignalResp(signal="Hold")
    if not signal_data:
        return signal_resp
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


@app.post("/todos", response_model=Todo)
async def create_todo(todo: Todo):
    todo_id = await redis_client.incr("todo_id")
    todo_key = f"todo:{todo_id}"
    todo_data = todo.model_dump()
    await redis_client.set(todo_key, json.dumps(todo_data))
    return todo


@app.get("/todos", response_model=list[Todo])
async def read_todos():
    # Retrieve all todos from Redis
    todo_ids = await redis_client.keys("todo:*")
    todos = [json.loads(await redis_client.get(todo_id)) for todo_id in todo_ids]
    return todos


@app.get("/todos/{todo_id}", response_model=Todo)
async def read_todo(todo_id: int):
    todo_key = f"todo:{todo_id}"
    todo_data = await redis_client.get(todo_key)
    if not todo_data:
        raise HTTPException(status_code=404, detail="Todo not found")
    return json.loads(todo_data)


@app.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: int, updated_todo: Todo):
    todo_key = f"todo:{todo_id}"
    todo_data = await redis_client.get(todo_key)
    if not todo_data:
        raise HTTPException(status_code=404, detail="Todo not found")
    updated_data = updated_todo.model_dump()
    await redis_client.set(todo_key, json.dumps(updated_data))
    return updated_todo


@app.delete("/todos/{todo_id}", response_model=Todo)
async def delete_todo(todo_id: int):
    todo_key = f"todo:{todo_id}"
    todo_data = await redis_client.get(todo_key)
    if not todo_data:
        raise HTTPException(status_code=404, detail="Todo not found")
    deleted_data = json.loads(todo_data)
    await redis_client.delete(todo_key)
    return deleted_data


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
