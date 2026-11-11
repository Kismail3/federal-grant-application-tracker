import streamlit as st
import pandas as pd
import requests
from pathlib import Path
import altair as alt
import base64

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Federal Grant Application Tracker",
    page_icon="📊",
    layout="wide"
)


st.markdown("""
<style>
/* Phase 3A.2: Navy, forest green, teal, and gold */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

/* Main titles and headings */
h1 {
    color: #E8EDE9 !important;
    font-weight: 750 !important;
    letter-spacing: -1px;
}
h2 {
    color: #E8EDE9 !important;
    font-weight: 650 !important;
    margin-top: 1.5rem !important;
}
h3 { color: #C9DAD2 !important; }

/* Forest green sidebar against navy page */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #061D2B 0%,
        #092B3B 100%
    ) !important;
    border-right: 1px solid rgba(73, 185, 181, 0.18);
}
[data-testid="stSidebar"] label { color: #E8EDE9; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #E8EDE9;
}
/* STEP 8B — Sidebar navigation styling */

/* Style each navigation option */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    border-radius: 7px;
    padding: 7px 10px;
    transition: background 0.2s ease;
}

/* Teal background and gold accent for selected page */
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: linear-gradient(
        90deg,
        #0D5960,
        #087B7C
    );
    border-left: 4px solid #E8B85B;
}

/* STEP 8C — Hide sidebar radio circles */

/* Hide Streamlit's radio indicator */
[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child {
    display: none !important;
}

/* Keep navigation text properly aligned */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    display: flex !important;
    align-items: center !important;
    padding: 10px 14px !important;
    cursor: pointer !important;
}

/* Add spacing between navigation options */
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] {
    gap: 5px !important;
}

/* Subtle green-tinted metric cards */
[data-testid="stMetric"] {
    background: #1A302D;
    border: 1px solid #365448;
    border-radius: 12px;
    padding: 18px 20px;
}
[data-testid="stMetricLabel"] { color: #C2D6CC; }
[data-testid="stMetricValue"] { color: #F1F4EF; }

/* Primary actions: teal; gold for hover/focus highlights */
.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"] {
    background-color: #248C83;
    border-color: #248C83;
    color: #FFFFFF;
    border-radius: 8px;
}
.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button[kind="primary"]:hover {
    background-color: #28796F;
    border-color: #C7A45B;
}
.stButton > button:focus-visible,
.stFormSubmitButton > button:focus-visible {
    outline: 2px solid #C7A45B;
    outline-offset: 2px;
}

/* Form borders and separators */
hr { border-color: #365448 !important; }
[data-testid="stForm"] {
    border: 1px solid #365448;
    border-radius: 12px;
    padding: 20px;
}

/* Hide the navigation radio label, but keep the options visible */
[data-testid="stSidebar"]
[data-testid="stRadio"]
[data-testid="stWidgetLabel"] {
    display: none !important;
}

/* STEP 10A — Custom Overview KPI cards */

.grant-kpi {
    display: flex;
    align-items: center;
    gap: 22px;
    min-height: 108px;
    padding: 20px 24px;
    border-radius: 13px;
    border: 1px solid rgba(82, 210, 204, 0.65);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.grant-kpi-icon {
    width: 56px;
    flex-shrink: 0;
    color: #FFFFFF;
}

.grant-kpi-icon svg {
    width: 48px;
    height: 48px;
    stroke: currentColor;
    fill: none;
    stroke-width: 1.8;
    stroke-linecap: round;
    stroke-linejoin: round;
}

.grant-kpi-label {
    color: #F1F4EF;
    font-size: 17px;
    font-weight: 600;
}

.grant-kpi-value {
    color: #FFFFFF;
    font-size: 42px;
    font-weight: 750;
    line-height: 1.15;
}

.grant-kpi-total {
    background: linear-gradient(135deg, #073B3B, #105451);
    border-bottom: 4px solid #E8B85B;
}

.grant-kpi-review {
    background: linear-gradient(135deg, #07535B, #0D7378);
    border-bottom: 4px solid #52D2CC;
}

.grant-kpi-priority {
    background: linear-gradient(135deg, #94702A, #665224);
    border: 1px solid #E8B85B;
    border-bottom: 4px solid #F2D27C;
}

/* STEP 11A — Chart panel styling */

.grant-chart-panel {
    background: #102633;
    border: 1px solid #284A50;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.10);
}

.grant-chart-heading {
    color: #E8EDE9;
    font-size: 17px;
    font-weight: 650;
    margin-bottom: 12px;
}

/* STEP 11E — Section heading with gold divider */

.grant-section-heading {
    display: flex;
    align-items: center;
    gap: 24px;
    margin-top: 18px;
    margin-bottom: 22px;
}

.grant-section-heading h2 {
    margin: 0 !important;
    white-space: nowrap;
    color: #C9DAD2 !important;
}

.grant-section-line {
    flex: 1;
    height: 2px;
    background: #E8B85B;
    border-radius: 2px;
}

/* STEP 11G — Styled chart panels */
[data-testid="stVerticalBlockBorderWrapper"]:has(.grant-panel-marker) {
    background: linear-gradient(145deg, #102C38, #0C202D) !important;
    border: 1px solid #315968 !important;
    border-radius: 14px !important;
    padding: 8px !important;
}

/* STEP 12D.2 — Application Details card */
[data-testid="stVerticalBlockBorderWrapper"]:has(.grant-details-marker) {
    background: linear-gradient(145deg, #102C38, #0C202D) !important;
    border: 1px solid #315968 !important;
    border-radius: 14px !important;
    padding: 18px 22px !important;
}

/* Funding KPIs: same dark teal and gold treatment as Total Applications */
.funding-kpi {
    background: linear-gradient(135deg, #073B3B, #105451);
    border: 1px solid rgba(82, 210, 204, 0.65);
    border-bottom: 4px solid #E8B85B;
    border-radius: 13px;
    min-height: 116px;
    padding: 20px 24px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}
.funding-kpi .grant-kpi-label { margin-bottom: 8px; }
.funding-kpi .grant-kpi-value { font-size: clamp(25px, 2.4vw, 38px); }

</style>
""", unsafe_allow_html=True)


