"""TNB Malaysia residential tariff calculator (Tariff A - Domestic)

Based on TNB's tiered pricing structure for domestic consumers.
Rates as of 2024 (sen/kWh):
  Block 1:   1-200 kWh   → 21.80 sen
  Block 2: 201-300 kWh   → 33.40 sen
  Block 3: 301-600 kWh   → 51.60 sen
  Block 4: 601-900 kWh   → 54.60 sen
  Block 5: 901+ kWh      → 57.10 sen

Minimum charge: RM3.00
Service tax (6%) applies on bills > RM28.50/month
KWTBB (1.6%) renewable energy surcharge
"""

TNB_TIERS = [
    (200, 0.218),   # Block 1: first 200 kWh at RM0.218/kWh
    (100, 0.334),   # Block 2: next 100 kWh at RM0.334/kWh
    (300, 0.516),   # Block 3: next 300 kWh at RM0.516/kWh
    (300, 0.546),   # Block 4: next 300 kWh at RM0.546/kWh
    (float('inf'), 0.571),  # Block 5: remainder at RM0.571/kWh
]

MINIMUM_CHARGE = 3.00
SERVICE_TAX_RATE = 0.06
SERVICE_TAX_THRESHOLD = 28.50
KWTBB_RATE = 0.016


def calculate_bill(kwh: float, include_tax: bool = True) -> dict:
    """Calculate TNB bill for given kWh consumption.

    Returns dict with breakdown: base_cost, service_tax, kwtbb, total, tier_breakdown.
    """
    if kwh <= 0:
        return {"base_cost": 0, "service_tax": 0, "kwtbb": 0, "total": 0, "tier_breakdown": []}

    remaining = kwh
    base_cost = 0.0
    tier_breakdown = []

    for limit, rate in TNB_TIERS:
        if remaining <= 0:
            break
        used_in_tier = min(remaining, limit)
        cost = used_in_tier * rate
        tier_breakdown.append({
            "kwh": used_in_tier,
            "rate": rate,
            "cost": cost,
        })
        base_cost += cost
        remaining -= used_in_tier

    base_cost = max(base_cost, MINIMUM_CHARGE)

    service_tax = 0.0
    kwtbb = 0.0
    if include_tax:
        if base_cost > SERVICE_TAX_THRESHOLD:
            service_tax = base_cost * SERVICE_TAX_RATE
        kwtbb = base_cost * KWTBB_RATE

    total = base_cost + service_tax + kwtbb

    return {
        "base_cost": round(base_cost, 2),
        "service_tax": round(service_tax, 2),
        "kwtbb": round(kwtbb, 2),
        "total": round(total, 2),
        "tier_breakdown": tier_breakdown,
    }


def estimate_monthly_cost(kwh_per_day: float) -> float:
    """Estimate monthly bill from daily consumption rate."""
    monthly_kwh = kwh_per_day * 30
    return calculate_bill(monthly_kwh)["total"]


def get_tier_for_kwh(kwh: float) -> int:
    """Return which tariff block (1-5) the household falls into."""
    if kwh <= 200:
        return 1
    elif kwh <= 300:
        return 2
    elif kwh <= 600:
        return 3
    elif kwh <= 900:
        return 4
    else:
        return 5


def format_bill_explanation(kwh: float, budget: float, language: str = "en") -> str:
    """Generate plain-language bill explanation."""
    bill = calculate_bill(kwh)
    tier = get_tier_for_kwh(kwh)
    total = bill["total"]
    over_budget = total > budget
    pct_of_budget = (total / budget * 100) if budget > 0 else 0

    if language == "ms":
        msg = f"Penggunaan anda bulan ini: {kwh:.0f} kWh\n"
        msg += f"Anggaran bil: RM {total:.2f}\n"
        msg += f"Blok tarif: Blok {tier}\n\n"
        if over_budget:
            msg += f"⚠️ AMARAN: Bil anda melebihi bajet (RM {budget:.2f}) sebanyak RM {total - budget:.2f}.\n"
            msg += f"Bil anda adalah {pct_of_budget:.0f}% daripada bajet bulanan."
        else:
            remaining = budget - total
            msg += f"✅ Anda masih dalam bajet. Baki: RM {remaining:.2f}"
    else:
        msg = f"Your usage this month: {kwh:.0f} kWh\n"
        msg += f"Estimated bill: RM {total:.2f}\n"
        msg += f"Tariff block: Block {tier}\n\n"
        if over_budget:
            msg += f"⚠️ WARNING: Your bill exceeds your budget (RM {budget:.2f}) by RM {total - budget:.2f}.\n"
            msg += f"Your bill is {pct_of_budget:.0f}% of your monthly budget."
        else:
            remaining = budget - total
            msg += f"✅ You are within budget. Remaining: RM {remaining:.2f}"

    return msg


