import collections.abc
import unittest
from typing import List

from pyprince.logger import logger, get_log_folder


class PyPrinceTestCase(unittest.TestCase):
    """Contains additional asserts for usage in pyprince tests"""

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        logger.add(get_log_folder() / "pyprince_test.log", level="TRACE", diagnose=True, retention=10, rotation="00:00")
        logger.debug(f"**** Starting test {methodName} ****")

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

    def assertContains(self, container: collections.abc.Collection, members: collections.abc.Collection, msg=None):
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
