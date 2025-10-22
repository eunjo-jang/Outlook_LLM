import json
import numpy as np

# File path specification
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(project_root, "data", "outlook_2021_cleaned.jsonl")

lengths = []
with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            record = json.loads(line)
            body = record.get("body", "").strip()
            if body:  # Only if body is not empty
                lengths.append(len(body))
        except Exception as e:
            print("❌ Error:", e)

if not lengths:
    print("No data available.")
else:
    arr = np.array(lengths)
    print(f"📊 Email body length statistics ({len(arr)} emails):")
    print(f"  - Average length: {arr.mean():.1f} characters")
    print(f"  - Median: {np.median(arr):.1f} characters")
    print(f"  - Minimum: {arr.min()} characters")
    print(f"  - Maximum: {arr.max()} characters")

    # Simple distribution check
    bins = [0, 100, 200, 300, 500,1000, 2000, 5000, np.inf]
    counts, _ = np.histogram(arr, bins=bins)
    print("\n📈 Email body length distribution:")
    for b1, b2, c in zip(bins[:-1], bins[1:], counts):
        print(f"  - {int(b1)} ~ {int(b2)}: {c} emails")