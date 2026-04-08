import subprocess
import os
import shutil
import time
import requests
from dotenv import load_dotenv

load_dotenv()

class PhoenixHealer:
    def __init__(self, golden_cid):
        self.cid = golden_cid
        self.webhook_url = os.getenv("DISCORD_WEBHOOK")

    def enforce_state(self, target_dir):
        try:
            print(f"[*] Enforcing Absolute Integrity for {target_dir}...")
            
            temp_path = "./.recovery_zone"
            if os.path.exists(temp_path):
                if os.path.isdir(temp_path):
                    shutil.rmtree(temp_path)
                else:
                    os.remove(temp_path)

            # 1. Fetch from IPFS
            # We don't use -o here to let IPFS manage the naming, 
            # or we handle the result specifically.
            subprocess.run(["ipfs", "get", self.cid, "-o", temp_path], check=True, capture_output=True)
            
            # 2. PURGE: Wipe the monitored directory
            for item in os.listdir(target_dir):
                item_path = os.path.join(target_dir, item)
                os.chmod(item_path, 0o777) if os.path.exists(item_path) else None
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)

            # 3. RESTORE: Logic based on whether CID was a file or folder
            if os.path.isdir(temp_path):
                # If it's a folder, copy its contents
                pulled_items = os.listdir(temp_path)
                if pulled_items:
                    source_content = os.path.join(temp_path, pulled_items[0])
                    if os.path.isdir(source_content):
                        for item in os.listdir(source_content):
                            shutil.move(os.path.join(source_content, item), os.path.join(target_dir, item))
                    else:
                        # It's just the file sitting in the temp dir
                        shutil.move(source_content, os.path.join(target_dir, pulled_items[0]))
            else:
                # If temp_path IS the file (CID was a single file)
                # We rename/move it to its original name. 
                # NOTE: You'll need the original filename. 
                # For now, let's assume 'important_file.py' or detect from CID metadata
                shutil.move(temp_path, os.path.join(target_dir, "important_file.py"))

            print("[+] System State Re-Synchronized.")
            
        except Exception as e:
            print(f"[CRITICAL] State Enforcement Failed: {e}")

    def send_alert(self, file_path, status="Neutralized"):
        if not self.webhook_url or "YOUR_DISCORD" in self.webhook_url:
            return
        
        data = {
            "embeds": [{
                "title": f"🛡️ Bastion-Protocol: {status}",
                "description": f"Integrity breach addressed at `{file_path}`.",
                "color": 15158332,
                "footer": {"text": "Bastion-Protocol v1 | Decentralized FIM"}
            }]
        }
        try:
            requests.post(self.webhook_url, json=data, timeout=5)
        except:
            pass
