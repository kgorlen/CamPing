"""
camping.py -- Check Blue Iris security camera status and ping healthchecks.io with results

Created on February 11, 2025

References:
    https://blueirissoftware.com/
    https://nwesterhausen.github.io/pyblueiris/index.html
    https://healthchecks.io/about/
    https://toml.io/en/ -- TOML: A config file format for humans


"""

__author__ = "Keith Gorlen"

import sys
from datetime import datetime
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
import tomllib
import asyncio
from typing import Any, NoReturn
from urllib.parse import urlparse, ParseResult


SCRIPT_DIR: Path = Path(__file__).absolute().parent
"""Path to directory containing this Python script."""
sys.path.append(str(SCRIPT_DIR))
"""Allow camping CLI to import modules from script directory."""

# pylint: disable=wrong-import-position
from __init__ import __version__  # pylint: disable=no-name-in-module
from platformdirs import user_config_dir, user_log_dir
import keyring
import requests  # type: ignore
from pyblueiris import BlueIris
from aiohttp import ClientSession

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

healthchecks_url: str = ""
"""healthchecks.io URL"""


def exit_with_status(status: int) -> NoReturn:
    """Exit with status.

    Args:
        status (int): exit status
    """
    logger.info(f'{"=" * 60}')
    logging.shutdown()
    sys.exit(status)


def signal_failure(msg: str) -> NoReturn:
    """Signal failure and exit.

    Args:
        msg (str): message to log
    """
    logger.info(f'Sending fail ping: "{msg}" ...')
    response = requests.post(healthchecks_url + "/fail", timeout=20, data=msg)
    response.raise_for_status()  # Raise an exception for bad status codes (4xx, 5xx)
    exit_with_status(1)


async def main() -> None:
    """Check Blue Iris security camera status.

    Raises:
        FileNotFoundError: Configuration file not found
        ValueError: Error reading configuration file.
        KeyError: Key not found in configuration .toml file.
        ValueError: BlueIris password not found in keyring.
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

    for key in ["blueiris_user", "blueiris_url", "healthchecks_url"]:
        if key not in config_data:
            raise KeyError(f'"{key}" not found in {config_file}')

    healthchecks_url = config_data["healthchecks_url"]

    blueiris_password = keyring.get_password("blueiris", config_data["blueiris_user"])
    if not blueiris_password:
        raise ValueError("BlueIris password not found in keyring.")

    logger.info(f"Parsing BlueIris URL {config_data["blueiris_url"]} ...")
    parsed_url: ParseResult = urlparse(config_data["blueiris_url"])
    protocol: str = parsed_url.scheme
    host: str | None = parsed_url.hostname
    port: int = parsed_url.port or (443 if protocol == "https" else 80)

    logger.info("Checking cameras ...")
    async with ClientSession(raise_for_status=True) as session:  # Create an aiohttp session
        bi = BlueIris(
            aiosession=session,
            user=config_data["blueiris_user"],
            password=blueiris_password,
            protocol=protocol,
            host=host,
            port=port,
            logger=logger,
            # debug=True
        )

        logger.info(
            f"Logging into {protocol}://{host}:{port} as {config_data["blueiris_user"]} ..."
        )

        try:
            if not await bi.setup_session():
                signal_failure("Blue Iris DOWN.")
        except Exception as e:  # pylint: disable=broad-exception-caught
            signal_failure(f"Blue Iris DOWN: {type(e).__name__}: {e}.")

        if bi.version == "noname":
            signal_failure("Blue Iris login failed.")

        logger.info(f"Blue Iris Version {bi.version} {bi.name}.")

        logger.info("Updating camera list ...")
        logger.setLevel(logging.WARNING)
        await bi.update_camlist()
        logger.setLevel(logging.INFO)

        down: list[str] = []

        for camera in bi.cameras:
            if camera.short_name == "@Index":
                continue

            await camera.update_camconfig()
            camera_name = f"{camera.display_name} ({camera.short_name})"
            if camera.is_enabled and camera.is_online and not camera.is_nosignal:
                logger.info(f"{camera_name} is UP.")
            else:
                down.append(camera_name)
                logger.info(f"{camera_name} is DOWN.")

        if down:
            signal_failure(f'Camera(s) DOWN: {", ".join(sorted(down))}.')

        logger.info("Pinging healthchecks.io ...")
        response = requests.get(healthchecks_url, timeout=20)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx, 5xx)
        logger.info("Successful ping sent.")
        exit_with_status(0)


def cli() -> None:
    """Command line interface for CamPing."""
    try:
        asyncio.run(main())
    except Exception as msg:  # pylint: disable=broad-exception-caught
        """Log a CRITICAL message and sys.exit(1)."""
        print(
            f"{datetime.now().strftime(DATE_FMT)} - CRITICAL - {msg}; exiting.",
            file=sys.stderr,
        )
        requests.post(healthchecks_url + "/fail", timeout=20, data=str(msg))
        logger.critical(f"{msg}; exiting.")
        exit_with_status(1)


if __name__ == "__main__":
    cli()
