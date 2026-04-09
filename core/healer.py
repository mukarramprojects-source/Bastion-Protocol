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
        """
        Wipes the compromised directory and restores the 'Golden State' from IPFS.
        """
        temp_path = "/tmp/bastion_recovery"
        
        try:
            print(f"[*] Enforcing Absolute Integrity for {target_dir}...")
            target_path = os.path.abspath(target_dir)

            # 1. CLEAN START: Remove any stale recovery data
            if os.path.exists(temp_path):
                subprocess.run(["sudo", "rm", "-rf", temp_path])

            # 2. PREPARE ENVIRONMENT: Create temp folder and grant 'kali' ownership
            os.makedirs(temp_path, exist_ok=True)
            subprocess.run(["sudo", "chown", "kali:kali", temp_path])
            subprocess.run(["sudo", "chmod", "777", temp_path])

            # 3. FETCH FROM DECENTRALIZED STORAGE: Pull Golden State from IPFS
            subprocess.run([
                "sudo", "-u", "kali", "env", "IPFS_PATH=/home/kali/.ipfs", 
                "ipfs", "get", self.cid, "-o", temp_path
            ], check=True)

            # 4. PURGE COMPROMISED FILES: Wipe the target directory
            subprocess.run(f"sudo rm -rf {target_path}/*", shell=True)

            # 5. RESTORE INTEGRITY: Move files from temp to target and fix permissions
            items = os.listdir(temp_path)
            content_source = temp_path
            
            # Handle IPFS subfolder naming if necessary
            if len(items) == 1 and os.path.isdir(os.path.join(temp_path, items[0])):
                content_source = os.path.join(temp_path, items[0])

            subprocess.run(f"sudo cp -r {content_source}/. {target_path}", shell=True)
            subprocess.run(["sudo", "chown", "-R", "kali:kali", target_path])

            print("[+] System State Re-Synchronized.")
            self.send_alert(target_dir, status="State Restored")

        except Exception as e:
            print(f"[CRITICAL] State Enforcement Failed: {e}")
            self.send_alert(target_dir, status="Heal Failed")
            
        finally:
            # Always clean up sensitive recovery data
            if os.path.exists(temp_path):
                shutil.rmtree(temp_path)

    def send_alert(self, file_path, status="Neutralized"):
        """
        Sends a notification to the Discord Webhook about the breach and remediation.
        """
        if not self.webhook_url or "YOUR_DISCORD" in self.webhook_url:
            return

        data = {
            "embeds": [{
                "title": f"🛡️ Bastion-Protocol: {status}",
                "description": f"Integrity breach addressed at `{file_path}`.",
                "color": 15158332,
                "footer": {"text": "Aegis-Ghost v1 | Decentralized Self-Healing FIM"}
            }]
        }
        
        try:
            requests.post(self.webhook_url, json=data, timeout=5)
        except Exception:
            # Silently fail if Discord is unreachable to prevent script hanging
            pass
