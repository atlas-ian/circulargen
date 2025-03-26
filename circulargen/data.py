import os
import json
import easyocr
import numpy as np
from pdf2image import convert_from_path

# Directory containing PDF files
pdf_dir = "pdf_circulars"
output_json = "merged_circulars.json"

# Initialize EasyOCR reader for English (add more languages if needed)
reader = easyocr.Reader(['en'])

def extract_text_from_pdf(pdf_path):
    """
    Convert all pages of the PDF to images and extract text using EasyOCR.
    """
    try:
        images = convert_from_path(pdf_path, dpi=300)
    except Exception as e:
        print(f"Error converting {pdf_path}: {e}")
        return ""
    
    full_text = ""
    for page_num, image in enumerate(images, start=1):
        # Convert PIL image to numpy array (EasyOCR requires a numpy array)
        img_array = np.array(image)
        # Extract text; detail=0 returns just the text strings
        page_texts = reader.readtext(img_array, detail=0, adjust_contrast=0.7)
        # Join all text from the current page and add a separator
        page_text = " ".join(page_texts)
        full_text += f"\n--- Page {page_num} ---\n{page_text}\n"
    return full_text.strip()

def process_pdfs_in_directory(directory):
    """
    Process all PDF files in the specified directory and return a list of dictionaries.
    Each dictionary contains the filename and the extracted text.
    """
    merged_data = []
    for filename in os.listdir(directory):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(directory, filename)
            print(f"Processing: {filename}")
            extracted_text = extract_text_from_pdf(pdf_path)
            # You can further parse the extracted text here if needed
            circular_data = {
                "filename": filename,
                "extracted_text": extracted_text
            }
            merged_data.append(circular_data)
    return merged_data

# Process PDFs and merge data into a single JSON file
data = process_pdfs_in_directory(pdf_dir)

with open(output_json, "w", encoding="utf-8") as outfile:
    json.dump(data, outfile, indent=4)

print(f"Merged JSON file created as '{output_json}'")
