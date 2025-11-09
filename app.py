
# Archaeobotanical Data Visualizer
# -----------------------------------------------------------------------------
# Purpose: This script provides a map-centered exploration of archaeobotanical
#          records together with a few compact analyses commonly used in the
#          discipline (abundance, ubiquity, co-occurrence).
# Audience: Archaeologists, archaeological scientists, and digital humanities
#           researchers who want a clear, reproducible way to inspect plant
#           macro-remain datasets without requiring GIS software.
#
# Run: streamlit run app.py
# Tip: create a virtual environment and `pip install -r requirements.txt` first.
#
# Notes on design:
# - The code is intentionally divided into short, named functions; this makes
#   the analysis steps explicit and easier to audit or reuse.
# - A light “column normalization” stage harmonizes field names from different
#   datasets so that the visualizations can work across projects.
# - We avoid advanced dependencies; the map uses OpenStreetMap tiles via Plotly,
#   which does not require API keys.

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional, Sequence

import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =====================================================================
# 1) Application configuration
# ---------------------------------------------------------------------
# Streamlit configuration defines the title, layout, and top-level notes
# visible to the user. The caption summarizes what this tool shows.
# =====================================================================

st.set_page_config(page_title="Archaeobotanical Data Visualizer", layout="wide")
st.title("🌿 Archaeobotanical Data Visualizer")
st.caption("Explore where plant types were found and inspect key patterns (abundance, ubiquity, co-occurrence).")

# The app attempts to load the first CSV found among these candidates.
# Adjust or extend this list to fit your repository layout.
DEFAULT_DATA_CANDIDATES: Sequence[Path] = (
    Path(__file__).parent / "processed" / "plants_enriched.csv",
    Path(__file__).parent / "plants_data.csv",
)

# =====================================================================
# 2) Utility helpers
# ---------------------------------------------------------------------
# These lightweight utilities keep the main code concise. They also make
# behavior explicit and easy to test.
# =====================================================================

def first_match(df: pd.DataFrame, candidates: Iterable[str]) -> Optional[str]:
    """Return the first candidate column that exists in the DataFrame (case-insensitive).

    Many archaeobotanical datasets use different field names for the same concept
    (e.g., 'lat' vs 'Latitude'). This helper allows us to supply a short list of
    reasonable aliases and pick whichever is present. Keeping this logic centralized
    avoids scattering defensive checks throughout the code.
    """
    for c in candidates:
        if c in df.columns:
            return c
    lower = {c.lower(): c for c in df.columns}
    for c in candidates:
        if c.lower() in lower:
            return lower[c.lower()]
    return None

