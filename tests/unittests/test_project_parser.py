from pathlib import Path
import sys
import sysconfig
import textwrap

from hamcrest import assert_that, contains_exactly, contains_inanyorder, has_items, is_, only_contains

from pyprince.parser.project_cache import ProjectCache
import tests.testutils as testutils
from tests.testutils import PackageGenerator, PyPrinceTestCase, test_utils
from pyprince.parser import parse_project, Project, Module


class TestProjectParser(PyPrinceTestCase):
    def setUp(self):
        self.test_root = testutils.get_test_scenarios_dir()
        testutils.remove_imported_modules()

    def test_parsing_single_dependency(self):
        test_name = Path(self.current_test_name())
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                from util import some_functionality

                def main():
                    some_functionality(["Mom", "Dad"], ["Grandpa", "Cousin"])
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "util.py",
            textwrap.dedent(
                """
                def some_functionality(parents, relatives):
                    print(f"Family: {parents + relatives}")
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        project: Project = parse_project(self.test_root / test_name / "main.py", shallow_stdlib=True)
        assert_that(project.get_modules(), contains_inanyorder("main", "util"))
        assert_that(project.get_module("main").submodules[0].name, is_("util"))

    def test_parser_with_shallow_stdlib(self):
        test_name = Path(self.current_test_name())
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                import os

                def main():
                    print((["Mom", "Dad"], ["Grandpa", "Cousin"]))
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        project: Project = parse_project(self.test_root / test_name / "main.py", shallow_stdlib=True)
        assert_that(project.get_modules(), contains_inanyorder("main", "os"))
        assert_that(project.get_module("main").submodules[0].name, is_("os"))

    def test_parsing_package_from_stdlib(self):
        test_name = self.current_test_name()
        gen = PackageGenerator()
        gen.add_file(
            Path(test_name) / "main.py",
            textwrap.dedent(
                """
                import os

                def main():
                    print((["Mom", "Dad"], ["Grandpa", "Cousin"]))
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        project: Project = parse_project(self.test_root / test_name / "main.py", shallow_stdlib=True)
        assert_that(project.list_packages(), contains_inanyorder(test_name, "stdlib"))
        assert_that(project.get_package(test_name).modules, contains_exactly("main"))
        assert_that(project.get_package("stdlib").modules, contains_exactly("os"))

    def test_parsing_package_from_local(self):
        test_name = self.current_test_name()
        test_path = Path(test_name)
        gen = PackageGenerator()
        gen.add_file(
            test_path / "main.py",
            textwrap.dedent(
                """
                from util import some_functionality

                def main():
                    some_functionality(["Mom", "Dad"], ["Grandpa", "Cousin"])
                """
            ).lstrip(),
        )
        gen.add_file(
            test_path / "util.py",
            textwrap.dedent(
                """
                def some_functionality(parents, relatives):
                    print(f"Family: {parents + relatives}")
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        project: Project = parse_project(self.test_root / test_name / "main.py", shallow_stdlib=True)
        assert_that(project.list_packages(), contains_exactly(test_name))
        assert_that(project.get_package(test_name).modules, contains_inanyorder("main", "util"))

    def test_parsing_package_from_site_packages(self):
        test_name = self.current_test_name()
        test_path = Path(test_name)
        gen = PackageGenerator()
        gen.add_file(
            test_path / "main.py",
            textwrap.dedent(
                """
                import libcst 

                def main():
                    some_functionality(["Mom", "Dad"], ["Grandpa", "Cousin"])
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        project: Project = parse_project(
            self.test_root / test_name / "main.py", shallow_stdlib=True, shallow_site_packages=True
        )
        assert_that(project.list_packages(), has_items(test_name, "libcst"))
        assert_that(project.get_package("libcst").modules, has_items("libcst"))

    def test_create_cache_with_parsing(self):
        test_name = self.current_test_name()
        gen = PackageGenerator()
        gen.add_file(
            Path(test_name) / "main.py",
            textwrap.dedent(
                """
                import os

                print((["Mom", "Dad"], ["Grandpa", "Cousin"]))
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        cache = ProjectCache()
        os_module = test_utils.create_module("os", testutils.stdlib_path() / "os.py")
        sys_module = test_utils.create_module("sys", testutils.stdlib_path() / "sys.py")
        os_module.add_submodule(sys_module.id)

        cache.project.add_module(os_module)
        cache.project.add_module(sys_module)

        project: Project = parse_project(self.test_root / test_name / "main.py", cache)
        assert_that(project.list_packages(), contains_inanyorder(test_name, "stdlib"))
        assert_that(project.get_package("stdlib").modules, contains_inanyorder("os", "sys"))
