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
from typing import List
from datetime import timedelta, datetime
import argparse

from rich.logging import RichHandler

from tracker.helpers import utils, sheets, cli

MODULE_NAME = "track_lochness"

console = utils.get_console()

logger = logging.getLogger(MODULE_NAME)
logargs = {
    "level": logging.DEBUG,
    # "format": "%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s",
    "format": "%(message)s",
    "handlers": [RichHandler(rich_tracebacks=True)],
}
logging.basicConfig(**logargs)


def get_last_updated(config_file: Path, network: str) -> datetime:
    worksheet = sheets.get_worksheet(config_file=config_file, sheet_name=network)

    row_idx = 3
    col_idx = 18

    last_run_str = sheets.read_cell(
        worksheet=worksheet, row_idx=row_idx, col_idx=col_idx, logger=logger
    )
    last_run = datetime.strptime(last_run_str, "%Y-%m-%d %H:%M:%S")

    return last_run


def check_if_within_threshold(config_file: Path, last_run: datetime) -> bool:
    """
    Checks if the last run was within the threshold.

    Args:
        config_file (Path): The path to the config file.
        last_run (datetime): The timestamp of the last run.

    Returns:
        bool: True if the last run was within the threshold, False otherwise.
    """
    config_params = utils.config(path=config_file, section="lochness")
    threshold = int(config_params["email_threshold_hours"])

    now = datetime.now()
    diff = now - last_run

    if diff < timedelta(hours=threshold):
        return True
    else:
        return False


def send_email(config_file: Path, network: str, last_run: datetime) -> None:
    lochness_config_params = utils.config(path=config_file, section="lochness")
    email_sender = lochness_config_params["email_sender"]
    recipients_r = lochness_config_params["email_recipients"]
    email_threshold_hours = lochness_config_params["email_threshold_hours"]

    recipients: List[str] = recipients_r.split(",")
    recipients = [r.strip() for r in recipients]

    subject = f"{network} - Lochness Sync is overdue"
    body = f"""
Lochness at {network} was last seen at {last_run}.

This is an automated message, that checks if Lochness is running every {email_threshold_hours} hours.
    """

    logger.info(f"Sending email to: {recipients}")
    cli.send_email(
        recipients=recipients,
        subject=subject,
        message=body,
        sender=email_sender,
        logger=logger,
    )


if __name__ == "__main__":
    console.rule(f"[bold red]{MODULE_NAME}")

    args = argparse.ArgumentParser()
    args.add_argument(
        "--network",
        type=str,
        help="The name of the network.",
        required=True,
    )

    args = args.parse_args()
    network = args.network

    config_file = utils.get_config_file_path()
    config_params = utils.config(config_file, "general")

    utils.configure_logging(
        config_file=config_file, module_name=MODULE_NAME, logger=logger
    )
    logger.info(f"Using config file: {config_file}")

    logger.info(f"On network: {network}")

    last_run = get_last_updated(config_file=config_file, network=network)
    logger.info(f"Last updated: {last_run}")

    within_threshold = check_if_within_threshold(
        config_file=config_file, last_run=last_run
    )
    logger.info(f"Within threshold: {within_threshold}")

    if not within_threshold:
        send_email(config_file=config_file, last_run=last_run, network=network)
    else:
        logger.info("Within threshold, not sending email.")
