"""
Test the latest trained model against ALL mock targets using the real SecurityAuditor
"""
import sys
import os
import glob
import re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from autonomous_scan import SecurityAuditor

TARGETS = [
    "http://localhost:5002", # E-Commerce
    "http://localhost:5003", # Social Media
    "http://localhost:5004", # Banking
    "http://localhost:5005", # Blog
    "http://localhost:5006"  # File Share
]

def get_latest_checkpoint():
    checkpoints = glob.glob("checkpoints/improved_mock_ep*.pth")
    if not checkpoints:
        return None, None
    
    checkpoint_episodes = []
    for path in checkpoints:
        match = re.search(r'ep(\d+)', path)
        if match:
            ep_num = int(match.group(1))
            checkpoint_episodes.append((ep_num, path))
    
    checkpoint_episodes.sort(key=lambda x: x[0], reverse=True)
    return checkpoint_episodes[0]

def test_all_targets():
    print("=" * 70)
    print("🧪 TESTING LATEST MODEL AGAINST ALL MOCK TARGETS")
    print("=" * 70)
    
    latest_ep, latest_path = get_latest_checkpoint()
    if not latest_path:
        print("❌ No checkpoints found!")
        return

    print(f"\n📦 Loading Model: {latest_path}")
    print(f"   Episode: {latest_ep}")
    
    total_findings = 0
    
    for url in TARGETS:
        print(f"\n" + "-" * 70)
        print(f"🎯 Target: {url}")
        print("-" * 70)
        
        try:
            # Initialize Security Auditor
            auditor = SecurityAuditor(
                base_url=url,
                model_path=latest_path
            )
            
            # Run audit
            # Using low exploration (epsilon=0.05) to rely on trained policy
            findings = auditor.start_audit(
                crawl_depth=0,      # Focus on the main page/api for quick test
                test_intensity=3,   # 3 episodes per target
                epsilon=0.05,
                scan_mode="auto"
            )
            
            print(f"\n📊 Findings for {url}: {len(findings)}")
            if findings:
                for i, f in enumerate(findings, 1):
                    # Handle Finding object attributes safely
                    v_type = getattr(f, 'vuln_type', 'Unknown')
                    v_payload = getattr(f, 'payload', 'N/A')
                    print(f"  {i}. {v_type} | Payload: {v_payload}")
                    
            total_findings += len(findings)
            
        except Exception as e:
            print(f"❌ Error scanning {url}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 70)
    print("🏁 FINAL SUMMARY")
    print("=" * 70)
    print(f"Total Vulnerabilities Found across all targets: {total_findings}")
    print("=" * 70)

if __name__ == "__main__":
    test_all_targets()
