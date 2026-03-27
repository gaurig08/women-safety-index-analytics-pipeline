import pandas as pd
from sqlalchemy import create_engine, text
from transform import transform

DB_URL = "postgresql://postgres:password@localhost:5433/safety_db"

def load():
    engine = create_engine(DB_URL)

    # Create tables
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS dim_location (
                location_id SERIAL PRIMARY KEY,
                state_name VARCHAR(100),
                district_name VARCHAR(100),
                UNIQUE(state_name, district_name)
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS fact_safety (
                id SERIAL PRIMARY KEY,
                location_id INT REFERENCES dim_location(location_id),
                year INT,
                total_crimes INT,
                safety_score FLOAT,
                risk_category VARCHAR(20),
                rape_women_above_18 FLOAT,
                rape_girls_below_18 FLOAT,
                dowry_deaths FLOAT,
                acid_attack FLOAT,
                human_trafficking FLOAT,
                kidnapping_and_abduction FLOAT,
                cruelty_by_husband_or_his_relatives FLOAT,
                assault_on_womenabove_18 FLOAT,
                murder_with_rape_gang_rape FLOAT
            );
        """))
        conn.commit()
    print("✅ Tables created")

    # Load data
    df = transform()

    # Insert locations
    locations = df[["state_name", "district_name"]].drop_duplicates()
    for _, row in locations.iterrows():
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO dim_location (state_name, district_name)
                VALUES (:state, :district)
                ON CONFLICT DO NOTHING
            """), {"state": row["state_name"], "district": row["district_name"]})
            conn.commit()

    # Get location IDs
    loc_map = pd.read_sql("SELECT location_id, state_name, district_name FROM dim_location", engine)
    df = df.merge(loc_map, on=["state_name", "district_name"], how="left")

    # Insert fact table
    fact_cols = [
        "location_id", "year", "total_crimes", "safety_score", "risk_category",
        "rape_women_above_18", "rape_girls_below_18", "dowry_deaths",
        "acid_attack", "human_trafficking", "kidnapping_and_abduction",
        "cruelty_by_husband_or_his_relatives", "assault_on_womenabove_18",
        "murder_with_rape_gang_rape"
    ]
    df[fact_cols].to_sql("fact_safety", engine, if_exists="append", index=False)

    print(f"✅ Loaded {len(df)} records into fact_safety")
    print(f"✅ Loaded {len(locations)} unique districts into dim_location")

if __name__ == "__main__":
    load()