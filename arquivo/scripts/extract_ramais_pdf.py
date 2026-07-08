#!/usr/bin/env python3
"""
Extract and parse hospital extensions (ramais) from PDF
Creates a structured JSON mapping departments to extensions
"""

import json
import re
from pathlib import Path

def parse_ramais_from_text(pdf_text):
    """
    Parse the ramais PDF text into structured data
    The PDF has a column-based layout with departments and extensions
    """
    
    lines = pdf_text.strip().split('\n')
    
    # Dictionary to store: department_name -> [extensions]
    ramais_dict = {}
    
    # Current section/column
    current_section = None
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Parse lines with department name and extensions
        # Pattern: "Department Name - Sub-dept" followed by extension numbers
        # Extensions are 4-digit numbers like 6569, 8046, etc
        
        # Extract all numbers from the line
        numbers = re.findall(r'\b\d{4}\b', line)
        
        # Remove numbers from the line to get the department name
        dept_name = re.sub(r'\b\d{4}\b', '', line).strip()
        
        # Skip lines that are just numbers or too short
        if dept_name and len(dept_name) > 3 and numbers:
            # Store the mapping
            if dept_name not in ramais_dict:
                ramais_dict[dept_name] = []
            ramais_dict[dept_name].extend(numbers)
    
    return ramais_dict

def extract_pdf_text(pdf_path):
    """
    Extract text from PDF file
    """
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text
    except ImportError:
        print("⚠️  PyPDF2 not installed. Trying pdfplumber...")
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text()
            return text
        except ImportError:
            print("❌ No PDF library available. Installing pdfplumber...")
            import subprocess
            subprocess.run(['pip3', 'install', 'pdfplumber'], check=True)
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text()
            return text

def main():
    pdf_path = Path('/Users/joaoperes/escalaHRO/Ramais HRO.pdf')
    
    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    print(f"📄 Extracting text from PDF: {pdf_path}")
    pdf_text = extract_pdf_text(pdf_path)
    
    print(f"✅ Text extracted ({len(pdf_text)} characters)")
    
    print("\n🔍 Parsing departments and extensions...")
    ramais_dict = parse_ramais_from_text(pdf_text)
    
    print(f"✅ Found {len(ramais_dict)} departments/sections")
    
    # Sort by department name for better readability
    sorted_ramais = dict(sorted(ramais_dict.items()))
    
    # Save to JSON
    output_path = Path('/Users/joaoperes/escalaHRO/ramais_hro.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_ramais, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved to: {output_path}")
    
    # Display sample
    print("\n📋 Sample entries:")
    for i, (dept, extensions) in enumerate(list(sorted_ramais.items())[:10]):
        print(f"  {dept}: {', '.join(extensions)}")
    
    print(f"\n... and {len(sorted_ramais) - 10} more entries")

if __name__ == "__main__":
    main()