st.title("Federal Grant Application Tracker")

if "status_update_message" in st.session_state:
    st.success(st.session_state.pop("status_update_message"))

try:
    response = requests.get(
        f"{API_URL}/applications",
        timeout=10
    )
    response.raise_for_status()

    applications = pd.DataFrame(response.json())

except requests.RequestException as error:
    st.error(f"Cannot connect to FastAPI: {error}")
    st.stop()

if applications.empty:
    st.info("No applications available.")
    st.stop()

total = len(applications)

under_review = (
    applications["status"] == "Under Review"
).sum()

high_priority = (
    applications["priority"] == "High"
).sum()


# Phase 3A.3 — Custom government dashboard sidebar

ASSETS_DIR = Path(__file__).resolve().parent / "assets"

#with st.sidebar:
    # Gold Capitol icon above the dashboard title
    #st.image(str(ASSETS_DIR / "capitol_icon.svg"), width=75)

    #st.title("Federal Grant Tracker")

    #st.caption("Government Operations Dashboard · Demo")
with st.sidebar:

    # Center the Capitol icon and dashboard branding
    st.markdown(
        """
        <div style="text-align: center;">
            <img src="data:image/svg+xml;base64,{}"
                 width="90"
                 style="display: block; margin: 0 auto 24px auto;">
            <h2 style="
                text-align: center;
                font-size: 25px;
                font-weight: 750;
                line-height: 1.2;
                margin-bottom: 18px;
            ">
                Federal Grant<br>Tracker
            </h2>
        </div>
        """.format(
            base64.b64encode(
                (ASSETS_DIR / "capitol_icon.svg").read_bytes()
            ).decode()
        ),
        unsafe_allow_html=True
    )

    page = st.radio(
        "Dashboard navigation",
        [
            "Overview",
            "Applications",
            "Reviewers",
            "Funding"
        ],
        label_visibility="collapsed",
        key="dashboard_navigation"
    )

    # Keep the original page names for your dashboard logic
    #page = page.split("  ", 1)[1]


    # Decorative Capitol illustration below navigation
    st.markdown("<div style='height: 330px;'></div>",
                unsafe_allow_html=True)

    st.image(
        str(ASSETS_DIR / "capitol_sidebar.svg"),
        width="stretch"
    )

