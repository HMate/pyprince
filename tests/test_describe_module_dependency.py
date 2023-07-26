from pathlib import Path
import textwrap

import tests.testutils as testutils
from tests.testutils import PackageGenerator, PyPrinceTestCase
from pyprince.parser import parse_project, Project
from pyprince import generators, serializer


class TestDescribeModuleDependency(PyPrinceTestCase):
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

        project: Project = parse_project(self.test_root / test_name / "main.py")
        expected = {"nodes": ["main", "util"], "edges": {"main": ["util"]}}
        actual = generators.describe_module_dependencies(project)
        self.assertDictEqual(expected, actual.to_dict())

    def test_json_serialize(self):
        deps = generators.DependencyDescriptor()
        deps.add_node("main")
        deps.add_node("util")
        deps.add_edge("main", "util")

        expected = textwrap.dedent(
            """\
            {
              "nodes": [
                "main",
                "util"
              ],
              "edges": {
                "main": [
                  "util"
                ]
              }
            }"""
        )
        actual = serializer.to_json(deps)
        self.assertEqual(expected, actual)

    def test_graphviz_serialize(self):
        deps = generators.DependencyDescriptor()
        deps.add_node("main")
        deps.add_node("util")
        deps.add_node("belize")
        deps.add_node("femme")
        deps.add_edge("main", "util")
        deps.add_edge("main", "belize")
        deps.add_edge("util", "femme")
        deps.add_edge("femme", "main")
        expected = textwrap.dedent(
            """\
            digraph G {
                "main" -> "util"
                "main" -> "belize"
                "util" -> "femme"
                "femme" -> "main"
            }"""
        )
        actual = serializer.to_graphviz_dot(deps)
        self.assertEqual(expected, actual)

    def test_io_module(self):
        """io modue has built-in dependencies on _io, _abc and import inside try-catch blocks
        We check if the parser gathers these correctly.
        """
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                import io
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        project: Project = parse_project(self.test_root / test_name / "main.py")
        expectedNodes = [
            "main",
            "io",
            "_io",
            "abc",
            "_abc",
        ]
        # module dependency nodes should be unique.
        actual = generators.describe_module_dependencies(project).to_dict()
        self.assertListElementsAreUnique(actual["nodes"])
        self.assertEquals(len(actual["nodes"]), 223)
        self.assertContains(actual["nodes"], expectedNodes)

    def test_argparse_module(self):
        """argparse module has 2 interesting scenarios:
        - dependecies on pyd modules (unicodedata.pyd)
        - uses the pwd module which is unix only
        We dont parse the code for these but we should still register the modules.
        """
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                import argparse
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        project: Project = parse_project(self.test_root / test_name / "main.py")
        expectedNodes = ["main", "argparse", "unicodedata", "pwd"]
        actual = generators.describe_module_dependencies(project).to_dict()
        self.assertContains(actual["nodes"], expectedNodes)

    # TODO: Additional test case: create 2 submodules with the same name, see if node names are unique
