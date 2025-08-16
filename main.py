# amazon_uk_tracker.py (Updated Version)

import requests
import csv
import os
import datetime
import json # Import json

# --- Configuration --- (remains the same)
SEARCH_URL = "https://www.amazon.jobs/en-gb/search.json?radius=24km&facets%5B%5D=location&facets%5B%5D=business_category&facets%5B%5D=category&facets%5B%5D=schedule_type_id&facets%5B%5D=employee_class&facets%5B%5D=normalized_location&facets%5B%5D=job_function_id&offset=0&result_limit=10000&sort=relevant&latitude=&longitude=&loc_group_id=&loc_query=&base_query=&city=&country=GBR&region=&county=&query_options=&category%5B%5D=software-development"
CSV_FILE = 'tracked_amazon_uk_jobs.csv'
SUMMARY_FILE = 'run_summary.json' # File to store the last run's summary
BASE_URL = "https://www.amazon.jobs"

def fetch_amazon_jobs():
    # ... (This function remains exactly the same as before)
    """Fetches job listings from the Amazon jobs JSON endpoint."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    print("Fetching current jobs from Amazon UK...")
    try:
        response = requests.get(SEARCH_URL, headers=headers, timeout=20)
        response.raise_for_status() 
        data = response.json()
        
        jobs_list = []
        for job in data.get('jobs', []):
            jobs_list.append({
                'id': job.get('id_icims'),
                'title': job.get('title'),
                'location': job.get('location'),
                'posted_date': job.get('posted_date'),
                'url': f"{BASE_URL}{job.get('job_path', '')}"
            })
        print(f"Successfully fetched {len(jobs_list)} jobs.")
        return jobs_list
    except requests.exceptions.RequestException as e:
        print(f"Error fetching jobs: {e}")
        return None

def load_tracked_jobs(filename):
    # ... (This function remains exactly the same as before)
    """Loads previously tracked jobs from a CSV file."""
    if not os.path.exists(filename):
        return []
    
    with open(filename, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_jobs_to_csv(filename, jobs):
    # ... (This function remains exactly the same as before)
    """Saves a list of jobs to a CSV file."""
    if not jobs:
        print("No jobs to save.")
        # Create an empty file with headers if it doesn't exist
        if not os.path.exists(filename):
            with open(filename, mode='w', newline='', encoding='utf-8') as f:
                 writer = csv.DictWriter(f, fieldnames=['id', 'title', 'location', 'posted_date', 'url'])
                 writer.writeheader()
        return
        
    fieldnames = jobs[0].keys()
    
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(jobs)

def compare_jobs(new_jobs, old_jobs):
    # ... (This function remains exactly the same as before)
    """Compares new and old job lists to find added and removed jobs."""
    old_job_ids = {job['id'] for job in old_jobs}
    new_job_ids = {job['id'] for job in new_jobs}

    added_ids = new_job_ids - old_job_ids
    removed_ids = old_job_ids - new_job_ids

    added_jobs = [job for job in new_jobs if job['id'] in added_ids]
    removed_jobs = [job for job in old_jobs if job['id'] in removed_ids]
    
    return added_jobs, removed_jobs

# This is the new function that will be called by the script runner
def run_tracker():
    """Main function to run the job tracker."""
    print("--- Amazon UK Job Tracker ---")
    run_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Run time: {run_time}")

    old_jobs = load_tracked_jobs(CSV_FILE)
    print(f"Found {len(old_jobs)} previously tracked jobs in '{CSV_FILE}'.")

    new_jobs = fetch_amazon_jobs()

    if new_jobs is None:
        print("Could not retrieve new jobs. Exiting.")
        summary = {
            "run_time": run_time,
            "error": "Failed to fetch jobs.",
            "total_jobs": len(old_jobs),
            "added_jobs": [],
            "removed_jobs": []
        }
        with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=4)
        return

    added_jobs, removed_jobs = compare_jobs(new_jobs, old_jobs)

    print("\n--- Tracker Summary ---")
    if not added_jobs and not removed_jobs:
        print("No changes detected since the last run.")
    else:
        if added_jobs: print(f"\n✅ Found {len(added_jobs)} new jobs.")
        if removed_jobs: print(f"\n❌ Found {len(removed_jobs)} removed/filled jobs.")

    print(f"\nSaving current list of {len(new_jobs)} jobs to '{CSV_FILE}'...")
    save_jobs_to_csv(CSV_FILE, new_jobs)

    # Save summary for the frontend
    summary = {
        "run_time": run_time,
        "total_jobs": len(new_jobs),
        "added_jobs": added_jobs,
        "removed_jobs": removed_jobs
    }
    with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=4)
    
    print("--- Tracker run complete. ---\n")

# This block ensures the code only runs when the script is executed directly
if __name__ == "__main__":
    run_tracker()
