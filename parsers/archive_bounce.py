import requests
import time
import random
import logging
from requests.exceptions import RequestException
from urllib3.exceptions import MaxRetryError
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def exponential_backoff(attempt, base_delay=5, max_delay=300):
    delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
    return delay

s3A = "gab1DoriNh68SrP6:HGF7XXfbz73ThYkF"

def download_via_archive(url, max_attempts=5):
    for attempt in range(max_attempts):
        try:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": "LOW %s" % os.getenv("S3A")
            }

            data = "url=%s/&if_not_archived_within=1d&capture_outlinks=0" % url

            logging.info(f"Attempting to archive URL: {url} (Attempt {attempt + 1}/{max_attempts})")
            req = requests.post("https://web.archive.org/save", headers=headers, data=data, timeout=30)

            if req.status_code != 200:
                logging.warning(f"Request failed. Status code: {req.status_code}")
                backoff_time = exponential_backoff(attempt)
                logging.info(f"Backing off for {backoff_time:.2f} seconds")
                time.sleep(backoff_time)
                continue

            result = req.json()
            job_id = result.get("job_id")

            if job_id is None:
                logging.info(f"Job completed immediately: {result}")
                return check_availability(url, headers)

            while True:
                time.sleep(5)
                status_req = requests.get(f"https://web.archive.org/save/status/{job_id}", headers=headers, timeout=30)
                status_data = status_req.json()
                status = status_data["status"]

                if status == "success":
                    logging.info(f"Successfully archived URL: {url}")
                    return check_availability(status_data["original_url"], headers)
                elif status == "error":
                    logging.error(f"Job failed: {status_data['message']}")
                    break

        except (RequestException, MaxRetryError) as e:
            logging.error(f"Attempt {attempt + 1} failed due to {str(e)}")
            if attempt < max_attempts - 1:
                backoff_time = exponential_backoff(attempt)
                logging.info(f"Backing off for {backoff_time:.2f} seconds")
                time.sleep(backoff_time)
            else:
                logging.error(f"Max attempts reached. Could not archive {url}")
                return False

    return False

def check_availability(url, headers):
    for attempt in range(10):
        try:
            logging.info(f"Checking availability of archived URL: {url} (Attempt {attempt + 1}/5)")
            url_check = requests.get(f"https://archive.org/wayback/available?url={url}", headers=headers, timeout=60)
            available_data = url_check.json()
            
            if available_data["archived_snapshots"]:
                snapshot = available_data["archived_snapshots"]["closest"]
                archived_url = snapshot["url"]
                logging.info(f"Successfully retrieved archived URL: {archived_url}")
                return archived_url
            
            logging.warning("Archived snapshot not found yet")
            time.sleep(2)
        except (RequestException, MaxRetryError) as e:
            logging.error(f"Error checking availability: {str(e)}")
            time.sleep(2)
    
    logging.error(f"Failed to retrieve archived URL for {url}")
    return False
