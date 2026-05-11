from pathlib import Path
import os


def load_environment_file(file_path: str = ".env") -> None:
    environment_file = Path(file_path)
    if not environment_file.exists():
        return

    for line in environment_file.read_text(encoding="utf-8").splitlines():
        normalized_line = line.strip()
        if not normalized_line or normalized_line.startswith("#"):
            continue

        if "=" not in normalized_line:
            continue

        key, value = normalized_line.split("=", 1)
        environment_key = key.strip()
        environment_value = value.strip().strip('"').strip("'")

        if environment_key and environment_key not in os.environ:
            os.environ[environment_key] = environment_value
