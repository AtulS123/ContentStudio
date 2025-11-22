import PyPDF2
import os
import sys

if len(sys.argv) < 2:
    print("Usage: python extract_pdf.py <pdf_filename>")
    sys.exit(1)

filename = sys.argv[1]
pdf_path = os.path.join(r"C:\Users\atuls\Startup\TinyLlama\adaptive_platform\Books\english", filename)
output_file = f"{os.path.splitext(filename)[0]}_text.txt"

if not os.path.exists(pdf_path):
    print(f"File not found: {pdf_path}")
else:
    try:
        reader = PyPDF2.PdfReader(pdf_path)
        print(f"Processing {filename}...")
        print(f"Number of pages: {len(reader.pages)}")
        with open(output_file, "w", encoding="utf-8") as f:
            for i, page in enumerate(reader.pages):
                f.write(f"--- Page {i+1} ---\n")
                f.write(page.extract_text())
                f.write("\n\n")
        print(f"Text extracted to {output_file}")
    except Exception as e:
        print(f"Error reading PDF: {e}")
