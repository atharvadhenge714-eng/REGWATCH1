import pypdf
import io
from services.ai_service import run_llm_completion, parse_json_safely

def extract_text_from_pdf_file(pdf_path: str) -> str:
    """Extract full readable text from all pages of a PDF file path."""
    try:
        reader = pypdf.PdfReader(pdf_path)
        if not reader.pages:
            print("[PARSER] PDF has 0 pages.")
            return ""
            
        text_pages = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text and page_text.strip():
                text_pages.append(f"[Page {i+1}]\n" + page_text.strip())
                
        full_text = "\n\n".join(text_pages)
        if not full_text.strip():
            print("[PARSER] PDF contains no extractable text (may be image-only).")
            return ""
        return full_text
    except Exception as e:
        print(f"[PARSER] PDF file extraction error: {e}")
        return ""

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract full readable text from all pages of a PDF in-memory byte stream."""
    try:
        stream = io.BytesIO(pdf_bytes)
        reader = pypdf.PdfReader(stream)
        if not reader.pages:
            print("[PARSER] PDF byte stream has 0 pages.")
            return ""
            
        text_pages = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text and page_text.strip():
                text_pages.append(f"[Page {i+1}]\n" + page_text.strip())
                
        full_text = "\n\n".join(text_pages)
        if not full_text.strip():
            print("[PARSER] PDF byte stream contains no extractable text.")
            return ""
        return full_text
    except Exception as e:
        print(f"[PARSER] PDF bytes extraction error: {e}")
        return ""

def parse_rbi_circular(pdf_path):
    print("[PARSER] Reading PDF...")
    text = extract_text_from_pdf_file(pdf_path)
    if not text:
        print("[PARSER] Text could not be extracted from this PDF.")
        return "{}"

    print("[PARSER] Sending extracted text to LLM...")

    prompt = f"""You are an RBI regulatory compliance expert.

Analyze this RBI circular and return ONLY a valid JSON object (no markdown code blocks, no extra text):
{{
    "title": "title of the circular",
    "main_change": "what regulation changed in simple words",
    "deadline": "compliance deadline or Not specified",
    "affected_domains": ["Data Protection", "Cybersecurity", "Financial Rules", "Reporting", "Third-Party Risk"],
    "severity": "High or Medium or Low",
    "action_required": "one sentence on what companies must do"
}}

Circular text:
{text[:12000]}"""

    response = run_llm_completion(prompt, system_prompt="You are an RBI compliance parser.", temperature=0.1)
    return response