st.markdown(
    """
    <style>
      .grant-table-wrap {overflow-x:auto; width:100%; margin:0.5rem 0 1rem;}
      .grant-table-wrap table {width:100%; border-collapse:collapse; table-layout:fixed;
        font-size:0.92rem; line-height:1.5;}
      .grant-table-wrap th, .grant-table-wrap td {padding:12px 13px;
        border:1px solid rgba(100,145,153,.20); text-align:left;
        overflow-wrap:anywhere; vertical-align:top;}
      .grant-table-wrap th {background:rgba(128,128,128,.12); font-weight:600;}
      .grant-table-wrap tr:hover td {background:rgba(128,128,128,.06);}
      .grant-table-wrap th:nth-child(1) {width:4%;}
      .grant-table-wrap th:nth-child(2) {width:17%;}
      .grant-table-wrap th:nth-child(3) {width:27%;}
      .grant-table-wrap th:nth-child(4) {width:17%;}
      .grant-table-wrap th:nth-child(5) {width:11%;}
      .grant-table-wrap th:nth-child(6) {width:13%;}
      .grant-table-wrap td:last-child {white-space:nowrap;}
      .reviewer-summary table {table-layout:auto;}
      .reviewer-summary th {width:auto !important;}
      .reviewer-summary td:nth-child(n+2) {text-align:right;}
    </style>
    """,
    unsafe_allow_html=True,
)

funding_data = applications.copy()
funding_data["requested_amount"] = pd.to_numeric(
    funding_data["requested_amount"], errors="coerce"
)

