import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("transformed_safety.csv")

sns.set_theme(style="darkgrid")
plt.rcParams["figure.dpi"] = 150
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle("Women's Safety Analytics Dashboard — India (2017–2022)\nSource: NCRB via India Data Portal",
             fontsize=15, fontweight="bold")

# --- Chart 1: Top 10 most dangerous states 2022 ---
state_2022 = df[df["year"] == 2022].groupby("state_name")["safety_score"].mean().reset_index()
state_2022 = state_2022.nlargest(10, "safety_score")
axes[0, 0].barh(state_2022["state_name"], state_2022["safety_score"], color="#e05c5c")
axes[0, 0].set_title("Top 10 States by Avg Safety Score (2022)", fontweight="bold")
axes[0, 0].set_xlabel("Average Safety Score (higher = more risk)")
axes[0, 0].invert_yaxis()

# --- Chart 2: Year wise total crimes trend ---
yearly = df.groupby("year")["total_crimes"].sum().reset_index()
axes[0, 1].plot(yearly["year"], yearly["total_crimes"], 
                marker="o", color="#e05c5c", linewidth=2.5, markersize=8)
axes[0, 1].fill_between(yearly["year"], yearly["total_crimes"], alpha=0.2, color="#e05c5c")
axes[0, 1].set_title("Total Crimes Against Women — Year Trend", fontweight="bold")
axes[0, 1].set_xlabel("Year")
axes[0, 1].set_ylabel("Total Crimes")
for x, y in zip(yearly["year"], yearly["total_crimes"]):
    axes[0, 1].annotate(f"{int(y):,}", (x, y), textcoords="offset points",
                        xytext=(0, 8), ha="center", fontsize=8)

# --- Chart 3: Risk category distribution ---
risk_order = ["Critical", "High", "Moderate", "Low"]
risk_colors = ["#c0392b", "#e67e22", "#f1c40f", "#2ecc71"]
risk_counts = df["risk_category"].value_counts().reindex(risk_order)
axes[1, 0].bar(risk_counts.index, risk_counts.values, color=risk_colors, edgecolor="white")
axes[1, 0].set_title("District Risk Category Distribution", fontweight="bold")
axes[1, 0].set_ylabel("Number of District-Year Records")
for i, v in enumerate(risk_counts.values):
    axes[1, 0].text(i, v + 20, f"{v:,}", ha="center", fontweight="bold")

# --- Chart 4: Top 5 crime types nationally ---
crime_cols = {
    "Cruelty by Husband": "cruelty_by_husband_or_his_relatives",
    "Kidnapping": "kidnapping_and_abduction",
    "Assault (Adult)": "assault_on_womenabove_18",
    "Rape (Adult)": "rape_women_above_18",
    "Dowry Deaths": "dowry_deaths"
}
crime_totals = {k: df[v].sum() for k, v in crime_cols.items()}
crime_df = pd.Series(crime_totals).sort_values(ascending=True)
axes[1, 1].barh(crime_df.index, crime_df.values, color="#8e44ad")
axes[1, 1].set_title("Top Crime Categories — National Total (2017–2022)", fontweight="bold")
axes[1, 1].set_xlabel("Total Reported Cases")
for i, v in enumerate(crime_df.values):
    axes[1, 1].text(v + 100, i, f"{int(v):,}", va="center", fontsize=9)

plt.tight_layout()
plt.savefig("dashboard.png", bbox_inches="tight")
print("✅ Dashboard saved as dashboard.png")
plt.show()