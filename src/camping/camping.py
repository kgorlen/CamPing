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

import asyncio
import logging
import os
import subprocess
import sys
import tomllib
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, NoReturn
from urllib.parse import ParseResult, urlparse

SCRIPT_DIR: Path = Path(__file__).absolute().parent
"""Path to directory containing this Python script."""
sys.path.append(str(SCRIPT_DIR))
"""Allow camping CLI to import modules from script directory."""

# pylint: disable=wrong-import-position

import keyring
from __init__ import __version__  # pylint: disable=no-name-in-module
from aiohttp import ClientSession
from platformdirs import user_config_dir, user_log_dir
from pyblueiris import BlueIris

# pylint: enable=wrong-import-position


# Global Constants

SCRIPT_NAME: str = Path(__file__).stem
"""Name of this script without .py extension."""
DATE_FMT = "%Y-%m-%d %H:%M:%S"
"""Format for dates in log messages."""

# Global Variables

logger = logging.getLogger(SCRIPT_NAME)
"""Logging facility."""
camping_log: Path = (
    Path(user_log_dir("CamPing", appauthor=False, ensure_exists=True)) / "camping.log"
)
"""CamPing log file."""

# Configure logging to console and file
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)  # Log ERROR and CRITICAL to console
console_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt=DATE_FMT,
)
console_handler.setFormatter(console_formatter)

rotating_handler = RotatingFileHandler(camping_log, maxBytes=5 * 1024 * 1024, backupCount=3)
"""Rotating log file handler."""
rotating_handler.setLevel(logging.INFO)
rotating_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Log format
        datefmt=DATE_FMT,
    )
)

# Setup root logger
logging.basicConfig(
    handlers=[console_handler, rotating_handler],
    level=logging.INFO,
)

ERROR_COUNT: int = 0
"""Count of errors encountered."""


def exit_with_status(status: int) -> NoReturn:
    """Exit with status.

    Args:
        status (int): exit status
    """
    logger.info(f'{"=" * 60}')
    logging.shutdown()
    sys.exit(status)


def ping_healthchecks(url: str, data: str = "", timeout=10) -> None:
    """Send ping to healthchecks.io: https://healthchecks.io/docs/.

    Arguments:
                url -- healthchecks.io URL with unique ping code
                data -- optional data to include in the ping
                timeout -- timeout for the ping request (default: 10 seconds)
    Raises:
                RuntimeError -- if the ping fails
                OSError -- if curl is not found
    """
    cmd = [
        "curl",
        "-fsS",
        "--max-time",
        str(timeout),
        "--retry",
        "5",
        "-o",
        "NUL" if os.name == "nt" else "/dev/null",
    ]
    if data:
        cmd += ["--data-raw", data]
    # cmd.append("http://this-hostname-should-not-exist.invalid")  # Test DNS failure
    # cmd.append("https://10.255.255.1") # For testing, simulates a 504 Gateway Timeout
    cmd.append(url)
    logger.info(f"Pinging healthchecks.io with command: {' '.join(cmd)} ...")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        err = result.stderr

        if result.returncode != 0:
            raise RuntimeError(f"{' '.join(cmd)} failed: {err.strip()}")

    except OSError as e:
        raise OSError(f"curl not found or error: {e}")  # pylint: disable=raise-missing-from


def signal_failure(url: str, msg: str) -> None:
    """Signal failure.

    Args:
        url (str): healthchecks.io URL
        msg (str): message to log
    """
    global ERROR_COUNT
    ERROR_COUNT += 1

    logger.info(f"Signaling failure to {url}, data='{msg}' ...")
    try:
        ping_healthchecks(url + "/fail", msg)
    except (RuntimeError, OSError) as e:
        logger.critical(f"Failed to ping {url}: {e}")
    except Exception as e:  # pylint: disable=broad-exception-caught  # noqa: BLE001
        logger.critical(f"Unexpected error pinging {url}: {type(e).__name__}: {e}")


def signal_critical_failure(url: str, msg: str) -> NoReturn:
    """Signal critical failure.

    Args:
        url (str): healthchecks.io URL
        msg (str): message to log
    """
    signal_failure(url, msg)
    logger.critical(msg + "; exiting.")
    exit_with_status(1)


def signal_error_failure(url: str, msg: str) -> None:
    """Signal error failure.

    Args:
        url (str): healthchecks.io URL
        msg (str): message to log
    """
    signal_failure(url, msg)
    logger.error(msg)


def load_config() -> dict[str, Any]:
    """Load configuration from camping.toml.

    Returns:
        dict: Configuration data
    """
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
        raise ValueError(f"Error reading configuration file {config_file}: {e}") from e

    logger.info(f'Configuration loaded from "{config_file}".')

    for key in [
        "blueiris_user",
        "blueiris_url",
        "blueiris_ping_url",
        "cameras_ping_url",
        "storage_ping_url",
        "min_free_gb",
    ]:
        if key not in config_data:
            raise KeyError(f'"{key}" not found in {config_file}')

    return config_data


