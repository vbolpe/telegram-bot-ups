import asyncio
from fastapi import FastAPI
from datetime import datetime
from .snmp_client import get_ups_status
from .state_manager import load_state, save_state
from .config import CHECK_INTERVAL
from .models import UPSStatus

app = FastAPI()

current_status = None
last_event = None

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(monitor_loop())

@app.get("/status", response_model=UPSStatus)
async def get_status():
    return current_status

@app.get("/event")
async def get_event():
    global last_event
    event = last_event
    last_event = None
    return event

async def monitor_loop():
    global current_status, last_event

    while True:
        new_status = get_ups_status()
        previous = load_state()

        if previous is None or previous["status"] != new_status["status"]:
            last_event = {
                "old": previous["status"] if previous else None,
                "new": new_status["status"],
                "timestamp": datetime.utcnow(),
            }
        
        save_state(new_status)

        current_status = UPSStatus(
            status=new_status["status"],
            battery=new_status["battery"],
            load=new_status["load"],
            last_update=datetime.utcnow(),
        )

        await asyncio.sleep(CHECK_INTERVAL)