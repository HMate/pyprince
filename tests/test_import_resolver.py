from pyprince.parser.Project import Project
import unittest

from pyprince.parser import parse_file
from tests import testutils


class TestImportResolver(unittest.TestCase):

    def test_imported_names(self):
        test_main = testutils.get_test_scenarios_dir() / "exmp01_import_modules/main.py"
        project: Project = parse_file(test_main)
        self.assertIsNotNone(project)
        self.assertIn("os", project.imports)
        self.assertIn("pl", project.imports)
        self.assertIn("os.path", project.imports)
        self.assertIn("sys", project.imports)
        self.assertIn("abc", project.imports)

        self.assertIn("utils", project.imports)
        self.assertIn("other", project.imports)
        self.assertIn("print_hello", project.imports)
        self.assertIn("diff", project.imports)
        self.assertIn("SomeGood", project.imports)
        self.assertIn("Diff", project.imports)

    def test_imported_paths(self):
        test_main = testutils.get_test_scenarios_dir() / "exmp01_import_modules/main.py"
        project: Project = parse_file(test_main)
        
        def test_module_path(alias, path, name):
            imp = project.imports[alias]
            self.assertEqual(path, imp.path)
            self.assertEqual(name, imp.name)

        test_module_path("os", "", "os")
        test_module_path("pl", "", "pathlib")
        test_module_path("os.path", "", "os.path")
        test_module_path("sys", "", "sys")
        test_module_path("abc", "", "abc")

        test_module_path("utils", ".", "utils")
        test_module_path("other", "", "other")
        
        test_module_path("print_hello", "utils", "print_hello")
        test_module_path("diff", "utils", "print_different_hello")
        test_module_path("SomeGood", "other", "SomeGood")
        test_module_path("Diff", "other", "SomeDifferent")


if __name__ == "__main__":
    unittest.main()