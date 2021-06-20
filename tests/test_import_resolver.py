import sys
import unittest
import textwrap
from pathlib import Path

from pyprince.parser import parse_project
from tests import testutils
from tests.testutils import PackageGenerator
from pyprince.parser.Project import Project


class TestImportResolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.known_mod_keys = None

    def setUp(self):
        self.test_root = testutils.get_test_scenarios_dir()
        # Remove modules that are imported during a previous test run
        mod_keys = set(sys.modules.keys())
        cls = type(self)
        if cls.known_mod_keys:
            unknown = mod_keys.difference(cls.known_mod_keys)
            if unknown:
                for key in unknown:
                    sys.modules.pop(key)
        cls.known_mod_keys = set(sys.modules.keys())

    def test_code_generate_simplest(self):
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent("""print("Hello pyparser")\n"""),
        )
        gen.generate_files(self.test_root)

        test_main = self.test_root / test_name / "main.py"
        project: Project = parse_project(test_main)
        expected = """print("Hello pyparser")\n"""
        actual = project.generate_code()
        self.assertEqual(expected, actual)

    def test_code_generate_local_func(self):
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                def some_functionality(parents, relatives):
                    return parents + relatives


                def main():
                    everybody = some_functionality(["Mom", "Dad"], ["Grandpa", "Cousin"])
                    print(f"Family: {everybody}")
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        test_main = self.test_root / test_name / "main.py"
        project: Project = parse_project(test_main)
        expected = textwrap.dedent(
            """

            def main():
                everybody = ["Mom", "Dad"] + ["Grandpa", "Cousin"]
                print(f"Family: {everybody}")
            """
        )
        actual = project.generate_code_one_level_expanded("main")
        self.assertEqual(expected, actual)

    # TODO: test scenarios:
    # - nest code in different module than main - maybe nest previously nested code -> definition maybe in another module
    # - substitute named arg
    # - substitute star, or kw args in called functions
    # - call functon from namespaced
    # - call void functon
    # - call async functon
    # - call functon nested in another function
    # - call functon nested in another expression (with statement? multiple assignments?)
    # - call multiple functons nested in another function
    # - call multiline function
    # - called functon has multiple returns
    # - called functon has multiple returns
    # - create class
    # - call class method
    # - return inside called functions loop
    # - no function implmentation found
    # - exceptions inside, outside, func called/returning in except, finally etc

    # optimization scenario: (needs dependency discovery)
    # - call Optional[], if ret is None:... -> ret is none can be merged into function code
    # - same if condition can be merged

    def test_imported_names(self):
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                import os
                import pathlib as pl
                import os.path
                import sys, abc
                from time import thread_time

                import other
                from utils import print_hello
                from utils import print_different_hello as diff
                from other import SomeGood, SomeDifferent as Diff

                print("hello main")
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "other.py",
            textwrap.dedent(
                """
                class SomeGood:
                    def __init__(self, name):
                        self.name = name


                class SomeDifferent:
                    def __init__(self, name_other):
                        self.name = name_other
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "utils.py",
            textwrap.dedent(
                """
                def print_hello():
                    print("Hello")

                def print_different_hello():
                    print("Hello")
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        test_main = self.test_root / test_name / "main.py"

        project: Project = parse_project(test_main)
        self.assertIsNotNone(project)
        self.assertIsNotNone(project.get_syntax_tree("os"))
        self.assertIsNotNone(project.get_syntax_tree("pathlib"))
        self.assertIsNotNone(project.get_syntax_tree("ntpath"))  # os.path gets "renamed"
        self.assertIsNone(project.get_syntax_tree("sys"))  # builtin
        self.assertIsNotNone(project.get_syntax_tree("abc"))
        self.assertIsNone(project.get_syntax_tree("time"))  # builtin

        self.assertIsNotNone(project.get_syntax_tree("utils"))
        self.assertIsNotNone(project.get_syntax_tree("other"))

    # TODO: this test is obsolete, rewrite for new parse
    def test_imported_paths(self):
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent(
                """
                import os
                import pathlib as pl
                import os.path
                import sys, abc
                from time import thread_time

                import other
                from utils import print_hello
                from utils import print_different_hello as diff
                from other import SomeGood, SomeDifferent as Diff

                print("hello main")
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "other.py",
            textwrap.dedent(
                """
                class SomeGood:
                    def __init__(self, name):
                        self.name = name


                class SomeDifferent:
                    def __init__(self, name_other):
                        self.name = name_other
                """
            ).lstrip(),
        )
        gen.add_file(
            test_name / "utils.py",
            textwrap.dedent(
                """
                def print_hello():
                    print("Hello")

                def print_different_hello():
                    print("Hello")
                """
            ).lstrip(),
        )
        gen.generate_files(self.test_root)

        test_main = self.test_root / test_name / "main.py"
        project: Project = parse_project(test_main)

        def test_module_path(alias, path, name):
            imp = project.imports[alias]
            self.assertEqual(path, imp.parent_name)
            self.assertEqual(name, imp.name)

        test_module_path("os", "", "os")
        test_module_path("pl", "", "pathlib")
        test_module_path("os.path", "", "os.path")
        test_module_path("sys", "", "sys")
        test_module_path("abc", "", "abc")
        test_module_path("thread_time", "", "time.thread_time")

        test_module_path("utils", "", "utils")
        test_module_path("other", "", "other")

        test_module_path("print_hello", "", "utils.print_hello")
        test_module_path("diff", "", "utils.print_different_hello")
        test_module_path("SomeGood", "", "other.SomeGood")
        test_module_path("Diff", "", "other.SomeDifferent")

    # TODO: test relative imports in subpackage
    # TODO: test start imports


if __name__ == "__main__":
    unittest.main()