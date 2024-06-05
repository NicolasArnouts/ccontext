import os
import shutil
from pathlib import Path

try:
    from importlib import resources  # Python 3.7+
except ImportError:
    import importlib_resources as resources  # Backport for older Python versions

DEFAULT_CONFIG_FILENAME = "config.json"
USER_CONFIG_DIR = Path.home() / ".ccontext"
USER_CONFIG_PATH = USER_CONFIG_DIR / DEFAULT_CONFIG_FILENAME


def copy_default_config():
    """Copy the default configuration file to the user-specific location."""
    try:
        if not USER_CONFIG_DIR.exists():
            USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        # Correctly use the context manager with resources.path
        with resources.path("ccontext", DEFAULT_CONFIG_FILENAME) as default_config_path:
            if not USER_CONFIG_PATH.exists():
                shutil.copy(default_config_path, USER_CONFIG_PATH)
                print(f"Copied default config to {USER_CONFIG_PATH}")
            else:
                print(f"Config file already exists at {USER_CONFIG_PATH}")

    except Exception as e:
        print(f"Error copying default config: {e}")


if __name__ == "__main__":
    copy_default_config()
