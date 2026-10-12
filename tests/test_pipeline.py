import pandas as pd
from pipeline import (add_efficiency, quality_checks,
                      summarize_inverters, flag_inverters)


def make_df():
    # three inverters at the same daytime moment; inv3 is clearly worse
    return pd.DataFrame({
        "DATE_TIME": pd.to_datetime(["2020-05-15 12:00"] * 3),
        "SOURCE_KEY": ["inv1", "inv2", "inv3"],
        "DC_POWER": [100.0, 100.0, 100.0],
        "AC_POWER": [98.0, 97.0, 50.0],
        "IRRADIATION": [0.8, 0.8, 0.8],
    })


def test_efficiency_is_ac_over_dc():
    df = add_efficiency(make_df())
    assert abs(df["EFFICIENCY"].iloc[0] - 0.98) < 1e-9


def test_efficiency_is_blank_when_dc_is_zero():
    df = make_df()
    df.loc[0, "DC_POWER"] = 0.0
    df = add_efficiency(df)
    assert pd.isna(df["EFFICIENCY"].iloc[0])


def test_quality_checks_find_bad_rows():
    df = make_df()
    df.loc[0, "AC_POWER"] = -5.0        # negative power
    df.loc[1, "AC_POWER"] = 120.0       # AC greater than DC
    df.loc[2, "IRRADIATION"] = None     # missing weather
    result = quality_checks(df)
    assert result["negative_power_rows"] == 1
    assert result["ac_greater_than_dc_rows"] == 1
    assert result["missing_weather_rows"] == 1
    assert result["missing_intervals"] == 0


def test_bad_inverter_is_flagged():
    df = add_efficiency(make_df())
    flagged = flag_inverters(summarize_inverters(df))
    assert flagged.loc["inv3", "low_efficiency"]
    assert flagged.loc["inv3", "low_output"]
    assert not flagged.loc["inv1", "low_efficiency"]