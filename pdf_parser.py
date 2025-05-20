from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def parse_invoice_data(text):
    # Example parsing logic; apne invoice format ke hisab se customize karo
    lines = text.split('\n')
    data = {
        "Invoice No": "",
        "Vendor": "",
        "Invoice Date": "",
        "Due Date": "",
        "Amount": ""
    }
    for line in lines:
        if "Invoice No" in line:
            data["Invoice No"] = line.split(":")[-1].strip()
        elif "Vendor" in line:
            data["Vendor"] = line.split(":")[-1].strip()
        elif "Invoice Date" in line:
            data["Invoice Date"] = line.split(":")[-1].strip()
        elif "Due Date" in line:
            data["Due Date"] = line.split(":")[-1].strip()
        elif "Amount" in line:
            data["Amount"] = line.split(":")[-1].strip()
    return data
