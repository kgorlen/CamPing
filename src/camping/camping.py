"""
camping.py -- Ping security cameras and healthecks.io

Created on February 11, 2025

References:
    https://stackoverflow.com/questions/2953462/pinging-servers-in-python
    https://pypi.org/project/tcppinglib/
    https://toml.io/en/ -- TOML: A config file format for humans


"""

__author__ = "Keith Gorlen"

import sys
from datetime import datetime
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
import tomllib
from typing import Any, NoReturn


SCRIPT_DIR: Path = Path(__file__).absolute().parent
"""Path to directory containing this Python script."""
sys.path.append(str(SCRIPT_DIR))
"""Allow camping CLI to import modules from script directory."""

# pylint: disable=wrong-import-position
from __init__ import __version__  # pylint: disable=no-name-in-module
from platformdirs import user_config_dir, user_log_dir
import requests  # type: ignore
from tcppinglib import multi_tcpping

# pylint: enable=wrong-import-position


# Global Constants


SCRIPT_NAME: str = Path(__file__).stem
"""Name of this script without .py extension."""
DATE_FMT = "%Y-%m-%d %H:%M:%S"
"""Format for dates in messages."""

# Global Variables

logging.basicConfig(
    handlers=[],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(SCRIPT_NAME)
"""Logging facility."""
camping_log: Path = (
    Path(user_log_dir("CamPing", appauthor=False, ensure_exists=True)) / "camping.log"
)
"""CamPing log file."""
rotating_handler = RotatingFileHandler(camping_log, maxBytes=5 * 1024 * 1024, backupCount=3)
"""Rotating log file handler."""
rotating_handler.setLevel(logging.INFO)
rotating_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Log format
        datefmt=DATE_FMT,  # Custom date format
    )
)
logging.getLogger().addHandler(rotating_handler)

healthchecks_url = ""


def exit_with_status(status: int) -> NoReturn:
    """Exit with status.

    Args:
        status (int): exit status
    """
    logger.info(f'{"=" * 60}')
    logging.shutdown()
    sys.exit(status)


def main() -> None:
    """Ping security cameras and healthecks.io.

    Raises:
        FileNotFoundError: Configuration file not found
        ValueError: Error reading configuration file.
        KeyError: healthchecks_url or [cameras] not found in configuration .toml file.
        ConnectionError: Dead camera(s) detected.
    """
    global healthchecks_url  # pylint: disable=global-statement

    logger.info(f'{"=" * 60}')
    logger.info(f"{SCRIPT_NAME} version {__version__} starting ...")

    config_file: Path = (
        Path(user_config_dir("CamPing", appauthor=False, roaming=True)) / "camping.toml"
    )
    """User-specific configuration file."""

    config_data: dict[str, Any]
    """Data from camping.toml file."""

    if not config_file.exists():
        raise FileNotFoundError(f'Configuration file not found: "{config_file}"')

    try:
        with config_file.open("rb") as f:
            config_data = tomllib.load(f)
    except Exception as e:
        raise ValueError(
            f"Error reading configuration file {
                            config_file}: {e}"
        ) from e

    logger.info(f'Configuration loaded from "{config_file}".')

    if "healthchecks_url" not in config_data:
        raise KeyError(f'"healthchecks_url" not found in {config_file}')

    healthchecks_url = config_data["healthchecks_url"]

    if "cameras" not in config_data:
        raise KeyError(f'"[cameras]" not found in {config_file}')

    down: list[str] = []

    logger.info("Pinging cameras ...")
    cams = multi_tcpping(
        [val[0] for val in config_data["cameras"].values()], port=80, timeout=1, count=3, interval=1
    )

    for cam, (camera, (ip, model, name)) in zip(cams, config_data["cameras"].items()):
        if cam.is_alive:
            logger.info(f"{camera} is UP:\t{ip}\t{model}\t{name}.")
        else:
            down.append(camera)
            logger.info(f"{camera} is DOWN:\t{ip}\t{model}\t{name}.")

    if down:
        msg = f'Camera(s) DOWN: {", ".join(down)}.'
        logger.info(f'Sending fail ping: "{msg}" ...')
        response = requests.post(healthchecks_url + "/fail", timeout=20, data=msg)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx, 5xx)
        exit_with_status(1)

    logger.info("Pinging healthchecks.io ...")
    response = requests.get(healthchecks_url, timeout=20)
    response.raise_for_status()  # Raise an exception for bad status codes (4xx, 5xx)
    logger.info("Successful ping sent.")
    exit_with_status(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as msg:  # pylint: disable=broad-exception-caught
        """Log a CRITICAL message and sys.exit(1)."""
        print(
            f"{datetime.now().strftime(DATE_FMT)} - CRITICAL - {msg}; exiting.",
            file=sys.stderr,
        )
        requests.post(healthchecks_url + "/fail", timeout=20, data=str(msg))
        logger.critical(f"{msg}; exiting.")
        exit_with_status(1)
