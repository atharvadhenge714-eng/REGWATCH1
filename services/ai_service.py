import os
import re
import sys
import json
import itertools
from groq import Groq
from dotenv import load_dotenv

# Ensure safe UTF-8 output across all consoles
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

load_dotenv()

# Collect all available API keys from environment only
RAW_KEYS = []
for k in ["GROQ_API_KEY", "GROQ_API_KEY_SECONDARY", "GROQ_API_KEY_TERTIARY"]:
    val = os.getenv(k)
    if val and val.strip() and val.strip() not in RAW_KEYS:
        RAW_KEYS.append(val.strip())

KEYS_POOL = list(RAW_KEYS)
if not KEYS_POOL:
    print("[AI] WARNING: No Groq API keys found in .env file!")

key_cycle = itertools.cycle(KEYS_POOL) if KEYS_POOL else itertools.cycle([""])

def get_next_client():
    """Retrieve the next Groq client in round-robin order."""
    api_key = next(key_cycle)
    return Groq(api_key=api_key), api_key

def clean_json_response(text: str) -> str:
    """Extract clean JSON string from LLM response, stripping thinking blocks and markdown notation."""
    if not text:
        return "{}"
    # Strip <think>...</think> reasoning tags
    text_clean = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    
    # Strip markdown code blocks
    if "```json" in text_clean:
        text_clean = text_clean.split("```json")[1].split("```")[0].strip()
    elif "```" in text_clean:
        text_clean = text_clean.split("```")[1].split("```")[0].strip()
        
    return text_clean

def parse_json_safely(text: str, default_val: dict) -> dict:
    """Parse JSON string cleanly, with robust fallback to default value."""
    if not text:
        return default_val
    try:
        cleaned = clean_json_response(text)
        val = json.loads(cleaned)
        if isinstance(val, dict):
            if "error" in val and ("Rate limit" in str(val.get("error")) or "invalid_api_key" in str(val.get("error"))):
                return default_val
            return val
        elif isinstance(val, list) and isinstance(default_val, dict):
            return default_val
        return default_val
    except Exception:
        # Try extracting outermost JSON object with regex
        try:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                val = json.loads(match.group(0))
                if isinstance(val, dict):
                    return val
        except Exception:
            pass
    return default_val

# Active verified Groq models for compliance workflows
VERIFIED_MODELS = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "allam-2-7b"
]

# Track whether we've already logged the all-keys-failed warning
_all_keys_failed_logged = False

def run_llm_completion(prompt: str, system_prompt: str = "You are an expert regulatory compliance analyst.", temperature: float = 0.2, response_format_json: bool = False) -> str:
    """Run an LLM completion load balanced across the API key pool.
    
    Returns the LLM response text on success, or None if all keys/models fail.
    """
    global _all_keys_failed_logged
    
    if not KEYS_POOL:
        if not _all_keys_failed_logged:
            print("[AI] CRITICAL: No API keys available. All analysis will use fallback data.")
            _all_keys_failed_logged = True
        return None
    
    last_exception = None
    all_auth_failures = True
    
    for model in VERIFIED_MODELS:
        for attempt in range(max(len(KEYS_POOL), 1)):
            try:
                client, key_used = get_next_client()
                kwargs = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": temperature
                }
                if response_format_json:
                    kwargs["response_format"] = {"type": "json_object"}
                    
                response = client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content
                if content:
                    return content.strip()
                
            except Exception as e:
                err_msg = str(e)
                if "401" not in err_msg and "invalid_api_key" not in err_msg:
                    all_auth_failures = False
                last_exception = e
                continue
                
    # All keys and models failed
    if all_auth_failures:
        if not _all_keys_failed_logged:
            print(f"[AI] CRITICAL: All API keys are INVALID (401). LLM analysis unavailable. Last: {last_exception}")
            _all_keys_failed_logged = True
        else:
            print(f"[AI] LLM call failed (all keys invalid).")
    else:
        print(f"[AI] LLM call failed. Last exception: {last_exception}")
    
    return None

