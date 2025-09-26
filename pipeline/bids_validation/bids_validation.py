#!/usr/bin/env python3
"""
bids_check.py — validator-only, import-friendly

Validate BIDS datasets using the official `bids-validator` and return a
normalized Python dict. Optionally write a JSON log. Usable both as a
library and as a CLI.

Install validator:
    npm install -g bids-validator
"""

import argparse
import platform
import shutil
import json
import logging
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, Union

PathLike = Union[str, Path]
__all__ = ["BIDSComplianceChecker", "validate_dataset"]


class BIDSComplianceChecker:
    def __init__(
        self,
        *,
        verbose: bool = False,
        logger: Optional[logging.Logger] = None,
        validator_cmd: str = "bids-validator",
        timeout_s: int = 600,
    ):
        self.timeout_s = timeout_s
        self.logger = logger or self._make_logger(verbose)
        # Resolve to full path if possible; keep as provided otherwise
        self.validator_cmd = shutil.which(validator_cmd) or validator_cmd

    def check(
        self,
        dataset_path: PathLike,
        *,
        log_path: Optional[PathLike] = None,
        write_log: bool = True,
    ) -> Tuple[bool, Dict[str, Any]]:
        dataset_path = Path(dataset_path).resolve()
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset path not found: {dataset_path}")

        is_win = platform.system() == "Windows"
        exe = self.validator_cmd
        args = [str(dataset_path), "--json", "--no-color"]

        # --- Windows-safe handling for .cmd/.bat ---
        if is_win and exe.lower().endswith((".cmd", ".bat")):
            # Build a single command line and use shell=True
            cmdline = subprocess.list2cmdline([exe] + args)
            self.logger.info("Running (shell=True): %s", cmdline)
            try:
                proc = subprocess.run(
                    cmdline,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_s,
                    shell=True,  # <-- key for .cmd/.bat
                )
            except subprocess.TimeoutExpired as e:
                raise RuntimeError("bids-validator timed out") from e
        else:
            # Non-Windows or real executables (.exe, no suffix, etc.)
            cmd = [exe] + args
            self.logger.info("Running: %s", " ".join(cmd))
            try:
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_s,
                )
            except subprocess.TimeoutExpired as e:
                raise RuntimeError("bids-validator timed out") from e


        stdout = (proc.stdout or "").strip()
        stderr = (proc.stderr or "").strip()

        # Parse validator JSON (be tolerant of extra output)
        payload: Dict[str, Any] = {}
        if stdout:
            try:
                payload = json.loads(stdout)
            except json.JSONDecodeError:
                payload = {"raw_stdout": stdout}

        normalized = self._normalize(payload, stderr)

        # If the validator didn't include path, fall back to the path we ran on
        if not normalized["summary"]["dataset_path"]:
            normalized["summary"]["dataset_path"] = str(dataset_path)

        is_valid = proc.returncode == 0
        normalized["summary"]["is_valid"] = is_valid
        normalized["summary"]["validator_returncode"] = proc.returncode

        # Default log path: <dataset>_validation_log.json next to the dataset
        if log_path is None:
            log_path = dataset_path.parent / f"{dataset_path.name}_validation_log.json"

        if write_log:
            Path(log_path).parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(normalized, f, indent=2)
            self.logger.info("Validation log saved to: %s", log_path)

        return is_valid, normalized

    @staticmethod
    def _make_logger(verbose: bool) -> logging.Logger:
        logger = logging.getLogger("BIDSComplianceChecker")
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(fmt)
            logger.addHandler(handler)
        logger.setLevel(logging.INFO if verbose else logging.WARNING)
        return logger

    @staticmethod
    def _normalize(payload: Dict[str, Any], stderr: str) -> Dict[str, Any]:
        dataset = payload.get("dataset", {})
        issues = payload.get("issues", {})

        def safe_paths(item: Dict[str, Any]) -> list[dict]:
            out = []
            for f in (item.get("files") or []):
                # Some entries are None or not dicts
                if not isinstance(f, dict):
                    continue
                path = None
                # Typical structure: {"file": {"path": "...", ...}, ...}
                file_obj = f.get("file")
                if isinstance(file_obj, dict):
                    path = file_obj.get("path")
                # Fallbacks seen in the wild
                if not path:
                    path = f.get("path") or f.get("evidence")
                if path:
                    out.append({"path": path})
            return out

        def extract(group: str):
            out = []
            for item in (issues.get(group) or []):
                out.append({
                    "severity": group,  # "errors" | "warnings"
                    "code": item.get("code"),
                    "message": item.get("reason") or item.get("message"),
                    "files": safe_paths(item),
                    "helpUrl": item.get("helpUrl"),
                })
            return out

        errors = extract("errors")
        warnings = extract("warnings")

        return {
            "summary": {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "dataset_path": str(dataset.get("path") or ""),
                "name": dataset.get("name"),
                "bids_validator_version": payload.get("version"),
                "n_errors": len(errors),
                "n_warnings": len(warnings),
                "stderr": stderr or None,
            },
            "issues": errors + warnings,
        }



def validate_dataset(
    dataset_path: PathLike,
    *,
    log_path: Optional[PathLike] = None,
    write_log: bool = True,
    validator_cmd: str = "bids-validator",
    timeout_s: int = 600,
    verbose: bool = False,
    logger: Optional[logging.Logger] = None,
) -> Tuple[bool, Dict[str, Any]]:
    """
    One-shot convenience function for programmatic use.

    Returns:
        (is_valid, normalized_result_dict)
    """
    checker = BIDSComplianceChecker(
        verbose=verbose,
        logger=logger,
        validator_cmd=validator_cmd,
        timeout_s=timeout_s,
    )
    return checker.check(dataset_path, log_path=log_path, write_log=write_log)


# -----------------------
# Optional CLI entrypoint
# -----------------------
def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Check BIDS compliance using the official bids-validator",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  python bids_check.py /data/bids_ds
  python bids_check.py /data/bids_ds --log /tmp/ds_log.json -v
        """,
    )
    p.add_argument("dataset_path", type=str, help="Path to the BIDS dataset")
    p.add_argument("--log", type=str, default=None, help="JSON log path")
    p.add_argument("--no-log", action="store_true", help="Do not write a log file")
    p.add_argument("--validator-cmd", type=str, default="bids-validator",
                   help="Path/name of bids-validator executable")
    p.add_argument("--timeout", type=int, default=600, help="Timeout in seconds")
    p.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    return p.parse_args()


def main():
    args = _parse_args()
    ds = Path(args.dataset_path).resolve()
    if not ds.exists():
        print(f"Dataset path not found: {ds}")
        sys.exit(1)

    try:
        ok, _ = validate_dataset(
            ds,
            log_path=args.log,
            write_log=not args.no_log,
            validator_cmd=args.validator_cmd,
            timeout_s=args.timeout,
            verbose=args.verbose,
        )
        sys.exit(0 if ok else 1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