async def main() -> None:
    """Check Blue Iris security camera status.

    Raises:
        FileNotFoundError: Configuration file not found
        ValueError: Error reading configuration file.
        KeyError: Key not found in configuration .toml file.
        ValueError: BlueIris password not found in keyring.
    """
    logger.info(f'{"=" * 60}')
    logger.info(f"{SCRIPT_NAME} version {__version__} starting ...")

    config_data: dict[str, Any] = load_config()

    blueiris_ping_url = config_data["blueiris_ping_url"]
    """healthchecks.io URL for Blue Iris."""
    cameras_ping_url = config_data["cameras_ping_url"]
    """healthchecks.io URL for cameras."""
    storage_ping_url = config_data["storage_ping_url"]
    """healthchecks.io URL for storage."""
    min_free_gb: float = config_data["min_free_gb"]
    """Minimum free disk space in GB."""

    logger.info("Settings:")
    for key in ["blueiris_ping_url", "cameras_ping_url", "storage_ping_url", "min_free_gb"]:
        logger.info(f"  {key} = {config_data[key]}")

    blueiris_password: str = keyring.get_password("blueiris", config_data["blueiris_user"]) or ""
    if not blueiris_password:
        raise ValueError("BlueIris password not found in keyring.")

    logger.info(f"Parsing BlueIris URL {config_data['blueiris_url']} ...")
    parsed_url: ParseResult = urlparse(config_data["blueiris_url"])
    protocol: str = parsed_url.scheme
    host: str | None = parsed_url.hostname
    port: int = parsed_url.port or (443 if protocol == "https" else 80)

    logger.info("Creating aiohttp session ...")
    async with ClientSession(raise_for_status=True) as session:
        bi = BlueIris(
            aiosession=session,
            user=config_data["blueiris_user"],
            password=blueiris_password,
            protocol=protocol,
            host=host,
            port=str(port),
            logger=logger,
            # debug=True
        )

        logger.info(
            f"Logging into {protocol}://{host}:{port} as {config_data['blueiris_user']} ..."
        )

        try:
            if not await bi.setup_session():
                signal_critical_failure(
                    blueiris_ping_url, "Blue Iris DOWN: Failed to setup session"
                )

        except Exception as e:  # pylint: disable=broad-exception-caught  # noqa: BLE001
            signal_critical_failure(blueiris_ping_url, f"Blue Iris DOWN: {type(e).__name__}: {e}")

        if bi.version == "noname":
            signal_critical_failure(blueiris_ping_url, "Blue Iris login failed")

        logger.info(f"Blue Iris Version {bi.version} {bi.name}.")

        logger.info("Retrieving Blue Iris status ...")
        async with session.post(
            bi.client.url,
            json={
                "cmd": "status",
                "session": bi.client.blueiris_session,
            },
        ) as response:
            response.raise_for_status()
            status_response = await response.json()

        if status_response.get("result") != "success":
            signal_critical_failure(
                blueiris_ping_url,
                f"Unable to retrieve Blue Iris status: {status_response!r}",
            )

        status = status_response["data"]

        logger.info("Checking video storage status ...")

        for volume in status.get("disks", []):
            logger.info(
                f"Blue Iris volume {volume['disk']}: {volume['free'] / 1024:.1f} GB free of {volume['total'] / 1024:.1f} GB total, error={volume['error']}",
            )

            if volume["free"] / 1024 < min_free_gb:
                signal_error_failure(
                    storage_ping_url,
                    f"Volume {volume['disk']} < {min_free_gb} GB free: {volume['free'] / 1024:.1f} GB free.",
                )

            if volume["error"]:
                signal_error_failure(
                    storage_ping_url, f"Volume {volume['disk']} has {volume['error']} error(s)."
                )

        if ERROR_COUNT == 0:
            logger.info("Blue Iris video storage OK.")
            ping_healthchecks(storage_ping_url)

        logger.info("Updating camera list ...")
        logger.setLevel(logging.WARNING)
        await bi.update_camlist()
        logger.setLevel(logging.INFO)

        down: list[str] = []
        """List of cameras that are down."""

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

        # Blue Iris responded OK
        ping_healthchecks(blueiris_ping_url)

        if down:
            signal_error_failure(
                cameras_ping_url, f'{len(down)} camera(s) DOWN: {", ".join(sorted(down))}.'
            )
            exit_with_status(1)

        # All cameras are UP
        ping_healthchecks(cameras_ping_url)

        exit_with_status(ERROR_COUNT > 0)


def cli() -> None:
    """Command line interface for CamPing."""
    try:
        asyncio.run(main())
    except Exception as msg:  # pylint: disable=broad-exception-caught  # noqa: BLE001
        logger.critical(f"{msg}; exiting.")
        exit_with_status(1)


if __name__ == "__main__":
    cli()
