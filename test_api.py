import io
import os

os.environ["GEMINI_API_KEY"] = ""  # force demo mode

from fastapi.testclient import TestClient
from PIL import Image

from app.estimation import estimate_materials, estimate_valuation, plan_project
from app.main import app

client = TestClient(app)


def _png() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (4, 4), "gray").save(buf, "PNG")
    return buf.getvalue()


def test_health():
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["ai_mode"] == "demo"


def test_estimate_math():
    r = estimate_materials(1000, 2)
    assert r["built_area_sqft"] == 2000
    assert r["total_material_cost_inr"] == round(sum(i["estimated_cost_inr"] for i in r["items"]), 2)


def test_estimate_endpoint_budget():
    r = client.post("/api/estimate", json={"area_sqft": 1000, "floors": 1, "budget_inr": 10_000_000})
    assert r.status_code == 200
    body = r.json()
    assert body["within_budget"] is True and body["budget_usage_percent"] > 0


def test_estimate_rejects_bad_input():
    assert client.post("/api/estimate", json={"area_sqft": -5}).status_code == 422


def test_valuation():
    v = estimate_valuation(1000, 3500, 10, "Fair")
    assert v["illustrative_value_inr"] == round(1000 * 3500 * 0.9 * 0.9, 2)
    assert client.post("/api/valuation", json={"area_sqft": 1000, "rate_per_sqft": 3500, "condition": "Bad"}).status_code == 422


def test_plan_phases_are_contiguous():
    p = plan_project(2000, 2, "Commercial")
    assert p["phases"][0]["start_month"] == 0
    assert abs(p["phases"][-1]["end_month"] - p["total_duration_months"]) < 0.5
    assert client.post("/api/plan", json={"area_sqft": 1500}).status_code == 200


def test_analyze_demo_text_only():
    r = client.post("/api/analyze", data={"description": "cracks near column"})
    assert r.status_code == 200 and r.json()["mode"] == "demo"


def test_analyze_with_image():
    r = client.post("/api/analyze", files={"image": ("a.png", _png(), "image/png")})
    assert r.status_code == 200


def test_analyze_rejects_fake_image_and_bad_type():
    r = client.post("/api/analyze", files={"image": ("a.png", b"not an image", "image/png")})
    assert r.status_code == 400
    r = client.post("/api/analyze", files={"image": ("a.txt", b"hi", "text/plain")})
    assert r.status_code == 415


def test_analyze_bad_project_json():
    assert client.post("/api/analyze", data={"project_json": "{bad"}).status_code == 422
