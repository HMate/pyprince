import pathlib

from loguru import logger

# Usage:
# from pyprince.logger import logger
# logger.debug("This is a debug message")
# logger.info("This is an info message")
# logger.warning("This is a warning message")
# logger.error("This is an error message")


def init():
    can_rotate = True

    def should_rotate_log(_msg, _file):
        """We want to create a new log file for every every invocation of init()
        So set the flag to False after the first log message.
        """
        nonlocal can_rotate
        if can_rotate:
            can_rotate = False
            return True
        return False

    logpath = get_log_folder() / "pyprince.log"

    logger.remove()
    logger.add(
        logpath,
        level="DEBUG",
        diagnose=True,
        retention=3,
        enqueue=True,
        rotation=should_rotate_log,
    )


def get_log_folder() -> pathlib.Path:
    return pathlib.Path().home() / ".pyprince"
