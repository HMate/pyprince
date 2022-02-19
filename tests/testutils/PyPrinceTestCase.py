import unittest


class PyPrinceTestCase(unittest.TestCase):
    """Contains additional asserts for usage in pyprince tests"""

    def assertListElementsAreUnique(self, container: list, msg=None):
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
