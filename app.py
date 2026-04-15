import streamlit as st
import requests
import pandas as pd

# ─── PAGE CONFIG ─────────────────────────────────────────
st.set_page_config(
    page_title="Job Scraper",
    page_icon="💼",
    layout="wide"
)

# ─── CUSTOM CSS ──────────────────────────────────────────
st.markdown("""
<style>
    /* Background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }

    /* Title */
    .main-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a78bfa, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }

    .sub-title {
        text-align: center;
        color: #a0aec0;
        font-size: 1rem;
        margin-bottom: 30px;
    }

    /* Search box */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(167,139,250,0.4);
        border-radius: 10px;
        color: white;
        padding: 12px;
    }

    .stNumberInput > div > div > input {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(167,139,250,0.4);
        border-radius: 10px;
        color: white;
    }

    /* Button */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #a78bfa, #60a5fa);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px;
        font-size: 1rem;
        font-weight: 700;
        cursor: pointer;
        transition: opacity 0.2s;
    }

    .stButton > button:hover {
        opacity: 0.85;
    }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(167,139,250,0.3);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
    }

    /* Job cards */
    .job-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(167,139,250,0.2);
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 14px;
        transition: border 0.2s;
    }

    .job-card:hover {
        border: 1px solid rgba(167,139,250,0.7);
    }

    .job-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #a78bfa;
        margin-bottom: 4px;
    }

    .job-company {
        font-size: 0.95rem;
        color: #60a5fa;
        margin-bottom: 8px;
    }

    .job-meta {
        font-size: 0.85rem;
        color: #a0aec0;
    }

    .job-tag {
        display: inline-block;
        background: rgba(96,165,250,0.15);
        border: 1px solid rgba(96,165,250,0.3);
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.75rem;
        color: #60a5fa;
        margin-right: 5px;
        margin-top: 6px;
    }

    .apply-btn {
        display: inline-block;
        margin-top: 10px;
        padding: 6px 18px;
        background: linear-gradient(90deg, #a78bfa, #60a5fa);
        color: white !important;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-decoration: none;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15,12,41,0.9);
        border-right: 1px solid rgba(167,139,250,0.2);
    }

    /* Divider */
    hr {
        border-color: rgba(167,139,250,0.2);
    }
</style>
""", unsafe_allow_html=True)

# ─── HEADER ──────────────────────────────────────────────
st.markdown('<div class="main-title">💼 Job Scraper</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Find remote jobs instantly — powered by RemoteOK</div>', unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────────────────────────
st.sidebar.markdown("## Search Filters")
keyword    = st.sidebar.text_input("Keyword", value="python", placeholder="e.g. python, data, ml")
min_salary = st.sidebar.number_input("Minimum Salary ($)", min_value=0, value=0, step=10000)
search     = st.sidebar.button("Search Jobs")

# ─── FETCH JOBS ──────────────────────────────────────────
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_jobs(keyword, min_salary):
    url      = f"https://remoteok.com/api?tag={keyword}"
    response = requests.get(url, headers=HEADERS)
    jobs     = response.json()[1:]

    job_list = []
    for job in jobs:
        salary = job.get("salary_min", 0) or 0
        if salary > 0 and salary < min_salary:
            continue
        job_list.append({
            "Title":    job.get("position", "N/A"),
            "Company":  job.get("company", "N/A"),
            "Location": job.get("location", "Remote"),
            "Tags":     job.get("tags", []),
            "Salary":   f"${salary:,}" if salary else "Not listed",
            "Date":     job.get("date", "N/A"),
            "Apply":    job.get("url", "N/A"),
        })
    return job_list

# ─── RESULTS ─────────────────────────────────────────────
if search:
    with st.spinner("Finding jobs..."):
        jobs = fetch_jobs(keyword, min_salary)

    if not jobs:
        st.warning("No jobs found. Try a different keyword.")
    else:
        # Metrics row
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Jobs",  len(jobs))
        col2.metric("Companies",   len(set(j["Company"] for j in jobs)))
        col3.metric("Keyword",     keyword.title())

        st.markdown("---")
        st.markdown(f"### Results for **{keyword}**")

        # Job cards
        for job in jobs:
            tags_html = "".join(
                f'<span class="job-tag">{tag}</span>'
                for tag in job["Tags"][:5]  # show max 5 tags
            )
            st.markdown(f"""
            <div class="job-card">
                <div class="job-title">{job['Title']}</div>
                <div class="job-company">{job['Company']} &nbsp;|&nbsp; {job['Location']} &nbsp;|&nbsp; {job['Salary']}</div>
                <div class="job-meta">{tags_html}</div>
                <a class="apply-btn" href="{job['Apply']}" target="_blank">Apply Now</a>
            </div>
            """, unsafe_allow_html=True)

        # Download button
        st.markdown("---")
        df  = pd.DataFrame(jobs)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label     = "Download All Jobs as CSV",
            data      = csv,
            file_name = f"jobs_{keyword}.csv",
            mime      = "text/csv"
        )
else:
    # Empty state
    st.markdown("""
    <div style="text-align:center; margin-top: 80px; color: #a0aec0;">
        <div style="font-size: 4rem;">🔍</div>
        <div style="font-size: 1.2rem; margin-top: 10px;">Enter a keyword and click Search Jobs</div>
        <div style="font-size: 0.9rem; margin-top: 5px;">Try: python, data, ml, react, django</div>
    </div>
    """, unsafe_allow_html=True)