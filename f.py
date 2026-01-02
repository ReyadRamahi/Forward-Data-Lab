import json

with open("asta_enriched_deduped.json", encoding="utf-8") as f:
    data = json.load(f)

for d in data:
    d.pop("question", None)

with open("asta_docs_only.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(len(data))
