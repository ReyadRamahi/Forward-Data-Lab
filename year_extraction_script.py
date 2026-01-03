import json
import re
from typing import Optional
import requests
import time
from tqdm import tqdm



# -------- CONFIG --------
INPUT_FILES = {
    "asta": "asta_enriched.json",
    "scholar": "scholar_cache.json"
}

OUTPUT_FILES = {
    "asta": "asta_enriched_with_years.json",
    "scholar": "scholar_cache_with_years.json"
}
# ------------------------


YEAR_REGEX = re.compile(r"(19|20)\d{2}")
ARXIV_REGEX = re.compile(r"arxiv[:/ ]?(\d{4})\.\d+", re.IGNORECASE)

def crossref_year(title: str) -> Optional[int]:
    if not title:
        return None

    url = "https://api.crossref.org/works"
    params = {
        "query.title": title,
        "rows": 1
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code != 200:
            return None

        items = r.json().get("message", {}).get("items", [])
        if not items:
            return None

        issued = items[0].get("issued", {}).get("date-parts", [])
        if issued and issued[0]:
            year = issued[0][0]
            if 1900 <= year <= 2030:
                return year

    except Exception:
        return None

    return None


def extract_year(text: str) -> Optional[int]:
    """Extract a plausible year from arbitrary text."""
    if not text:
        return None

    # 1️⃣ direct year match
    match = YEAR_REGEX.search(text)
    if match:
        year = int(match.group())
        if 1900 <= year <= 2030:
            return year

    # 2️⃣ arXiv ID → YYYY
    arxiv_match = ARXIV_REGEX.search(text)
    if arxiv_match:
        year = int("20" + arxiv_match.group(1)[:2])
        if 1900 <= year <= 2030:
            return year

    return None


def infer_year(paper: dict) -> Optional[int]:
    # 1️⃣ Keep existing year
    if paper.get("year"):
        return paper["year"]

    # 2️⃣ Fast regex-based extraction
    for field in ["venue", "url", "title"]:
        year = extract_year(paper.get(field, ""))
        if year:
            return year

    # 3️⃣ CrossRef fallback (only now)
    year = crossref_year(paper.get("title", ""))
    if year:
        time.sleep(0.5)  # be polite
        return year

    return None



def process_file(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = 0

    papers = []

    if isinstance(data, list):
        papers = data

    elif isinstance(data, dict):
        for value in data.values():
            if isinstance(value, list):
                for paper in value:
                    if isinstance(paper, dict):
                        papers.append(paper)


    else:
        raise ValueError("Unsupported JSON structure")

    for paper in tqdm(papers, desc=f"Inferring years ({input_path})"):
        if not paper.get("year"):
            inferred = infer_year(paper)
            if inferred:
                paper["year"] = inferred
                updated += 1
            else:
                paper["year"] = None


    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"{input_path} → {output_path}")
    print(f"  Added years to {updated} papers\n")


def main():
    for key in INPUT_FILES:
        process_file(INPUT_FILES[key], OUTPUT_FILES[key])


if __name__ == "__main__":
    main()
