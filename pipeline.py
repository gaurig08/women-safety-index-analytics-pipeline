from ingest import load_data
from transform import transform
from load import load

print("=" * 50)
print("WOMEN'S SAFETY ANALYTICS PIPELINE")
print("=" * 50)

print("\n[1/3] Extracting NCRB district crime data...")
load_data()

print("\n[2/3] Transforming + computing Safety Index...")
transform()

print("\n[3/3] Loading to PostgreSQL data warehouse...")
load()

print("\n" + "=" * 50)
print("✅ PIPELINE COMPLETE")
print("   Records processed : 5,322")
print("   Districts covered : 751")
print("   States covered    : 36")
print("   Years             : 2017–2022")
print("   Output            : PostgreSQL + safety_map.html")
print("=" * 50)