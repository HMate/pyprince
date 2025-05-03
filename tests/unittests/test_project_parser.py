from pathlib import Path
import textwrap

from hamcrest import assert_that, contains_exactly, contains_inanyorder, has_items, is_, only_contains

import tests.testutils as testutils
from pyprince.parser.project import PackageType
from pyprince.parser.project_cache import ProjectCache
from pyprince.parser import parse_project, Project, Module


class TestProjectParser(testutils.PyPrinceTestCase):
    def setUp(self):
        self.test_root = testutils.get_test_scenarios_dir()
        testutils.remove_imported_modules()

    def test_parsing_single_dependency(self):
        test_name = self.current_test_name()
        test_path = Path(test_name)
        gen = testutils.PackageGenerator()
        gen.add_file(
            test_path / "main.py",
            textwrap.dedent(
                """
                from util import some_functionality
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
        assert_that(project.get_modules(), contains_inanyorder("main", "util"))
        assert_that(project.get_module("main").submodules[0].name, is_("util"))
        assert_that(project.get_package(test_name).package_type, PackageType.Local)

    def test_parsing_stdlib_module_with_shallow_stdlib(self):
        test_name = Path(self.current_test_name())
        gen = testutils.PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                import os
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        project: Project = parse_project(self.test_root / test_name / "main.py", shallow_stdlib=True)
        assert_that(project.get_modules(), contains_inanyorder("main", "os"))
        assert_that(project.get_module("main").submodules[0].name, is_("os"))

    def test_parsing_stdlib_module_has_submodules(self):
        test_name = Path(self.current_test_name())
        gen = testutils.PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                import os
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        project: Project = parse_project(self.test_root / test_name / "main.py", shallow_stdlib=True)
        assert_that(project.get_modules(), contains_inanyorder("main", "os"))
        submodules = [sub.name for sub in project.get_module("os").submodules]
        assert_that(submodules, has_items("abc", "sys", "stat"))  # in cpython 3.9.13

    def test_parsing_stdlib_module_has_correct_package(self):
        test_name = self.current_test_name()
        gen = testutils.PackageGenerator()
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
        gen = testutils.PackageGenerator()
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
        assert_that(project.get_package(test_name).package_type, PackageType.Local)

    def test_parsing_package_from_site_packages(self):
        test_name = self.current_test_name()
        test_path = Path(test_name)
        gen = testutils.PackageGenerator()
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
        assert_that(project.get_package("libcst").package_type, PackageType.Site)

    def test_parse_stdlib_package_from_cache(self):
        test_name = self.current_test_name()
        gen = testutils.PackageGenerator()
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
        os_module = testutils.create_module("os", testutils.stdlib_path() / "os.py")
        sys_module = testutils.create_module("sys", testutils.stdlib_path() / "sys.py")
        os_module.add_submodule(sys_module.id)

        cache._project.add_module(os_module)
        cache._project.add_module(sys_module)

        project: Project = parse_project(self.test_root / test_name / "main.py", cache)
        assert_that(project.list_packages(), contains_inanyorder(test_name, "stdlib"))
        assert_that(project.get_package("stdlib").modules, contains_inanyorder("os", "sys"))
        assert_that(project.get_package("stdlib").package_type, PackageType.StandardLib)
