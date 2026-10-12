import pandas as pd

gen = pd.read_csv("data/Plant_2_Generation_Data.csv")
weather = pd.read_csv("data/Plant_2_Weather_Sensor_Data.csv")

print(gen.head())
print("Generation shape:", gen.shape)
print("Inverters:", gen["SOURCE_KEY"].nunique())
print("Missing Values:")
print(gen.isna().sum())

print(weather.head())
print("Weather Shape:", weather.shape)