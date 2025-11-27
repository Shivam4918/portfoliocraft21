# ai_processor.py
import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv
import pdfplumber


load_dotenv(dotenv_path=r"D:\portfoliocraft\PortfolioCraft\.env")
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in .env at D:\\portfoliocraft\\PortfolioCraft\\.env")

genai.configure(api_key=API_KEY)


def extract_text_from_pdf(filepath):
    text = ""
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print("❌ pdfplumber error:", e)
    print("📄 Extracted resume text preview:", text[:500])
    return text.strip()

def extract_text_from_file(filepath):
    if filepath.lower().endswith(".pdf"):
        return extract_text_from_pdf(filepath)

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""


def _extract_json_from_text(text):
    """Try to pull first JSON array/object from text (handles code fences)."""
    if not text:
        raise ValueError("No text to extract JSON from")
   
    text_clean = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text_clean = re.sub(r"\s*```$", "", text_clean, flags=re.IGNORECASE)

   
    arr = re.search(r"(\[\s*\{[\s\S]*?\}\s*\])", text_clean)
    if arr:
        return arr.group(1)

    
    obj = re.search(r"(\{\s*\"?type\"?[\s\S]*?\})", text_clean)
    if obj:
        return obj.group(1)

    
    fb = text_clean.find('[')
    fc = text_clean.find('{')
    if fb != -1 and (fc == -1 or fb < fc):
        last = text_clean.rfind(']')
        if last != -1:
            return text_clean[fb:last+1]
    if fc != -1:
        last = text_clean.rfind('}')
        if last != -1:
            return text_clean[fc:last+1]

   
    return text_clean


def generate_portfolio_sections(resume_text):
    """
    Returns: list of section dicts on success, or dict {'error': message} on failure.
    """
    if not resume_text or not resume_text.strip():
        return {"error": "No resume text provided."}

    
    prompt = f"""
You are an assistant that converts the following resume text into strictly valid JSON ONLY.
Return a JSON LIST of section objects. Each section object must include:
- type: one of (summary, skills, experience, projects, education, certifications, achievements, contact)
- title: string
- content: string (or list of strings)
Optional keys: theme, layout, image

Resume:
\"\"\"{resume_text[:12000]}\"\"\"
"""

    candidates = [
        "models/gemini-2.5-flash",
        "models/gemini-2.5-pro",
        "models/gemini-pro-latest",
        "models/gemini-flash-latest",
        "models/gemini-2.5-flash-preview-05-20",
        "models/text-bison-001",
    ]

    last_err = None
    for model_name in candidates:
        try:
            print("➡️ Trying model:", model_name)
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            # extract textual content from common SDK response shapes
            raw_text = None
            if hasattr(response, "text"):
                raw_text = response.text
            elif hasattr(response, "candidates"):
                try:
                    raw_text = response.candidates[0].content
                except Exception:
                    raw_text = str(response)
            else:
                raw_text = str(response)

            raw_text = str(raw_text)
            print("🤖 Raw model output preview:", raw_text[:800])

            
            json_block = _extract_json_from_text(raw_text)
            parsed = json.loads(json_block)

          
            if isinstance(parsed, dict):
                parsed = [parsed]
            if not isinstance(parsed, list):
                raise ValueError("Parsed JSON is not a list")

            
            for sec in parsed:
                if not isinstance(sec, dict):
                    raise ValueError("Section item is not an object")
                if not (sec.get("title") or sec.get("type") or sec.get("content")):
                    raise ValueError("Section missing title/type/content")

            print("✅ Parsed sections from", model_name, ":", [s.get("title") or s.get("type") for s in parsed])
            return parsed

        except json.JSONDecodeError as jde:
            print(f"❌ JSON decode error for {model_name}:", jde)
            last_err = str(jde)
            continue
        except Exception as e:
            print(f"❌ Model {model_name} failed:", e)
            last_err = str(e)
            continue

    return {"error": f"All candidate models failed. Last error: {last_err}"}


def parse_resume_file(filepath):
    txt = extract_text_from_file(filepath)
    return generate_portfolio_sections(txt)
