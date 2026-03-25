from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from config.unicorn import get_unicorn_prompt
import json

app = FastAPI()

client = OpenAI()

# In-memory storage (temporary)
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
# ANALYSIS (AI)
# -----------------------------
@app.post("/analyze")
async def analyze_event(event: Event):
    messages = [
        {"role": "system", "content": get_unicorn_prompt()},
        {"role": "user", "content": str(event.dict())}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        # Try to convert AI response into real JSON
        try:
            content = response.choices[0].message.content
            parsed = json.loads(content)

            return {
                "analysis": parsed
            }

        except:
            return {
                "analysis": response.choices[0].message.content
            }

    except Exception as e:
        return {
            "error": f"OpenAI request failed: {str(e)}"
        }