from scholarly import scholarly
import csv
import json
import time
import os

questions = []

with open("questions.csv", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        questions.append(row[0])

if os.path.exists("scholar_cache.json"):
    with open("scholar_cache.json", "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {}

for question in questions:
    if question in data:
        continue

    try:
        search = scholarly.search_pubs(question)
        results = []

        for _ in range(3):
            try:
                pub = next(search)
            except StopIteration:
                break

            record = {
                "question": question,
                "title": pub.get("bib", {}).get("title"),
                "authors": pub.get("bib", {}).get("author"),
                "year": pub.get("bib", {}).get("year"),
                "venue": pub.get("bib", {}).get("venue"),
                "citations": pub.get("num_citations"),
                "url": pub.get("pub_url") or pub.get("eprint_url")
            }

            results.append(record)

        data[question] = results

        with open("scholar_cache.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        time.sleep(30)

    except Exception as e:
        print(f"Error on question: {question}")
        print(e)
        time.sleep(3600)
        continue


