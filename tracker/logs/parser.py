from datetime import timedelta, datetime
from pathlib import Path
from typing import Optional


def get_runtime(log: Path) -> timedelta:
    """
    Parses the runtime from a log file.

    Looks for lines like this:
        Current time: 18:03:49

    Returns the difference between the first and last matches.

    Args:
        log (Path): The path to the log file.

    Returns:
        timedelta: The runtime.
    """
    with open(log, "r") as f:
        lines = f.readlines()

    # Get the lines that contain the runtime
    runtime_lines = [line for line in lines if "Current time" in line]

    # Get the first and last matches
    try:
        first_match = runtime_lines[0]
        last_match = runtime_lines[-1]
    except IndexError:
        return timedelta(seconds=0)

    # Get the times
    first_time = first_match.split()[2]
    last_time = last_match.split()[2]

    # Convert to datetime objects
    first_time = datetime.strptime(first_time, "%H:%M:%S")
    last_time = datetime.strptime(last_time, "%H:%M:%S")

    # Get the difference
    runtime = last_time - first_time

    return runtime


def get_datetime_from_filename(file: Path) -> datetime:
    """
    Parses the time from a filename.

    Looks for a timestamp in the filename.

    Example:
        >>> filename = "file_1703230348.txt"
        >>> get_time_from_filename(filename)
        datetime.datetime(2017, 3, 23, 3, 48)

    Args:
        filename (str): The filename.

    Returns:
        datetime: The datetime object.
    """
    # Get the timestamp from the filename
    filename = file.name
    timestamp = filename.split("_")[-1].split(".")[0]

    # Convert to datetime object
    dt = datetime.fromtimestamp(int(timestamp))

    return dt


def get_error(log: Path) -> Optional[str]:
    """
    Parses the error from a log file.

    Looks for lines that contain:
        ERROR:*
        Traceback (most recent call last):

    Returns the error message., if found.

    Args:
        log (Path): The path to the log file.

    Returns:
        Optional[str]: The error.
    """
    with open(log, "r") as f:
        lines = f.readlines()

    if len(lines) == 0:
        return "Empty log file"

    # Get the lines that contain the error
    error_lines = [line for line in lines if "ERROR:" in line or "Traceback" in line]

    if len(error_lines) > 0:
        return "Python Error"

    pipeline_rejection = [line for line in lines if "Exiting, please requeue" in line]

    if len(pipeline_rejection) > 0:
        return "Pipeline Rejected"

    return None
