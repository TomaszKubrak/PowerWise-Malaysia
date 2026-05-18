# PowerWise Malaysia

Household energy tracking app built with Streamlit.

## Features

- **Dashboard** — Real-time KPIs (power, consumption, export) and interactive Plotly charts with configurable time range and bin intervals
- **Device Management** — Add/remove energy meters, view connection status and latest readings
- **Data Ingestion** — Manual entry, webhook simulator (HardWario-compatible JSON), and sample data generator for testing

## Quick Start

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app uses SQLite (auto-created `powerwise.db`) — no external database needed.
