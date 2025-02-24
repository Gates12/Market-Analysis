import os
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from collections import Counter
from nltk.corpus import stopwords
import nltk
from urllib.parse import urlparse

# Ensure stopwords are downloaded
nltk.download("stopwords")

# Define data folder and ensure it exists
DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)

# Load the CSV file safely
csv_path = os.path.join(DATA_FOLDER, "seo_audit_serpapi.csv")
try:
    df = pd.read_csv(csv_path)
    articles = df.get("Top Articles", []).dropna().tolist()
except (FileNotFoundError, KeyError):
    print("⚠️ CSV file not found or invalid format.")
    articles = []

# Flatten and extract blog titles & URLs
titles, urls = [], []
for article in articles:
    lines = article.split("\n")  # Each article is separated by a newline
    for line in lines:
        match = re.match(r"(.+?) \((https?://[^\s)]+)\)", line)  # Extract title & URL
        if match:
            titles.append(match.group(1))
            urls.append(match.group(2))

# Use nltk stopwords + additional filtering
stopwords_set = set(stopwords.words("english"))
custom_exclusions = {"blog", "post", "guide", "top", "best", "how", "why"}  # Common non-topic words
stopwords_set.update(custom_exclusions)

# Count common words in titles (excluding stopwords)
word_counts = Counter()
for title in titles:
    words = re.findall(r'\b\w+\b', title.lower())  # Tokenize
    words = [word for word in words if word not in stopwords_set]  # Remove stopwords
    word_counts.update(words)

# Get top 10 most common blog topics
common_topics = [word for word, _ in word_counts.most_common(10)]
print("Common Blog Topics:", common_topics)

# Function to fetch metadata from a webpage
def get_metadata(url):
    """Fetch title, H1, and meta description from a given URL."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        title_tag = soup.find("title").text.strip() if soup.find("title") else "N/A"
        h1_tag = soup.find("h1").text.strip() if soup.find("h1") else "N/A"
        meta_desc = (
            soup.find("meta", attrs={"name": "description"})["content"].strip()
            if soup.find("meta", attrs={"name": "description"})
            else "N/A"
        )

        return title_tag, h1_tag, meta_desc
    except Exception:
        return "N/A", "N/A", "N/A"

# Filter URLs related to common topics
filtered_urls = [url for title, url in zip(titles, urls) if any(topic in title.lower() for topic in common_topics)]

# Dictionary to store unique website metadata
unique_websites = {}

# Fetch metadata for selected URLs, ensuring only one entry per website
for url in filtered_urls:
    domain = urlparse(url).netloc  # Extract domain name
    if domain not in unique_websites:  # Only add the first occurrence of a domain
        title, h1, description = get_metadata(url)
        unique_websites[domain] = {"URL": url, "Title": title, "H1": h1, "Meta Description": description}

# Convert to DataFrame and save as CSV inside data folder
metadata_csv_path = os.path.join(DATA_FOLDER, "blog_metadata.csv")
metadata_df = pd.DataFrame(unique_websites.values())
metadata_df.to_csv(metadata_csv_path, index=False)

print(f"✅ Metadata extraction complete. Results saved in {metadata_csv_path}")
