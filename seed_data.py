"""Seed data for PowerWise Malaysia demo scenarios.

Creates a realistic household history where:
- Normal months: ~300-350 kWh (within RM200 budget)
- Recent months: spike to ~500 kWh due to hot weather (AC heavy usage)
- This triggers budget alerts and AC-specific recommendations
"""

import numpy as np
from datetime import datetime, timedelta
import db


def seed():
    db.init_db()

    if db.get_device_count() > 0:
        print("Database already seeded. Delete powerwise.db to reseed.")
        return

    # ── Household profile (Aisyah's family in KL) ─────────────────────────────
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
    # Normal months ~300-350 kWh, last 2 months spike to 480-520 kWh (hot season)
    import tariff

    bills_data = [
        ("2025-06", 310), ("2025-07", 325), ("2025-08", 340),
        ("2025-09", 305), ("2025-10", 295), ("2025-11", 320),
        ("2025-12", 350), ("2026-01", 330), ("2026-02", 315),
        ("2026-03", 380),  # starting to get hotter
        ("2026-04", 485),  # hot season spike
        ("2026-05", 520),  # current month — over budget!
    ]

    for month, kwh in bills_data:
        bill = tariff.calculate_bill(kwh)
        db.add_bill(month, kwh, bill["total"])

    print(f"Added {len(bills_data)} monthly bills")

    # ── Hourly energy readings (last 30 days, shows AC-heavy pattern) ─────────
    np.random.seed(42)
    days = 30
    num_points = days * 24
    start_time = datetime.now() - timedelta(days=days)

    readings = []
    cumulative = 14500.0  # realistic cumulative reading

    for i in range(num_points):
        ts = start_time + timedelta(hours=i)
        hour = ts.hour

        # Simulate hot-weather household: heavy AC from noon to midnight
        if 0 <= hour <= 5:
            base_power = 200   # standby + fridge
        elif 6 <= hour <= 8:
            base_power = 800   # morning routine
        elif 9 <= hour <= 11:
            base_power = 400   # out at work
        elif 12 <= hour <= 17:
            base_power = 1800  # AC on full blast (hot afternoon)
        elif 18 <= hour <= 22:
            base_power = 2200  # evening: AC + cooking + TV + lights
        else:
            base_power = 1200  # AC still on at night (hot)

        noise = np.random.normal(0, 0.1)
        power = max(100, base_power * (1 + noise))

        # Spikes: kettle, iron, oven
        if np.random.random() < 0.03:
            power += np.random.uniform(1000, 2500)

        delta_kwh = power / 1000.0  # 1 hour
        cumulative += delta_kwh

        readings.append((meter_id, ts.isoformat(), round(cumulative, 2), 0.0, round(power, 1)))

    db.add_readings_bulk(readings)
    print(f"Added {len(readings)} hourly readings (30 days)")

    # ── Appliances registered ─────────────────────────────────────────────────
    db.add_appliance("Living Room AC", "air_conditioner", 1500, 10.0, "3-star", 2018)
    db.add_appliance("Bedroom AC", "air_conditioner", 1200, 8.0, "3-star", 2019)
    db.add_appliance("Refrigerator", "refrigerator", 150, 24.0, "2-star", 2015)
    db.add_appliance("Washing Machine", "washing_machine", 500, 1.0, "4-star", 2021)
    print("Added 4 household appliances")

    print("\n✅ Demo ready! Run: streamlit run app.py")
    print("   - Dashboard shows budget EXCEEDED (RM520 bill vs RM200 budget)")
    print("   - Usage Analysis shows evening/afternoon AC peaks")
    print("   - Appliance Savings shows AC upgrade comparison + SAVE 4.0 rebate")


if __name__ == "__main__":
    seed()
