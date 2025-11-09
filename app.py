# Run: streamlit run app.py

from pathlib import Path
from typing import Optional

import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ----------------------------
# App config
# ----------------------------
st.set_page_config(page_title="Archaeobotanical Data Visualizer", layout="wide")
st.title("🌿 Archaeobotanical Data Visualizer")
st.caption("Explore where plant types were found and inspect key patterns (abundance, ubiquity, co-occurrence).")

# ----------------------------
# Data loading
# ----------------------------
DATA_PATH = Path(__file__).parent / "plants_data.csv"

@st.cache_data(show_spinner=True)
def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        st.error(f"Dataset not found: {path}")
        st.stop()

    # Use low_memory=False to avoid dtype guessing across chunks
    df = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
    return df

df = load_data(DATA_PATH)

# ----------------------------
# Light normalization (map-style like your snippet)
# ----------------------------
def first_match(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    # Try exact, then case-insensitive
    for c in candidates:
        if c in df.columns:
            return c
    lower = {c.lower(): c for c in df.columns}
    for c in candidates:
        if c.lower() in lower:
            return lower[c.lower()]
    return None

# Coordinates
lat_col = first_match(df, ["lat", "Latitude", "Lat", "Y"])
lon_col = first_match(df, ["lon", "Longitude", "Long", "Lng", "X"])
if not lat_col or not lon_col:
    st.error("Latitude/Longitude columns not found. Expected 'lat'/'lon' (or Latitude/Longitude).")
    st.stop()

df["Latitude"] = pd.to_numeric(df[lat_col], errors="coerce")
df["Longitude"] = pd.to_numeric(df[lon_col], errors="coerce")
df = df[df["Latitude"].between(-90, 90) & df["Longitude"].between(-180, 180)].copy()

# Plant (Taxon)
plant_col = first_match(df, [
    "taxon_std_norm", "taxon_std", "taxon",
    "Plant type", "Taxon", "Gebruiksplant", "Nederlands", "Engels"
])
df["Plant"] = df[plant_col].astype(str) if plant_col else pd.NA

# Site
site_col = first_match(df, ["site_name", "Site", "plaats", "site_nr"])
df["Site"] = df[site_col].astype(str) if site_col else pd.NA

# Optional hover fields
ctx_col  = first_match(df, ["Context", "context_type", "feature_type", "feature_code"])
pres_col = first_match(df, ["Preservation", "preservation_desc", "pres_mode_desc", "pres_mode"])
ref_col  = first_match(df, ["Reference", "report_nr", "archis_zaaknr"])
qty_col  = first_match(df, ["count_filled", "count_estimate", "min_n", "max_n", "presence", "Quantity"])

if ctx_col:  df["Context"] = df[ctx_col]
if pres_col: df["Preservation"] = df[pres_col]
if ref_col:  df["Reference"] = df[ref_col]
if qty_col:  df["Quantity"] = df[qty_col]

# Quant columns for charts
# presence
if "presence" not in df.columns:
    # Derive presence from any count-like column if possible
    candidates = [c for c in ["count_filled", "count_estimate", "max_n", "min_n", "count", "nr"] if c in df.columns]
    if candidates:
        df["presence"] = (pd.to_numeric(df[candidates[0]], errors="coerce").fillna(0) > 0).astype(int)
    else:
        df["presence"] = 1  # last-resort fallback

# count_filled
if "count_filled" not in df.columns:
    prefer = [c for c in ["count_estimate", "max_n", "min_n", "count", "nr"] if c in df.columns]
    def _coalesce_row(row):
        for k in prefer:
            v = row.get(k, np.nan)
            if pd.notna(v): return v
        return np.nan
    df["count_filled"] = df.apply(_coalesce_row, axis=1)
df["count_filled"] = pd.to_numeric(df["count_filled"], errors="coerce")

# sample_nr for co-occurrence
sample_col = first_match(df, ["sample_nr", "sample_id", "sample", "monster", "monster_id"])
if sample_col:
    df["sample_nr"] = df[sample_col]

st.sidebar.header("Filters")

plant_options = sorted([p for p in df["Plant"].dropna().unique() if p != "nan"]) if "Plant" in df.columns else []
sel_plants = st.sidebar.multiselect("Plant (Taxon)", options=plant_options, default=[])

filtered = df.copy()
if sel_plants:
    filtered = filtered[filtered["Plant"].isin(sel_plants)]

# ----------------------------
# Metrics + Map (Mapbox open-street-map, like your reference)
# ----------------------------
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
    color="Period" if "Period" in filtered.columns else None,  # for visual context only
    zoom=6,          # NL-friendly default; users can pan/zoom
    height=820,      # make it bigger
)
fig.update_layout(
    mapbox_style="open-street-map",
    margin=dict(l=0, r=0, t=0, b=0),
)
st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# Tabs: Top taxa (abundance) · Ubiquity by taxon · Co-occurrence (Jaccard)
# ----------------------------
t1, t2, t3 = st.tabs(["Top taxa (abundance)", "Ubiquity by taxon", "Co-occurrence (Jaccard)"])

with t1:
    st.caption("Sum of quantitative counts per plant (uses `count_filled`, falls back to derived values).")
    if "Plant" in filtered.columns:
        topN = st.slider("Top N", 5, 50, 20)
        by_taxon = (
            filtered.groupby("Plant", dropna=False)["count_filled"]
            .sum()
            .sort_values(ascending=False)
            .head(topN)
        )
        fig1 = px.bar(by_taxon, title="Top plant types by abundance (sum of count_filled)")
        st.plotly_chart(fig1, use_container_width=True)
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
        grp = filtered.groupby("Plant", dropna=False)
        ubiq = grp["presence"].mean().mul(100).sort_values(ascending=False).head(30)
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
        mat = (
            filtered.assign(val=1)
            .pivot_table(index="sample_nr", columns="Plant", values="val", aggfunc="max", fill_value=0)
        )
        preval = mat.sum(axis=0).sort_values(ascending=False)
        K = st.slider("Max plant types in matrix", 10, 80, 30)
        keep = preval.index[:K]
        M = mat[keep].to_numpy(dtype=float)
        inter = M.T @ M
        row_sums = preval[keep].to_numpy()
        unions = (row_sums[:, None] + row_sums[None, :] - inter)
        with np.errstate(divide='ignore', invalid='ignore'):
            jac = np.where(unions > 0, inter / unions, 0.0)
        heat = go.Figure(data=go.Heatmap(z=jac, x=keep, y=keep, coloraxis="coloraxis"))
        heat.update_layout(title="Plant type co-occurrence (Jaccard)", coloraxis_colorscale="Viridis")
        st.plotly_chart(heat, use_container_width=True)
        try:
            buf = io.BytesIO(); heat.write_image(buf, format="png")
            st.download_button("Download matrix (PNG)", data=buf.getvalue(), file_name="cooccurrence_jaccard.png", mime="image/png")
        except Exception:
            st.caption("Install `kaleido` to enable PNG download of figures.")
    else:
        st.info("A sample identifier column (e.g., `sample_nr`) is required to compute co-occurrence.")

# ----------------------------
# (Optional) quick peek
# ----------------------------
with st.expander("Preview filtered rows"):
    cols = [c for c in ["Site","Latitude","Longitude","Period","Plant","Context","Preservation","Quantity","Reference"] if c in filtered.columns]
    st.dataframe(filtered[cols].reset_index(drop=True), use_container_width=True)
