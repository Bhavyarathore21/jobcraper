import requests
import pandas as pd
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ─── SETTINGS ───────────────────────────────────────────
KEYWORDS     = ["python", "data", "ml"]   # searches all 3
YOUR_EMAIL   = "rathoresakshi2908@gmail.com"
APP_PASSWORD = "fnsgdotditvocdcv"        # ← keep your working password here
MIN_SALARY   = 50   # minimum salary in USD (jobs below this are filtered out)
# ────────────────────────────────────────────────────────

HEADERS  = {"User-Agent": "Mozilla/5.0"}
SEEN_FILE = "seen_jobs.txt"  # tracks jobs we already saved before


# ─── LOAD PREVIOUSLY SEEN JOB IDs ───────────────────────
# This prevents saving duplicate jobs across multiple runs
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        seen_ids = set(f.read().splitlines())
else:
    seen_ids = set()

# ─── FETCH JOBS FOR ALL KEYWORDS ────────────────────────
all_jobs = []

for keyword in KEYWORDS:
    print(f"Searching: {keyword}...")
    url      = f"https://remoteok.com/api?tag={keyword}"
    response = requests.get(url, headers=HEADERS)
    jobs     = response.json()[1:]  # skip metadata

    for job in jobs:
        job_id  = str(job.get("id", ""))
        salary  = job.get("salary_min", 0) or 0  # some jobs have no salary info

        # ── Skip if already seen before ─────────────────
        if job_id in seen_ids:
            continue

        # ── Skip if salary is below minimum ─────────────
        if salary > 0 and salary < MIN_SALARY:
            continue

        all_jobs.append({
            "ID":       job_id,
            "Title":    job.get("position", "N/A"),
            "Company":  job.get("company", "N/A"),
            "Location": job.get("location", "Remote"),
            "Tags":     ", ".join(job.get("tags", [])),
            "Salary":   f"${salary:,}" if salary else "Not listed",
            "Date":     job.get("date", "N/A"),
            "Apply":    job.get("url", "N/A"),
        })

        # Mark this job as seen
        seen_ids.add(job_id)

print(f"\nNew jobs found: {len(all_jobs)}")

# ─── SAVE SEEN JOB IDs SO WE DON'T REPEAT THEM ─────────
with open(SEEN_FILE, "w") as f:
    f.write("\n".join(seen_ids))

# ─── SAVE TO EXCEL ───────────────────────────────────────
if all_jobs:
    df = pd.DataFrame(all_jobs)
    df.drop(columns=["ID"], inplace=True)  # ID not needed in Excel
    df.to_excel("jobs.xlsx", index=False)
    print("Saved to jobs.xlsx")
else:
    print("No new jobs found — all already seen or below salary filter.")

# ─── SEND EMAIL ──────────────────────────────────────────
print("Sending email...")

top_jobs = all_jobs[:10]

if top_jobs:
    rows = ""
    for j in top_jobs:
        rows += f"""
        <tr>
            <td>{j['Title']}</td>
            <td>{j['Company']}</td>
            <td>{j['Location']}</td>
            <td>{j['Salary']}</td>
            <td><a href="{j['Apply']}">Apply</a></td>
        </tr>
        """
    html = f"""
    <h2>{len(all_jobs)} New Jobs Found Today</h2>
    <p>Keywords searched: <b>{", ".join(KEYWORDS)}</b></p>
    <table border="1" cellpadding="6" cellspacing="0">
        <tr>
            <th>Title</th><th>Company</th>
            <th>Location</th><th>Salary</th><th>Link</th>
        </tr>
        {rows}
    </table>
    <p>Full list saved in jobs.xlsx</p>
    """
else:
    html = "<h2>No new jobs found today. Check back tomorrow!</h2>"

msg            = MIMEMultipart("alternative")
msg["Subject"] = f" {len(all_jobs)} New Jobs Today — {', '.join(KEYWORDS)}"
msg["From"]    = YOUR_EMAIL
msg["To"]      = YOUR_EMAIL

msg.attach(MIMEText(html, "html"))

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(YOUR_EMAIL, APP_PASSWORD)
    server.sendmail(YOUR_EMAIL, YOUR_EMAIL, msg.as_string())

print("Email sent! Check your inbox !!")