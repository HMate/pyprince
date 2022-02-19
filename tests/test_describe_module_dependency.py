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
        self.assertDictEqual(expected, actual)

    def test_json_serialize(self):
        raw = {"nodes": ["main", "util"], "edges": {"main": ["util"]}}
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
        ).encode()
        actual = serializer.to_json(raw)
        self.assertEqual(expected, actual)

    def test_io_module(self):
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
            "_frozen_importlib",
            "_frozen_importlib_external",
            "_imp",
            "nt",
            "builtins",
            "os",
            "abc",
            "_abc",
            "collections.abc",
            "ntpath",
            "genericpath",
            "stat",
            "_stat",
            "sys",
            "site",
            "_sitebuiltins",
            "types",
            "_warnings",
            "marshal",
            "winreg",
            "_thread",
            "_weakref",
        ]
        # module dependencie nodes should be unique. The built-in io can lie about this
        actual = generators.describe_module_dependencies(project)
        self.assertListElementsAreUnique(actual["nodes"])
        self.assertListEqual(expectedNodes, actual["nodes"])

    # TODO: Additional test case: create 2 submodules with the same name, see if node names are unique
