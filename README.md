# Japan Disaster Risk Analysis

A Streamlit web app that combines flood and landslide records with population density for all 47 Japanese prefectures, then shows a holistic risk score on an interactive map.

**Live app:** https://japan-data-analysis.streamlit.app/

## What it does

- Loads historical flood and landslide damage records from an Excel workbook (`flood.xlsx`).
- Joins them to population data (`Japan_population_data.csv`) by prefecture.
- Normalises each measure to a 0–1 scale and combines them into a single holistic risk score.
- Plots population density and risk per prefecture on a map built from `japan_prefectures.geojson`.

## Skills demonstrated

- **Data wrangling:** reading Excel files with multi-row headers, renaming Japanese-language columns, dropping empty rows and joining tables on a shared key.
- **Feature scaling:** min-max normalisation with scikit-learn so that different units can be compared.
- **Geospatial visualisation:** choropleth maps with Plotly from GeoJSON boundaries.
- **Web apps:** Streamlit layout, caching with `st.cache_data`, and deployment to Streamlit Community Cloud.

## Run it locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app reads its data files from the working directory, so run the command from the repository root.

## Data sources

Population figures come from the Statistics Bureau of Japan (census). Flood and landslide figures are from the national disaster records included in `flood.xlsx`.