REBATE_PROGRAMS = [
    {
        "name": "SAVE 4.0",
        "provider": "SEDA Malaysia",
        "description": "RM200 e-rebate for purchasing energy-efficient appliances (5-star rated air-conditioners and refrigerators)",
        "eligibility": "All Malaysian households. Appliance must be 5-star energy rated.",
        "amount": 200.0,
        "appliance_types": ["air_conditioner", "refrigerator"],
        "url": "https://www.seda.gov.my/saveprogram/",
    },
    {
        "name": "Program Nikmat Untuk Rakyat (NUR)",
        "provider": "SEDA Malaysia",
        "description": "Free solar PV installation for low-income households (B40)",
        "eligibility": "B40 households with monthly income below RM4,849.",
        "amount": 0.0,
        "appliance_types": ["solar"],
        "url": "https://www.seda.gov.my/nur/",
    },
]


APPLIANCE_DATABASE = {
    "air_conditioner": {
        "old_typical_watts": 1500,
        "efficient_watts": 900,
        "label": "Air Conditioner (1.5HP)",
        "efficient_label": "5-Star Inverter AC (1.5HP)",
    },
    "refrigerator": {
        "old_typical_watts": 150,
        "efficient_watts": 70,
        "label": "Refrigerator (Standard)",
        "efficient_label": "5-Star Inverter Fridge",
    },
    "washing_machine": {
        "old_typical_watts": 500,
        "efficient_watts": 300,
        "label": "Washing Machine",
        "efficient_label": "5-Star Front-Load Washer",
    },
    "water_heater": {
        "old_typical_watts": 3000,
        "efficient_watts": 800,
        "label": "Electric Water Heater",
        "efficient_label": "Heat Pump Water Heater",
    },
    "fan": {
        "old_typical_watts": 75,
        "efficient_watts": 35,
        "label": "Ceiling Fan",
        "efficient_label": "DC Motor Ceiling Fan",
    },
}


def compare_appliance(appliance_type: str, hours_per_day: float, current_watts: float | None = None) -> dict:
    """Compare old vs efficient appliance running costs."""
    info = APPLIANCE_DATABASE.get(appliance_type)
    if not info:
        return {}

    old_watts = current_watts or info["old_typical_watts"]
    new_watts = info["efficient_watts"]

    old_monthly_kwh = old_watts * hours_per_day * 30 / 1000
    new_monthly_kwh = new_watts * hours_per_day * 30 / 1000
    savings_kwh = old_monthly_kwh - new_monthly_kwh

    old_cost = calculate_bill(old_monthly_kwh)["total"]
    new_cost = calculate_bill(new_monthly_kwh)["total"]
    monthly_savings = old_cost - new_cost
    yearly_savings = monthly_savings * 12

    return {
        "old_label": info["label"],
        "new_label": info["efficient_label"],
        "old_watts": old_watts,
        "new_watts": new_watts,
        "old_monthly_kwh": round(old_monthly_kwh, 1),
        "new_monthly_kwh": round(new_monthly_kwh, 1),
        "savings_kwh": round(savings_kwh, 1),
        "old_monthly_cost": round(old_cost, 2),
        "new_monthly_cost": round(new_cost, 2),
        "monthly_savings": round(monthly_savings, 2),
        "yearly_savings": round(yearly_savings, 2),
    }
