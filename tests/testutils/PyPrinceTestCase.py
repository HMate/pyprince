import collections.abc
import unittest
from typing import Iterable, List, Optional, TypeVar

from pyprince.utils import logger, get_log_folder

g_log_should_rotate = True

T = TypeVar("T")


class PyPrinceTestCase(unittest.TestCase):
    """Contains additional asserts for usage in pyprince tests"""

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)

        def should_rotate_log(_msg, _file):
            """We want to create a new log file for every every invocation of init()
            So set the flag to False after the first log message.
            """
            global g_log_should_rotate
            if g_log_should_rotate:
                g_log_should_rotate = False
                return True
            return False

        if g_log_should_rotate:
            logger.add(
                get_log_folder() / "pyprince_test.log",
                level="TRACE",
                diagnose=True,
                retention=20,
                rotation=should_rotate_log,
            )
        logger.info(f"**** Starting test {methodName} ****")

    def current_test_name(self):
        return self.id().split(".")[2]
