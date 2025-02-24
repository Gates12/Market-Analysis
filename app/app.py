from flask import Flask, render_template
import pandas as pd
import os

app = Flask(__name__)

# Get project root dynamically
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Correct file paths
cta_csv_path = os.path.join(base_dir, "data", "cta_analysis.csv")
top_urls_csv_path = os.path.join(base_dir, "data", "top_urls.csv")  # Fixed `.csv.csv` issue

# Read CSV files
cta_df = pd.read_csv(cta_csv_path)
top_urls_df = pd.read_csv(top_urls_csv_path)

@app.route("/")
def dashboard():
    return render_template(
        "index.html", 
        competitor_keyword="Sample Keyword",
        top_ranking_sites=top_urls_df.to_dict(orient="records"),
        cta_data=cta_df.to_dict(orient="records")
    )

if __name__ == "__main__":
    app.run(debug=True)
