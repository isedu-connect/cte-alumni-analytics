import pandas as pd
import plotly.express as px
import streamlit as st

from data_source import load_data, load_from_upload


def show_chart(fig):
    """Apply consistent Inter font + white background, then render."""
    fig.update_layout(
        font_family="Inter, Segoe UI, sans-serif",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=30, b=10, l=10, r=10),
    )
    st.plotly_chart(fig, use_container_width=True)



MAROON = "#6A0D1F"
MAROON_DARK = "#4A0915"
GOLD = "#F4C542"
GOLD_DARK = "#DAA520"
BG_GRAY = "#F8F9FA"

st.set_page_config(
    page_title="CTE Alumni Tracer Analytics",
    page_icon="\U0001F393",
    layout="wide",
)

# Shared Plotly styling so every chart matches the rest of the dashboard
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = [MAROON, GOLD, "#28a745", "#17a2b8", "#dc3545", GOLD_DARK]

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}

    .stApp {{
        background-color: {BG_GRAY};
    }}

    /* ---- Title ---- */
    h1 {{
        color: {MAROON} !important;
        font-weight: 800 !important;
        padding-bottom: 0.6rem;
        border-bottom: 3px solid {GOLD};
        margin-bottom: 0.8rem !important;
    }}

    h2, h3 {{
        color: {MAROON} !important;
        font-weight: 700 !important;
    }}

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {MAROON} 0%, {MAROON_DARK} 100%);
    }}

    /* Default: text sits directly on the dark maroon background -> gold */
    section[data-testid="stSidebar"] {{
        color: {GOLD} !important;
    }}
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] .stMarkdown {{
        color: {GOLD} !important;
    }}

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        border: none !important;
    }}

    /* Filter boxes (multiselect / file uploader / text input) have a LIGHT
       background, so their own text needs to be dark for contrast - this
       overrides the gold-everywhere rule above specifically inside them. */
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div,
    section[data-testid="stSidebar"] .stFileUploader section,
    section[data-testid="stSidebar"] input {{
        background-color: rgba(244, 197, 66, 0.12) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(244, 197, 66, 0.35) !important;
    }}

    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div,
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] * ,
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] .stFileUploader section,
    section[data-testid="stSidebar"] .stFileUploader section * {{
        color: {MAROON_DARK} !important;
    }}

    section[data-testid="stSidebar"] .stFileUploader section {{
        border: 1.5px dashed rgba(244, 197, 66, 0.6) !important;
        background-color: rgba(255, 255, 255, 0.9) !important;
    }}

    /* Multiselect selected tags: gold background -> maroon text, including
       the label span and the little "x" remove icon inside it */
    section[data-testid="stSidebar"] span[data-baseweb="tag"] {{
        background-color: {GOLD} !important;
        color: {MAROON} !important;
        font-weight: 600;
    }}

    section[data-testid="stSidebar"] span[data-baseweb="tag"] * {{
        color: {MAROON} !important;
        fill: {MAROON} !important;
    }}

    /* ---- Metric cards ---- */
    div[data-testid="stMetric"] {{
        background-color: white;
        border-radius: 12px;
        padding: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-bottom: 3px solid {GOLD};
    }}

    div[data-testid="stMetricValue"] {{
        color: {MAROON} !important;
        font-weight: 800;
    }}

    div[data-testid="stMetricLabel"] {{
        color: #666 !important;
        font-weight: 500;
    }}

    /* ---- Buttons ---- */
    .stButton > button, .stDownloadButton > button {{
        background: linear-gradient(135deg, {MAROON} 0%, {MAROON_DARK} 100%);
        color: {GOLD};
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.2rem;
        transition: all 0.25s ease;
    }}

    .stButton > button:hover, .stDownloadButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(106, 13, 31, 0.35);
        color: white;
    }}

    section[data-testid="stSidebar"] .stButton > button {{
        background: {GOLD};
        color: {MAROON} !important;
        width: 100%;
    }}

    section[data-testid="stSidebar"] .stButton > button:hover {{
        background: {GOLD_DARK};
    }}

    /* ---- Text input ---- */
    .stTextInput input {{
        border-radius: 8px !important;
        border: 1px solid #dee2e6 !important;
    }}

    .stTextInput input:focus {{
        border-color: {GOLD} !important;
        box-shadow: 0 0 0 0.2rem rgba(244, 197, 66, 0.25) !important;
    }}

    /* ---- Alerts (info/warning/error/success) ---- */
    div[data-testid="stAlert"] {{
        border-radius: 10px;
    }}

    /* ---- Dataframe / table container ---- */
    div[data-testid="stDataFrame"] {{
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #e9ecef;
    }}

    /* ---- Chart containers ---- */
    div[data-testid="stPlotlyChart"] {{
        background-color: white;
        border-radius: 12px;
        padding: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}

    hr {{
        border-top: 1px solid rgba(106, 13, 31, 0.15);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("\U0001F393 CTE Alumni Tracer — Analytics Dashboard")
st.caption("ISPSC Tagudin Campus · College of Teacher Education")

# ---------- Load data ----------
mode = st.secrets.get("DATA_MODE", "upload")

df = pd.DataFrame()

if mode == "upload":
    st.sidebar.header("Data")
    uploaded_file = st.sidebar.file_uploader(
        "Upload the exported CSV",
        type=["csv"],
        help="From the admin panel, click 'Export for Dashboard' to download the CSV, then drag it in here.",
    )
    if uploaded_file is not None:
        try:
            df = load_from_upload(uploaded_file)
            st.sidebar.success(f"Loaded {len(df):,} records.")
        except Exception as e:
            st.error(f"Couldn't read that CSV: {e}")
            st.stop()
    else:
        st.info(
            "\U0001F446 Upload the exported CSV in the sidebar to see the dashboard.\n\n"
            "Export it from your admin panel's **Export for Dashboard** button "
            "(`action/export_csv.php`), then drag the downloaded file into the box on the left."
        )
        st.stop()
else:
    try:
        df = load_data()
    except Exception as e:
        st.error(f"Couldn't load data: {e}")
        st.stop()
    if st.sidebar.button("\U0001F504 Refresh data"):
        st.cache_data.clear()
        st.rerun()

if df.empty:
    st.warning("No tracer records found yet.")
    st.stop()

EMPLOYED_STATUSES = ["Employed", "Employed-Non Teaching", "Self-Employed"]

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")

years = sorted(df["year_graduated"].dropna().unique().tolist())
year_sel = st.sidebar.multiselect("Year graduated", years, default=years)

courses = sorted(df["course"].dropna().unique().tolist())
course_sel = st.sidebar.multiselect("Program", courses, default=courses)

genders = sorted(df["gender"].dropna().unique().tolist())
gender_sel = st.sidebar.multiselect("Gender", genders, default=genders)

statuses = sorted(df["employment_status"].dropna().unique().tolist())
status_sel = st.sidebar.multiselect("Employment status", statuses, default=statuses)

filtered = df[
    df["year_graduated"].isin(year_sel)
    & df["course"].isin(course_sel)
    & df["gender"].isin(gender_sel)
    & df["employment_status"].isin(status_sel)
]

if filtered.empty:
    st.warning("No records match the current filters.")
    st.stop()

# ---------- KPI row ----------
total = len(filtered)
employed = filtered["employment_status"].isin(EMPLOYED_STATUSES).sum()
unemployed = (filtered["employment_status"] == "Unemployed").sum()
further_studies = (
    (filtered["employment_status"] == "Student") | (filtered["further_studies"] == "Yes")
).sum()
employment_rate = round(employed / total * 100, 1) if total else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Records", f"{total:,}")
c2.metric("Employed", f"{employed:,}")
c3.metric("Unemployed", f"{unemployed:,}")
c4.metric("Further Studies", f"{further_studies:,}")
c5.metric("Employment Rate", f"{employment_rate}%")

st.divider()

# ---------- Charts row 1 ----------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Employment Status")
    emp_df = pd.DataFrame({
        "Status": ["Employed", "Unemployed", "Further Studies"],
        "Count": [employed, unemployed, further_studies],
    })
    fig = px.pie(emp_df, names="Status", values="Count", hole=0.5,
                 color="Status",
                 color_discrete_map={"Employed": "#28a745", "Unemployed": "#dc3545", "Further Studies": "#17a2b8"})
    show_chart(fig)

with col2:
    st.subheader("Program Distribution")
    course_counts = filtered["course"].value_counts().reset_index()
    course_counts.columns = ["Program", "Graduates"]
    fig = px.bar(course_counts, x="Graduates", y="Program", orientation="h",
                 color_discrete_sequence=[GOLD])
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    show_chart(fig)

# ---------- Trends over years ----------
st.subheader("Employment Trends by Graduation Year")
trend = filtered.groupby("year_graduated").apply(
    lambda g: pd.Series({
        "Employed": g["employment_status"].isin(EMPLOYED_STATUSES).sum(),
        "Unemployed": (g["employment_status"] == "Unemployed").sum(),
        "Further Studies": ((g["employment_status"] == "Student") | (g["further_studies"] == "Yes")).sum(),
    })
).reset_index()
trend_long = trend.melt(id_vars="year_graduated", var_name="Status", value_name="Count")
fig = px.line(trend_long, x="year_graduated", y="Count", color="Status", markers=True,
              color_discrete_map={"Employed": "#28a745", "Unemployed": "#dc3545", "Further Studies": "#17a2b8"})
fig.update_xaxes(title="Year Graduated", dtick=1)
show_chart(fig)

# ---------- Charts row 2 ----------
col3, col4, col5 = st.columns(3)

with col3:
    if "satisfaction" in filtered.columns and filtered["satisfaction"].notna().any():
        st.subheader("Satisfaction")
        order = ["Very satisfied", "Satisfied", "Neutral", "Unsatisfied", "Very unsatisfied"]
        sat_counts = filtered["satisfaction"].value_counts().reindex(order).dropna().reset_index()
        sat_counts.columns = ["Satisfaction", "Count"]
        fig = px.bar(sat_counts, x="Satisfaction", y="Count", color_discrete_sequence=[MAROON])
        show_chart(fig)

with col4:
    if "job_relevance" in filtered.columns and filtered["job_relevance"].notna().any():
        st.subheader("Job Relevance")
        rel_counts = filtered["job_relevance"].value_counts().reset_index()
        rel_counts.columns = ["Relevance", "Count"]
        fig = px.pie(rel_counts, names="Relevance", values="Count", hole=0.4,
                     color_discrete_sequence=["#28a745", GOLD, "#dc3545"])
        show_chart(fig)

with col5:
    if "employment_sector" in filtered.columns:
        sector_counts = filtered["employment_sector"].dropna()
        sector_counts = sector_counts[sector_counts.str.strip() != ""]
        if not sector_counts.empty:
            st.subheader("Employment Sector")
            sc = sector_counts.value_counts().reset_index()
            sc.columns = ["Sector", "Count"]
            fig = px.pie(sc, names="Sector", values="Count", hole=0.4)
            show_chart(fig)

st.divider()

# ---------- Gender & Location ----------
col6, col7 = st.columns(2)

with col6:
    st.subheader("Gender Distribution")
    g = filtered["gender"].value_counts().reset_index()
    g.columns = ["Gender", "Count"]
    fig = px.pie(g, names="Gender", values="Count", hole=0.4)
    show_chart(fig)

with col7:
    if "employment_location" in filtered.columns and filtered["employment_location"].notna().any():
        st.subheader("Employment Location")
        loc = filtered["employment_location"].value_counts().reset_index()
        loc.columns = ["Location", "Count"]
        fig = px.pie(loc, names="Location", values="Count", hole=0.4,
                     color_discrete_sequence=[MAROON, GOLD, "#28a745"])
        show_chart(fig)

st.divider()

# ---------- Data table + export ----------
st.subheader("Records")
search = st.text_input("Search by name or program")
table_df = filtered.drop(columns=["user_id"], errors="ignore")
if search:
    mask = table_df.apply(lambda row: search.lower() in str(row.values).lower(), axis=1)
    table_df = table_df[mask]

st.dataframe(table_df, use_container_width=True, hide_index=True)

st.download_button(
    "\U0001F4E5 Download filtered data as CSV",
    data=table_df.to_csv(index=False).encode("utf-8"),
    file_name="alumni_tracer_filtered.csv",
    mime="text/csv",
)