if page == "Overview":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="grant-kpi grant-kpi-total">
            <div class="grant-kpi-icon">
                <svg viewBox="0 0 48 48">
                    <path d="M10 4 H29 L38 13 V43 H10 Z"/>
                    <path d="M29 4 V13 H38"/>
                    <path d="M17 22 H31"/>
                    <path d="M17 29 H31"/>
                    <path d="M17 36 H27"/>
                </svg>
            </div>
            <div>
                <div class="grant-kpi-label">Total Applications</div>
                <div class="grant-kpi-value">{total}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="grant-kpi grant-kpi-review">
            <div class="grant-kpi-icon">
                <svg viewBox="0 0 48 48">
                    <circle cx="21" cy="21" r="13"/>
                    <path d="M31 31 L43 43"/>
                </svg>
            </div>
            <div>
                <div class="grant-kpi-label">Under Review</div>
                <div class="grant-kpi-value">{int(under_review)}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="grant-kpi grant-kpi-priority">
            <div class="grant-kpi-icon">
                <svg viewBox="0 0 48 48">
                    <path d="M10 5 V43"/>
                    <path d="M10 9 Q20 3 30 10 Q36 13 42 9 L38 29 Q26 24 10 30"/>
                </svg>
            </div>
            <div>
                <div class="grant-kpi-label">High Priority</div>
                <div class="grant-kpi-value">{int(high_priority)}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


    
    # STEP 11E — Application Distribution heading with gold divider

    st.markdown(
        """

        <div class="grant-section-heading">
            <h2>Application Distribution</h2>
            <div class="grant-section-line"></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    chart_col1, chart_col2 = st.columns(2, gap="medium")

    with chart_col1:
        with st.container(border=True):
            st.markdown(
                '<span class="grant-panel-marker"></span>',
                unsafe_allow_html=True
            )
            st.write("**Applications by Status**")

            status_counts = (
                applications["status"]
                .value_counts()
                .rename_axis("Status")
                .reset_index(name="Count")
            )

            status_colors = {
                "Approved": "#258F88",
                "Under Review": "#49BDB6",
            }

            status_counts["Color"] = status_counts["Status"].map(
                status_colors
            ).fillna("#A1DFD6")

            status_bars = alt.Chart(status_counts).mark_bar(
                size=95
            ).encode(
                x=alt.X(
                    "Status:N",
                    title="Application Status",
                    sort=["Approved", "Under Review"],
                    axis=alt.Axis(labelAngle=0)
                ),
                y=alt.Y(
                    "Count:Q",
                    title="Number of Applications",
                    axis=alt.Axis(format="d", tickMinStep=1)
                ),
                color=alt.Color(
                    "Color:N",
                    scale=None,
                    legend=None
                ),
                tooltip=["Status:N", "Count:Q"]
            )

            status_labels = alt.Chart(status_counts).mark_text(
                dy=-12,
                color="#E8EDE9",
                fontSize=16,
                fontWeight="bold"
            ).encode(
                x=alt.X("Status:N", sort=["Approved", "Under Review"]),
                y="Count:Q",
                text="Count:Q"
            )

            st.altair_chart(
                (status_bars + status_labels).properties(height=300),
                width="stretch"
            )

    with chart_col2:
        with st.container(border=True):
            st.markdown(
                '<span class="grant-panel-marker"></span>',
                unsafe_allow_html=True
            )
            st.write("**Applications by Priority**")

            priority_counts = (
                applications["priority"]
                .value_counts()
                .rename_axis("Priority")
                .reset_index(name="Count")
            )

            priority_colors = {
                "High": "#258F88",
                "Low": "#36ACA4",
                "Normal": "#A1DFD6",
            }

            priority_counts["Color"] = priority_counts["Priority"].map(
                priority_colors
            ).fillna("#A1DFD6")

            priority_bars = alt.Chart(priority_counts).mark_bar(
                size=85
            ).encode(
                x=alt.X(
                    "Priority:N",
                    title="Priority Level",
                    sort=["High", "Low", "Normal"],
                    axis=alt.Axis(labelAngle=0)
                ),
                y=alt.Y(
                    "Count:Q",
                    title="Number of Applications",
                    axis=alt.Axis(format="d", tickMinStep=1)
                ),
                color=alt.Color(
                    "Color:N",
                    scale=None,
                    legend=None
                ),
                tooltip=["Priority:N", "Count:Q"]
            )

            priority_labels = alt.Chart(priority_counts).mark_text(
                dy=-12,
                color="#E8EDE9",
                fontSize=16,
                fontWeight="bold"
            ).encode(
                x=alt.X(
                    "Priority:N",
                    sort=["High", "Low", "Normal"]
                ),
                y="Count:Q",
                text="Count:Q"
            )

            st.altair_chart(
                (priority_bars + priority_labels).properties(height=300),
                width="stretch"
            )





elif page == "Applications":

    st.markdown(
        """
        <div class="grant-section-heading">
            <h2>Application Overview</h2>
            <div class="grant-section-line"></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Filter Applications")
    
    col_status, col_priority, col_reviewer = st.columns(3)

    with col_status:
        selected_status = st.selectbox(
            "Application Status",
            ["All"] + sorted(applications["status"].dropna().unique().tolist())
        )

    with col_priority:
        selected_priority = st.selectbox(
            "Priority Level",
            ["All"] + sorted(applications["priority"].dropna().unique().tolist())
        )

    with col_reviewer:
        selected_reviewer = st.selectbox(
            "Assigned Reviewer",
            ["All"] + sorted(applications["reviewer_name"].dropna().unique().tolist())
        )

    filtered = applications.copy()

    if selected_status != "All":
        filtered = filtered[filtered["status"] == selected_status]

    if selected_priority != "All":
        filtered = filtered[filtered["priority"] == selected_priority]

    if selected_reviewer != "All":
        filtered = filtered[filtered["reviewer_name"] == selected_reviewer]

    st.caption(f"Showing {len(filtered)} of {len(applications)} applications")

    # Display a concise, readable overview while preserving the full API data.
    overview_columns = {
        "application_id": "ID",
        "organization_name": "Organization",
        "grant_program_name": "Grant Program",
        "reviewer_name": "Reviewer",
        "status": "Status",
        "requested_amount": "Requested Funding",
        "submission_date": "Submitted On",
    }
    visible_columns = [column for column in overview_columns if column in filtered.columns]
    overview = filtered[visible_columns].rename(columns=overview_columns).copy()
    if "Requested Funding" in overview:
        overview["Requested Funding"] = overview["Requested Funding"].map(
            lambda value: f"${value:,.0f}" if pd.notna(value) else "—"
        )

    # A small HTML table wraps long program names instead of clipping them.
    # Pandas escapes the values to keep API-provided text safe to display.
    st.markdown(
        '<div class="grant-table-wrap">' + overview.to_html(index=False, escape=True) + '</div>',
        unsafe_allow_html=True,
    )




    # Comfortable separation without a horizontal divider.
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)

    with st.container(border=True):

        st.markdown(
            '<span class="grant-details-marker"></span>',
            unsafe_allow_html=True
        )

        st.subheader("Application Details")

        selected_id = st.selectbox(
            "Select an Application ID",
            applications["application_id"].tolist()
        )

        try:
            detail_response = requests.get(
                f"{API_URL}/applications/{selected_id}",
                timeout=10
            )
            detail_response.raise_for_status()

            history_response = requests.get(
                f"{API_URL}/applications/{selected_id}/history",
                timeout=10
            )
            history_response.raise_for_status()

            details = detail_response.json()
            history = history_response.json()["history"]

            # Compact two-column summary; status history remains below.
            left_col, right_col = st.columns(2, gap="large")

            with left_col:
                st.caption("Organization")
                st.markdown(f"**{details['organization_name']}**")
                st.caption("Assigned Reviewer")
                st.markdown(f"**{details['reviewer_name']}**")
                st.caption("Status")
                st.markdown(f"**{details['status']}**")

            with right_col:
                st.caption("Grant Program")
                st.markdown(f"**{details['grant_program_name']}**")
                st.caption("Requested Funding")
                st.markdown(f"**${details['requested_amount']:,.2f}**")
                st.caption("Priority")
                st.markdown(f"**{details['priority']}**")

            st.subheader("Application Status History")

            if history:
                history_df = pd.DataFrame(history)

                history_df = history_df.rename(
                    columns={
                        "application_id": "Application ID",
                        "old_status": "Previous Status",
                        "new_status": "New Status",
                        "changed_by": "Updated By",
                        "notes": "Notes"
                    }
                )

                st.dataframe(
                    history_df,
                    width="stretch",
                    hide_index=True
                )

            else:
                st.info(
                    "No history available for this application."
                )

        except requests.RequestException as error:
            st.error(
                f"Unable to retrieve application details: {error}"
            )



    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
    st.subheader("Update Application Status")

    editable_ids = applications["application_id"].tolist()

    # Keep the selector outside the form so changing applications refreshes
    # the displayed status, reviewer, and allowed transitions immediately.
    update_id = st.selectbox(
        "Application to Update",
        editable_ids
    )

    # The single-application API provides the authoritative assigned reviewer ID.
    # The applications list only includes the reviewer's display name.
    assigned_reviewer_id = None
    try:
        reviewer_response = requests.get(
            f"{API_URL}/applications/{update_id}", timeout=10
        )
        reviewer_response.raise_for_status()
        assigned_reviewer_id = reviewer_response.json().get("reviewer_id")
        if assigned_reviewer_id is not None:
            assigned_reviewer_id = int(assigned_reviewer_id)
    except (requests.RequestException, ValueError, TypeError) as error:
        st.error(f"Unable to load the assigned reviewer ID: {error}")

    with st.form("status_update_form"):
        selected_application = applications[
            applications["application_id"] == update_id
        ].iloc[0]

        current_status = selected_application["status"]

        st.write("Current Status:", current_status)
        st.write("Assigned Reviewer:", selected_application["reviewer_name"])

        transitions = {
            "Submitted": ["Under Review"],
            "Under Review": ["Approved", "Rejected"],
            "Approved": [],
            "Rejected": []
        }

        available_statuses = transitions.get(current_status, [])

        if available_statuses:
            new_status = st.selectbox(
                "New Status",
                available_statuses
            )
        else:
            new_status = None
            st.info("This application has reached a final status.")

        if assigned_reviewer_id is not None:
            st.caption(f"Assigned Reviewer ID: {assigned_reviewer_id}")
        else:
            st.error("This application has no assigned reviewer ID. Status updates are disabled.")

        notes = st.text_area(
            "Review Notes",
            placeholder="Explain why the status is changing..."
        )

        submitted = st.form_submit_button(
            "Update Status",
            disabled=not available_statuses or assigned_reviewer_id is None
        )

    if submitted:
        payload = {
            "new_status": new_status,
            "reviewer_id": assigned_reviewer_id,
            "notes": notes
        }

        try:
            result = requests.patch(
                f"{API_URL}/applications/{update_id}/status",
                json=payload,
                timeout=10
            )

            if result.status_code == 200:
                # Verify the update using fresh API reads before reporting success.
                check_detail = requests.get(
                    f"{API_URL}/applications/{update_id}", timeout=10
                )
                check_history = requests.get(
                    f"{API_URL}/applications/{update_id}/history", timeout=10
                )
                check_list = requests.get(f"{API_URL}/applications", timeout=10)
                check_detail.raise_for_status()
                check_history.raise_for_status()
                check_list.raise_for_status()

                saved_detail = check_detail.json()
                saved_history = check_history.json().get("history", [])
                latest_applications = check_list.json()
                status_saved = saved_detail.get("status") == new_status
                history_saved = any(
                    str(item.get("new_status")) == new_status
                    for item in saved_history
                )
                list_updated = any(
                    str(item.get("application_id")) == str(update_id)
                    and item.get("status") == new_status
                    for item in latest_applications
                )

                if status_saved and history_saved and list_updated:
                    st.session_state["status_update_message"] = (
                        f"Application {update_id} updated to {new_status}. "
                        "Status, history, and application list verified via API. "
                        "Dashboard metrics and reviewer tables refreshed."
                    )
                    st.rerun()
                else:
                    st.warning(
                        "The API accepted the update, but one or more verification "
                        "checks did not match. Refresh and inspect the application "
                        "status and history before trying another update."
                    )
            else:
                try:
                    error_detail = result.json().get("detail", result.text)
                except ValueError:
                    error_detail = result.text

                st.error(f"Update failed: {error_detail}")

        except requests.RequestException as error:
            st.error(f"API connection error: {error}")



    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
    st.subheader("Export Application Data")

    st.write(
        "Download the current application records "
        "for reporting and analysis."
    )

    csv_data = applications.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Applications CSV",
        data=csv_data,
        file_name="federal_grant_applications.csv",
        mime="text/csv"
    )

    st.caption(
        "Application workflow records are simulated "
        "for demonstration purposes."
    )




