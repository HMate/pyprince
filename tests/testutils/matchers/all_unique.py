from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.helpers.hasmethod import hasmethod
from hamcrest.core.description import Description


class AllUnique(BaseMatcher):
    def __init__(self):
        self.errorMsg: str = ""

    def _matches(self, item) -> bool:
        container = item
        uniques = set(container)
        if len(uniques) == len(container):
            return True

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
        self.errorMsg = f"Elements found multiple times: {elemCount}"
        return False

    def describe_mismatch(self, item, mismatch_description: Description) -> None:
        mismatch_description.append_text(self.errorMsg)


def all_unique() -> AllUnique:
    return AllUnique()
