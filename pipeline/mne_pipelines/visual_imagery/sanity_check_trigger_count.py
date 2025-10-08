# my_analysis.py
from pathlib import Path
from pipeline.mne_pipelines.kit_general_pipelines.trigger_count_sanity_check import run_trigger_count

CON = Path(r"sub-test-visual-imagery.con")
CSV = Path(r"VI_trig_debug.csv")

res = run_trigger_count(
    confile=CON,
    csv_expected=CSV,
    channels=["MISC 001","MISC 002","MISC 003","MISC 004",
              "MISC 005","MISC 006","MISC 007","MISC 008"],
    threshold=0.5,
    min_stable_win=5,
    bit_order="lsb_first",  # keep this, matches 2^(0:7)
    csv_format = "vi",
    plot=True,
    return_figs=True,
)





print("Observed counts:")
print(res["observed_counts"])

print("\nExpected (aggregated) from CSV:")
print(res["expected_tidy"][["TrigType","code","expected"]])

print("\nComparison:")
print(res["comparison"])

# If you requested figures:
# figs = res.get("figs", {})
# for name, fig in figs.items():
#     fig.savefig(f"{name}.png", dpi=150)
