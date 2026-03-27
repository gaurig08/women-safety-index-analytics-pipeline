import pandas as pd
import folium
from folium.plugins import HeatMap
import requests
from sqlalchemy import create_engine

DB_URL = "postgresql://postgres:password@localhost:5433/safety_db"
engine = create_engine(DB_URL)

def get_district_coordinates(district_name, state_name):
    """Get lat/long from OpenStreetMap Nominatim API"""
    try:
        query = f"{district_name}, {state_name}, India"
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": query, "format": "json", "limit": 1},
            headers={"User-Agent": "safety-pipeline/1.0"}
        )
        results = r.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    except:
        pass
    return None, None

def build_map():
    # Load 2022 data
    df = pd.read_sql("""
        SELECT l.state_name, l.district_name, 
               f.safety_score, f.risk_category, 
               f.total_crimes, f.year
        FROM fact_safety f
        JOIN dim_location l ON f.location_id = l.location_id
        WHERE f.year = 2022
        ORDER BY f.safety_score DESC
    """, engine)

    print(f"Loaded {len(df)} districts for 2022")
    print("Fetching coordinates (this takes 2-3 mins)...")

    # Get coordinates for top 100 districts by safety score
    # (fetching all 750 would take too long)
    df_top = df.head(100).copy()
    
    coords = []
    for i, row in df_top.iterrows():
        lat, lon = get_district_coordinates(row["district_name"], row["state_name"])
        coords.append({"lat": lat, "lon": lon, 
                       "score": row["safety_score"],
                       "district": row["district_name"],
                       "state": row["state_name"],
                       "risk": row["risk_category"],
                       "crimes": row["total_crimes"]})
        if i % 10 == 0:
            print(f"  Processed {i}/100...")

    coords_df = pd.DataFrame(coords).dropna(subset=["lat", "lon"])
    print(f"Got coordinates for {len(coords_df)} districts")

    # Build Folium map
    m = folium.Map(
        location=[20.5937, 78.9629],  # Center of India
        zoom_start=5,
        tiles="CartoDB dark_matter"
    )

    # Add heatmap layer
    heat_data = [
        [row["lat"], row["lon"], row["score"] / 100]
        for _, row in coords_df.iterrows()
    ]
    HeatMap(
        heat_data,
        min_opacity=0.4,
        radius=25,
        blur=15,
        gradient={0.2: "blue", 0.5: "yellow", 0.8: "orange", 1.0: "red"}
    ).add_to(m)

    # Add circle markers with popups
    for _, row in coords_df.iterrows():
        color = {
            "Critical": "red",
            "High": "orange", 
            "Moderate": "yellow",
            "Low": "green"
        }.get(row["risk"], "blue")

        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=8,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(
                f"""
                <b>{row['district']}, {row['state']}</b><br>
                Risk Level: <b>{row['risk']}</b><br>
                Safety Score: <b>{row['score']:.1f}/100</b><br>
                Total Crimes: <b>{int(row['crimes'])}</b><br>
                Year: 2022
                """,
                max_width=200
            )
        ).add_to(m)

    # Add title
    title_html = """
        <div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
                    z-index: 1000; background-color: rgba(0,0,0,0.7); 
                    padding: 10px 20px; border-radius: 8px; color: white;">
            <h3 style="margin:0; font-family: Arial;">
                🔴 Women's Safety Index — India 2022
            </h3>
            <p style="margin:0; font-size:12px; color:#ccc;">
                Top 100 highest-risk districts | Source: NCRB via India Data Portal
            </p>
        </div>
    """
    m.get_root().html.add_child(folium.Element(title_html))

    m.save("safety_map.html")
    print("✅ Interactive map saved as safety_map.html")
    print("   Open safety_map.html in your browser to view")

if __name__ == "__main__":
    build_map()