import subprocess
import time
import os
import signal
import sys
import re
from utils.model_loader import find_latest_checkpoint

# Configuration
TARGETS = [
    {
        "name": "Banking App",
        "script": "env/target_app_banking.py",
        "port": 5004,
        "url": "http://localhost:5004"
    },
    {
        "name": "Blog Platform",
        "script": "env/target_app_blog.py",
        "port": 5005,
        "url": "http://localhost:5005"
    },
    {
        "name": "E-Commerce",
        "script": "env/target_app_ecommerce.py",
        "port": 5002,
        "url": "http://localhost:5002"
    },
    {
        "name": "File Share",
        "script": "env/target_app_fileshare.py",
        "port": 5006,
        "url": "http://localhost:5006"
    },
    {
        "name": "Social Media",
        "script": "env/target_app_social.py",
        "port": 5003,
        "url": "http://localhost:5003"
    }
]

# Find latest model dynamically
latest_ep, latest_model_path = find_latest_checkpoint()
if latest_model_path:
    MODEL_PATH = latest_model_path
    print(f"Using latest model: {MODEL_PATH} (Episode {latest_ep})")
else:
    MODEL_PATH = "dqn_web_sec_model.pth"
    print(f"Using default model: {MODEL_PATH}")

EPISODES = 5

def start_target(script_path):
    """Start the target application in a subprocess"""
    print(f"🚀 Starting {script_path}...")
    process = subprocess.Popen(
        [sys.executable, script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.getcwd()
    )
    time.sleep(3)  # Wait for startup
    return process

def run_agent(target_url):
    """Run the agent against the target"""
    print(f"🤖 Running agent against {target_url}...")
    try:
        result = subprocess.run(
            [sys.executable, "deploy_agent.py", "--target", target_url, "--model", MODEL_PATH, "--episodes", str(EPISODES), "--epsilon", "0.2"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        return result.stdout + "\n" + result.stderr
    except Exception as e:
        print(f"Error running agent: {e}")
        return ""

def parse_results(output):
    """Parse the agent output to find vulnerabilities and actions"""
    vulns = []
    actions = []
    
    # Look for lines like "🚨 VULNERABILITY FOUND: Action Name (Reward: X)"
    # or the summary section
    
    # Simple regex to catch vulnerabilities reported in the summary
    summary_pattern = re.compile(r"Episode \d+: (.+) \(Step \d+, Reward: ([\d.]+)\)")
    
    # Regex to catch actions
    action_pattern = re.compile(r"Action: (.+?)\s+\|")
    
    lines = output.split('\n')
    in_summary = False
    
    for line in lines:
        # Capture actions
        action_match = action_pattern.search(line)
        if action_match:
            actions.append(action_match.group(1).strip())

        if "🔴 Vulnerabilities Detected:" in line:
            in_summary = True
            continue
        
        if in_summary:
            match = summary_pattern.search(line)
            if match:
                vulns.append(match.group(1))
    
    if not actions:
        print("DEBUG: No actions found. Raw output:")
        print(output[:1000]) # Print first 1000 chars
        
    return list(set(vulns)), list(set(actions))  # Unique vulnerabilities and actions

def main():
    results = {}
    
    for target in TARGETS:
        print(f"\n{'='*50}")
        print(f"Testing {target['name']}")
        print(f"{'='*50}")
        
        # Start target
        target_process = start_target(target['script'])
        
        try:
            # Run agent
            output = run_agent(target['url'])
            # print(output) # Debugging
            
            # Parse results
            detected_vulns, actions_taken = parse_results(output)
            results[target['name']] = {
                "vulns": detected_vulns,
                "actions": actions_taken
            }
            print(f"✅ Detected: {', '.join(detected_vulns) if detected_vulns else 'None'}")
            print(f"👀 Actions Taken: {', '.join(actions_taken[:5])}..." if actions_taken else "No actions recorded")
            
        finally:
            # Kill target
            print(f"🛑 Stopping {target['name']}...")
            target_process.terminate()
            try:
                target_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                target_process.kill()
            
            # Ensure port is freed
            time.sleep(2)

    # Generate Markdown Table
    print("\n\n" + "="*50)
    print("RESULTS TABLE")
    print("="*50)
    
    table = "| Mock Website | Vulnerabilities Detected by Double DQN | Actions Attempted (Sample) |\n"
    table += "| :--- | :--- | :--- |\n"
    
    for name, data in results.items():
        vuln_str = ", ".join(data['vulns']) if data['vulns'] else "None"
        action_str = ", ".join(data['actions'][:3]) + ("..." if len(data['actions']) > 3 else "")
        table += f"| {name} | {vuln_str} | {action_str} |\n"
    
    print(table)
    
    # Save to file
    with open("agent_test_results.md", "w", encoding="utf-8") as f:
        f.write("# Agent Test Results\n\n")
        f.write(table)
        f.write("\n\n*Note: Results based on 5 test episodes per target.*")

if __name__ == "__main__":
    main()
