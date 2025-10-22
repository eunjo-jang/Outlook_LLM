import json
from dateutil.parser import parse
from bs4 import BeautifulSoup
import re

import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_path = os.path.join(project_root, "data", "outlook_2021.jsonl")
output_path = os.path.join(project_root, "data", "outlook_2021_cleaned.jsonl")

# Subject prefixes to exclude
exclude_subject_prefixes = [
    "[SOCIAL NETWORK]", "[SPAM]", "[AUTOREPLY]", "[BOT]",
    "Newsletter", "Weekly Digest", "Your Amazon Order"
]

def clean_html(text):
    """Remove HTML from email body"""
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator="\n")

def should_exclude(record):
    """Check exclusion criteria"""
    subject = (record.get("subject") or "").strip()
    body = (record.get("body") or "").strip()

    # Exclude based on subject
    if any(subject.startswith(prefix) for prefix in exclude_subject_prefixes):
        return True
    
    # Exclude empty body
    if not body:
        return True

    return False

with open(input_path, "r", encoding="utf-8") as infile, \
     open(output_path, "w", encoding="utf-8") as outfile:

    for line in infile:
        try:
            record = json.loads(line)

            if should_exclude(record):
                continue

            # Clean HTML
            record["body"] = clean_html(record.get("body", ""))

            # Standardize date format
            try:
                record["date"] = parse(record.get("date", "")).isoformat()
            except:
                record["date"] = ""

            outfile.write(json.dumps(record, ensure_ascii=False) + "\n")

        except Exception as e:
            print(f"❌ Error during processing: {e}")