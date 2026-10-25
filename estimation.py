from typing import Dict, Any

# Illustrative rates only. Replace with verified local rates and engineering quantities.
MATERIAL_RATES = {
    "cement_bag": 420.0,
    "sand_cuft": 55.0,
    "aggregate_cuft": 65.0,
    "steel_kg": 68.0,
    "bricks_piece": 10.0,
}

def estimate_materials(area_sqft: float, floors: int = 1) -> Dict[str, Any]:
    if area_sqft <= 0 or floors < 1:
        raise ValueError("Area must be positive and floors must be at least 1.")
    built_area = area_sqft * floors
    # Very rough demonstration factors, not a bill of quantities.
    quantities = {
        "cement_bag": round(built_area * 0.40, 1),
        "sand_cuft": round(built_area * 1.80, 1),
        "aggregate_cuft": round(built_area * 1.20, 1),
        "steel_kg": round(built_area * 3.5, 1),
        "bricks_piece": round(built_area * 8, 0),
    }
    items = []
    for material, qty in quantities.items():
        rate = MATERIAL_RATES[material]
        items.append({
            "material": material.replace("_", " ").title(),
            "quantity": qty,
            "unit": {"cement_bag":"bags", "sand_cuft":"cu ft", "aggregate_cuft":"cu ft",
                     "steel_kg":"kg", "bricks_piece":"pieces"}[material],
            "illustrative_rate_inr": rate,
            "estimated_cost_inr": round(qty * rate, 2)
        })
    return {
        "built_area_sqft": built_area,
        "items": items,
        "total_material_cost_inr": round(sum(x["estimated_cost_inr"] for x in items), 2),
        "disclaimer": "Illustrative estimate only. Verify quantities and local rates with a qualified professional."
    }

def estimate_valuation(area_sqft: float, rate_per_sqft: float, age_years: float = 0,
                       condition: str = "Good") -> Dict[str, Any]:
    if area_sqft <= 0 or rate_per_sqft <= 0 or age_years < 0:
        raise ValueError("Area and rate must be positive; age cannot be negative.")
    depreciation = min(age_years * 0.01, 0.30)
    condition_factor = {"Excellent": 1.05, "Good": 1.0, "Fair": 0.90, "Poor": 0.75}.get(condition, 1.0)
    value = area_sqft * rate_per_sqft * (1 - depreciation) * condition_factor
    return {
        "area_sqft": area_sqft,
        "base_rate_inr_per_sqft": rate_per_sqft,
        "age_years": age_years,
        "condition": condition,
        "illustrative_value_inr": round(value, 2),
        "disclaimer": "Not a formal appraisal. Use recent comparable sales and a qualified local valuer."
    }


def add_budget_check(estimate: Dict[str, Any], budget_inr: float) -> Dict[str, Any]:
    """Compare material cost with a total budget. Materials are only one part of total cost."""
    total = estimate["total_material_cost_inr"]
    estimate["budget_inr"] = budget_inr
    estimate["budget_usage_percent"] = round(total / budget_inr * 100, 1)
    estimate["within_budget"] = total <= budget_inr
    estimate["budget_note"] = (
        "Materials are only one part of total cost. Labour, design, approvals, finishes, "
        "contingency and taxes must also fit within the budget."
    )
    return estimate


# Illustrative phase shares of total duration and key checks per phase.
_PHASES = [
    ("Design, drawings & approvals", 0.15, ["Finalise structural drawings", "Obtain local permits", "Soil investigation"]),
    ("Site preparation & foundation", 0.15, ["Verify setting-out", "Inspect reinforcement before pouring", "Curing records"]),
    ("Structure (columns, beams, slabs)", 0.30, ["Concrete cube tests", "Check formwork and props", "Cover and bar spacing"]),
    ("Masonry, MEP rough-in", 0.15, ["Coordinate services before plastering", "Pressure-test plumbing"]),
    ("Finishing", 0.20, ["Waterproofing checks", "Quality snag list"]),
    ("Inspection & handover", 0.05, ["Final safety inspection", "Occupancy / completion certificate"]),
]
_TYPE_FACTOR = {"Residential": 1.0, "Commercial": 1.3, "Industrial": 1.2, "Infrastructure": 1.6}


def plan_project(area_sqft: float, floors: int = 1, building_type: str = "Residential") -> Dict[str, Any]:
    if area_sqft <= 0 or floors < 1:
        raise ValueError("Area must be positive and floors must be at least 1.")
    built_area = area_sqft * floors
    months = (3 + built_area / 1000 * 1.5 + floors * 0.5) * _TYPE_FACTOR.get(building_type, 1.0)
    months = round(min(max(months, 2), 60), 1)
    phases, start = [], 0.0
    for name, share, checks in _PHASES:
        duration = round(months * share, 1)
        phases.append({
            "phase": name,
            "start_month": round(start, 1),
            "end_month": round(start + duration, 1),
            "duration_months": duration,
            "key_checks": checks,
        })
        start += duration
    return {
        "building_type": building_type,
        "built_area_sqft": built_area,
        "total_duration_months": months,
        "phases": phases,
        "disclaimer": "Illustrative schedule only. Real timelines depend on approvals, weather, labour, and contractor capacity.",
    }
