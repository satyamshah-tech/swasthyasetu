# SwasthyaSetu — Smart Health Hackathon MVP

A responsive decision-support dashboard for the challenge: AI-driven health centre and supply chain management.

## Demo features
- Four sample PHC/CHC facilities.
- District-level patient footfall, bed availability, doctor attendance and diagnostics.
- Medicine stock, expiry, bed-pressure, staff and test-availability alerts.
- Transparent 7-day trend extrapolation for patient demand.
- Rule-based medicine redistribution proposal for human review.
- Interactive centre updates and a patient-surge/medicine-use scenario simulation.
- Search facilities and switch dashboard labels between English and Hindi.

## Important
All data is synthetic demo data, not live government or hospital data. The forecast is simple trend extrapolation, not a trained ML model. Alerts and redistribution are decision support, not automatic clinical or supply-chain decisions. Do not enter patient-identifiable information.

This app writes demo values to `data.json`. Cloud Run's local filesystem is not durable and may not be shared between instances. For a production system, replace it with a managed database and add authentication, role-based access, audit logs, secure APIs, encryption and privacy review.

## Run locally
Python 3.10+ recommended.
1. Extract the ZIP.
2. Open this folder in VS Code.
3. Run `python -m venv .venv`
4. Windows: `.venv\\Scripts\\activate`
5. Run `pip install -r requirements.txt`
6. Run `python app.py`
7. Open `http://127.0.0.1:8080`

## Deploy to Render
This repository is currently configured for a Render Web Service.

1. Create a new **Web Service** connected to this GitHub repository.
2. Build command: `pip install -r requirements.txt`
3. Start command: `gunicorn app:app`
4. Deploy, then open the service URL. Check `/health` for a basic status response.

### Demo data persistence
The prototype reads and writes `data.json` on the service's local filesystem. Local files may not survive a restart or redeploy, and they are not shared as a database across multiple instances. Use a managed database or host-supported persistent storage if demo changes must be retained reliably. Keep synthetic data only; do not enter real patient information.

## Suggested judge pitch
"SwasthyaSetu helps district health teams spot shortages earlier by putting medicine inventory, bed pressure, doctor attendance and diagnostics in one operational view. The prototype raises transparent threshold-based alerts, shows a simple demand trend and proposes a stock transfer for staff review. Today it uses synthetic data; the next phase would connect approved facility data sources, validate forecasts on historical records, and add secure role-based workflows."
