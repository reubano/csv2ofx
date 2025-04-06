import os
import platform

is_GitHub_Linux = bool(
    os.environ.get("GITHUB_ACTIONS") and platform.system() == "Linux"
)

collect_ignore = [
    "csv2ofx/mappings/ubs-ch-fr.py",
] * is_GitHub_Linux
