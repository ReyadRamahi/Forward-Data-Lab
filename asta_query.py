import csv, json, os, time, re, tempfile, random
from tqdm import tqdm
from scholarly import scholarly

INPUT_CSV = "asta_sources_unique.csv"
CACHE_JSON = "asta_enriched.json"
MIN_SLEEP = 5
MAX_SLEEP = 10

def norm(s: str) -> str:
    if not s:
        return ""
    s = s.lower().replace("\u00a0", " ")
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def atomic_write_json(path: str, data) -> None:
    d = os.path.dirname(path) or "."
    fd, tmp_path = tempfile.mkstemp(prefix=".tmp_", suffix=".json", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except:
            pass

def load_cache(path: str) -> dict:
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except json.JSONDecodeError:
        return {}
    if not isinstance(raw, list):
        return {}
    cache = {}
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        original = (entry.get("input_title") or entry.get("title") or "").strip()
        if not original:
            continue
        k = norm(original)
        if not k:
            continue
        entry["cache_key"] = k
        entry.setdefault("input_title", original)
        cache[k] = entry
    return cache

def load_csv_titles(path: str) -> list[str]:
    titles = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            t = (r.get("title") or "").strip()
            if t:
                titles.append(t)
    return titles

def unique_titles_in_order(titles: list[str]) -> list[str]:
    out, seen = [], set()
    for t in titles:
        k = norm(t)
        if k and k not in seen:
            seen.add(k)
            out.append(t)
    return out

def is_good_pub_match(query_key: str, pub_title: str) -> bool:
    return norm(pub_title) == query_key if pub_title else False

def main():
    if not os.path.exists(INPUT_CSV):
        raise FileNotFoundError(f"Missing {INPUT_CSV}")

    titles_raw = load_csv_titles(INPUT_CSV)
    titles = unique_titles_in_order(titles_raw)
    csv_keys = {norm(t) for t in titles}

    cache = load_cache(CACHE_JSON)

    cache_in_csv = {k: v for k, v in cache.items() if k in csv_keys}

    if len(cache_in_csv) != len(cache):
        cache = cache_in_csv
        atomic_write_json(CACHE_JSON, list(cache.values()))

    remaining = [t for t in titles if norm(t) not in cache]

    print(f"CSV unique titles: {len(titles)}")
    print(f"Cached (CSV-aligned): {len(cache)}")
    print(f"Remaining: {len(remaining)}")

    for title in tqdm(remaining, desc="Processing"):
        key = norm(title)
        if key in cache:
            continue

        try:
            search = scholarly.search_pubs(f'"{title}"')
            pub = None
            for _ in range(5):
                candidate = next(search)
                bib = candidate.get("bib", {}) or {}
                cand_title = bib.get("title") or ""
                if is_good_pub_match(key, cand_title):
                    pub = candidate
                    break
                if pub is None:
                    pub = candidate

            if pub is None:
                raise StopIteration()

            bib = pub.get("bib", {}) or {}
            authors = bib.get("author") or []
            if isinstance(authors, str):
                authors = [authors]

            citations = pub.get("num_citations", None)
            if isinstance(citations, str):
                try:
                    citations = int(citations)
                except:
                    citations = None

            record = {
                "input_title": title,
                "cache_key": key,
                "title": bib.get("title"),
                "authors": authors,
                "year": bib.get("year"),
                "venue": bib.get("venue") or bib.get("journal"),
                "citations": citations,
                "url": pub.get("pub_url"),
                "source": "ASTA",
            }

            cache[key] = record
            atomic_write_json(CACHE_JSON, list(cache.values()))
            
            # Random sleep after success
            time.sleep(random.uniform(MIN_SLEEP, MAX_SLEEP))

        except StopIteration:
            cache[key] = {
                "input_title": title,
                "cache_key": key,
                "title": None,
                "authors": [],
                "year": None,
                "venue": None,
                "citations": None,
                "url": None,
                "source": "ASTA",
                "error": "no_result",
            }
            atomic_write_json(CACHE_JSON, list(cache.values()))
            
            # Random sleep after no result found
            time.sleep(random.uniform(MIN_SLEEP, MAX_SLEEP))

        except Exception as e:
            print(f"Error enriching: {title}")
            print(repr(e))
            break
        
    print(f"Final cached (CSV-aligned): {len(cache)} / {len(titles)}")

if __name__ == "__main__":
    main()