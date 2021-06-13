import sys
from pyprince.parser.Project import Project
import unittest
import textwrap

from pyprince.parser import parse_project
from tests import testutils


class TestImportResolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.known_mod_keys = None

    def setUp(self):
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
        test_main = testutils.get_test_scenarios_dir() / "exmp00_no_imports/main.py"
        project: Project = parse_project(test_main)
        expected = """print("Hello pyparser")\n"""
        actual = project.generate_code()
        self.assertEqual(expected, actual)

    def test_code_generate_local_func(self):
        test_main = testutils.get_test_scenarios_dir() / "exmp03_local_func/main.py"
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

    # optimization scenario: (needs dependency discovery)
    # - call Optional[], if ret is None:... -> ret is none can be merged into function code
    # - same if condition can be merged

    def test_imported_names(self):
        test_main = testutils.get_test_scenarios_dir() / "exmp01_import_modules/main.py"
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
        test_main = testutils.get_test_scenarios_dir() / "exmp01_import_modules/main.py"
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