import PyPDF2
import glob
import os
import sys

# Ensure utf-8 output for characters like ligatures
sys.stdout.reconfigure(encoding='utf-8')

texts = {}
try:
    for f in glob.glob('Related Works/*.pdf'):
        try:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for i in range(min(3, len(reader.pages))):
                text += reader.pages[i].extract_text() + "\n"
            texts[os.path.basename(f)] = text
        except Exception as e:
            print(f"Error reading {f}: {e}")

    for name, text in texts.items():
        print(f"\n{'='*40}")
        print(f"--- {name} ---")
        # Print first 2000 chars to get a good sense of the paper
        print(text[:2000] + "...")
except Exception as e:
    print(f"Global error: {e}")
