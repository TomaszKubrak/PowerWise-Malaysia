"""Seed data for PowerWise Malaysia demo — aligned with presentation scenarios.

Scenario story:
- Aisyah's family in PJ, budget RM 200/month
- Normal months (Jun 2025–Feb 2026): 280–350 kWh, bills RM 77–110 (well within budget)
- March 2026: 450 kWh (RM ~166) — getting hotter, approaching budget warning
- April 2026: 550 kWh (RM ~222) — over budget, hot season
- May 2026: 650 kWh (RM ~279) — way over budget, peak hot season, AC running all day

This creates a clear visual spike in the dashboard chart and triggers budget alerts.
"""

import numpy as np
from datetime import datetime, timedelta
import db


def seed():
    db.init_db()

    if db.get_device_count() > 0:
        return

    # ── Household profile (Aisyah's family in PJ) ────────────────────────────
    db.update_household(
        household_name="Rumah Aisyah",
        location="Petaling Jaya",
        state="Selangor",
        provider="TNB",
        household_size=5,
        monthly_budget=200.0,
        alert_threshold=0.8,
        language="en",
    )

    # ── Meter ─────────────────────────────────────────────────────────────────
    meter_id = db.add_device("Main Meter", "MY-2024-8831")
    db.update_device_connection(meter_id, True)

    # ── Bill history (12 months) ──────────────────────────────────────────────
    import tariff

    bills_data = [
        ("2025-06", 290),
        ("2025-07", 310),
        ("2025-08", 320),
        ("2025-09", 295),
        ("2025-10", 280),
        ("2025-11", 305),
        ("2025-12", 330),
        ("2026-01", 315),
        ("2026-02", 340),
        ("2026-03", 450),   # hot season starts — approaching warning threshold
        ("2026-04", 550),   # over budget
        ("2026-05", 650),   # peak hot season — way over budget (~RM 279)
    ]

    for month, kwh in bills_data:
        bill = tariff.calculate_bill(kwh)
        db.add_bill(month, kwh, bill["total"])

    # ── Hourly energy readings (last 30 days) ─────────────────────────────────
    # Pattern shows clear AC-driven peaks from noon to night
    np.random.seed(42)
    days = 30
    num_points = days * 24
    start_time = datetime.now() - timedelta(days=days)

    readings = []
    cumulative = 14500.0

    for i in range(num_points):
        ts = start_time + timedelta(hours=i)
        hour = ts.hour

        # Hot-weather household: AC dominates afternoon and evening
        if 0 <= hour <= 5:
            base_power = 180    # fridge + standby only
        elif 6 <= hour <= 8:
            base_power = 700    # morning routine (water heater, cooking)
        elif 9 <= hour <= 11:
            base_power = 350    # family out, fridge + minimal
        elif 12 <= hour <= 14:
            base_power = 1900   # AC kicks in (hot afternoon)
        elif 15 <= hour <= 17:
            base_power = 2100   # peak heat, AC at full
        elif 18 <= hour <= 20:
            base_power = 2500   # evening: AC + cooking + TV + lights
        elif 21 <= hour <= 22:
            base_power = 1800   # winding down, AC still on
        else:
            base_power = 1000   # late night AC on low

        noise = np.random.normal(0, 0.12)
        power = max(100, base_power * (1 + noise))

        # Occasional spikes: kettle, iron, oven
        if np.random.random() < 0.03:
            power += np.random.uniform(1000, 2500)

        delta_kwh = power / 1000.0
        cumulative += delta_kwh

        readings.append((meter_id, ts.isoformat(), round(cumulative, 2), 0.0, round(power, 1)))

    db.add_readings_bulk(readings)

    # ── Household appliances (matches Scenario 2: AC upgrade decision) ────────
    db.add_appliance("Living Room AC", "air_conditioner", 1500, 10.0, "3-star", 2018)
    db.add_appliance("Bedroom AC", "air_conditioner", 1200, 8.0, "3-star", 2019)
    db.add_appliance("Refrigerator", "refrigerator", 150, 24.0, "2-star", 2015)
    db.add_appliance("Washing Machine", "washing_machine", 500, 1.0, "4-star", 2021)


if __name__ == "__main__":
    seed()
