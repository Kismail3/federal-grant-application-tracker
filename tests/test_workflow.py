"""Non-destructive integration tests using a temporary copy of the demo database."""
import csv
import io
import shutil

import pytest
from fastapi.testclient import TestClient
import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    copied_db = tmp_path / 'federal_grants.db'
    shutil.copy2(main.DB_PATH, copied_db)
    monkeypatch.setattr(main, 'DB_PATH', copied_db)
    with TestClient(main.app) as test_client:
        yield test_client


def test_database_and_read_endpoints(client):
    health = client.get('/health')
    assert health.status_code == 200
    assert health.json()['application_count'] == 5
    applications = client.get('/applications')
    assert applications.status_code == 200
    assert len(applications.json()) == 5
    assert client.get('/applications/999999').status_code == 404


def test_reviewer_status_transition_and_history(client):
    applications = client.get('/applications').json()
    candidate = next(a for a in applications if a['status'] == 'Under Review')
    application_id = candidate['application_id']
    detail = client.get(f'/applications/{application_id}').json()
    reviewer_id = detail['reviewer_id']
    assert reviewer_id is not None
    before = client.get(f'/applications/{application_id}/history').json()['history']

    response = client.patch(
        f'/applications/{application_id}/status',
        json={'new_status': 'Approved', 'reviewer_id': reviewer_id,
              'notes': 'Automated test on temporary database copy'},
    )
    assert response.status_code == 200, response.text
    assert client.get(f'/applications/{application_id}').json()['status'] == 'Approved'
    after = client.get(f'/applications/{application_id}/history').json()['history']
    assert len(after) == len(before) + 1
    assert after[-1]['old_status'] == 'Under Review'
    assert after[-1]['new_status'] == 'Approved'

    repeat = client.patch(
        f'/applications/{application_id}/status',
        json={'new_status': 'Approved', 'reviewer_id': reviewer_id},
    )
    assert repeat.status_code == 409


def test_csv_export_data_roundtrip(client):
    """Validates the same application records and CSV serialization used by Streamlit."""
    import pandas as pd
    rows = client.get('/applications').json()
    df = pd.DataFrame(rows)
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    parsed = list(csv.DictReader(io.StringIO(csv_bytes.decode('utf-8'))))
    assert len(parsed) == len(rows) == 5
    assert {'application_id', 'organization_name', 'requested_amount', 'status'} <= set(parsed[0])
    assert sum(float(row['requested_amount']) for row in parsed) == 3950000
