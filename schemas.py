from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class ProjectInfo(BaseModel):
    project_name: str = "Sample Construction Project"
    location: str = "Not specified"
    building_type: str = "Residential"
    area_sqft: float = Field(default=1000, gt=0)
    floors: int = Field(default=1, ge=1, le=100)
    budget_inr: Optional[float] = Field(default=None, gt=0)
    stage: str = "Under construction"


class Finding(BaseModel):
    title: str
    severity: str
    description: str
    recommendation: str


class AnalysisResponse(BaseModel):
    mode: str
    summary: str
    safety_findings: List[Finding]
    crack_findings: List[Finding]
    planning_advice: List[str]
    limitations: List[str]
    project: Dict[str, Any]


class EstimateRequest(BaseModel):
    area_sqft: float = Field(gt=0, le=10_000_000)
    floors: int = Field(default=1, ge=1, le=100)
    budget_inr: Optional[float] = Field(default=None, gt=0)


class ValuationRequest(BaseModel):
    area_sqft: float = Field(gt=0, le=10_000_000)
    rate_per_sqft: float = Field(gt=0)
    age_years: float = Field(default=0, ge=0, le=200)
    condition: Literal["Excellent", "Good", "Fair", "Poor"] = "Good"


class PlanRequest(BaseModel):
    area_sqft: float = Field(gt=0, le=10_000_000)
    floors: int = Field(default=1, ge=1, le=100)
    building_type: Literal["Residential", "Commercial", "Industrial", "Infrastructure"] = "Residential"
