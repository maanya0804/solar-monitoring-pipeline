# Solar Inverter Monitoring Pipeline

A small Python experiment that loads, cleans and quality-checks inverter-level
solar generation data and flags inverters that underperform the rest of the fleet.
Public data; not a production system.

## Data
Kaggle "Solar Power Generation Data" (two plants, ~15-minute readings, 34 days).
Download it from https://www.kaggle.com/anikannal/solar-power-generation-data
and place the four CSVs in a `data/` folder. Not included in this repo.

## What it does
1. Loads generation and weather files and merges them by timestamp.
2. Removes duplicate readings.
3. Runs data-quality checks (missing weather, negative power, AC > DC,
   missing time intervals).
4. Computes efficiency (AC/DC) and average daytime output per inverter.
5. Flags inverters below the fleet median on efficiency or output, or with
   daytime zero output.

## Results (Plant 2: 22 inverters, 67,698 readings, 15 May - 17 Jun 2020)
- Data quality: 0 negative-power rows, 0 missing weather rows, 18 rows with
  AC > DC (~0.03%), 4,000 missing inverter-timestamp readings (~5.6% of expected).
- Efficiency (AC/DC, daytime) was nearly uniform across inverters (median 0.979-0.980),
  so the efficiency flag did not trigger.
- 3 of 22 inverters were flagged as low output (below 80% of the fleet median).
  The same three had the most daytime zero-output readings (279-318 vs. ~23 for the best).
  [add what the extra check above showed]

## Limitations
- Thresholds (2 percentage points efficiency, 80% of median output, irradiation > 0.2)
  were chosen by me and not validated against known faults.
- Assumes inverters are similar in size; larger or smaller inverters could be
  wrongly flagged.
- 15-minute data with no inverter temperature, so overheating cannot be detected.
- Single dataset
- The efficiency check did not separate inverters in this plant.
- Output varies continuously across the fleet, so the 80% cut is arbitrary.
- Zero-output readings were counted as offline without confirming a cause.   


## Run
pip install -r requirements.txt
python run.py
python -m pytest -q