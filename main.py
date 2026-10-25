import io
import json
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError
from pydantic import ValidationError

from .ai_service import analyze
from .estimation import add_budget_check, estimate_materials, estimate_valuation, plan_project
from .schemas import (AnalysisResponse, EstimateRequest, PlanRequest, ProjectInfo,
                      ValuationRequest)

load_dotenv()
app = FastAPI(title="Construction AI Assistant API", version="1.1.0")

origins = {o.strip() for o in os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").split(",") if o.strip()}
origins.add("http://127.0.0.1:5173")
app.add_middleware(
    CORSMiddleware, allow_origins=sorted(origins),
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

MAX_IMAGE_BYTES = 10 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
DEFAULT_PROJECT = json.dumps({
    "project_name": "Sample Construction Project", "location": "Not specified",
    "building_type": "Residential", "area_sqft": 1000, "floors": 1, "stage": "Under construction",
})


@app.get("/health")
def health():
    live = bool(os.getenv("GEMINI_API_KEY", "").strip())
    return {"status": "ok", "service": "Construction AI Assistant", "ai_mode": "gemini" if live else "demo"}


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_site(
    description: str = Form(default="", max_length=5000),
    project_json: str = Form(default=DEFAULT_PROJECT),
    image: Optional[UploadFile] = File(default=None),
):
    try:
        project = ProjectInfo.model_validate(json.loads(project_json)).model_dump()
    except (json.JSONDecodeError, ValidationError) as exc:
        raise HTTPException(status_code=422, detail=f"Invalid project_json: {exc}") from exc

    image_bytes, mime_type = None, "image/jpeg"
    if image and image.filename:
        if image.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=415, detail="Upload a JPEG, PNG, or WEBP image.")
        image_bytes = await image.read(MAX_IMAGE_BYTES + 1)
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Uploaded image is empty.")
        if len(image_bytes) > MAX_IMAGE_BYTES:
            raise HTTPException(status_code=413, detail="Image must be 10 MB or smaller.")
        try:  # confirm the bytes really are an image, whatever the client claimed
            with Image.open(io.BytesIO(image_bytes)) as img:
                img.verify()
        except (UnidentifiedImageError, OSError) as exc:
            raise HTTPException(status_code=400, detail="File is not a valid image.") from exc
        mime_type = image.content_type

    try:
        result = await analyze(description, project, image_bytes, mime_type)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Analysis failed: {exc}") from exc
    result["project"] = project
    return result


@app.post("/api/estimate")
def estimate(req: EstimateRequest):
    try:
        result = estimate_materials(req.area_sqft, req.floors)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if req.budget_inr:
        add_budget_check(result, req.budget_inr)
    return result


@app.post("/api/valuation")
def valuation(req: ValuationRequest):
    try:
        return estimate_valuation(req.area_sqft, req.rate_per_sqft, req.age_years, req.condition)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/plan")
def plan(req: PlanRequest):
    try:
        return plan_project(req.area_sqft, req.floors, req.building_type)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
