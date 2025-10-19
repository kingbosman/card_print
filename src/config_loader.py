"""
Configuration loader module.

Handles loading and parsing configuration files.
"""

import os
import shutil
import sys


def load_config(config_file):
    """
    Load configuration from file with fallback to default.conf.

    If current.conf doesn't exist, copies default.conf to current.conf.
    If neither exists, prints error and exits.

    Args:
        config_file: Path to configuration file

    Returns:
        dict: Configuration dictionary with parsed values
    """
    # Check if config file exists
    if not os.path.exists(config_file):
        # Try to fall back to default.conf
        config_dir = os.path.dirname(config_file)
        default_config = os.path.join(config_dir, "default.conf")

        if os.path.exists(default_config):
            # Copy default to current
            print(f"⚠️  current.conf not found, using default.conf")
            shutil.copy(default_config, config_file)
            print(f"✓ Copied default.conf to current.conf")
        else:
            # Neither exists - error and exit
            print(f"❌ ERROR: Configuration file not found!")
            print(f"   Searched for:")
            print(f"     - {config_file}")
            print(f"     - {default_config}")
            print(
                f"\n   Please create a config file or restore default.conf (from github)"
            )
            sys.exit(1)

    config = {}
    with open(config_file, "r") as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            # Parse key = value
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Convert to appropriate type
                if value.lower() in ("true", "false"):
                    config[key] = value.lower() == "true"
                elif value.replace(".", "", 1).replace("-", "", 1).isdigit():
                    # Number (int or float)
                    config[key] = float(value) if "." in value else int(value)
                else:
                    # String
                    config[key] = value
    return config
