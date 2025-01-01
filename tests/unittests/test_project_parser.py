from pathlib import Path
import textwrap

import tests.testutils as testutils
from tests.testutils import PackageGenerator, PyPrinceTestCase
from pyprince.parser import parse_project, Project


class TestProjectParser(PyPrinceTestCase):
    def setUp(self):
        self.test_root = testutils.get_test_scenarios_dir()
        testutils.remove_imported_modules()

    def test_single_dependency(self):
        test_name = Path(self._testMethodName)
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
        self.assertUnorderedEqual(project.get_modules(), ["main", "util"])
        self.assertEqual(project.get_module("main").submodules[0].name, "util")

    def test_parser_with_shallow_stdlib(self):
        test_name = Path(self._testMethodName)
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
        self.assertUnorderedEqual(project.get_modules(), ["main", "os"])
        self.assertEqual(project.get_module("main").submodules[0].name, "os")

    def test_package_parsing(self):
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
        self.assertUnorderedEqual(project.list_packages(), [test_name, "stdlib"])
        self.assertUnorderedEqual(project.get_package(test_name).modules, ["main"])
        self.assertUnorderedEqual(project.get_package("stdlib").modules, ["os"])
