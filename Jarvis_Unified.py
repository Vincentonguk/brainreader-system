import os
import csv
import requests
import time
from dotenv import load_dotenv

# SLRPD Ecosystem Orchestrator - ALIGNED REGISTRY
print("--- Initializing Clean Data Flow (Governance Mode) ---")
load_dotenv()

# Alignment Settings
SESSION_ID = os.getenv("SLRPD_SESSION_ID")
URL = os.getenv("RENDER_ENDPOINT")
CSV_FILE = "lab_session_20260305_1952.csv"

def push_kinetic_flow():
    if not os.path.exists(CSV_FILE):
        print(f"ERROR: {CSV_FILE} not found. Check your folder!")
        return

    print(f"Pushing to: {URL}")
    
    with open(CSV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # --- STRICT SCHEMA ALIGNMENT ---
            # The server error confirms it MUST be "action_type"
            formatted_payload = {
                "action_type": "telemetry_push", 
                "payload": {
                    "gX": float(row.get('gX', 0)),
                    "gY": float(row.get('gY', 0)),
                    "gZ": float(row.get('gZ', 0)),
                    "id": row.get('id', 'N/A')
                }
            }

            try:
                response = requests.post(URL, json=formatted_payload, timeout=10)
                
                if response.status_code in [200, 201]:
                    print(f"✅ OK | Vector {row.get('id', 'N/A')} | 86% Flowing...")
                else:
                    # This prints the exact error so we can see what's missing
                    print(f"❌ BLOCKED {response.status_code}")
                    print(f"SERVER SAYS: {response.text}")
                    break 
                    
            except Exception as e:
                print(f"⚠️ PIPELINE ERROR: {e}")
                break
            
            time.sleep(0.5) 

if __name__ == "__main__":
    push_kinetic_flow()