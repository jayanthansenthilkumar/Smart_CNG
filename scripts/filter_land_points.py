import sys
import os
import json
import requests
import pandas as pd
from shapely.geometry import Point, shape
from shapely.ops import unary_union


NE_LAND_GEOJSON_URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_land.geojson"
)


def load_land_union() -> object:
    """Download Natural Earth land polygons as GeoJSON and return a unary union geometry."""
    resp = requests.get(NE_LAND_GEOJSON_URL, timeout=60)
    resp.raise_for_status()
    gj = resp.json()
    geoms = []
    for feat in gj.get("features", []):
        geom = feat.get("geometry")
        if geom:
            geoms.append(shape(geom))
    if not geoms:
        raise RuntimeError("No land polygons loaded from Natural Earth GeoJSON")
    return unary_union(geoms)


def filter_csv_to_land(input_csv: str, output_csv: str) -> None:
    df = pd.read_csv(input_csv)

    # Find lat/lon columns robustly
    lower_cols = {str(c).strip().lower(): c for c in df.columns}
    lat_col = next((lower_cols[c] for c in ["lat", "latitude", "@lat"] if c in lower_cols), None)
    lon_col = next((lower_cols[c] for c in ["lng", "lon", "long", "longitude", "@lon"] if c in lower_cols), None)
    if not lat_col or not lon_col:
        raise ValueError("Latitude/Longitude columns not found in CSV")

    land_union = load_land_union()

    def is_on_land(lat_val, lon_val) -> bool:
        try:
            lat_f = float(lat_val)
            lon_f = float(lon_val)
        except Exception:
            return False
        pt = Point(lon_f, lat_f)
        return land_union.contains(pt) or land_union.touches(pt) or land_union.intersects(pt)

    mask = [is_on_land(lat, lon) for lat, lon in zip(df[lat_col], df[lon_col])]
    cleaned = df[mask].copy()
    cleaned.to_csv(output_csv, index=False)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/filter_land_points.py <input_csv> <output_csv>")
        sys.exit(1)
    inp = sys.argv[1]
    out = sys.argv[2]
    if not os.path.exists(inp):
        print(f"Input file not found: {inp}")
        sys.exit(1)
    filter_csv_to_land(inp, out)


