import os
import matplotlib.pyplot as plt
from pipeline import (load_data, clean_data, quality_checks,
                      add_efficiency, summarize_inverters, flag_inverters)

PLANT = 2  # change to 1 to run the other plant

gen_path = f"data/Plant_{PLANT}_Generation_Data.csv"
weather_path = f"data/Plant_{PLANT}_Weather_Sensor_Data.csv"

df = load_data(gen_path, weather_path)
print("Rows loaded:", len(df))
print("Date range:", df["DATE_TIME"].min(), "to", df["DATE_TIME"].max())

df = clean_data(df)
print("Rows after cleaning:", len(df))

print("\nData quality report")
for name, count in quality_checks(df).items():
    print(f"  {name}: {count}")

df = add_efficiency(df)
summary = flag_inverters(summarize_inverters(df))
summary = summary.sort_values("avg_ac_power")

print("\nInverter summary")
print(summary)

# save results
os.makedirs("outputs", exist_ok=True)
summary.to_csv(f"outputs/plant{PLANT}_inverter_summary.csv")

# bar chart: flagged inverters in red
flagged = summary["low_efficiency"] | summary["low_output"]
colors = ["red" if f else "steelblue" for f in flagged]
summary["avg_ac_power"].plot(kind="bar", color=colors, figsize=(10, 5))
plt.ylabel("Average daytime AC power")
plt.title(f"Plant {PLANT}: average daytime AC power per inverter (red = flagged)")
plt.tight_layout()
plt.savefig(f"outputs/plant{PLANT}_avg_ac_power.png")
print("\nSaved results to the outputs folder")

# Do the flagged inverters still look low if we ignore zero-output readings?
running = df[(df["IRRADIATION"] > 0.2) & (df["AC_POWER"] > 0)]
print("\nAverage daytime AC power, ignoring zero-output readings")
print(running.groupby("SOURCE_KEY")["AC_POWER"].mean().sort_values())