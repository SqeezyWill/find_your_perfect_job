import fitz  # PyMuPDF

def extract_text_from_cv(filepath):
    """
    Extracts text from a PDF CV file using PyMuPDF.
    Only works with PDF files.
    """
    try:
        text = ""
        with fitz.open(filepath) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        return f"Failed to extract text: {str(e)}"
