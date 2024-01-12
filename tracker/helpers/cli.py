import logging
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable, List, Optional
from datetime import datetime


def get_repo_root() -> str:
    """
    Returns the root directory of the current Git repository.

    Uses the command `git rev-parse --show-toplevel` to get the root directory.
    """
    repo_root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
    repo_root = repo_root.decode("utf-8").strip()
    return repo_root


def execute_commands(
    command_array: list,
    shell: bool = False,
    logger: Optional[logging.Logger] = None,
    on_fail: Callable = lambda: sys.exit(1),
) -> subprocess.CompletedProcess:
    """
    Executes a command and returns the result.

    Args:
        command_array (list): The command to execute as a list of strings.
        shell (bool, optional): Whether to execute the command in a shell. Defaults to False.
        logger (Optional[logging.Logger], optional): The logger to use for logging. Defaults to None.
        on_fail (Callable, optional): The function to call if the command fails. Defaults to lambda: sys.exit(1).

    Returns:
        subprocess.CompletedProcess: The result of the command execution.

    """

    if logger is None:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

    logger.debug("Executing command:")
    # cast to str to avoid error when command_array is a list of Path objects
    command_array = [str(x) for x in command_array]

    if logger:
        logger.debug(" ".join(command_array))

    if shell:
        result = subprocess.run(
            " ".join(command_array),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )
    else:
        result = subprocess.run(
            command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    if result.returncode != 0:
        logger.error("=====================================")
        logger.error("Command: " + " ".join(command_array))
        logger.error("=====================================")
        logger.error("stdout:")
        logger.error(result.stdout.decode("utf-8"))
        logger.error("=====================================")
        logger.error("stderr:")
        logger.error(result.stderr.decode("utf-8"))
        logger.error("=====================================")
        logger.error("Exit code: " + str(result.returncode))
        logger.error("=====================================")

        if on_fail:
            on_fail()

    return result


def send_email(
    subject: str,
    message: str,
    recipients: List[str],
    sender: str,
    attachments: List[Path] = [],
    logger: Optional[logging.Logger] = None,
) -> None:
    """
    Send an email with the given subject and message to the given recipients.

    Uses the `mail` binary to send the email.

    Args:
        subject (str): The subject of the email.
        message (str): The message of the email.
        recipients (List[str]): The recipients of the email.
        sender (str): The sender of the email.
        attachments (List[Path], optional): The attachments to add to the email. Defaults to [].
        logger (Optional[logging.Logger], optional): The logger to use for logging. Defaults to None.

    Returns:
        None
    """

    if logger is None:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

    mail_binary = Path("/usr/bin/mail")

    if not mail_binary.exists():
        logger.error("[red][u]mail[/u] binary not found.[/red]", extra={"markup": True})
        logger.warning(
            "[yellow]Skipping sending email.[/yellow]", extra={"markup": True}
        )
        return

    with tempfile.NamedTemporaryFile(mode="w", prefix="email_", suffix=".eml") as temp:
        temp.write(f"From: {sender}\n")
        temp.write(f"To: {','.join(recipients)}\n")
        temp.write(f"Subject: {subject}\n")
        temp.write("\n")
        temp.write(message)
        temp.write("\n")
        if attachments:
            temp.write("\n")
            temp.write(f"{len(attachments)} Attachment(s):\n")
            for attachment in attachments:
                temp.write(str(attachment.name) + "\n")
        temp.write("\n")
        temp.write(f"Sent at: {datetime.now()} {datetime.now().astimezone().tzinfo}")
        temp.flush()

        command_array = [
            str(mail_binary),
            "-s",
            f"'{subject}'",  # wrap subject in quotes to avoid issues with special characters
        ]

        for attachment in attachments:
            command_array += ["-a", str(attachment)]

        command_array += recipients

        command_array += ["<", temp.name]

        logger.debug("Sending email:")
        logger.debug(" ".join(command_array))
        with open(temp.name, "r") as f:
            logger.debug("Email contents:")
            logger.debug(f.read())
        execute_commands(command_array, shell=True)
