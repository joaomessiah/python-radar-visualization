# 🌿 Archaeobotanical Data Visualizer (Python RADAR Visualization)

**Archaeobotanical Data Visualizer** is an interactive research tool built with Python and designed as an accessible web-based tool for exploring archaeobotanical data. It helps archaeologists, archaeobotanists, and digital humanities researchers explore, analyze, and communicate findings from plant macro-remain datasets in a clear and accessible way.

It provides a reproducible and FAIR-compliant framework for turning raw archaeobotanical data into visual insights that highlight patterns in plant distribution, ecology, and human–environment interaction.

Inspired by datasets from the Lower Rhine Delta (Netherlands), the project aims to make archaeobotanical data more accessible, transparent, and reusable for comparative and interdisciplinary work.

The original archaeobotanical dataset used in this visualization originates from the [Zadendatabase (RADAR)](https://www.cultureelerfgoed.nl/onderwerpen/b/bronnen-en-kaarten/overzicht/zadendatabase), maintained by the Cultural Heritage Agency of the Netherlands (Rijksdienst voor het Cultureel Erfgoed).

For installation instructions, see the [installation guide](INSTALLATION.md).


## 🌍 What the Visualization Does

This visualization allows users to:

1. **Visualize** archaeobotanical data on an interactive map with zoom and filtering.  
2. **Filter by plant taxa** to see specific patterns across archaeological sites.  
3. **Quantify patterns** using abundance, ubiquity, and co-occurrence analyses.  
4. **Inspect metadata** such as site name, feature type, preservation mode, and report number.  
5. **Export** visual outputs (charts and heatmaps) as PNG for publication or teaching.

By combining visual exploration with statistical summaries, the tool bridges the gap between raw excavation data and interpretive research questions in archaeobotany and environmental archaeology.


## 📊 Main Features

| Section | Description |
|----------|-------------|
| **Interactive Map** | Displays plant finds across sites using OpenStreetMap tiles. Each point represents an archaeological sample. |
| **Top Taxa (Abundance)** | Highlights which plant taxa are most common in the dataset, based on counts. |
| **Ubiquity by Taxon** | Shows how widespread each plant type is across samples (% of presence). |
| **Co-occurrence (Jaccard)** | Generates a similarity matrix showing which plants tend to appear together in the same contexts. |
| **Data Preview** | Expandable preview of filtered data with key metadata fields for transparency. |


## 🧩 FAIR Principles

This project adheres to the [FAIR Data Principles](https://www.go-fair.org/fair-principles/) to ensure **Findability, Accessibility, Interoperability, and Reusability** of both data and software.

| Principle | Implementation |
|------------|----------------|
| **Findable** | Code and documentation are openly available on GitHub. Dataset filename and location are explicit (`plants_data.csv`). |
| **Accessible** | The visualization and dataset can be used locally or deployed online through Streamlit Cloud or Hugging Face Spaces. |
| **Interoperable** | Data stored in UTF-8 CSV format with standardized field names suitable for Python, R, and GIS workflows. |
| **Reusable** | Includes detailed paradata and transparent code logic to ensure reproducibility and scholarly reusability. |


## 🧪 Paradata: Data Cleaning and Processing Workflow

The *paradata* documents every transformation applied to the raw archaeobotanical dataset to make it ready for exploration and visualization.

**1. Data Integration**  
Raw datasets from different excavation reports and laboratory sources were merged into a single standardized file (`plants_data.csv`). Each record represents a sample from a defined archaeological feature at a specific site.

**2. Column Standardization**  
Flexible mapping via `first_match()` identifies column variants (`Latitude`, `lat`, `Y`, etc.).  
Taxon names were harmonized using standard taxonomic fields (`taxon_std_norm`).  
Coordinates were converted to numeric form and filtered for validity.

**3. Quantitative Normalization**  
Missing `count_filled` values were derived from `count_estimate`, `max_n`, or `min_n`.  
Presence/absence values were inferred where necessary.  
Rows with invalid coordinates were excluded to avoid spatial noise.

**4. Derived Variables**  
New standardized fields were generated: `Site`, `Plant`, `Latitude`, `Longitude`, `Context`, `Preservation`, `Reference`, `Quantity`, and `presence`.

**5. Analytical Layers**  
Abundance = sum of counts per plant taxon.  
Ubiquity = % of samples containing each taxon.  
Co-occurrence = Jaccard similarity between taxa across samples.  


## 🧠 Python Libraries Used

| Library | Purpose |
|----------|----------|
| **Streamlit** | Provides the interactive web interface. |
| **Pandas** | Data cleaning, transformation, and analysis. |
| **NumPy** | Numerical and matrix computations. |
| **Plotly Express / Graph Objects** | Visualization of maps, charts, and heatmaps. |
| **Kaleido** | Exports charts as PNG images. |
| **PyProj** | Coordinate transformations for geographic consistency. |
| **Polars** | High-performance dataframe operations for large datasets. |
| **Scikit-learn** | Matrix-based statistical operations and similarity calculations. |
| **Pathlib / io** | File handling and in-memory buffering. |


## 🧰 Tech Stack

- **Python 3.13**
- [Streamlit 1.51.0](https://streamlit.io/)
- [Pandas 2.3.3](https://pandas.pydata.org/)
- [NumPy 2.3.4](https://numpy.org/)
- [Plotly 6.4.0](https://plotly.com/python/)
- [Kaleido 1.2.0](https://github.com/plotly/Kaleido)
- [Scikit-learn 1.7.2](https://scikit-learn.org/)
- [PyProj 3.7.2](https://pyproj4.github.io/pyproj/stable/)
- [Polars 1.35.2](https://pola.rs/)


## 🧭 Example Outputs

- **Map:** Archaeobotanical sample locations across the Netherlands  
- **Charts:** Top taxa by abundance and ubiquity  
- **Heatmap:** Taxon co-occurrence matrix based on Jaccard similarity  


## 📚 Scientific and Educational Context

This visualization was developed to support archaeobotanical research in the **Lower Rhine Delta**, part of the Roman frontier zone.  
By offering intuitive access to large, complex datasets, it aims to:
- Facilitate pattern recognition across sites and periods  
- Support teaching in digital archaeology and environmental data interpretation  
- Promote transparency and reuse in archaeobotanical data management  
- Serve as a reproducible model for similar digital heritage datasets  


## 📄 Citation

If you use this visualization or its methodology, please cite:

> [João Silva, ORCID 0009-0007-4716-3957](https://orcid.org/0009-0007-4716-3957). *Archaeobotanical Data Visualizer (Python RADAR Visualization) – A FAIR Streamlit visualization for exploring plant macro-remain datasets*. GitHub Repository. [https://github.com/joaomessiah/python-radar-visualization](https://github.com/joaomessiah/python-radar-visualization)


## 🪶 License

This project is distributed under the **MIT License**, allowing reuse and adaptation with attribution.


## 💬 Acknowledgments

This project benefits from open archaeological datasets, the Streamlit open-source ecosystem, and the collective effort to make archaeobotanical data FAIR, transparent, and reusable.
