from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from config.unicorn import get_unicorn_prompt
import json
import os

app = FastAPI()

# Safe OpenAI init
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

# In-memory storage
events = []


# -----------------------------
# MODELS
# -----------------------------
class Event(BaseModel):
    session_id: str = "unknown"
    timestamp: str = "unknown"
    signal: float = 0
    frequency: str = "unknown"
    engagement: float = 0


class StateResponse(BaseModel):
    status: str
    total_events: int
    system_mode: str


# -----------------------------
# ROOT (Render needs this)
# -----------------------------
@app.get("/")
def root():
    return {
        "system": "BrainReader API",
        "status": "running"
    }


# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# -----------------------------
# EVENT INGESTION
# -----------------------------
@app.post("/event")
async def receive_event(event: Event):
    structured_event = event.dict()
    events.append(structured_event)

    return {
        "status": "structured",
        "event": structured_event
    }


# -----------------------------
# SYSTEM STATE
# -----------------------------
@app.get("/state", response_model=StateResponse)
def get_state():
    return {
        "status": "running",
        "total_events": len(events),
        "system_mode": "collecting"
    }


# -----------------------------
# LOCAL INTERPRETATION (NO AI)
# -----------------------------
def interpret_signal(signal: float):
    if signal < 20:
        return "ACTIVE THOUGHT DETECTED"
    else:
        return "RESTING STATE"


# -----------------------------
# QUICK PROCESS (FAST)
# -----------------------------
@app.post("/process")
def process_signal(event: Event):
    state = interpret_signal(event.signal)

    return {
        "signal": event.signal,
        "state": state
    }


# -----------------------------
# AI ANALYSIS
# -----------------------------
@app.post("/analyze")
async def analyze_event(event: Event):
    if not client:
        return {
            "error": "OpenAI API key not configured"
        }

    messages = [
        {"role": "system", "content": get_unicorn_prompt()},
        {"role": "user", "content": str(event.dict())}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        content = response.choices[0].message.content

        try:
            parsed = json.loads(content)
            return {"analysis": parsed}
        except:
            return {"analysis": content}

    except Exception as e:
        return {
            "error": f"OpenAI request failed: {str(e)}"
        }
