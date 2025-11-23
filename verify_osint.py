
from env.web_sec_env import WebSecurityGym
import time

def verify_osint():
    print("🧪 Verifying OSINT Skills...")
    env = WebSecurityGym()
    obs, _ = env.reset()
    
    # Test Action 46: OSINT Files
    print("\n[1] Testing Action 46: OSINT File Scan")
    obs, reward, done, truncated, info = env.step(46)
    print(f"    Result: URL={info.get('url')} | Status={info.get('status', 'N/A')} | Reward={reward}")
    
    # Test Action 47: OSINT Fingerprint
    print("\n[2] Testing Action 47: OSINT Fingerprint")
    obs, reward, done, truncated, info = env.step(47)
    print(f"    Result: URL={info.get('url')} | Status={info.get('status', 'N/A')} | Reward={reward}")
    
    print("\n✅ Verification Complete!")
    env.close()

if __name__ == "__main__":
    verify_osint()
