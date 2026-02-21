import zipfile
import re
import sys

docx_path = 'IEEE onference-template-a4.docx'

try:
    with zipfile.ZipFile(docx_path, 'r') as z:
        if 'word/document.xml' in z.namelist():
            xml_content = z.read('word/document.xml').decode('utf-8')
            # Extract basic text content by removing XML tags
            text_only = re.sub(r'<[^>]+>', '', xml_content)
            print("Extracted text (first 2000 chars):")
            print(text_only[:2000])
        else:
            print("word/document.xml not found. This might not be a valid DOCX.")
except Exception as e:
    print(f"Error: {e}")
