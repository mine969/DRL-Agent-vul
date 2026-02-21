import os
import pypdf
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_dir = r"research\Related Works"
pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
out_file = r"research\All_14_Abstracts.txt"

with open(out_file, 'w', encoding='utf-8') as f:
    for pdf_name in pdf_files:
        filepath = os.path.join(pdf_dir, pdf_name)
        f.write(f"====== {pdf_name} ======\n")
        try:
            reader = pypdf.PdfReader(filepath)
            text = ""
            for i in range(min(2, len(reader.pages))):
                text += reader.pages[i].extract_text()
            # Clean up and just keep first ~1500 chars which should cover the abstract
            text = text.replace('\n', ' ')[:1500] 
            f.write(text + "\n\n")
        except Exception as e:
            f.write(f"Error reading: {e}\n\n")

print(f"Successfully wrote abstracts for {len(pdf_files)} PDFs to {out_file}")
