import os
import pypdf
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"d:\github\DRL Agents\DQN web vul\research\Related Works\26278-62647-1-PB.pdf"
out_file = r"d:\github\DRL Agents\DQN web vul\research\new_pdf_extract.txt"

with open(out_file, 'w', encoding='utf-8') as f:
    try:
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for i in range(min(2, len(reader.pages))):
            text += reader.pages[i].extract_text()
        # Clean up and just keep first ~2500 chars to get title, authors, and abstract
        text = text.replace('\n', ' ')[:2500] 
        f.write(text + "\n\n")
    except Exception as e:
        f.write(f"Error reading: {e}\n\n")

print(f"Successfully wrote extract to {out_file}")
