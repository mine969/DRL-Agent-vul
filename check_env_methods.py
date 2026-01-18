import sys
import os
import gym
from gym import spaces

# Mock requirements to load the class
try:
    import numpy as np
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    pass

# We need to inspect the class BEFORE instantiation because instantiation crashes
# So we parse the file content.

file_path = "d:\\github\\DRL Agents\\DQN web vul\\env\\web_sec_env.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Extract expected method names from action_book
import re
# Look for self.method_name
# Pattern: digits: self.(method_name),
matches = re.findall(r'\d+:\s*self\.(\w+),', content)
expected_methods = set(matches)

# Extract defined methods
# Pattern: def method_name(self
defined_matches = re.findall(r'def\s+(\w+)\s*\(self', content)
defined_methods = set(defined_matches)

missing = expected_methods - defined_methods

print(f"Total expected methods: {len(expected_methods)}")
print(f"Total defined methods: {len(defined_methods)}")
print(f"MISSING METHODS ({len(missing)}):")
for m in sorted(list(missing)):
    print(f"- {m}")

# Also check for the JuiceShop bug
if "self.action_space = spaces.Discrete(79)" in content:
    print("\n⚠️  WARNING: Found code resetting action_space to 79!")
