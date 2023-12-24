import logging
from pathlib import Path
from typing import List

from rich.console import Console
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TaskProgressColumn,
    MofNCompleteColumn,
    TimeRemainingColumn,
)

from tracker.helpers import cli
from tracker.helpers.config import config

_console = Console(color_system="standard")


def get_progress_bar() -> Progress:
    """
    Returns a rich Progress object with standard columns.

    Returns:
        Progress: A rich Progress object with standard columns.
    """
    return Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    )


def get_console() -> Console:
    """
    Returns a Console object with standard color system.

    Returns:
        Console: A Console object with standard color system.
    """
    return _console


def configure_logging(config_file: Path, module_name: str, logger: logging.Logger):
    """
    Configures logging for a given module using the specified configuration file.

    Args:
        config_file (str): The path to the configuration file.
        module_name (str): The name of the module to configure logging for.
        logger (logging.Logger): The logger object to use for logging.

    Returns:
        None
    """
    log_params = config(config_file, "logging")
    log_file = log_params[module_name]

    file_handler = logging.FileHandler(log_file, mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s  - %(process)d - %(name)s - %(levelname)s - %(message)s"
        )
    )

    logging.getLogger().addHandler(file_handler)

    logger.info(f"Logging to {log_file}")


def get_config_file_path() -> Path:
    """
    Returns the path to the config file.

    Returns:
        str: The path to the config file.

    Raises:
        ConfigFileNotFoundExeption: If the config file is not found.
    """
    repo_root = cli.get_repo_root()
    config_file_path = repo_root + "/config.ini"

    # Check if config_file_path exists
    if not Path(config_file_path).is_file():
        raise FileNotFoundError(f"Config file not found at {config_file_path}")

    return Path(config_file_path)


def get_network_logs_path(config_file: Path, network: str, task: str) -> Path:
    """
    Returns the path to the network logs directory.

    Args:
        config_file (Path): The path to the config file.
        network (str): The name of the network.
        task (str): The name of the task.

    Returns:
        str: The path to the network logs directory.]

    Raises:
        KeyError: If the key is not found in the config file.
    """

    config_params = config(config_file, "log-source-dir")

    key = f"{network.lower()}_{task}_logs"
    if key not in config_params:
        raise KeyError(f"Key {key} not found in config file")

    network_logs_path = config_params[key]

    return Path(network_logs_path)


def get_most_recent_file(files: List[str]) -> Path:
    """
    Returns the most recent file from a list of files.

    The file's name, which contains the timestamp, is used to determine the most recent file.

    Example:
        >>> files = ["file1_1703230348.txt", "file2_1703040196.txt"]
        >>> get_most_recent_file(files)
        "file1_1703230348.txt"

    Args:
        files (List[str]): A list of files.

    Returns:
        str: The most recent file.
    """

    file_paths = [Path(file) for file in files]

    # Sort the files by name
    file_paths.sort()

    most_recent_file = file_paths[-1]

    return most_recent_file
