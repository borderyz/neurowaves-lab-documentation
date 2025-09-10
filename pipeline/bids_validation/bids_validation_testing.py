from pathlib import Path
from bids_validation import validate_dataset


# Build the path relative to the user's home directory
home = Path.home()
DATA_ROOT = (
    home
    / "PycharmProjects"
    / "neurowaves-lab-documentation"
    / "data"
    / "test_data"
    / "scenario_2_existing_project"
    / "existing-bids-project"
)

ok, report = validate_dataset(str(DATA_ROOT), write_log=True)

summary = {
    "ok": ok,
    "n_errors": report["summary"]["n_errors"],
    "n_warnings": report["summary"]["n_warnings"],
    "log_file": str((DATA_ROOT.parent / f"{DATA_ROOT.name}_validation_log.json").resolve()),
}

print(summary)
