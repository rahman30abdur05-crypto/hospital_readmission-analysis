import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3

# ── STEP 1: Load CSV Data ─────────────────────────────────────
print("=" * 55)
print("  🏥 HOSPITAL READMISSION ANALYSIS")
print("=" * 55)

print("\n📂 Loading dataset...")
df = pd.read_csv("diabetic_data.csv")

print(f"✅ Loaded! Shape: {df.shape}")
print(f"\nFirst 5 rows:")
print(df.head())

print(f"\nColumn Names:")
print(df.columns.tolist())

print(f"\nBasic Info:")
print(df.dtypes)

print(f"\nMissing Values:")
print(df.isnull().sum())



#step:2  creating SQL database
# ── STEP 2: Load Data into SQL Database ──────────────────────
print("\n" + "=" * 55)
print("  🗄️  LOADING INTO SQL DATABASE")
print("=" * 55)

# Create SQLite database file
conn = sqlite3.connect("hospital.db")
print("✅ Database created: hospital.db")

# Load the dataframe into SQL table
# This is exactly like creating a table in a real hospital DB
df.to_sql("patients",
          conn,
          if_exists="replace",
          index=False)
print("✅ Data loaded into 'patients' table")

# ── STEP 3: First SQL Queries ─────────────────────────────────
print("\n" + "=" * 55)
print("  📊 SQL QUERIES")
print("=" * 55)

# SQL Query 1 — Count total patients
# SELECT = choose what to show
# COUNT = count rows
# FROM  = which table
query1 = """
SELECT COUNT(*) as total_patients
FROM patients
"""
result1 = pd.read_sql_query(query1, conn)
print(f"\n🔍 Query 1: Total patients")
print(f"SQL: SELECT COUNT(*) FROM patients")
print(result1)

# SQL Query 2 — Readmission breakdown
# GROUP BY = group rows by a column value
# ORDER BY = sort the results
query2 = """
SELECT readmitted,
       COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / 101766, 2) as percentage
FROM patients
GROUP BY readmitted
ORDER BY count DESC
"""
result2 = pd.read_sql_query(query2, conn)
print(f"\n🔍 Query 2: Readmission breakdown")
print(f"SQL: SELECT readmitted, COUNT(*) GROUP BY readmitted")
print(result2)

# SQL Query 3 — Average hospital stay by readmission
query3 = """
SELECT readmitted,
       ROUND(AVG(time_in_hospital), 2) as avg_days,
       ROUND(AVG(num_medications), 2)  as avg_medications,
       ROUND(AVG(num_lab_procedures), 2) as avg_lab_tests
FROM patients
GROUP BY readmitted
"""
result3 = pd.read_sql_query(query3, conn)
print(f"\n🔍 Query 3: Avg stay & medications by readmission")
print(result3)

# SQL Query 4 — Top 10 medical specialties
query4 = """
SELECT medical_specialty,
       COUNT(*) as patient_count,
       ROUND(AVG(time_in_hospital), 2) as avg_stay
FROM patients
WHERE medical_specialty != '?'
GROUP BY medical_specialty
ORDER BY patient_count DESC
LIMIT 10
"""
result4 = pd.read_sql_query(query4, conn)
print(f"\n🔍 Query 4: Top 10 medical specialties")
print(result4)

# SQL Query 5 — Readmission by age group
query5 = """
SELECT age,
       COUNT(*) as total,
       SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END)
           as readmitted_under_30,
       ROUND(SUM(CASE WHEN readmitted = '<30'
             THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2)
           as readmission_rate
FROM patients
GROUP BY age
ORDER BY age
"""
result5 = pd.read_sql_query(query5, conn)
print(f"\n🔍 Query 5: Readmission rate by age group")
print(result5)

print("\n✅ SQL Queries Complete!")




#step:3 visualisation
# ── STEP 4: Visualizations ────────────────────────────────────
print("\n" + "=" * 55)
print("  🎨 GENERATING CHARTS")
print("=" * 55)

sns.set_style("whitegrid")
plt.figure(figsize=(16, 12))

# ── Chart 1: Readmission Distribution ────────────────────────
plt.subplot(2, 3, 1)
colors  = ["#2ecc71", "#f39c12", "#e74c3c"]
labels  = ["No Readmission\n54.9%",
           ">30 Days\n34.9%",
           "<30 Days\n11.2%"]
sizes   = [54864, 35545, 11357]
plt.pie(sizes, labels=labels,
        colors=colors, startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 2})
