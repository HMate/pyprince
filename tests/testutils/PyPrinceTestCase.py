import collections.abc
import unittest
from typing import Iterable, List, Optional, TypeVar

from pyprince.logger import logger, get_log_folder

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

    def assertListElementsAreUnique(self, container: List, msg=None):
        uniques = set(container)
        if len(uniques) == len(container):
            return

        # to make a good fail message, collect elems that are not unique
        counter = dict()
        duplicates = set()
        for elem in container:
            if elem in counter:
                counter[elem] += 1
                duplicates.add(elem)
            else:
                counter[elem] = 1

        elemCount = ", ".join([f"{repr(elem)}({counter[elem]} times)" for elem in duplicates])
        standardMsg = f"These element can be found multiple times: {elemCount}"
        self.fail(self._formatMessage(msg, standardMsg))

    def assertContains(
        self, container: collections.abc.Collection[T], members: collections.abc.Collection[T], msg=None
    ):
        missing = set()
        for member in members:
            if member not in container:
                missing.add(member)

        if len(missing) == 0:
            # success
            return

        standardMsg = (
            f"These members are missing from container: {repr(missing)}\noriginal container: {repr(container)}"
        )
        self.fail(self._formatMessage(msg, standardMsg))

    def assertUnorderedEqual(self, container: Optional[Iterable], other_container: Optional[Iterable]):
        if container is None:
            self.fail(f"First container should not be None")
        if other_container is None:
            self.fail(f"Second container should not be None")
        members1 = set(container)
        members2 = set(other_container)
        self.assertSetEqual(members1, members2)
