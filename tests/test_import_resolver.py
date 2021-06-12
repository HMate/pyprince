from pyprince.parser.Project import Project
import unittest

from pyprince.parser import parse_project
from tests import testutils


class TestImportResolver(unittest.TestCase):

    # TODO: Finish test
    def test_code_generate(self):
        test_main = testutils.get_test_scenarios_dir() / "exmp00_no_imports/main.py"
        project: Project = parse_project(test_main)
        expected = """print("Hello pyparser")"""
        actual = project.generate_code()
        self.assertEqual(expected, actual)

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

        # test_module_path("Test", "sub", ".mod.Test")

    # TODO: test relative imports in subpackage
    # TODO: test start imports


if __name__ == "__main__":
    unittest.main()