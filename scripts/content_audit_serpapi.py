import os
import csv
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 🔑 Load SERP API Key
SERP_API_KEY = os.getenv("SERP_API_KEY")

def get_seo_metrics(domain):
    """Fetch SEO metrics from SERP API for a given domain."""
    url = f"https://serpapi.com/search.json?engine=google&q=site:{domain}&api_key={SERP_API_KEY}"

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[403, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        organic_results = data.get("organic_results", [])
        if not organic_results:
            return None

        # Extract top 5 ranking articles
        top_articles = [{"title": res["title"], "url": res["link"]} for res in organic_results[:5]]

        return {
            "Domain": domain,
            "Total Organic Results": len(organic_results),
            "Top Articles": top_articles
        }

    except requests.exceptions.RequestException:
        return None  # Silently handle failed requests

def extract_domain(url):
    """Extract domain name from URL."""
    return url.split("//")[-1].split("/")[0]

def read_top_urls(filename=os.path.join("data", "top_urls.csv")):
    """Read top-ranking URLs from a CSV file inside the data folder."""
    urls = []
    try:
        with open(filename, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            urls = [row[2] for row in reader if len(row) > 2]  # Extract URLs from column 3
    except Exception as e:
        print(f"⚠️ Failed to read URLs from {filename}: {e}")  # Debugging output
    return urls


def export_to_csv(data, filename="seo_audit_serpapi.csv"):
    """Export SEO metrics to a CSV file inside the 'data' folder."""
    if not data:
        return  # No need to create an empty file

    file_path = os.path.join("data", filename)  # Save inside 'data' folder
    os.makedirs("data", exist_ok=True)  # Ensure 'data' folder exists

    file_exists = os.path.isfile(file_path)

    with open(file_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["Domain", "Total Organic Results", "Top Articles"])

        for entry in data:
            top_articles = "\n".join([f"{a['title']} ({a['url']})" for a in entry["Top Articles"]])
            writer.writerow([entry["Domain"], entry["Total Organic Results"], top_articles])

    print(f"✅ SEO Audit data saved to {file_path}")

if __name__ == "__main__":
    urls = read_top_urls()
    seo_data = [get_seo_metrics(extract_domain(url)) for url in urls if url]
    seo_data = [entry for entry in seo_data if entry]  # Remove None values
    export_to_csv(seo_data)
