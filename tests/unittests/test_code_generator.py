from pathlib import Path
import textwrap

from hamcrest import assert_that, equal_to
import tests.testutils as testutils
from tests.testutils import PackageGenerator
from pyprince.parser import parse_project, Project
from pyprince import generators


class TestCodeGenerator(testutils.PyPrinceTestCase):
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

        project: Project = parse_project(self.test_root / test_name / "main.py", shallow_stdlib=False)
        expected = """print("Hello pyparser")"""
        actual = generators.generate_code(project)
        assert_that(actual, equal_to(expected))
