import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import csv  # Fix: Import csv module
import os  # Import os module for directory handling

# Ensure 'data' directory exists
os.makedirs("data", exist_ok=True)

# Load URLs from blog_metadata.csv
df = pd.read_csv("data/blog_metadata.csv")  # Read from 'data' directory

# Ensure "URL" column exists
if "URL" not in df.columns:
    raise ValueError("No 'URL' column found in blog_metadata.csv")

# Extract URLs
urls = df["URL"].dropna().tolist()

# Common CTA keywords
cta_keywords = ["buy", "shop", "subscribe", "sign up", "get started", "learn more",
                "add to cart", "start free", "discover", "explore", "join", "book now", "order"]

# List to store CTA analysis results
cta_data = []

# Function to extract CTAs and their placement
def extract_cta(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract CTA-related elements
        buttons = {btn.text.strip(): "Button" for btn in soup.find_all("button") if btn.text.strip()}
        links = {a.text.strip(): "Link" for a in soup.find_all("a") if a.text.strip()}
        spans = {span.text.strip(): "Span" for span in soup.find_all("span") if span.text.strip()}
        divs = {div.text.strip(): "Div" for div in soup.find_all("div") if div.text.strip()}

        # Combine all text elements with type
        all_ctas = {**buttons, **links, **spans, **divs}

        # Filter relevant CTAs
        cta_matches = {text: all_ctas[text] for text in all_ctas if any(re.search(rf"\b{cta}\b", text, re.IGNORECASE) for cta in cta_keywords)}

        # Placement detection
        header_ctas = [text for text, tag in cta_matches.items() if soup.find(["nav", "header"], string=re.compile(rf"\b{text}\b", re.IGNORECASE))]
        footer_ctas = [text for text, tag in cta_matches.items() if soup.find("footer", string=re.compile(rf"\b{text}\b", re.IGNORECASE))]
        body_ctas = list(cta_matches.keys())  # Any CTA found in content

        return {
            "URL": url,
            "Common CTAs": "; ".join(cta_matches.keys()) if cta_matches else "None",
            "Header CTAs": "; ".join(header_ctas) if header_ctas else "None",
            "Footer CTAs": "; ".join(footer_ctas) if footer_ctas else "None",
            "Body CTAs": "; ".join(body_ctas) if body_ctas else "None",
            "Total CTAs": len(cta_matches)
        }
    except Exception as e:
        return {"URL": url, "Common CTAs": "Error", "Header CTAs": "Error", "Footer CTAs": "Error", "Body CTAs": "Error", "Total CTAs": 0}

# Process all URLs
for url in urls:
    cta_data.append(extract_cta(url))

# Convert to DataFrame and save as CSV in 'data' directory
cta_df = pd.DataFrame(cta_data)
cta_df.to_csv("data/cta_analysis.csv", index=False, quoting=csv.QUOTE_ALL)

print("CTA extraction completed. Results saved to data/cta_analysis.csv.")
