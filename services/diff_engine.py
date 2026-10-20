import json
import re
from services.ai_service import run_llm_completion, parse_json_safely

def evaluate_document_comparability(text1: str, text2: str, title1: str = "", title2: str = "") -> dict:
    """Validate document readability and check for domain/topic comparability."""
    t1_clean = re.sub(r'\s+', ' ', text1 or '').strip()
    t2_clean = re.sub(r'\s+', ' ', text2 or '').strip()

    if not t1_clean or len(t1_clean) < 20:
        return {
            "valid": False,
            "error_message": "Text could not be extracted from Document A or text is unreadable."
        }
        
    if not t2_clean or len(t2_clean) < 20:
        return {
            "valid": False,
            "error_message": "Text could not be extracted from Document B or text is unreadable."
        }

    # Extract non-stopword distinct terms (>4 chars)
    stopwords = {"about", "above", "after", "again", "against", "all", "also", "among", "and", "any", "are", "been", "before", "being", "below", "between", "both", "but", "by", "can", "could", "did", "does", "doing", "down", "during", "each", "few", "for", "from", "further", "had", "has", "have", "having", "her", "here", "hers", "herself", "him", "himself", "his", "how", "into", "its", "itself", "just", "more", "most", "my", "myself", "nor", "not", "now", "off", "once", "only", "other", "our", "ours", "out", "over", "own", "same", "she", "should", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then", "there", "these", "they", "this", "those", "through", "too", "under", "until", "up", "very", "was", "were", "what", "when", "where", "which", "while", "who", "whom", "why", "with", "would", "your", "yours", "yourself"}
    
    w1 = set([w for w in re.findall(r'\b[a-zA-Z]{4,}\b', t1_clean.lower()) if w not in stopwords])
    w2 = set([w for w in re.findall(r'\b[a-zA-Z]{4,}\b', t2_clean.lower()) if w not in stopwords])

    # Check for distinct regulatory domain mismatch
    t1_combined = (title1 + " " + t1_clean[:1000]).lower()
    t2_combined = (title2 + " " + t2_clean[:1000]).lower()

    # Provide optional warning if overlap is low, but NEVER mark as invalid if readable text exists
    unrelated_warning = None
    if w1 and w2:
        intersection = w1.intersection(w2)
        min_size = min(len(w1), len(w2))
        overlap_ratio = len(intersection) / min_size if min_size > 0 else 0
        if overlap_ratio < 0.15 and len(intersection) < 5:
            unrelated_warning = "These documents appear to cover different regulatory topics. The comparison will highlight structural differences."

    return {
        "valid": True,
        "unrelated_warning": unrelated_warning,
        "len1": len(t1_clean),
        "len2": len(t2_clean)
    }


def compare_regulatory_documents(old_text: str, new_text: str, company_profile: dict = None, doc1_title: str = "Document A", doc2_title: str = "Document B") -> dict:
    """Compare two versions of a regulatory document using LLM and extract differences.
    
    Returns structured results adhering strictly to the response schema:
    - success (bool)
    - severity (HIGH / MEDIUM / LOW / NO_SIGNIFICANT_CHANGE / UNAVAILABLE)
    - summary (str)
    - why_this_matters (str)
    - impact (str)
    - effective_date (str)
    - added_sections (list)
    - removed_sections (list)
    - modified_sections (list)
    - changed_values (list)
    - recommended_actions (list)
    - source_a (str)
    - source_b (str)
    """
    comp_check = evaluate_document_comparability(old_text, new_text, doc1_title, doc2_title)
    
    if not comp_check["valid"]:
        return {
            "success": False,
            "status": "error",
            "severity": "UNAVAILABLE",
            "change_severity": "UNAVAILABLE",
            "summary": "The documents could not be reliably compared.",
            "why_this_matters": "The documents could not be reliably compared.",
            "impact": "Not available",
            "company_impact_summary": "Not available",
            "effective_date": "Not specified",
            "added_sections": [],
            "removed_sections": [],
            "modified_sections": [],
            "modified_requirements": [],
            "changed_values": [],
            "recommended_actions": [],
            "source_a": doc1_title,
            "source_b": doc2_title,
            "doc1_title": doc1_title,
            "doc2_title": doc2_title,
            "error_message": comp_check.get("error_message", "Unable to compare these documents. Please verify that both documents contain readable text.")
        }

    # Extract target entity description dynamically (NEVER hardcode ICICI, Google Pay, or Paytm)
    company_name = None
    if company_profile and isinstance(company_profile, dict):
        company_name = company_profile.get("company_name")
        
    target_entity_desc = f"'{company_name}'" if company_name else "regulated financial entities"

    # Analyze up to 12,000 characters per document to fit provider context limits cleanly
    MAX_CHARS = 12000
    old_content = old_text[:MAX_CHARS]
    new_content = new_text[:MAX_CHARS]

    parse_note = None
    if len(old_text) > MAX_CHARS or len(new_text) > MAX_CHARS:
        parse_note = f"Document comparison performed (analyzed key regulatory provisions up to {MAX_CHARS} characters per document)."

    prompt = f"""You are a precise, objective regulatory compliance engineer and diff auditor. Compare the following two regulatory documents.

    DOCUMENT A (Baseline / Reference - '{doc1_title}'):
    {old_content}

    DOCUMENT B (Updated / Comparison - '{doc2_title}'):
    {new_content}

    Target Context: {target_entity_desc}

    Identify all actual statutory changes between Document A and Document B. 
    Do NOT invent changes. 
    Do NOT invent company names. 
    If the documents have identical or nearly identical obligations, set severity to "NO_SIGNIFICANT_CHANGE".

    Return ONLY a valid JSON object with this exact structure:
    {{
        "severity": "HIGH / MEDIUM / LOW / NO_SIGNIFICANT_CHANGE / UNAVAILABLE",
        "summary": "Concise executive summary of the actual differences detected.",
        "why_this_matters": "Grounded explanation of what these statutory updates represent.",
        "impact": "Explanation of direct compliance and operational impact on {target_entity_desc}.",
        "effective_date": "Effective date mentioned in text, or 'Not specified'",
        "added_sections": [
            {{
                "title": "Section Title",
                "text": "Brief summary of added obligation",
                "obligations": "Specific requirement"
            }}
        ],
        "removed_sections": [
            {{
                "title": "Section Title",
                "text": "Brief summary of removed obligation"
            }}
        ],
        "modified_sections": [
            {{
                "item": "Requirement name (e.g. Penalty, Reporting Deadline, Net Worth)",
                "old_val": "Baseline value",
                "new_val": "Updated value",
                "change_type": "Threshold / Deadline / Penalty / Obligation / Wording",
                "impact_level": "HIGH / MEDIUM / LOW"
            }}
        ],
        "changed_values": [
            {{
                "parameter": "Parameter name",
                "old_value": "Original threshold",
                "new_value": "New threshold"
            }}
        ],
        "recommended_actions": [
            {{
                "action": "Description of recommended action",
                "priority": "HIGH / MEDIUM / LOW",
                "team": "Compliance / Engineering / Product / Legal"
            }}
        ]
    }}

    Return ONLY the raw JSON object."""

    system_prompt = "You are a precise, logical regulatory auditor that performs document diff comparisons without hallucinating."

    response_text = run_llm_completion(prompt, system_prompt=system_prompt, temperature=0.1)

    # Handle LLM failure or fallback string
    if not response_text or "Rate limit or connection issue" in response_text or "Fallback data" in response_text:
        return {
            "success": False,
            "status": "error",
            "severity": "UNAVAILABLE",
            "change_severity": "UNAVAILABLE",
            "summary": "The documents could not be reliably compared.",
            "why_this_matters": "The documents could not be reliably compared.",
            "impact": "Not available",
            "company_impact_summary": "Not available",
            "effective_date": "Not specified",
            "added_sections": [],
            "removed_sections": [],
            "modified_sections": [],
            "modified_requirements": [],
            "changed_values": [],
            "recommended_actions": [],
            "source_a": doc1_title,
            "source_b": doc2_title,
            "doc1_title": doc1_title,
            "doc2_title": doc2_title,
            "error_message": "Unable to compare these documents. Please verify that both documents contain readable text."
        }

    default_fallback = {
        "severity": "UNAVAILABLE",
        "summary": "The documents could not be reliably compared.",
        "why_this_matters": "The documents could not be reliably compared.",
        "impact": "Not available",
        "effective_date": "Not specified",
        "added_sections": [],
        "removed_sections": [],
        "modified_sections": [],
        "changed_values": [],
        "recommended_actions": []
    }

    res = parse_json_safely(response_text, default_fallback)

    if not isinstance(res, dict) or res.get("severity") == "UNAVAILABLE" and not res.get("summary"):
        return {
            "success": False,
            "status": "error",
            "severity": "UNAVAILABLE",
            "change_severity": "UNAVAILABLE",
            "summary": "The documents could not be reliably compared.",
            "why_this_matters": "The documents could not be reliably compared.",
            "impact": "Not available",
            "company_impact_summary": "Not available",
            "effective_date": "Not specified",
            "added_sections": [],
            "removed_sections": [],
            "modified_sections": [],
            "modified_requirements": [],
            "changed_values": [],
            "recommended_actions": [],
            "source_a": doc1_title,
            "source_b": doc2_title,
            "doc1_title": doc1_title,
            "doc2_title": doc2_title,
            "error_message": "Unable to compare these documents. Please verify that both documents contain readable text."
        }

    # Normalize fields according to schema
    sev_raw = str(res.get("severity", "UNAVAILABLE")).upper().strip()
    if sev_raw not in ["HIGH", "MEDIUM", "LOW", "NO_SIGNIFICANT_CHANGE", "UNAVAILABLE"]:
        sev_raw = "MEDIUM" if res.get("modified_sections") or res.get("added_sections") else "NO_SIGNIFICANT_CHANGE"

    summary_val = res.get("summary") or res.get("why_this_matters") or "Comparison complete."
    why_val = res.get("why_this_matters") or summary_val or "Not available"
    impact_val = res.get("impact") or res.get("company_impact_summary") or "Not available"

    mod_sections = res.get("modified_sections") or res.get("modified_requirements") or []

    # Map aliases consistently so backend and frontend agree
    result = {
        "success": True,
        "status": "success",
        "severity": sev_raw,
        "change_severity": sev_raw,
        "summary": summary_val,
        "why_this_matters": why_val,
        "impact": impact_val,
        "company_impact_summary": impact_val,
        "effective_date": res.get("effective_date", "Not specified"),
        "added_sections": res.get("added_sections", []),
        "removed_sections": res.get("removed_sections", []),
        "modified_sections": mod_sections,
        "modified_requirements": mod_sections,
        "changed_values": res.get("changed_values", []),
        "recommended_actions": res.get("recommended_actions", []),
        "source_a": doc1_title,
        "source_b": doc2_title,
        "doc1_title": doc1_title,
        "doc2_title": doc2_title
    }

    if comp_check.get("unrelated_warning"):
        result["unrelated_warning"] = comp_check["unrelated_warning"]
        
    if parse_note:
        result["parse_note"] = parse_note

    return result
