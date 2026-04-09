#!/usr/bin/env python3
import time
import subprocess
import os
from pathlib import Path # More reliable for absolute paths
from dotenv import load_dotenv
from core.healer import PhoenixHealer
from core.monitor import BastionWatcher

# 1. SETUP ABSOLUTE PATHS
# This finds exactly where bastion.py is located
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
MONITORED_PATH = BASE_DIR / "monitored_dir"

# 2. LOAD ENV PROPERLY
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    print(f"[CRITICAL] .env file not found at {ENV_PATH}")
    exit(1)

# Ensure the CID is clean (no quotes or spaces)
GOLDEN_CID = os.getenv("GOLDEN_CID", "").strip().strip("'").strip('"')

if not GOLDEN_CID:
    print("[CRITICAL] GOLDEN_CID is empty in .env!")
    exit(1)

watcher = None

def get_current_cid():
    try:
        # Use the absolute path discovered at startup
        result = subprocess.run(
            ["ipfs", "add", "-n", "-r", "-Q", str(MONITORED_PATH)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception as e:
        print(f"DEBUG Error: {e}")
        return None

def handle_incident(event_type, file_path):
    global watcher
    if watcher.is_healing:
        return

    time.sleep(0.3) 

    current_hash = get_current_cid()
    # Log comparison for your report evidence
    print(f"DEBUG: Comparing Current({current_hash}) with Golden({GOLDEN_CID})")
    
    if current_hash == GOLDEN_CID:
        return 

    print(f"[!] {event_type} detected: {file_path}")
    
    watcher.is_healing = True 
    # Pass the verified GOLDEN_CID to the healer
    healer = PhoenixHealer(GOLDEN_CID)
    
    # Use the absolute path for enforcement
    healer.enforce_state(str(MONITORED_PATH))
    
    time.sleep(1)
    watcher.is_healing = False
    print("[+] System Healed and Monitoring Resumed.")

def start_bastion():
    global watcher
    print("[-] Initializing Bastion Protocol...")
    print(f"[-] Monitoring Path: {MONITORED_PATH}")
    
    watcher = BastionWatcher(path=str(MONITORED_PATH), callback=handle_incident)
    watcher.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
        print("\n[-] Bastion Deactivated.")

if __name__ == "__main__":
    start_bastion()
