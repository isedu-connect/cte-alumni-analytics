"""
Data access layer for the alumni tracer analytics dashboard.

Modes, controlled by st.secrets["DATA_MODE"]:

  "upload" (default) -> no live connection at all. You export a CSV from the
             admin panel (action/export_csv.php) and drag it into the app's
             file uploader. Works regardless of hosting restrictions.

  "api"    -> fetches JSON from ajax/streamlit_data.php on your PHP host.
             Only works if your host doesn't block non-browser requests.

  "mysql"  -> connects directly to MySQL with pymysql.
             Only works if your host allows remote MySQL access.

Switching modes is just a secrets.toml change — no code edits needed.
"""

import pandas as pd
import requests
import streamlit as st


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    if "years_employed" in df.columns:
        df["years_employed"] = pd.to_numeric(df["years_employed"], errors="coerce")
    if "year_graduated" in df.columns:
        df["year_graduated"] = pd.to_numeric(df["year_graduated"], errors="coerce").astype("Int64")
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    return df


def load_from_upload(uploaded_file) -> pd.DataFrame:
    """Load data from the CSV exported by the site's existing export feature."""
    df = pd.read_csv(uploaded_file, encoding="utf-8-sig")

    rename_map = {
        "Full Name": "graduate_name",
        "Gender": "gender",
        "Course/Program": "course",
        "Year Graduated": "year_graduated",
        "Employment Status": "employment_status",
        "Job Title/Position": "job_title",
        "Company/Organization": "company",
        "Employment Sector": "employment_sector",
        "Employment Type": "employment_type",
        "Employment Location": "employment_location",
        "Years of Employment": "years_employed",
        "Job Relevance": "job_relevance",
        "Further Studies": "further_studies",
        "Further Studies Status": "further_studies_status",
        "Studies Program": "studies_program",
        "Studies School": "studies_school",
        "Satisfaction": "satisfaction",
        "Date Submitted": "created_at",
    }
    df = df.rename(columns=rename_map)

    # Drop personally-identifying / contact columns that aren't needed for
    # aggregate analytics (address, personal email, phone number, etc).
    drop_cols = [
        "Student ID", "User Name", "User Email", "Address", "Contact Email",
        "Contact Number", "Looking for Job", "Unemployment Reason",
        "Subjects Relevance", "Useful Skills", "Studies Level",
        "Program Strengths", "Areas for Improvement", "Advice/Suggestions",
        "Additional Comments", "Employment Date", "Last Updated",
    ]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    return _normalize(df)


@st.cache_data(ttl=300, show_spinner="Fetching latest data...")
def load_data() -> pd.DataFrame:
    mode = st.secrets.get("DATA_MODE", "upload")

    if mode == "mysql":
        df = _load_from_mysql()
    elif mode == "api":
        df = _load_from_api()
    else:
        # "upload" mode is handled in app.py directly via the file uploader,
        # since it needs a widget, not a secret. This function only covers
        # the two automatic modes.
        return pd.DataFrame()

    return _normalize(df)


def _load_from_api() -> pd.DataFrame:
    url = st.secrets["API_URL"]
    api_key = st.secrets["API_KEY"]

    headers = {
        "X-API-Key": api_key,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }

    last_error = None
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=headers, timeout=20)
            snippet = resp.text[:300].replace("\n", " ")
            try:
                payload = resp.json()
            except ValueError:
                raise RuntimeError(
                    f"Non-JSON response (status {resp.status_code}): {snippet!r}"
                )
            if "error" in payload:
                raise RuntimeError(f"API error: {payload['error']}")
            return pd.DataFrame(payload.get("records", []))
        except Exception as e:
            last_error = e

    raise RuntimeError(f"Could not reach the API after 3 attempts: {last_error}")


def _load_from_mysql() -> pd.DataFrame:
    import pymysql

    conn = pymysql.connect(
        host=st.secrets["MYSQL_HOST"],
        user=st.secrets["MYSQL_USER"],
        password=st.secrets["MYSQL_PASSWORD"],
        database=st.secrets["MYSQL_DATABASE"],
        cursorclass=pymysql.cursors.DictCursor,
    )

    programs = [
        'BSEd - English', 'BSEd - Mathematics', 'BSEd - Science',
        'BSEd - Filipino', 'BSEd - Social Studies', 'BEED', 'BPEd'
    ]
    placeholders = ", ".join(["%s"] * len(programs))

    sql = f"""
        SELECT
            t.id, t.user_id, u.name AS graduate_name, t.course,
            t.year_graduated, t.gender, t.employment_status,
            t.employment_location, t.employment_sector, t.years_employed,
            t.further_studies, t.further_studies_status, t.satisfaction,
            t.job_relevance, t.created_at
        FROM tracer_data t
        JOIN users u ON t.user_id = u.id
        WHERE t.course IN ({placeholders})
        ORDER BY t.created_at DESC
    """

    try:
        with conn.cursor() as cur:
            cur.execute(sql, programs)
            rows = cur.fetchall()
    finally:
        conn.close()

    return pd.DataFrame(rows)
