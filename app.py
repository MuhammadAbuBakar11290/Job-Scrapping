import csv
import json
import openai
from jobspy import scrape_jobs

# 🔹 Step 1: Define job sites to scrape
sites = ["linkedin","indeed", "zip_recruiter", "google", "bayt"]  
all_jobs = []

# 🔹 Step 2: Scrape jobs from each site (20 per site)
for site in sites:
    jobs = scrape_jobs(
        site_name=[site],
        search_term="software engineer",
        location="Islamabad, Pakistan",
        results_wanted=20,
        hours_old=72,
        country_indeed="Pakistan",
    )
    all_jobs.extend(jobs.to_dict(orient="records"))  # Convert to dictionary format

# 🔹 Step 3: Convert to structured format
formatted_jobs = []
for job in all_jobs:
    formatted_jobs.append({
        "job_title": job.get("title", "N/A"),
        "company": job.get("company", "N/A"),
        "experience": "N/A",  # Experience will be filled by GPT
        "jobNature": "onsite" if "onsite" in job.get("location", "").lower() else "remote",
        "location": job.get("location", "N/A"),
        "salary": job.get("salary", "N/A"),
        "apply_link": job.get("job_url", "N/A"),
    })

# 🔹 Save raw jobs to a CSV for debugging
with open("raw_jobs.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=formatted_jobs[0].keys())
    writer.writeheader()
    writer.writerows(formatted_jobs)

# 🔹 Convert to JSON format
formatted_json = json.dumps({"relevant_jobs": formatted_jobs}, indent=4)

# 🔹 Step 4: Send data to OpenAI GPT for Refinement
openai.api_key = ""

prompt = f"""
The following is a list of job postings. Please:
1. Fill in missing experience levels based on job titles.
2. Ensure consistency in job nature (onsite, remote, hybrid).
3. Format in the following JSON format:

{{
 "relevant_jobs": [
 {{
 "job_title": "Full Stack Engineer",
 "company": "XYZ Pvt Ltd",
 "experience": "2+ years",
 "jobNature": "onsite",
 "location": "Islamabad, Pakistan",
 "salary": "100,000 PKR",
 "apply_link": "https://linkedin.com/job123"
 }}
 ]
}}

Here is the raw job data:
{formatted_json}
"""

# 🔹 Call OpenAI API
response = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.2,
)

# 🔹 Extract formatted job listings
structured_jobs = response["choices"][0]["message"]["content"]

# 🔹 Save final JSON output
with open("structured_jobs.json", "w", encoding="utf-8") as f:
    f.write(structured_jobs)

print("✅ Formatted job listings saved to 'structured_jobs.json'.")


