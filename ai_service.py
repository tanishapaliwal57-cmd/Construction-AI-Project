import asyncio
import json
import os
from typing import Any, Dict, Optional
from google import genai
from google.genai import types

SYSTEM_INSTRUCTION = """
You are an assistant for construction project planning. Analyze only what is visible/provided.
Return one JSON object matching this schema:
{
 "summary": "string",
 "safety_findings": [{"title":"string","severity":"Low|Medium|High|Unknown","description":"string","recommendation":"string"}],
 "crack_findings": [{"title":"string","severity":"Low|Medium|High|Unknown","description":"string","recommendation":"string"}],
 "planning_advice": ["string"],
 "limitations": ["string"]
}
Do not claim to certify structural safety. If image evidence is insufficient, say so and use Unknown.
Do not infer hidden defects. Recommendations must advise qualified professional review for high-risk findings.
"""

def _demo_analysis(description: str, project: Dict[str, Any], has_image: bool) -> Dict[str, Any]:
    return {
        "summary": (
            "Demo mode: no live AI analysis was performed. "
            + ("An image was uploaded, but configure GEMINI_API_KEY to analyze it." if has_image else
               "Provide an image and configure GEMINI_API_KEY for multimodal analysis.")
        ),
        "safety_findings": [{
            "title": "Site safety review required",
            "severity": "Unknown",
            "description": "This demo response does not inspect or verify site conditions.",
            "recommendation": "Have a competent site supervisor inspect PPE, access, edges, scaffolding, and housekeeping."
        }],
        "crack_findings": [{
            "title": "Crack assessment unavailable in demo mode",
            "severity": "Unknown",
            "description": "No crack type or severity can be reliably determined without live image analysis and expert inspection.",
            "recommendation": "If a crack is visible, document its width and progression and request a structural engineer's assessment."
        }],
        "planning_advice": [
            "Confirm drawings, measurements, permits, and scope before scheduling work.",
            "Track dependencies, material lead times, inspections, and weather constraints."
        ],
        "limitations": [
            "Demo mode: AI provider was not called.",
            "Image-based screening is not a substitute for an on-site safety or structural inspection."
        ]
    }

async def analyze(description: str, project: Dict[str, Any], image_bytes: Optional[bytes], mime_type: str) -> Dict[str, Any]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        result = _demo_analysis(description, project, image_bytes is not None)
        result["mode"] = "demo"
        return result

    client = genai.Client(api_key=api_key)
    prompt = (
        f"{SYSTEM_INSTRUCTION}\n\nProject information:\n{json.dumps(project, ensure_ascii=False)}"
        f"\n\nUser description:\n{description or 'No description provided.'}\n"
        "Return JSON only. Be cautious and distinguish visible evidence from uncertainty."
    )
    contents = [prompt]
    if image_bytes:
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type or "image/jpeg"))
    # The Gemini SDK call is synchronous; run it in a thread so the event loop isn't blocked.
    response = await asyncio.to_thread(
        client.models.generate_content,
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=contents,
        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2),
    )
    try:
        data = json.loads(response.text or "{}")
    except json.JSONDecodeError as exc:
        raise RuntimeError("AI provider returned invalid JSON. Please retry.") from exc
    # Validate expected top-level fields and supply safe defaults.
    if not isinstance(data, dict):
        raise RuntimeError("AI provider returned an unexpected format. Please retry.")
    data.setdefault("summary", "Analysis returned incomplete information.")
    data.setdefault("safety_findings", [])
    data.setdefault("crack_findings", [])
    data.setdefault("planning_advice", [])
    data.setdefault("limitations", [])
    data["mode"] = "gemini"
    return data
