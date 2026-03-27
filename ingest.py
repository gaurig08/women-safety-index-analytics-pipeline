import pandas as pd

DATA_PATH = "data/data.csv"

def load_data():
    print("Loading dataset...")
    df = pd.read_csv(DATA_PATH)
    
    print(f"✅ Loaded {len(df)} records")
    print(f"   Years: {sorted(df['year'].unique())}")
    print(f"   States: {df['state_name'].nunique()} states")
    print(f"   Districts: {df['district_name'].nunique()} districts")
    
    return df

if __name__ == "__main__":
    df = load_data()
    print("\nSample:")
    print(df[["year", "state_name", "district_name", "rape_women_above_18", 
              "dowry_deaths", "cruelty_by_husband_or_his_relatives"]].head(5))