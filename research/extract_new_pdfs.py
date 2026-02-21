import os
import pypdf
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_files = [
    r"research\Related Works\A Scalable Continual Reinforcement Learning Framework for autonomous penetration testing.pdf",
    r"research\Related Works\Automatic penetration testing model based on reinforcement learning for complex network environments.pdf"
]

for file in pdf_files:
    try:
        reader = pypdf.PdfReader(file)
        print("=======", os.path.basename(file), "=======")
        text = ""
        for i in range(min(2, len(reader.pages))):
            text += reader.pages[i].extract_text()
        print(text.replace('\n', ' ')[:1500])
        print("\n")
    except Exception as e:
        print(f"Error reading {os.path.basename(file)}: {e}")
