import json
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np

# -------- CONFIG --------
FILES = {
    "ASTA": "data/processed/asta_enriched_with_years.json",
    "Scholar": "data/processed/scholar_cache_with_years.json"
}

OUTPUT_PREFIX = "fig_"
DPI = 300
# ------------------------


# ---------- BUCKETS ----------
YEAR_BUCKETS = [
    ("≤2000", lambda y: y is not None and y <= 2000),
    ("2001–2005", lambda y: 2001 <= y <= 2005),
    ("2006–2010", lambda y: 2006 <= y <= 2010),
    ("2011–2015", lambda y: 2011 <= y <= 2015),
    ("2016–2020", lambda y: 2016 <= y <= 2020),
    ("2021–2025", lambda y: 2021 <= y <= 2025),
]

CITATION_BUCKETS = [
    ("0", lambda c: c == 0),
    ("1–10", lambda c: 1 <= c <= 10),
    ("11–50", lambda c: 11 <= c <= 50),
    ("51–200", lambda c: 51 <= c <= 200),
    ("201–1000", lambda c: 201 <= c <= 1000),
    (">1000", lambda c: c > 1000),
]


# ---------- HELPERS ----------
def flatten_records(data):
    """Handles both list and question->list dict formats."""
    if isinstance(data, list):
        return data
    records = []
    for v in data.values():
        if isinstance(v, list):
            records.extend(v)
    return records


def bucketize(values, buckets):
    counts = Counter()
    for v in values:
        for label, rule in buckets:
            if rule(v):
                counts[label] += 1
                break
    return counts


def normalize(counter):
    total = sum(counter.values())
    return {k: (v / total) * 100 if total else 0 for k, v in counter.items()}


# ---------- LOAD DATA ----------
results = {}

for name, path in FILES.items():
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    records = flatten_records(raw)

    years = [r.get("year") for r in records if isinstance(r.get("year"), int)]
    citations = [r.get("citations", 0) for r in records if isinstance(r.get("citations"), int)]

    results[name] = {
        "year": normalize(bucketize(years, YEAR_BUCKETS)),
        "citations": normalize(bucketize(citations, CITATION_BUCKETS))
    }


# ---------- PLOTTING ----------
def plot_grouped(data_key, buckets, title, filename):
    labels = [b[0] for b in buckets]
    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5))

    for i, (source, vals) in enumerate(results.items()):
        y = [vals[data_key].get(label, 0) for label in labels]
        ax.bar(x + (i - 0.5) * width, y, width, label=source)

    ax.set_ylabel("Percentage of papers (%)")
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig(filename, dpi=DPI)
    plt.close()


plot_grouped(
    "year",
    YEAR_BUCKETS,
    "Publication Year Distribution (ASTA vs Google Scholar)",
    OUTPUT_PREFIX + "year_distribution.png"
)

plot_grouped(
    "citations",
    CITATION_BUCKETS,
    "Citation Count Distribution (ASTA vs Google Scholar)",
    OUTPUT_PREFIX + "citation_distribution.png"
)

print("Saved figures:")
print(" - fig_year_distribution.png")
print(" - fig_citation_distribution.png")
