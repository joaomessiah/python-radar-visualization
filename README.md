# 🌿 Archaeobotanical Data Visualizer (Python RADAR Visualization)

**Archaeobotanical Data Visualizer** is an interactive Python and [Streamlit](https://streamlit.io/) application for exploring plant macro-remain datasets from archaeological contexts.  
It visualizes where plant taxa were found, their relative abundance, ubiquity across samples, and co-occurrence patterns — supporting quantitative, spatial, and ecological analysis of archaeobotanical data.

---

## 🚀 Quick Start

### Requirements
```bash
pip install streamlit pandas numpy plotly kaleido
```

### Run the app
```bash
streamlit run app.py
```

The app expects the enriched dataset to be available at:
```
./plants_data.csv
```

---

## 📊 Features

| Section | Description |
|----------|--------------|
| **Interactive Map** | Displays all plant finds on a map (OpenStreetMap background). Each point represents a site or sample with taxonomic and contextual metadata. |
| **Top Taxa (Abundance)** | Bar chart of the most abundant plant taxa, based on quantitative counts (`count_filled` or derived equivalents). |
| **Ubiquity by Taxon** | Shows how frequently each plant type occurs across samples (percentage of samples with presence). |
| **Co-occurrence (Jaccard)** | Heatmap showing similarity between plant taxa based on shared occurrence in samples (Jaccard index). |
| **Data Preview** | Expandable table showing filtered data rows for quick inspection. |

---

## 🧩 FAIR Principles

This project follows the [FAIR Data Principles](https://www.go-fair.org/fair-principles/):

| Principle | Implementation                                                                                                             |
|------------|----------------------------------------------------------------------------------------------------------------------------|
| **Findable** | Source code and documentation are openly available on GitHub. Dataset location is explicit (`plants_data.csv`). |
| **Accessible** | The app and dataset can be freely used locally or deployed on the web via Streamlit Cloud or similar platforms.            |
| **Interoperable** | Data is stored as a clean UTF-8 CSV file with standardized field names, ready for analysis in Python, R, or GIS tools.     |
| **Reusable** | Code and documentation include metadata and paradata describing cleaning and processing steps, ensuring reproducibility.   |

---

## 🧪 Paradata: Data Cleaning and Processing Workflow

The *paradata* below document how the raw archaeobotanical records were cleaned, harmonized, and integrated before visualization.

### 1. Data Integration
- Multiple excavation reports and archaeobotanical datasets were merged into a single file: `plants_data.csv`.
- Each row represents a **sample** from an archaeological **feature** at a **site**.
- Metadata from the original reports (context type, preservation, chronology, etc.) were standardized.

### 2. Standardization
- **Column matching**: the script dynamically identifies equivalent columns using a helper function (`first_match`) that accepts alternative names (`lat`, `Latitude`, `Y`, etc.).
- **Taxon normalization**: plant names were harmonized under `taxon_std_norm`.
- **Coordinates**: latitude and longitude values were coerced to numeric form and filtered to valid geographic ranges.
- **Site and context names** were normalized (`plaats`, `site_nr`, `feature_type`, etc.).

### 3. Quantitative Cleaning
- Missing quantitative fields (`count_filled`) were **derived** from alternatives (`count_estimate`, `max_n`, `min_n`, etc.).
- **Presence/absence** was inferred as `1` when any count > 0.
- Samples with invalid or missing coordinates were excluded from mapping.

### 4. Enrichment
- New standardized columns were added: `Site`, `Plant`, `Latitude`, `Longitude`, `Context`, `Preservation`, `Reference`, `Quantity`, and `presence`.
- Derived variables allow unified filtering and visualization across heterogeneous data sources.

### 5. Analytical Layers
- **Abundance**: sum of quantitative values per taxon.
- **Ubiquity**: percentage of samples in which a taxon occurs.
- **Co-occurrence**: Jaccard similarity computed over sample × taxon matrices.

All transformations are performed transparently within `app.py`, ensuring reproducibility and traceability from raw to processed data.

---

## 🧠 Python Libraries Used

| Library | Purpose |
|----------|----------|
| **Streamlit** | Web framework for interactive data visualization and dashboarding. |
| **Pandas** | Data cleaning, normalization, and aggregation of tabular archaeobotanical data. |
| **NumPy** | Matrix and numerical computations (e.g., Jaccard similarity). |
| **Plotly Express** | Interactive charts (bar plots, maps). |
| **Plotly Graph Objects** | Advanced visualizations like heatmaps. |
| **Kaleido** | Enables PNG export of visualizations. |
| **Pathlib / io** | File and buffer handling. |

---

## 🗺️ Example Output

- **Map:** Locations of plant finds across the Netherlands  
- **Bar charts:** Top 20 plant taxa by abundance and ubiquity  
- **Heatmap:** Jaccard similarity among the most frequent taxa  

---

## 🧠 Scientific Context

This visualization was developed as part of ongoing archaeobotanical research in the **Lower Rhine Delta (Netherlands)**, focusing on spatial and temporal distribution of plant taxa in Roman and post-Roman contexts.

The goal is to enhance **data transparency**, **comparability**, and **explorability** in archaeobotanical studies by following FAIR and open science practices.

---

## 📄 Citation

If you use this tool or its methodology, please cite:

> [João Silva, ORCID 0009-0007-4716-3957](https://orcid.org/0009-0007-4716-3957). *Archaeobotanical Data Visualizer (Python RADAR Visualization) – A FAIR Streamlit application for exploring plant macro-remain datasets*. GitHub Repository. [https://github.com/joaomessiah/python-radar-visualization](https://github.com/joaomessiah/python-radar-visualization)

---

## 🪶 License

This project is released under the **MIT License**.  
You are free to reuse and adapt it, provided attribution is given.

---

## 🧰 Tech Stack

- **Python 3.10+**
- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Plotly Express](https://plotly.com/python/plotly-express/)
- [NumPy](https://numpy.org/)
- [Kaleido](https://github.com/plotly/Kaleido)

---

## 🧩 Folder Structure
```
├── app.py
├── plants_data.csv
├── README.md
└── requirements.txt
```

---

## 💬 Acknowledgments
This work builds on open archaeological datasets and community efforts to make archaeobotanical data interoperable and reusable under FAIR principles.
