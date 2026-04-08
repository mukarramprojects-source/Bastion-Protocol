#!/usr/bin/env python3
import time
import subprocess
import os
from dotenv import load_dotenv
from core.healer import PhoenixHealer
from core.monitor import BastionWatcher


# Get the absolute path of the directory where bastion.py sits
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

GOLDEN_CID = os.getenv("GOLDEN_CID")
# Verify it loaded
if not GOLDEN_CID:
    print("[CRITICAL] Could not find GOLDEN_CID in .env!")
    exit(1)

watcher = None

def get_current_cid():
    try:
        # Use the --offline flag so it doesn't try to talk to the repo if it's locked
        # Or use the local API if the daemon is running
        result = subprocess.run(
            ["ipfs", "add", "-n", "-r", "-Q", "./monitored_dir"],
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

    # Small delay to let the OS finish the 'mv' or 'rm' operation
    time.sleep(0.1) 

    current_hash = get_current_cid()
    print(f"DEBUG: Current CID: {current_hash}")
    
    if current_hash == GOLDEN_CID:
        return 

    print(f"[!] {event_type} detected: {file_path}")
    
    watcher.is_healing = True 
    healer = PhoenixHealer(GOLDEN_CID)
    
    # Force the entire folder to match the baseline
    healer.enforce_state("./monitored_dir")
    
    time.sleep(1)
    watcher.is_healing = False
    print("[+] System Healed and Monitoring Resumed.")

def start_bastion():
    global watcher
    print("[-] Initializing Bastion Protocol...")
    
    watcher = BastionWatcher(path="./monitored_dir", callback=handle_incident)
    watcher.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
        print("\n[-] Bastion Deactivated.")

if __name__ == "__main__":
    start_bastion()
