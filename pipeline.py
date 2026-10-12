import pandas as pd


def load_data(gen_path, weather_path):
    """Read both CSV files, fix the dates, and join them on time."""
    gen = pd.read_csv(gen_path)
    weather = pd.read_csv(weather_path)

    # dayfirst=True because some of the files use day-month-year
    gen["DATE_TIME"] = pd.to_datetime(gen["DATE_TIME"], dayfirst=True)
    weather["DATE_TIME"] = pd.to_datetime(weather["DATE_TIME"], dayfirst=True)

    # weather has one sensor for the whole plant, so these columns aren't needed
    weather = weather.drop(columns=["PLANT_ID", "SOURCE_KEY"])

    # keep every generation row; rows with no weather reading get blanks (NaN)
    return gen.merge(weather, on="DATE_TIME", how="left")


def clean_data(df):
    """Remove duplicate readings and sort by inverter and time."""
    df = df.drop_duplicates(subset=["DATE_TIME", "SOURCE_KEY"])
    df = df.sort_values(["SOURCE_KEY", "DATE_TIME"]).reset_index(drop=True)
    return df


def quality_checks(df):
    """Count the rows that look wrong. Returns a dictionary of counts."""
    # every inverter should have a reading at every timestamp
    expected_rows = df["DATE_TIME"].nunique() * df["SOURCE_KEY"].nunique()

    return {
        "missing_weather_rows": int(df["IRRADIATION"].isna().sum()),
        "negative_power_rows": int(((df["DC_POWER"] < 0) | (df["AC_POWER"] < 0)).sum()),
        # an inverter can't output more power than it receives
        "ac_greater_than_dc_rows": int((df["AC_POWER"] > df["DC_POWER"]).sum()),
        "missing_intervals": int(expected_rows - len(df)),
    }


def add_efficiency(df):
    """Efficiency = AC power / DC power (left blank when DC is zero)."""
    df = df.copy()
    df["EFFICIENCY"] = df["AC_POWER"] / df["DC_POWER"].where(df["DC_POWER"] > 0)
    return df


def summarize_inverters(df, irr_min=0.2):
    """One row per inverter, using daytime readings only."""
    # only count times when the sun is really shining
    day = df[df["IRRADIATION"] > irr_min]

    summary = pd.DataFrame({
        "median_efficiency": day.groupby("SOURCE_KEY")["EFFICIENCY"].median(),
        "avg_ac_power": day.groupby("SOURCE_KEY")["AC_POWER"].mean(),
    })

    # readings where the sun is up but the inverter outputs nothing
    offline = day[day["AC_POWER"] == 0].groupby("SOURCE_KEY").size()
    summary["offline_rows"] = offline
    summary["offline_rows"] = summary["offline_rows"].fillna(0).astype(int)
    return summary


def flag_inverters(summary, eff_drop=0.02, power_ratio=0.8):
    """Mark inverters that are worse than the typical (median) inverter."""
    summary = summary.copy()
    typical_eff = summary["median_efficiency"].median()
    typical_power = summary["avg_ac_power"].median()

    summary["low_efficiency"] = summary["median_efficiency"] < typical_eff - eff_drop
    summary["low_output"] = summary["avg_ac_power"] < power_ratio * typical_power
    return summary  