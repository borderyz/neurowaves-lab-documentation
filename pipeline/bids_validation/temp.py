import os, shutil, platform, sys
from pathlib import Path

print("Python:", sys.executable)
print("Platform:", platform.platform())
print("\n--- PATH as seen by Python ---")
print(os.environ.get("PATH", ""))

print("\nwhich('bids-validator'):", shutil.which("bids-validator"))
print("which('bids-validator.cmd'):", shutil.which("bids-validator.cmd"))

home = Path.home()
expected = home / "AppData" / "Roaming" / "npm" / "bids-validator.cmd"
print("\nExpected npm shim exists?:", expected, "->", expected.exists())
