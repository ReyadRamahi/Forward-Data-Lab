# Forward Data First Task – Research Pipeline

This repository contains the complete data collection, processing, and analysis pipeline used to compare ASTA-curated academic sources with Google Scholar sources. The objective of this project is to analyze differences in publication recency and citation distributions in a reproducible and transparent manner.

## Repository Structure

Forward-Data-First-Task-Research/
|
|-- data/
|   |-- raw/
|   |   |-- asta_sources_unique.csv
|   |   |-- asta_titles.csv
|   |   |-- scholar_cache.json
|   |
|   |-- processed/
|   |   |-- asta_enriched.json
|   |   |-- asta_enriched_with_years.json
|   |   |-- scholar_cache_with_years.json
|   |
|   |-- derived/
|       |-- fig_year_distribution.png
|       |-- fig_citation_distribution.png
|
|-- scripts/
|   |-- 01_asta_query.py
|   |-- 02_scholar_query.py
|   |-- 03_year_extraction.py
|   |-- 04_graph_makers.py
|
|-- requirements.txt
|-- README.md
|-- .gitignore

## Pipeline Overview

1. ASTA data collection
   The script 01_asta_query.py queries ASTA and produces enriched metadata for each source.

2. Google Scholar data collection
   The script 02_scholar_query.py queries Google Scholar and caches results locally to avoid repeated requests.

3. Year inference and normalization
   The script 03_year_extraction.py fills missing publication years using regex extraction from titles, venues, URLs, and arXiv identifiers.

4. Analysis and visualization
   The script 04_graph_makers.py generates publication-ready figures comparing ASTA and Google Scholar distributions.

## Figures Produced

fig_year_distribution.png  
Side-by-side normalized percentage distribution of publication years.

fig_citation_distribution.png  
Side-by-side normalized percentage distribution of citation count buckets.

All figures are generated at 300 DPI and are suitable for direct inclusion in academic papers.

## Environment Setup

A Python virtual environment is recommended.

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Required packages:
matplotlib
numpy
tqdm
requests

## Running the Pipeline

python scripts/01_asta_query.py
python scripts/02_scholar_query.py
python scripts/03_year_extraction.py
python scripts/04_graph_makers.py

## Notes

Raw input data is preserved and never overwritten. All processed and derived artifacts are reproducible from the provided scripts. Figures are normalized to avoid dataset size bias between ASTA and Google Scholar.

This repository is intended to support transparent, reproducible research.