elif page == "Reviewers":
    # Match the Overview and Applications headings without a top green divider.
    st.markdown(
        """
        <div class="grant-section-heading">
            <h2>Reviewer Overview</h2>
            <div class="grant-section-line"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    reviewer_workload = (
        applications.groupby("reviewer_name")
        .agg(
            assigned_applications=("application_id", "count"),
            total_requested_funding=("requested_amount", "sum")
        )
        .reset_index()
    )

    st.subheader("Reviewer Assignment Summary")

    reviewer_display = reviewer_workload.rename(
        columns={
            "reviewer_name": "Reviewer",
            "assigned_applications": "Assigned Applications",
            "total_requested_funding": "Total Requested Funding ($)",
        }
    ).copy()
    reviewer_display["Total Requested Funding ($)"] = reviewer_display[
        "Total Requested Funding ($)"
    ].map(lambda amount: f"${amount:,.0f}")
    st.markdown(
        '<div class="grant-table-wrap reviewer-summary">' + reviewer_display.to_html(index=False, escape=True) + '</div>',
        unsafe_allow_html=True,
    )


    st.subheader("Applications Awaiting Review Decisions")

    pending_applications = applications[
        applications["status"].isin(["Submitted", "Under Review"])
    ].copy()

    pending_summary = (
        pending_applications.groupby("reviewer_name")
        .agg(
            pending_applications=("application_id", "count"),
            pending_funding=("requested_amount", "sum")
        )
        .reset_index()
    )

    pending_display = pending_summary.rename(
        columns={
            "reviewer_name": "Reviewer",
            "pending_applications": "Pending Applications",
            "pending_funding": "Requested Funding Pending Decision ($)",
        }
    ).copy()
    pending_display["Requested Funding Pending Decision ($)"] = pending_display[
        "Requested Funding Pending Decision ($)"
    ].map(lambda amount: f"${amount:,.0f}")
    st.markdown(
        '<div class="grant-table-wrap reviewer-summary">' + pending_display.to_html(index=False, escape=True) + '</div>',
        unsafe_allow_html=True,
    )

elif page == "Funding":
    # Use the same page-heading treatment as Applications and Reviewers.
    st.markdown(
        """
        <div class="grant-section-heading">
            <h2>Funding Overview</h2>
            <div class="grant-section-line"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # These are simulated application requests, not HRSA awarded funding.
    funding_data = applications.copy()
    funding_data["requested_amount"] = pd.to_numeric(
        funding_data["requested_amount"], errors="coerce"
    )

    total_requested = funding_data["requested_amount"].sum()
    average_requested = funding_data["requested_amount"].mean()
    highest_request = funding_data["requested_amount"].max()

    funding_metrics = [
        ("Total Funding Requested", total_requested),
        ("Average Funding Request", average_requested),
        ("Largest Funding Request", highest_request),
    ]
    for column, (label, amount) in zip(st.columns(3), funding_metrics):
        with column:
            st.markdown(
                f"""
                <div class="funding-kpi">
                    <div class="grant-kpi-label">{label}</div>
                    <div class="grant-kpi-value">${amount:,.0f}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(
            '<span class="grant-panel-marker"></span>',
            unsafe_allow_html=True,
        )
        st.markdown("**Requested Funding by Grant Program**")

        program_funding = (
            funding_data.groupby("grant_program_name", dropna=True)["requested_amount"]
            .sum()
            .reset_index(name="Requested Funding")
            .sort_values("Requested Funding", ascending=False)
        )
        # Match the teal palette used by the Application Distribution charts.
        teal_palette = ["#258F88", "#49BDB6", "#A1DFD6"]
        program_funding["Bar Color"] = [
            teal_palette[i % len(teal_palette)]
            for i in range(len(program_funding))
        ]

        # Reserve space on the right for dollar labels outside the bars.
        funding_axis_max = float(program_funding["Requested Funding"].max()) * 1.22

        funding_bars = alt.Chart(program_funding).mark_bar(size=32).encode(
            y=alt.Y(
                "grant_program_name:N",
                title=None,
                sort="-x",
                axis=alt.Axis(labelLimit=400, labelFontSize=12),
            ),
            x=alt.X(
                "Requested Funding:Q",
                title="Requested Funding ($)",
                axis=alt.Axis(format="$,.0f", tickCount=5),
                scale=alt.Scale(domain=[0, funding_axis_max], nice=False),
            ),
            color=alt.Color("Bar Color:N", scale=None, legend=None),
            tooltip=[
                alt.Tooltip("grant_program_name:N", title="Grant Program"),
                alt.Tooltip("Requested Funding:Q", format="$,.0f"),
            ],
        )

        funding_labels = alt.Chart(program_funding).mark_text(
            align="left", baseline="middle", dx=8,
            color="#E8EDE9", fontSize=13, fontWeight="bold",
        ).encode(
            y=alt.Y("grant_program_name:N", sort="-x"),
            x="Requested Funding:Q",
            text=alt.Text("Requested Funding:Q", format="$,.0f"),
        )

        st.altair_chart(
            (funding_bars + funding_labels).properties(
                height=max(220, 85 * len(program_funding))
            ).configure_view(stroke=None).configure_axis(
                labelColor="#E8EDE9", titleColor="#E8EDE9"
            ),
            width="stretch",
        )
