import pandas as pd
from ingest import load_data

def transform():
    df = load_data()

    print("\nTransforming...")

    # Drop duplicates
    df = df.drop_duplicates()

    # Fill nulls with 0
    crime_cols = [
        "murder_with_rape_gang_rape", "dowry_deaths", "acid_attack",
        "attempt_to_acid_attack", "cruelty_by_husband_or_his_relatives",
        "kidnapping_and_abduction", "rape_women_above_18", "rape_girls_below_18",
        "attempt_to_commit_rape_above_18", "attempt_to_commit_rape_girls_below_18",
        "assault_on_womenabove_18", "assault_on_women_below_18",
        "human_trafficking", "selling_of_minor_girls", "buying_of_minor_girls",
        "protection_of_women_from_domestic_violence", "dowry_prohibition",
        "child_rape", "sexual_assault_of_children", "child_sexual_harassment"
    ]
    df[crime_cols] = df[crime_cols].fillna(0)

    # Total crimes per district per year
    df["total_crimes"] = df[crime_cols].sum(axis=1)

    # Weighted Safety Index
    # Higher weight to severe crimes
    df["safety_index"] = (
        df["murder_with_rape_gang_rape"] * 5 +
        df["rape_women_above_18"] * 4 +
        df["rape_girls_below_18"] * 4 +
        df["acid_attack"] * 4 +
        df["human_trafficking"] * 4 +
        df["dowry_deaths"] * 3 +
        df["kidnapping_and_abduction"] * 2 +
        df["cruelty_by_husband_or_his_relatives"] * 1 +
        df["assault_on_womenabove_18"] * 1
    )

    # Normalize using 95th percentile as ceiling
    # Prevents one outlier (Mumbai) from making everything else look low
    df["safety_score"] = df.groupby("year")["safety_index"].transform(
    lambda x: (
        (x - x.min()) / (x.quantile(0.95) - x.min()) * 100
    ).clip(0, 100).round(2)
   )

    # Risk category
    def risk_category(score):
      if score >= 60:
        return "Critical"
      elif score >= 35:
        return "High"
      elif score >= 15:
        return "Moderate"
      else:
        return "Low"

    df["risk_category"] = df["safety_score"].apply(risk_category)

    # Clean state names
    df["state_name"] = df["state_name"].str.strip().str.title()
    df["district_name"] = df["district_name"].str.strip().str.title()

    print(f"✅ Transform complete: {len(df)} records")
    print(f"\nRisk distribution:")
    print(df["risk_category"].value_counts())
    print(f"\nTop 5 most dangerous districts (2022):")
    top = df[df["year"] == 2022].nlargest(5, "safety_score")[
        ["state_name", "district_name", "safety_score", "risk_category", "total_crimes"]
    ]
    print(top.to_string(index=False))

    df.to_csv("transformed_safety.csv", index=False)
    return df

if __name__ == "__main__":
    transform()