import io
import json
from pathlib import Path

from hamcrest import (
    assert_that,
    contains_exactly,
    contains_inanyorder,
    equal_to,
    has_entry,
    has_items,
    has_key,
    is_,
    only_contains,
)

from pyprince.parser import constants
from pyprince.parser.package_finder import PackageFinder
from pyprince.parser.project import Module, ModuleIdentifier
from pyprince.parser.project_cache import ProjectCache
from tests import testutils


class TestProjectCacheSerialization(testutils.PyPrinceTestCase):
    def test_cache_save(self):
        cache = ProjectCache()
        package_finder = PackageFinder(cache.project)
        os_path = testutils.stdlib_path() / "os.py"
        os_module = testutils.create_module("os", os_path)
        cache.project.add_module(os_module)
        cache.project.add_package(package_finder.STDLIB_PACKAGE)
        package_finder.STDLIB_PACKAGE.add_module(os_module)

        with io.StringIO() as stream:
            cache.serialize(stream)

            result_content = stream.getvalue()
            result = json.loads(result_content)
            assert_that(result, has_key(constants.STDLIB_PACKAGE_NAME))
            assert_that(result[constants.STDLIB_PACKAGE_NAME], has_entry("os", {"name": "os", "path": str(os_path)}))

    def test_reading_cache(self):
        cache = ProjectCache()
        os_path = testutils.stdlib_path() / "os.py"
        content = {constants.STDLIB_PACKAGE_NAME: {"os": {"name": "os", "path": str(os_path)}}}
        with io.StringIO() as stream:
            stream.write(json.dumps(content))
            stream.seek(0)

            cache.load_stream(stream)

            assert_that(cache.project.get_package(constants.STDLIB_PACKAGE_NAME).modules, contains_exactly("os"))
            assert_that(cache.project.has_module("os"), is_(True))
            assert_that(
                cache.project.get_module("os"), equal_to(Module(ModuleIdentifier("os", None), str(os_path), None))
            )
