import PyPDF2
import os

pdf_path = r"C:\Users\atuls\Startup\TinyLlama\adaptive_platform\Books\english\Unit 1 Fables and Folk Tales.pdf"

if not os.path.exists(pdf_path):
    print(f"File not found: {pdf_path}")
else:
    try:
        reader = PyPDF2.PdfReader(pdf_path)
        print(f"Number of pages: {len(reader.pages)}")
        with open("unit1_text.txt", "w", encoding="utf-8") as f:
            for i, page in enumerate(reader.pages):
                f.write(f"--- Page {i+1} ---\n")
                f.write(page.extract_text())
                f.write("\n\n")
        print("Text extracted to unit1_text.txt")
    except Exception as e:
        print(f"Error reading PDF: {e}")
