
from pathlib import Path
import sqlite3

from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="Federal Grant Application Tracker",
    description="Demo API combining real HRSA grant data with simulated application workflows.",
    version="1.0.0"
)

DB_PATH = Path(__file__).resolve().parent / "federal_grants.db"


def get_connection():
    if not DB_PATH.is_file():
        raise RuntimeError("Database file not found.")

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@app.get("/")
def home():
    return {"message": "Federal Grant Application Tracker API"}


@app.get("/health")
def health():
    with get_connection() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM applications"
        ).fetchone()[0]

    return {
        "status": "ok",
        "application_count": count
    }


@app.get("/applications")
def get_applications():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                a.application_id,
                ap.organization_name,
                g.grant_program_name,
                r.reviewer_name,
                a.submission_date,
                a.requested_amount,
                a.status,
                a.priority
            FROM applications a
            JOIN applicants ap
                ON a.applicant_id = ap.applicant_id
            JOIN grants g
                ON a.grant_number = g.grant_number
            LEFT JOIN reviewers r
                ON a.reviewer_id = r.reviewer_id
            ORDER BY a.application_id
        """).fetchall()

    return [dict(row) for row in rows]


from datetime import date
from pydantic import BaseModel, Field


class ApplicationCreate(BaseModel):
    applicant_id: int
    grant_number: str
    reviewer_id: int | None = None
    submission_date: date
    requested_amount: float = Field(ge=0)


def classify_priority(amount):
    if amount >= 1_000_000:
        return "High"
    elif amount >= 500_000:
        return "Normal"
    return "Low"


@app.post("/applications", status_code=201)
def create_application(application: ApplicationCreate):

    priority = classify_priority(
        application.requested_amount
    )

    try:
        with get_connection() as conn:

            cursor = conn.execute("""
                INSERT INTO applications (
                    applicant_id,
                    grant_number,
                    reviewer_id,
                    submission_date,
                    requested_amount,
                    status,
                    priority
                )
                VALUES (?, ?, ?, ?, ?, 'Submitted', ?)
            """, (
                application.applicant_id,
                application.grant_number,
                application.reviewer_id,
                application.submission_date.isoformat(),
                application.requested_amount,
                priority
            ))

            new_id = cursor.lastrowid

            conn.execute("""
                INSERT INTO status_history (
                    application_id,
                    old_status,
                    new_status,
                    changed_by,
                    notes
                )
                VALUES (?, NULL, 'Submitted', ?, ?)
            """, (
                new_id,
                application.reviewer_id,
                "Application submitted through FastAPI"
            ))

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Invalid application data or referenced ID."
        )

    return {
        "message": "Application created successfully",
        "application_id": new_id,
        "status": "Submitted",
        "priority": priority
    }



@app.get("/applications/{application_id}")
def get_one_application(application_id: int):
    with get_connection() as conn:
        row = conn.execute("""
            SELECT
                a.application_id,
                ap.organization_name,
                a.grant_number,
                g.grant_program_name,
                a.reviewer_id,
                r.reviewer_name,
                a.submission_date,
                a.requested_amount,
                a.status,
                a.priority
            FROM applications a
            JOIN applicants ap
                ON a.applicant_id = ap.applicant_id
            JOIN grants g
                ON a.grant_number = g.grant_number
            LEFT JOIN reviewers r
                ON a.reviewer_id = r.reviewer_id
            WHERE a.application_id = ?
        """, (application_id,)).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    return dict(row)



from typing import Literal

class StatusUpdate(BaseModel):
    new_status: Literal[
        "Submitted", "Under Review", "Approved", "Rejected"
    ]
    reviewer_id: int
    notes: str = ""


@app.patch("/applications/{application_id}/status")
def change_application_status(
    application_id: int,
    update: StatusUpdate
):
    with get_connection() as conn:
        current = conn.execute("""
            SELECT status, reviewer_id
            FROM applications
            WHERE application_id = ?
        """, (application_id,)).fetchone()

        if current is None:
            raise HTTPException(
                status_code=404,
                detail="Application not found"
            )

        old_status = current["status"]

        if current["reviewer_id"] != update.reviewer_id:
            raise HTTPException(
                status_code=403,
                detail="Reviewer is not assigned to this application"
            )

        if old_status == update.new_status:
            raise HTTPException(
                status_code=409,
                detail="Application already has this status"
            )

        allowed_transitions = {
            "Submitted": {"Under Review"},
            "Under Review": {"Approved", "Rejected"},
            "Approved": set(),
            "Rejected": set()
        }

        if update.new_status not in allowed_transitions[old_status]:
            raise HTTPException(
                status_code=409,
                detail="Invalid status transition"
            )

        conn.execute("""
            UPDATE applications
            SET status = ?
            WHERE application_id = ?
        """, (update.new_status, application_id))

        conn.execute("""
            INSERT INTO status_history (
                application_id,
                old_status,
                new_status,
                changed_by,
                notes
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            application_id,
            old_status,
            update.new_status,
            update.reviewer_id,
            update.notes
        ))

    return {
        "application_id": application_id,
        "old_status": old_status,
        "new_status": update.new_status,
        "message": "Status updated successfully"
    }



@app.get("/applications/{application_id}/history")
def get_application_history(application_id: int):
    with get_connection() as conn:

        application = conn.execute("""
            SELECT application_id
            FROM applications
            WHERE application_id = ?
        """, (application_id,)).fetchone()

        if application is None:
            raise HTTPException(
                status_code=404,
                detail="Application not found"
            )

        rows = conn.execute("""
            SELECT
                application_id,
                old_status,
                new_status,
                changed_by,
                notes
            FROM status_history
            WHERE application_id = ?
            ORDER BY rowid
        """, (application_id,)).fetchall()

    return {
        "application_id": application_id,
        "history": [dict(row) for row in rows]
    }