plt.title("Readmission Distribution",
          fontsize=13, fontweight="bold")

# ── Chart 2: Readmission Rate by Age ─────────────────────────
plt.subplot(2, 3, 2)
age_data = result5.copy()
bars = plt.bar(age_data["age"],
               age_data["readmission_rate"],
               color="#e74c3c", alpha=0.8)
plt.xlabel("Age Group")
plt.ylabel("Readmission Rate %")
plt.title("Readmission Rate by Age",
          fontsize=13, fontweight="bold")
plt.xticks(rotation=45)
for bar, rate in zip(bars, age_data["readmission_rate"]):
    plt.text(bar.get_x() + bar.get_width()/2,
             bar.get_height() + 0.1,
             f"{rate}%", ha="center",
             va="bottom", fontsize=8)

# ── Chart 3: Top Specialties ──────────────────────────────────
plt.subplot(2, 3, 3)
top5 = result4.head(5)
plt.barh(top5["medical_specialty"],
         top5["patient_count"],
         color="#3498db", alpha=0.8)
plt.xlabel("Number of Patients")
plt.title("Top 5 Medical Specialties",
          fontsize=13, fontweight="bold")

# ── Chart 4: Avg Stay by Readmission ─────────────────────────
plt.subplot(2, 3, 4)
colors4 = ["#e74c3c", "#f39c12", "#2ecc71"]
bars4   = plt.bar(result3["readmitted"],
                  result3["avg_days"],
                  color=colors4, alpha=0.8)
plt.xlabel("Readmission Status")
plt.ylabel("Average Days")
plt.title("Avg Hospital Stay by Readmission",
          fontsize=13, fontweight="bold")
for bar, days in zip(bars4, result3["avg_days"]):
    plt.text(bar.get_x() + bar.get_width()/2,
             bar.get_height() + 0.05,
             f"{days} days",
             ha="center", va="bottom", fontsize=10)

# ── Chart 5: Avg Medications by Readmission ───────────────────
plt.subplot(2, 3, 5)
plt.bar(result3["readmitted"],
        result3["avg_medications"],
        color=["#e74c3c", "#f39c12", "#2ecc71"],
        alpha=0.8)
plt.xlabel("Readmission Status")
plt.ylabel("Avg Medications")
plt.title("Avg Medications by Readmission",
          fontsize=13, fontweight="bold")

# ── Chart 6: Avg Lab Tests by Readmission ────────────────────
plt.subplot(2, 3, 6)
plt.bar(result3["readmitted"],
        result3["avg_lab_tests"],
        color=["#e74c3c", "#f39c12", "#2ecc71"],
        alpha=0.8)
plt.xlabel("Readmission Status")
plt.ylabel("Avg Lab Tests")
plt.title("Avg Lab Tests by Readmission",
          fontsize=13, fontweight="bold")

plt.tight_layout()
plt.savefig("readmission_charts.png",
            dpi=150, bbox_inches="tight")
plt.show(block=False)
plt.pause(3)
plt.close()
print("✅ Charts saved!")

# ── STEP 5: Final Report ──────────────────────────────────────
print("\n" + "=" * 55)
print("   📋 READMISSION ANALYSIS REPORT")
print("=" * 55)
print(f"""
DATASET:
  Total patients    : 101,766
  Hospitals         : 130 US hospitals
  Period            : 10 years

READMISSION RATES:
  No readmission    : 53.91%
  After 30 days     : 34.93%
  Within 30 days    : 11.16% ← critical metric

HIGH RISK GROUPS:
  Highest risk age  : 20-30 years (14.24%)
  Busiest dept      : Internal Medicine (14,635)
  Longest stay dept : Pulmonology (5.24 days)

SICKEST PATIENTS (readmitted <30 days):
  Avg hospital stay : 4.77 days
  Avg medications   : 16.9
  Avg lab tests     : 44.2

KEY FINDINGS:
  1. 11.16% patients readmitted within 30 days
  2. Young adults (20-30) have highest readmission
  3. More medications = higher readmission risk
  4. Internal Medicine handles most diabetic patients
  5. Pulmonology has longest average hospital stay

CLINICAL RECOMMENDATION:
  Focus readmission prevention programs on:
  → Young adults (20-30 age group)
  → Patients with >15 medications
  → Internal Medicine department
""")
print("=" * 55)
print("✅ Analysis Complete!")

conn.close()
print("✅ Database connection closed!")