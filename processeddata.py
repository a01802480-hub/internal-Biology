import glob
import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def infer_stock_conc(prefix: str):
    """Map inconsistent Vernier dataset names to stock ethanol concentration (%)."""
    p = prefix.strip().lower()
    if "water" in p:
        return 0.0
    if "20" in p:
        return 20.0
    if "40" in p:
        return 40.0
    if "60" in p:
        return 60.0
    if "80" in p or "data set 5" in p:
        return 80.0
    return None

records = []
time_series_by_conc = {}

# 1. Read all Trial-*.csv files in this folder
trial_files = sorted(glob.glob(os.path.join(BASE_DIR, "Trial-*.csv")))
if not trial_files:
    raise FileNotFoundError(f"No Trial-*.csv files found in {BASE_DIR}")
# 7. Individual Time-Course Graph for Each Trial (for Appendix)
for filepath in trial_files:
    trial_name = os.path.basename(filepath)
    raw_df = pd.read_csv(filepath)
    raw_df.columns = raw_df.columns.str.strip()

    plt.figure(figsize=(8, 5), dpi=300)
    time_cols = [c for c in raw_df.columns if c.endswith(":Time(s)")]

    # Sort curves by ethanol concentration so the legend is in order
    curves = []
    for time_col in time_cols:
        prefix = time_col.replace(":Time(s)", "")
        stock_conc = infer_stock_conc(prefix)
        a780_col = f"{prefix}:Absorbance @ 780 nm"
        if stock_conc is not None and a780_col in raw_df.columns:
            actual_conc = round(stock_conc * (1.70 / 2.00), 1)
            t = pd.to_numeric(raw_df[time_col], errors="coerce")
            a = pd.to_numeric(raw_df[a780_col], errors="coerce")
            curves.append((actual_conc, t, a))

    for actual_conc, t, a in sorted(curves, key=lambda x: x[0]):
        plt.plot(t, a, linewidth=1.8, label=f"{actual_conc}% v/v")

    plt.xlim(0, 180)
    plt.ylim(bottom=0)
    plt.title(f"{trial_name.replace('.csv', '')} — Absorbance at 780 nm", fontsize=11)
    plt.xlabel("Time (s)", fontsize=11)
    plt.ylabel("Absorbance at 780 nm (AU)", fontsize=11)
    plt.legend(frameon=True, fontsize=9)
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    out_name = f"appendix_{trial_name.replace('.csv', '')}_780nm.png"
    plt.savefig(os.path.join(BASE_DIR, out_name), dpi=300)
    plt.close()