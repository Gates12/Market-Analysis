import csv
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

SERP_API_KEY = os.getenv("SERP_API_KEY")

def get_primary_keyword():
    """Reads the extracted primary keyword from data/scraped_data.csv."""
    file_path = os.path.join("data", "scraped_data.csv")  # Correct file path

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            data = next(reader)  # Read first row
            return data["primary_keyword"]
    except Exception as e:
        print(f"⚠️ Failed to read keyword from {file_path}: {e}")
        return None


def get_top_ranking_urls(query):
    """Fetch top ranking URLs for the extracted keyword."""
    url = f"https://serpapi.com/search?q={query}&api_key={SERP_API_KEY}&num=10"

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[403, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        results = response.json()
        return [{"rank": idx + 1, "title": res["title"], "url": res["link"]} 
                for idx, res in enumerate(results.get("organic_results", []))]
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Failed to fetch search results: {e}")
        return []

def export_to_csv(data):
    """Export search results to a CSV file inside the 'data' folder."""
    filename = os.path.join("data", "top_urls.csv")  # Save inside 'data' folder

    file_exists = os.path.isfile(filename)

    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["Rank", "Title", "URL"])  # Added Rank column

        for entry in data:
            writer.writerow([entry["rank"], entry["title"], entry["url"]])

    print(f"✅ Results exported to {filename}")

if __name__ == "__main__":
    keyword = get_primary_keyword()

    if keyword:
        print(f"🔍 Searching Google for: {keyword}")
        results = get_top_ranking_urls(keyword)
        
        if results:
            export_to_csv(results)
        else:
            print("⚠️ No results found.")
    else:
        print("⚠️ No primary keyword found in scraped data.")
