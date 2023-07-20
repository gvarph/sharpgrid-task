import logging

from env import LOG_LEVEL
from colorlog import ColoredFormatter


def get_logger(name: str) -> logging.Logger:
    """
    Creates and returns a logger with the given name.

    The logger will have a level set as defined in the LOG_LEVEL environment variable and
    will have a console handler that outputs colored logs.

    :param name: The name of the logger.
    :return: A logger with the given name, a set level, and a console handler.
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(white)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={},
        style="%",
    )

    # Create a console handler and add the formatter to it
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Add the console handler to the logger
    logger.addHandler(console_handler)
    return logger
