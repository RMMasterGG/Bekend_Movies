import logging
from logging import INFO

import colorlog
from colorlog.escape_codes import escape_codes

escape_codes["info_white"] = "\033[38;5;250m"

def create_logger(name: str, get_logger: str, level: str = INFO) -> logging.Logger:
    new_logger = logging.getLogger(get_logger)
    new_logger.handlers.clear()
    new_logger.setLevel(level)
    console_handler = logging.StreamHandler()
    formatter = colorlog.ColoredFormatter(
    fmt=f"%(log_color)s%(levelname)-8s | (%(asctime)s) - {name} - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors=dict(
        DEBUG="white",
        INFO="info_white",
        WARNING="yellow",
        ERROR="red",
        CRITICAL="red")
    )
    console_handler.setFormatter(formatter)
    new_logger.addHandler(console_handler)

    return new_logger
