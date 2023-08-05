import unittest
from pathlib import Path
import textwrap

import tests.testutils as testutils
from tests.testutils import PackageGenerator, PyPrinceTestCase
from pyprince.parser import parse_project, Project
from pyprince import generators


class TestCodeGenerator(PyPrinceTestCase):
    def setUp(self):
        self.test_root = testutils.get_test_scenarios_dir()
        testutils.remove_imported_modules()

    def test_generate_original_code(self):
        test_name = Path(self._testMethodName)
        gen = PackageGenerator()
        gen.add_file(
            test_name / "main.py",
            textwrap.dedent("""print("Hello pyparser")"""),
        )
        gen.generate_files(self.test_root)

        project: Project = parse_project(self.test_root / test_name / "main.py")
        expected = """print("Hello pyparser")"""
        actual = generators.generate_code(project)
        self.assertEqual(expected, actual)
