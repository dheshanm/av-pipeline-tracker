#!/usr/bin/env python

import sys
from pathlib import Path


file = Path(__file__).resolve()
parent = file.parent
root = None
for parent in file.parents:
    if parent.name == "av-pipeline-tracker":
        root = parent
sys.path.append(str(root))

# remove current directory from path
try:
    sys.path.remove(str(parent))
except ValueError:
    pass

import logging
from typing import Dict, List
from glob import glob
from datetime import timedelta, datetime

from rich.logging import RichHandler

from tracker.helpers import utils, sheets
from tracker.logs import parser

MODULE_NAME = "track_logs"

console = utils.get_console()

logger = logging.getLogger(MODULE_NAME)
logargs = {
    "level": logging.DEBUG,
    # "format": "%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s",
    "format": "%(message)s",
    "handlers": [RichHandler(rich_tracebacks=True)],
}
logging.basicConfig(**logargs)


class TaskResults:
    def __init__(
        self,
        task: str,
        subtask: str,
        site_id: str,
        runtime: timedelta,
        status: str,
        last_run: datetime,
        logs: str,
    ):
        self.task = task
        self.subtask = subtask
        self.site_id = site_id
        self.runtime = runtime
        self.status = status
        self.last_run = last_run
        self.logs = logs


def log_to_sheet(
    config_file: Path, network: str, TaskResults: List[TaskResults]
) -> None:
    worksheet = sheets.get_worksheet(config_file=config_file, sheet_name=network)

    for task_result in TaskResults:
        site_id = task_result.site_id

        row_idx = sheets.get_row_idx(
            sheet=worksheet, col=1, value=site_id, logger=logger
        )

        if task == "offsite":
            sub_tasks_col_idx: Dict[str, int] = {
                "audio_process": 7,
                "transcript_process": 10,
                "video_process": 13,
            }
        elif task == "daily_journal":
            sub_tasks_col_idx: Dict[str, int] = {
                "audio_process": 20,
                "transcript_process": 23,
            }
        else:
            raise NotImplementedError(f"Task: {task} not implemented")

        subtask_col_idx = sub_tasks_col_idx[task_result.subtask]

        status_col_idx = subtask_col_idx
        last_run_col_idx = subtask_col_idx + 1
        runtime_col_idx = subtask_col_idx + 2

        sheets.update_cell(
            worksheet=worksheet,
            row_idx=row_idx,
            col_idx=status_col_idx,
            value=task_result.status,
            logger=logger,
        )
        sheets.update_note(
            worksheet=worksheet,
            row_idx=row_idx,
            col_idx=status_col_idx,
            note=task_result.logs,
            logger=logger,
        )

        sheets.update_cell(
            worksheet=worksheet,
            row_idx=row_idx,
            col_idx=last_run_col_idx,
            value=str(task_result.last_run),
            logger=logger,
        )
        sheets.update_cell(
            worksheet=worksheet,
            row_idx=row_idx,
            col_idx=runtime_col_idx,
            value=str(task_result.runtime),
            logger=logger,
        )


def log_completion(config_file: Path, network: str) -> None:
    worksheet = sheets.get_worksheet(config_file=config_file, sheet_name=network)

    current_time = datetime.now()

    row_idx = 3
    col_idx = 18

    sheets.update_cell(
        worksheet=worksheet,
        row_idx=row_idx,
        col_idx=col_idx,
        value=str(current_time),
        logger=logger,
    )


def track_site_logs(config_file: Path, task: str, site_logs: Path) -> None:
    logger.info(f"Tracking {task} logs for site: {site_logs.name}")
    site_id = site_logs.name[-2:]

    offsite_subtasks: List[str] = [
        "audio_process",
        "transcript_process",
        "video_process",
    ]
    diary_subtasks: List[str] = ["audio_process", "transcript_process"]

    if task == "offsite":
        subtasks = offsite_subtasks
    elif task == "daily_journal":
        subtasks = diary_subtasks
    else:
        raise ValueError(f"Invalid task: {task}")

    task_results: List[TaskResults] = []

    for subtask in subtasks:
        # logger.info(f"Tracking {subtask} logs for site: {site_logs.name}")
        pattern = glob(str(site_logs / f"{subtask}_*.txt"))

        if len(pattern) == 0:
            raise FileNotFoundError(f"No logs found for {subtask} at {site_logs}")

        recent_log_file = utils.get_most_recent_file(pattern)
        # logger.debug(f"Most recent log file: {recent_log_file}")
        runtime = parser.get_runtime(log=recent_log_file)
        # logger.debug(f"Runtime: {runtime}")
        run_time = parser.get_datetime_from_filename(recent_log_file)
        # logger.debug(f"Run time: {run_time}")
        status = parser.get_error(log=recent_log_file)
        if status is None:
            status = "No errors"
        # logger.debug(f"Status: {status}")

        logs = parser.get_logs(log=recent_log_file)

        task_result = TaskResults(
            task=task,
            subtask=subtask,
            site_id=site_id,
            runtime=runtime,
            status=status,
            last_run=run_time,
            logs=logs,
        )

        task_results.append(task_result)

    log_to_sheet(config_file=config_file, network=network, TaskResults=task_results)


def track_logs(config_file: Path, network: str, task: str) -> None:
    """
    Tracks logs for a given network and task.

    Args:
        config_file (Path): The path to the config file.
        network (str): The name of the network.
        task (str): The name of the task.

    Returns:
        None
    """
    logger.info(f"Tracking logs for network: {network} and task: {task}")

    network_logs_path = utils.get_network_logs_path(
        config_file=config_file, network=network, task=task
    )

    logger.info(f"Logs path: {network_logs_path}")

    # Get the list of sites
    # each site is its own directory

    for site in network_logs_path.iterdir():
        if site.is_dir():
            if site.name == "TOTAL":
                continue
            track_site_logs(config_file=config_file, task=task, site_logs=site)


if __name__ == "__main__":
    console.rule(f"[bold red]{MODULE_NAME}")

    config_file = utils.get_config_file_path()
    config_params = utils.config(config_file, "general")

    utils.configure_logging(
        config_file=config_file, module_name=MODULE_NAME, logger=logger
    )
    logger.info(f"Using config file: {config_file}")

    network = config_params["network"]
    logger.info(f"On network: {network}")

    tasks = ["daily_journal", "offsite"]
    for task in tasks:
        logger.info(f"On task: {task}")
        track_logs(config_file=config_file, network=network, task=task)

    log_completion(config_file=config_file, network=network)

    logger.info("Done!")
