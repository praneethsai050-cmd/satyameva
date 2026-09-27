"""
Gemini AI service for extracting document metadata from uploaded files.

Uses the official google-genai SDK with multimodal input to reliably extract
student name, roll number, document type, and title from uploaded PDFs and images.
"""
from __future__ import annotations

import json
import logging
import re

log = logging.getLogger(__name__)

# Accepted document types that Satyameva recognizes
_KNOWN_TYPES = {
    'DEGREE': ('DEGREE', 'DEGREE CERTIFICATE', 'BACHELOR', 'MASTER', 'DOCTOR', 'B.TECH', 'M.TECH'),
    'MARKSHEET': ('MARKSHEET', 'TRANSCRIPT', 'GRADE CARD', 'MARK SHEET'),
    'TC': ('TC', 'TRANSFER CERTIFICATE', 'TRANSFER'),
    'MIGRATION': ('MIGRATION', 'MIGRATION CERTIFICATE'),
    'BONAFIDE': ('BONAFIDE', 'BONAFIDE CERTIFICATE', 'BONA FIDE'),
    'INTERNSHIP': ('INTERNSHIP', 'INTERNSHIP CERTIFICATE', 'TRAINING'),
}

_SYSTEM_PROMPT = """You are an academic document parser for an Indian university verification system.
Extract the following fields from the provided document image or PDF:
- student_name: full legal name of the student
- roll_number: student roll / enrollment / registration number
- student_email: email address of the student if found on the document
- doc_type: one of DEGREE, MARKSHEET, TC, MIGRATION, BONAFIDE, or INTERNSHIP
- title: exact credential title (e.g. "Bachelor of Technology in Computer Science")
- institution: name of the issuing university or institute

Respond ONLY with a valid JSON object in this exact format:
{"student_name": "...", "roll_number": "...", "student_email": "...", "doc_type": "...", "title": "...", "institution": "..."}

If a field cannot be determined, use an empty string "" for it.
Do not output any markdown or explanation outside the JSON."""


def _match_doc_type(raw_type: str) -> str:
    """Normalize and match extracted document type against recognized system types."""
    upper = (raw_type or '').upper().strip()
    for key, aliases in _KNOWN_TYPES.items():
        if upper == key or any(alias in upper for alias in aliases):
            return key
    return ''


def extract_document_fields(
    file_bytes: bytes,
    mime_type: str,
    api_key: str,
) -> dict[str, str]:
    """
    Send the uploaded document to Gemini and return extracted fields.

    Returns:
        dict with keys: student_name, roll_number, doc_type, title, institution.
        On any failure returns an empty dict so user can enter data manually.
    """
    if not api_key:
        log.warning('GEMINI_API_KEY not configured — skipping AI extraction')
        return {}

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
        prompt = "Extract student_name, roll_number, doc_type, title, and institution from this document."

        # Model cascade: try fast & responsive models in order
        candidate_models = ['gemini-3.1-flash-lite', 'gemini-3.5-flash-lite', 'gemini-flash-latest']
        response_text = None

        for model_name in candidate_models:
            try:
                resp = client.models.generate_content(
                    model=model_name,
                    contents=[part, prompt],
                    config=types.GenerateContentConfig(
                        system_instruction=_SYSTEM_PROMPT,
                        response_mime_type="application/json",
                        temperature=0.1,
                    )
                )
                if resp and resp.text:
                    response_text = resp.text.strip()
                    break
            except Exception as model_err:
                log.info('Model %s returned: %s, trying next candidate...', model_name, model_err)

        if not response_text:
            return {}

        # Strip markdown fences if present
        raw = response_text
        if '```' in raw:
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw, re.DOTALL)
            if match:
                raw = match.group(1)
            else:
                raw = raw.replace('```json', '').replace('```', '').strip()

        data = json.loads(raw)

        return {
            'student_name': str(data.get('student_name') or '').strip(),
            'roll_number': str(data.get('roll_number') or '').strip(),
            'student_email': str(data.get('student_email') or '').strip().lower(),
            'doc_type': _match_doc_type(str(data.get('doc_type') or '')),
            'title': str(data.get('title') or '').strip(),
            'institution': str(data.get('institution') or '').strip(),
        }

    except Exception as exc:
        log.warning('Gemini extraction failed: %s', exc)
        return {}