@st.cache_data(show_spinner=True)
def load_first_available(paths: Sequence[Path]) -> pd.DataFrame:
    """Load the first existing CSV from a list of candidate paths.

    - `st.cache_data` memoizes the loaded DataFrame to accelerate re-runs while
      you adjust filters or charts in the app.
    - `low_memory=False` prevents type-guessing across chunks, which can cause
      subtle inconsistencies in large CSV files.
    """
    for p in paths:
        if p.exists():
            return pd.read_csv(p, encoding="utf-8-sig", low_memory=False)
    st.error("Dataset not found. Tried:\n" + "\n".join(str(p) for p in paths))
    st.stop()

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Harmonize key columns so the app can work across datasets.

    What this function does:
    - Ensures we have numeric latitude/longitude and filters out invalid values.
    - Chooses a reasonable 'Plant' (taxon) field among common aliases.
    - Creates a 'Site' label for hover cards and summary metrics.
    - Adds optional fields for hover: Context, Preservation, Reference, Quantity.
    - Derives a binary 'presence' when absent (1 if a count-like field > 0).
    - Coalesces a numeric 'count_filled' when absent, choosing the first available
      quantity-like field (e.g., count_estimate, max_n).
    - Standardizes a sample identifier as 'sample_nr' (if any), used for co-occurrence.

    The aim is not to re-model the entire dataset but to provide a minimal,
    well-documented interface that most projects can satisfy.
    """
    out = df.copy()

    # --- Coordinates ---
    lat_col = first_match(out, ["lat", "Latitude", "Lat", "Y"])
    lon_col = first_match(out, ["lon", "Longitude", "Long", "Lng", "X"])
    if not lat_col or not lon_col:
        st.error("Latitude/Longitude columns not found. Expected columns like 'lat'/'lon' or 'Latitude'/'Longitude'.")
        st.stop()

    out["Latitude"] = pd.to_numeric(out[lat_col], errors="coerce")
    out["Longitude"] = pd.to_numeric(out[lon_col], errors="coerce")
    out = out[out["Latitude"].between(-90, 90) & out["Longitude"].between(-180, 180)].copy()

    # --- Plant (Taxon) ---
    plant_col = first_match(
        out,
        ["taxon_std_norm", "taxon_std", "taxon", "Plant type", "Taxon", "Gebruiksplant", "Nederlands", "Engels"],
    )
    out["Plant"] = out[plant_col].astype(str) if plant_col else pd.NA

    # --- Site (used in hover + KPIs) ---
    site_col = first_match(out, ["site_name", "Site", "plaats", "site_nr"])
    out["Site"] = out[site_col].astype(str) if site_col else pd.NA

    # --- Optional hover fields ---
    ctx_col  = first_match(out, ["Context", "context_type", "feature_type", "feature_code"])
    pres_col = first_match(out, ["Preservation", "preservation_desc", "pres_mode_desc", "pres_mode"])
    ref_col  = first_match(out, ["Reference", "report_nr", "archis_zaaknr"])
    qty_col  = first_match(out, ["count_filled", "count_estimate", "min_n", "max_n", "presence", "Quantity"])

    if ctx_col:  out["Context"] = out[ctx_col]
    if pres_col: out["Preservation"] = out[pres_col]
    if ref_col:  out["Reference"] = out[ref_col]
    if qty_col:  out["Quantity"] = out[qty_col]

    # --- presence (binary) ---
    if "presence" not in out.columns:
        candidates = [c for c in ["count_filled", "count_estimate", "max_n", "min_n", "count", "nr"] if c in out.columns]
        if candidates:
            out["presence"] = (pd.to_numeric(out[candidates[0]], errors="coerce").fillna(0) > 0).astype(int)
        else:
            out["presence"] = 1  # conservative fallback: assume present

    # --- count_filled (numeric) ---
    if "count_filled" not in out.columns:
        prefer = [c for c in ["count_estimate", "max_n", "min_n", "count", "nr"] if c in out.columns]
        def _coalesce_row(row):
            for k in prefer:
                v = row.get(k, np.nan)
                if pd.notna(v):
                    return v
            return np.nan
        out["count_filled"] = out.apply(_coalesce_row, axis=1)
    out["count_filled"] = pd.to_numeric(out["count_filled"], errors="coerce")

    # --- sample identifier for co-occurrence ---
    sample_col = first_match(out, ["sample_nr", "sample_id", "sample", "monster", "monster_id"])
    if sample_col:
        out["sample_nr"] = out[sample_col]

    return out

# =====================================================================
# 3) Analysis helpers
# ---------------------------------------------------------------------
# These functions implement three compact, textbook-style measures:
# - Abundance (sum of counts per plant type)
# - Ubiquity (percentage of samples in which a plant occurs)
# - Co-occurrence (Jaccard similarity across plant types)
#
# They are small by design so their behavior is transparent.
# =====================================================================

def compute_top_abundance(df: pd.DataFrame, top_n: int = 20) -> pd.Series:
    """Sum of quantitative counts per plant (uses `count_filled`)."""
    return (
        df.groupby("Plant", dropna=False)["count_filled"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
    )

def compute_ubiquity(df: pd.DataFrame, top_n: int = 30) -> pd.Series:
    """Ubiquity = % of samples in which a plant occurs (uses `presence`)."""
    grp = df.groupby("Plant", dropna=False)
    return grp["presence"].mean().mul(100).sort_values(ascending=False).head(top_n)

def compute_jaccard_matrix(df: pd.DataFrame, max_taxa: int = 30) -> tuple[np.ndarray, Sequence[str]]:
    """Jaccard similarity between plant types across samples.

    We convert the dataset into a sample-by-plant binary matrix (1 if the plant
    occurs in the sample, 0 otherwise). Jaccard similarity for two plants A and B
    is defined as: intersection(A,B) / union(A,B). This emphasizes co-occurrence
    while down-weighting ubiquitous taxa.
    """
    if "sample_nr" not in df.columns or "Plant" not in df.columns:
        raise ValueError("Need 'sample_nr' and 'Plant' columns to compute co-occurrence.")
    mat = (
        df.assign(val=1)
        .pivot_table(index="sample_nr", columns="Plant", values="val", aggfunc="max", fill_value=0)
    )
    preval = mat.sum(axis=0).sort_values(ascending=False)
    keep = preval.index[:max_taxa]
    M = mat[keep].to_numpy(dtype=float)
    inter = M.T @ M
    row_sums = preval[keep].to_numpy()
    unions = (row_sums[:, None] + row_sums[None, :] - inter)
    with np.errstate(divide='ignore', invalid='ignore'):
        jac = np.where(unions > 0, inter / unions, 0.0)
    return jac, list(keep)

# =====================================================================
# 4) Load data and normalize fields
# ---------------------------------------------------------------------
# The resulting DataFrame ('df') is the unified view used by all visuals.
# =====================================================================

raw_df = load_first_available(DEFAULT_DATA_CANDIDATES)
df = normalize_columns(raw_df)

# =====================================================================
# 5) Sidebar filters (Plant)
# ---------------------------------------------------------------------
# Filters operate on the normalized columns. They are intentionally simple
# (exact match selections) to keep the interface predictable.
# =====================================================================

st.sidebar.header("Filters")

plant_options = sorted([p for p in df["Plant"].dropna().unique() if p != "nan"]) if "Plant" in df.columns else []
sel_plants = st.sidebar.multiselect("Plant (Taxon)", options=plant_options, default=[])

filtered = df.copy()
if sel_plants:
    filtered = filtered[filtered["Plant"].isin(sel_plants)]

# =====================================================================
# 6) Overview metrics and main map
# ---------------------------------------------------------------------
# Quick counters (records, sites, distinct plants) provide immediate
# context for any filter setting. The map is the primary entry point
# for spatial exploration and uses OpenStreetMap as a base.
# =====================================================================

c1, c2, c3 = st.columns(3)
c1.metric("Records", f"{len(filtered):,}")
c2.metric("Sites", f"{filtered['Site'].nunique():,}")
c3.metric("Distinct plants", f"{filtered['Plant'].nunique():,}")

st.subheader("🗺 Map of plant finds")

hover_cols = [c for c in ["Site","Period","Plant","Context","Preservation","Quantity","Reference"] if c in filtered.columns]

fig = px.scatter_mapbox(
    filtered,
    lat="Latitude",
    lon="Longitude",
    hover_name="Site" if "Site" in filtered.columns else None,
    hover_data=hover_cols,
    zoom=6,          # Netherlands-friendly default; adjust for other regions
    height=820,      # generous vertical space for comfortable exploration
)
fig.update_layout(
    mapbox_style="open-street-map",
    margin=dict(l=0, r=0, t=0, b=0),
)
st.plotly_chart(fig, use_container_width=True)

# =====================================================================
# 7) Analysis tabs
# ---------------------------------------------------------------------
# Three tabs provide compact, complementary views:
# - Top taxa by abundance (sum of 'count_filled')
# - Ubiquity (% of samples in which each plant occurs)
# - Co-occurrence (Jaccard similarity heatmap)
# =====================================================================

t1, t2, t3 = st.tabs(["Top taxa (abundance)", "Ubiquity by taxon", "Co-occurrence (Jaccard)"])

with t1:
    st.caption("Sum of quantitative counts per plant (uses `count_filled`, with sensible fallbacks).")
    if "Plant" in filtered.columns:
        topN = st.slider("Top N", 5, 50, 20)
        by_taxon = compute_top_abundance(filtered, top_n=topN)
        fig1 = px.bar(by_taxon, title="Top plant types by abundance (sum of count_filled)")
        st.plotly_chart(fig1, use_container_width=True)
        # Optional figure download (requires kaleido, already in requirements)
        try:
            buf = io.BytesIO(); fig1.write_image(buf, format="png")
            st.download_button("Download chart (PNG)", data=buf.getvalue(), file_name="top_plant_types_abundance.png", mime="image/png")
        except Exception:
            st.caption("Install `kaleido` to enable PNG download of figures.")
    else:
        st.info("No 'Plant' column found.")

with t2:
    st.caption("Ubiquity = % of samples in which a plant occurs (uses `presence`).")
    if "Plant" in filtered.columns:
        ubiq = compute_ubiquity(filtered, top_n=30)
        fig2 = px.bar(ubiq, title="Ubiquity (% of samples with plant type)")
        st.plotly_chart(fig2, use_container_width=True)
        try:
            buf = io.BytesIO(); fig2.write_image(buf, format="png")
            st.download_button("Download chart (PNG)", data=buf.getvalue(), file_name="ubiquity.png", mime="image/png")
        except Exception:
            st.caption("Install `kaleido` to enable PNG download of figures.")
    else:
        st.info("No 'Plant' column found.")

with t3:
    st.caption("Jaccard similarity between plant types across samples (requires a sample identifier column).")
    if "sample_nr" in filtered.columns and filtered["sample_nr"].nunique() > 0 and "Plant" in filtered.columns:
        K = st.slider("Max plant types in matrix", 10, 80, 30)
        jac, labels = compute_jaccard_matrix(filtered, max_taxa=K)
        heat = go.Figure(data=go.Heatmap(z=jac, x=labels, y=labels, coloraxis="coloraxis"))
        heat.update_layout(title="Plant type co-occurrence (Jaccard)", coloraxis_colorscale="Viridis")
        st.plotly_chart(heat, use_container_width=True)
        try:
            buf = io.BytesIO(); heat.write_image(buf, format="png")
            st.download_button("Download matrix (PNG)", data=buf.getvalue(), file_name="cooccurrence_jaccard.png", mime="image/png")
        except Exception:
            st.caption("Install `kaleido` to enable PNG download of figures.")
    else:
        st.info("A sample identifier column (e.g., `sample_nr`) is required to compute co-occurrence.")

# =====================================================================
# 8) Data preview
# ---------------------------------------------------------------------
# A compact, readable preview helps verify which rows are currently in
# scope after filtering. This can guide export or further analysis steps.
# =====================================================================

with st.expander("Preview filtered rows"):
    cols = [c for c in ["Site","Latitude","Longitude","Period","Plant","Context","Preservation","Quantity","Reference"] if c in filtered.columns]
    st.dataframe(filtered[cols].reset_index(drop=True), use_container_width=True)
