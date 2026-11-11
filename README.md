# Federal Grant Application Tracker

A portfolio demonstration of government-grant application operations, built with **Python, SQLite, FastAPI, Streamlit, pandas, and Altair**.

## What it does

- **Overview:** application counts and charts by status and priority.
- **Applications:** filter applications, view details and status history, update statuses, and export CSV records.
- **Reviewers:** compare assignments and pending decision workload.
- **Funding:** summarize requested funding by grant program.
- **API:** read applications, create demo applications, and perform validated status transitions with history tracking.

### Data provenance and scope

The SQLite database contains **real HRSA grant identifiers and historical award records**, originally imported from HRSA Active Grants and Awarded Grants files. **Applicants, reviewers, application submissions, requested funding, statuses, and review histories are simulated demonstration records**, not actual HRSA application or review data. Funding cards reflect *simulated requested funding*, not HRSA dollars awarded. The demo's simple funding-based priority classification is illustrative, not an official federal grant policy.

The bundled SQLite file is a snapshot for running the demo. No user authentication or authorization layer is implemented: the API checks that the supplied reviewer ID matches the assigned reviewer, but this is **not identity verification**. Do not deploy this demo publicly with write access or use it for real grant decisions without appropriate security, data governance, and access controls.

## Project structure

```text
federal-grant-tracker/
├── main.py                 # FastAPI application
├── dashboard.py            # Streamlit dashboard
├── federal_grants.db       # SQLite demo snapshot
├── assets/
│   ├── capitol_icon.svg
│   └── capitol_sidebar.svg
├── tests/
│   └── test_workflow.py
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Run locally

Requires **Python 3.10+**.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Open **two terminals**, both with the virtual environment activated and both in the project folder.

Terminal 1 — start API:

```bash
uvicorn main:app --reload
```

Terminal 2 — start dashboard:

```bash
streamlit run dashboard.py
```

Visit the Streamlit URL printed in Terminal 2 (typically `http://localhost:8501`). API docs are available at `http://127.0.0.1:8000/docs`.

The dashboard expects the API at `http://127.0.0.1:8000`. Start the API before the dashboard.

## Run automated tests

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

Tests use **a temporary copy of the database**, leaving the bundled demo snapshot untouched. They check API reads, a valid status transition and history entry, duplicate-transition rejection, and the data/CSV round trip. They do not automate a browser click on the Streamlit CSV download button.

## Example workflow

1. Open **Applications**, filter by status or reviewer, and inspect a selected application's history.
2. Choose an application **Under Review** and update it to **Approved** or **Rejected** with review notes.
3. Confirm the status appears in the application table and history, and observe updated Overview/Reviewer summaries.
4. Export the applications as CSV.

**Note:** Updating records changes the local database snapshot. To reset the demo, replace `federal_grants.db` with a fresh copy from this repository.

## Design notes

The dashboard uses a navy, teal, and gold theme, custom Capitol SVG assets, and matching metric cards. The API uses SQLite foreign keys and records each permitted status transition in `status_history`. The workflow allows `Submitted → Under Review → Approved/Rejected`; approved and rejected are terminal states.

## Future improvements

Authentication and role-based access control, audit actor identity, migration tooling, configuration for API URL/database location, pagination, broader automated tests, and production-grade deployment.
