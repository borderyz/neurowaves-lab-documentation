# reports/utils_report.py
from __future__ import annotations
import os
from pathlib import Path
import shutil
import yaml
import pandas as pd
import matplotlib.pyplot as plt

# Optional: interactive Plotly
try:
    import plotly.express as px
    PLOTLY_OK = True
except Exception:
    PLOTLY_OK = False


def load_config(config_path: str | Path) -> dict:
    p = Path(config_path).expanduser().resolve()
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def resolve_bids_root(cfg: dict, dataset_override: str | None = None) -> tuple[Path, str]:
    proj = cfg.get("project", {}) or {}
    dataset = dataset_override or proj.get("name")
    if not dataset:
        raise ValueError("Dataset name is missing — pass params.dataset in Quarto or set project.name in YAML.")
    root_override = proj.get("root_override")
    if root_override:
        root = Path(root_override).expanduser()
    else:
        root_env = proj.get("root_env", "MEG_DATA")
        env_val = os.getenv(root_env)
        if not env_val:
            raise EnvironmentError(f"{root_env} is not set and project.root_override not provided.")
        root = Path(env_val)
    return (root / dataset).resolve(), dataset


def load_derivative_tables(bids_root: Path) -> dict:
    d = {}
    deriv = bids_root / "derivatives"

    p = deriv / "sanity_check" / "sanity_check_overview.csv"
    if p.exists():
        d["sanity"] = pd.read_csv(p)
        d["sanity_path"] = str(p)

    p = deriv / "kit2fiff" / "kit2fiff_summary.csv"
    if p.exists():
        d["kit2fiff"] = pd.read_csv(p)
        d["kit2fiff_path"] = str(p)

    p = deriv / "triggers_to_events" / "auto_events_index.csv"
    if p.exists():
        d["events"] = pd.read_csv(p)
        d["events_path"] = str(p)

    return d


def save_matplot(fig, out_dir: Path, base_name: str) -> tuple[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    png = out_dir / f"{base_name}.png"
    svg = out_dir / f"{base_name}.svg"
    fig.tight_layout()
    fig.savefig(png, dpi=200)
    fig.savefig(svg)
    plt.close(fig)
    return png.name, svg.name


def build_static_figures(tables: dict, fig_dir: Path) -> list[dict]:
    """Return a list of dicts: {title, png, svg} placed under fig_dir."""
    figs = []

    # 1) sanity: CSV vs detected per subject
    if "sanity" in tables:
        df = tables["sanity"]
        if not df.empty and {"subject", "csv_events", "detected_events"}.issubset(df.columns):
            agg = df.groupby("subject")[["csv_events", "detected_events"]].sum().reset_index()
            fig = plt.figure()
            import matplotlib.pyplot as plt
            plt.bar(agg["subject"], agg["csv_events"], label="csv_events")
            plt.bar(agg["subject"], agg["detected_events"], alpha=0.6, label="detected_events")
            plt.legend()
            plt.title("Sanity: events per subject (CSV vs detected)")
            png, svg = save_matplot(fig, fig_dir, "sanity_events_per_subject")
            figs.append({"title": "Sanity: events per subject", "png": png, "svg": svg})

    # 2) kit2fiff: success rate by subject
    if "kit2fiff" in tables:
        df = tables["kit2fiff"]
        if not df.empty and {"subject", "status"}.issubset(df.columns):
            rate = df.groupby("subject")["status"].apply(lambda s: (s == "success").mean()).reset_index()
            fig = plt.figure()
            plt.bar(rate["subject"], rate["status"])
            plt.title("KIT→FIFF success rate by subject")
            png, svg = save_matplot(fig, fig_dir, "kit2fiff_success_rate")
            figs.append({"title": "KIT→FIFF success rate by subject", "png": png, "svg": svg})

    # 3) events: histogram of n_events
    if "events" in tables:
        df = tables["events"]
        if not df.empty and "n_events" in df.columns:
            fig = plt.figure()
            plt.hist(df["n_events"], bins=20)
            plt.title("Distribution of n_events across outputs")
            png, svg = save_matplot(fig, fig_dir, "events_count_distribution")
            figs.append({"title": "Events per run (histogram)", "png": png, "svg": svg})

    return figs


def build_interactive_html_blocks(tables: dict) -> list[dict]:
    """Return list of dicts: {title, html} (for HTML-only inclusion)."""
    inter = []
    if not PLOTLY_OK:
        return inter
    if "events" in tables:
        df = tables["events"]
        if not df.empty and {"subject", "n_events"}.issubset(df.columns):
            fig = px.box(df, x="subject", y="n_events", title="Interactive: n_events by subject")
            inter.append({"title": "n_events by subject (interactive)", "html": fig.to_html(full_html=False)})
    return inter


def copy_config_snapshot(cfg: dict, out_dir: Path) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    snap = out_dir / "config_snapshot.yml"
    with open(snap, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False, indent=2)
    return str(snap)
