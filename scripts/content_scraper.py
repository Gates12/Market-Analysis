import requests
import os
import csv
from bs4 import BeautifulSoup
import nltk
nltk.download('punkt')
from rake_nltk import Rake

def extract_primary_keyword(title, description):
    """Extracts the most relevant keyword from title & meta description."""
    r = Rake()
    r.extract_keywords_from_text(f"{title} {description}")
    keywords = r.get_ranked_phrases()
    return keywords[0] if keywords else "No Keyword Found"

def scrape_website(url):
    """Extract title, description, H1 tags, and primary keyword from a webpage."""
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string.strip() if soup.title else "No Title"
        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = meta_desc["content"].strip() if meta_desc and meta_desc.get("content") else "No Description"
        h1_tags = [h1.get_text(strip=True) for h1 in soup.find_all("h1")] or ["No H1 Tags"]
        
        primary_keyword = extract_primary_keyword(title, description)

        return {
            "url": url, 
            "title": title, 
            "description": description, 
            "h1": "; ".join(h1_tags), 
            "primary_keyword": primary_keyword
        }

    except requests.exceptions.RequestException as e:
        return {"url": url, "error": f"Failed to fetch ({str(e)})"}


def save_to_csv(data, filename="scraped_data.csv"):
    """Save extracted data to a CSV file inside the 'data' folder."""
    file_path = os.path.join("data", filename)  # Save inside 'data' folder

    fieldnames = ["url", "title", "description", "h1", "primary_keyword"]

    with open(file_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        if file.tell() == 0:  # Write header if file is empty
            writer.writeheader()

        writer.writerow(data)


if __name__ == "__main__":
    test_url = input("Enter a website URL: ")
    scraped_data = scrape_website(test_url)
    print(scraped_data)

    if "error" not in scraped_data:
        save_to_csv(scraped_data)
        print(f"✅ Data saved to 'scraped_data.csv'")
    else:
        print(f"❌ Error: {scraped_data['error']}")
