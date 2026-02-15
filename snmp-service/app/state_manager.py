import json
import os 
from datetime import datetime
from .config import STATE_FILE

def load_state():
    if not os.path.exists(STATE_FILE):
        return None
    
    with open(STATE_FILE, "r") as f:
        return json.load(f)
    
def save_state(data: dict):
    data["last_update"] = datetime.utcnow().isoformat()

    with open(STATE_FILE, "w") as f:
        json.dump(data, f)
        